#!/usr/bin/env python3
"""
Robinhood Scanner for Bob's Ingestion Pipeline
Scans Gmail for Robinhood option order emails and writes to ledger.

Usage:
    python3 robinhood_scanner.py <midday|end_of_day|safety>

Schedule:
    midday     - 11:00 AM PST
    end_of_day - 1:15 PM PST  
    safety     - 6:00 PM PST
"""
import imaplib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo
import email.message
from email.message import Message
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import Bob's modules
sys.path.insert(0, str(Path(__file__).parent))
from ledger import append_trade, load_ledger
from events import emit_trade_detected, emit_ledger_updated, emit_ingestion_error

# Add lib to path for run registry
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "lib"))
from runRegistry import create_run, complete_run

# Configure logging
LOG_PATH = Path("~/.openclaw/workspace/logs/bob_robinhood.log").expanduser()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bob.robinhood_scanner")

# Paths
AGENT_DIR = Path(__file__).parent
ENV_PATH = AGENT_DIR.parent.parent / ".env"
LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def load_credentials() -> Dict[str, str]:
    """Load Gmail credentials from .env file."""
    credentials = {"user": "", "password": ""}
    
    # Try .env in agent directory first
    env_files = [
        ENV_PATH,
        Path("~/.openclaw/workspace/.env").expanduser(),
    ]
    
    for env_path in env_files:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key == "GMAIL_USER":
                            credentials["user"] = value
                        elif key in ("GMAIL_APP_PASSWORD", "GMAIL_PASSWORD"):
                            credentials["password"] = value
    
    if not credentials["user"] or not credentials["password"]:
        raise ValueError("GMAIL credentials not found in .env")
    
    return credentials


def connect_gmail(credentials: Dict[str, str]) -> imaplib.IMAP4_SSL:
    """Connect to Gmail via IMAP."""
    logger.info("Connecting to Gmail...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(credentials["user"], credentials["password"])
    logger.info("Connected!")
    return mail


def search_robinhood_emails(mail, days_back: int = 3) -> List[Message]:
    """
    Search for Robinhood option order emails.
    
    Args:
        mail: IMAP connection
        days_back: Only search emails from the last N days
    
    Returns:
        List of email messages
    """
    mail.select("INBOX")
    
    # Calculate date filter (last N days)
    from datetime import date, timedelta
    search_date = (date.today() - timedelta(days=days_back)).strftime("%d-%b-%Y")
    
    # Search for both subject types
    subjects = ["Option order executed", "Option order partially executed"]
    all_emails = []
    
    for subject in subjects:
        search_query = f'SUBJECT "{subject}" SINCE {search_date}'
        logger.info(f"Searching: {subject} since {search_date}...")
        
        try:
            status, messages = mail.search(None, search_query)
            if status != "OK":
                logger.warning(f"Search failed for {subject}")
                continue
                
            message_ids = messages[0].split()
            logger.info(f"Found {len(message_ids)} emails for '{subject}'")
            
            for msg_id in message_ids:
                try:
                    status, msg_data = mail.fetch(msg_id, "(RFC822)")
                    if status == "OK":
                        msg = email.message_from_bytes(msg_data[0][1])
                        all_emails.append(msg)
                except Exception as e:
                    logger.debug(f"Failed to fetch message {msg_id}: {e}")
        except Exception as e:
            logger.warning(f"Search error for {subject}: {e}")
    
    return all_emails


def parse_email_for_trade(msg: Message) -> Optional[Dict[str, Any]]:
    """Extract trade from email message with unified timestamp handling."""
    try:
        # Get email body - handle both HTML and plain text
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
                elif content_type == "text/html" and not body:
                    # Fall back to HTML if no plain text
                    html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    # Strip HTML tags to get text
                    import re as re_module
                    body = re_module.sub(r'<[^>]+>', ' ', html_body)
                    body = re_module.sub(r'\s+', ' ', body)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="ignore")
        
        if not body:
            return None
        
        # Parse ticker - look for "X contracts of TICKER"
        ticker_match = re.search(r'(\d+)\s+contracts?\s+of\s+([A-Z]{1,5})\s+\$', body)
        if not ticker_match:
            return None
        ticker = ticker_match.group(2)
        
        # Parse side (buy/sell) - handle variable whitespace
        side = None
        if re.search(r'Your\s+limit\s+order\s+to\s+buy', body):
            side = "buy"
        elif re.search(r'Your\s+limit\s+order\s+to\s+sell', body):
            side = "sell"
        
        if not side:
            return None
        
        # Parse contracts
        contracts_match = re.search(r'(\d+)\s+contracts?\s+of\s+', body)
        if not contracts_match:
            return None
        contracts = int(contracts_match.group(1))
        
        # Check for partial fills
        partial_match = re.search(r"So Far,\s*(\d+)\s*of\s*(\d+)\s*contracts", body)
        if partial_match:
            contracts = int(partial_match.group(1))
        
        # Parse strike price and option type
        strike_match = re.search(r'\$(\d+(?:\.\d+)?)\s+(Put|Call)\s+', body)
        if not strike_match:
            return None
        strike = float(strike_match.group(1))
        option_type = "PUT" if strike_match.group(2) == "Put" else "CALL"
        
        # Parse expiration date
        expiration_match = re.search(r'(\d{1,2})/(\d{1,2})(?!\d)', body)
        if not expiration_match:
            return None
        exp_month = int(expiration_match.group(1))
        exp_day = int(expiration_match.group(2))
        
        # Parse premium/price - check for "per contract" to normalize
        # Robinhood emails show price in different formats:
        # - "executed at an average price of $15.00" = per contract (need to divide by 100)
        # - "$15.00 per contract" = per contract (need to divide by 100)
        # Our ledger stores per-share price, so normalize: $15.00/contract -> $0.15/share
        price = None
        per_contract = "per contract" in body.lower()
        
        price_match = re.search(r'executed at an average price of\s*\$\s*(\d+(?:\.\d+)?)', body)
        if not price_match:
            price_match = re.search(r'approximate\s*\$\s*(\d+(?:\.\d+)?)', body)
        if not price_match:
            price_match = re.search(r'\$(\d+(?:\.\d+)?)\s*per\s*contract', body)
        
        if price_match:
            price = float(price_match.group(1))
            # Normalize: if "per contract" is mentioned, convert to per-share (divide by 100)
            if per_contract:
                price = price / 100.0
                logger.debug(f"Normalized per-contract price: {price_match.group(1)} -> {price}")
        
        if price is None:
            return None
        
        # Parse timestamp from email body
        # Format: "March 5, 2026 at 10:18 AM" or similar
        timestamp_match = re.search(r'on\s+([A-Za-z]+,?\s+\d{1,2},?\s+\d{4})\s+at\s+(\d{1,2}:\d{2}\s*[AP]M)', body)
        
        if timestamp_match:
            dt_string = f"{timestamp_match.group(1)} {timestamp_match.group(2)}"
            dt_string = dt_string.replace(",", "")
            
            # Parse as naive datetime
            timestamp = datetime.strptime(dt_string, "%B %d %Y %I:%M %p")
            
            # Interpret as Eastern Time and convert to UTC
            et_tz = ZoneInfo("America/New_York")
            timestamp_et = timestamp.replace(tzinfo=et_tz)
            timestamp_utc = timestamp_et.astimezone(timezone.utc)
            
            # Format as ISO 8601 UTC
            formatted_timestamp = timestamp_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            # Fallback to current time
            formatted_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        # Determine event type
        event_type = "BUY_TO_CLOSE" if side == "buy" else "SELL_TO_OPEN"
        
        # Get current year for expiration
        current_year = datetime.now().year
        
        # Create event object
        event = {
            "timestamp": formatted_timestamp,
            "account": "Robinhood",
            "ticker": ticker,
            "option_type": option_type,
            "strike": strike,
            "expiration": f"{current_year}-{exp_month:02d}-{exp_day:02d}",
            "contracts": contracts,
            "price": price,
            "event_type": event_type,
            "source": "robinhood_email",
        }
        
        return event
        
    except Exception as e:
        logger.debug(f"Parse error: {e}")
        return None


def check_and_create_expirations() -> int:
    """
    Check for expired Robinhood options and create EXPIRE_WORTHLESS events.
    
    Rules:
    - Only process Robinhood positions (not Schwab)
    - Open position = SELL_TO_OPEN exists + no BUY_TO_CLOSE + no ASSIGNMENT + no EXPIRE_WORTHLESS
    - Expiration condition: expiration_date < today
    - Idempotent: never create duplicate expiration events
    
    Returns:
        Number of expiration events created
    """
    import hashlib
    from datetime import date, datetime, timezone, timedelta
    from pathlib import Path
    
    HOME_DIR = Path.home()
    LEDGER_PATH = HOME_DIR / ".openclaw" / "workspace" / "data" / "options" / "trades.json"
    
    today = date.today()
    
    try:
        # Load ledger
        try:
            with open(LEDGER_PATH) as f:
                ledger = json.load(f)
        except FileNotFoundError:
            logger.error(f"Ledger not found: {LEDGER_PATH}. Cannot continue ingestion.")
            return {"error": "Ledger file not found", "status": "failed"}
        except json.JSONDecodeError as e:
            logger.error(f"Ledger corrupted (invalid JSON): {LEDGER_PATH}. Error: {e}. Manual restore required.")
            return {"error": f"Ledger JSON corrupted: {e}", "status": "failed"}
        
        events = ledger.get("events", [])
        
        # Build position map: key -> {opens, closes, expirations, account}
        # Key: ticker|strike|expiration
        position_map = {}
        
        for event in events:
            account = event.get("account", "")
            if account != "Robinhood":
                continue
            
            ticker = event.get("ticker", "")
            strike = event.get("strike", 0)
            expiration = event.get("expiration", "")
            event_type = event.get("event_type", "")
            contracts = event.get("contracts", 0)
            option_type = event.get("option_type", "PUT")  # Default to PUT for expirations
            
            key = f"{ticker}|{strike}|{expiration}"
            
            if key not in position_map:
                position_map[key] = {
                    "ticker": ticker,
                    "strike": strike,
                    "expiration": expiration,
                    "account": account,
                    "option_type": option_type,
                    "opens": 0,
                    "closes": 0,
                    "assignments": 0,
                    "expired": 0
                }
            
            if event_type == "SELL_TO_OPEN":
                position_map[key]["opens"] += contracts
                position_map[key]["option_type"] = option_type  # Capture from opening event
            elif event_type == "BUY_TO_CLOSE":
                position_map[key]["closes"] += contracts
            elif event_type == "ASSIGNMENT":
                position_map[key]["assignments"] += contracts
            elif event_type == "EXPIRE_WORTHLESS":
                position_map[key]["expired"] += contracts
        
        # Find open positions that have expired
        expirations_to_create = []
        
        for key, pos in position_map.items():
            opens = pos["opens"]
            closes = pos["closes"]
            assignments = pos["assignments"]
            expired = pos["expired"]
            
            # Check if position is open
            net_position = opens - closes - assignments - expired
            if net_position <= 0:
                continue
            
            # Check if expired
            try:
                exp_date = datetime.strptime(pos["expiration"], "%Y-%m-%d").date()
            except:
                continue
            
            if exp_date > today:
                continue
            
            # Only expire if:
            # - expiration_date < today (expired yesterday or earlier)
            # - OR expiration_date == today AND current_time >= 1:00 PM PST
            from zoneinfo import ZoneInfo
            current_time_pst = datetime.now(ZoneInfo("America/Los_Angeles")).hour
            cutoff_hour_pst = 13  # 1 PM PST
            
            if exp_date == today and current_time_pst < cutoff_hour_pst:
                continue  # Don't expire during morning scans (before 1 PM PST)
            
            # Create expiration event
            # Generate trade_id for idempotency check (include option_type)
            event_id_input = f"{pos['ticker']}{pos['strike']}{pos['expiration']}{pos.get('option_type', 'PUT')}EXPIRE_WORTHLESS{pos['account']}"
            trade_id = hashlib.sha1(event_id_input.encode()).hexdigest()[:16]
            
            # Check if already expired (include option_type in key)
            existing = any(
                e.get("id") == trade_id 
                for e in events 
                if e.get("event_type") == "EXPIRE_WORTHLESS"
                and f"{e.get('ticker')}|{e.get('strike')}|{e.get('expiration')}|{e.get('option_type', 'PUT')}" == f"{pos['ticker']}|{pos['strike']}|{pos['expiration']}|{pos.get('option_type', 'PUT')}"
            )
            
            if existing:
                continue
            
            expirations_to_create.append({
                "id": trade_id,
                "event_type": "EXPIRE_WORTHLESS",
                "account": pos["account"],
                "ticker": pos["ticker"],
                "strike": pos["strike"],
                "option_type": pos.get("option_type", "PUT"),
                "expiration": pos["expiration"],
                "contracts": net_position,
                "price": 0,
                # Use actual expiration date, not current date. Market close: 1:05 PM PST = 21:05 UTC
                "timestamp": f"{pos['expiration']}T21:05:00.000Z",
                "source": "expiration_engine",
            })
        
        # Write expirations to ledger via append_trade() for thread-safety
        created_count = 0
        for exp_event in expirations_to_create:
            # Use append_trade which handles duplicate detection and file locking
            success, message = append_trade(exp_event)
            if success:
                created_count += 1
                logger.info(f"Expiration created: {message}")
        
        logger.info(f"Expiration check: {created_count} events created")
        return created_count
        
    except Exception as e:
        logger.warning(f"Expiration check failed: {e}")
        return 0


def run(schedule: str) -> Dict[str, Any]:
    """
    Main ingestion runner.
    
    Args:
        schedule: One of 'midday', 'end_of_day', 'safety'
    
    Returns:
        Scan result dict
    """
    # Map schedule to job name
    job_name_map = {
        "midday": "robinhood-midday-ingestion",
        "end_of_day": "robinhood-eod-ingestion",
        "safety": "robinhood-safety-scan"
    }
    job_name = job_name_map.get(schedule, "robinhood-ingestion")
    
    # Create run entry for tracking
    run_id = create_run(job_name, "bob")
    start_time = time.time()
    
    try:
        # 1. Load credentials
        credentials = load_credentials()
        
        # 2. Connect to Gmail
        mail = connect_gmail(credentials)
        
        # 3. Search for emails (last 3 days)
        emails = search_robinhood_emails(mail, days_back=3)
        mail.logout()
        
        # 4. Parse trades
        trades = []
        for msg in emails:
            trade = parse_email_for_trade(msg)
            if trade:
                trades.append(trade)
        
        logger.info(f"Parsed {len(trades)} trades from {len(emails)} emails")
        
        # 5. Write to ledger
        new_count = 0
        for trade in trades:
            success, message = append_trade(trade)
            if success:
                new_count += 1
                # Emit TRADE_DETECTED (non-blocking)
                try:
                    emit_trade_detected(schedule, trade)
                except Exception as e:
                    logger.warning(f"Event emission failed: {e}")
            logger.info(message)
        
        duplicates = len(trades) - new_count
        
        # 6. Run expiration checker (always runs, even if no new emails)
        expirations_created = check_and_create_expirations()
        
        runtime_ms = int((time.time() - start_time) * 1000)
        
        # 6. Emit LEDGER_UPDATED (non-blocking)
        try:
            emit_ledger_updated(schedule, new_count, duplicates, runtime_ms)
        except Exception as e:
            logger.warning(f"Event emission failed: {e}")
        
        logger.info(f"Ingestion complete: {new_count} new, {duplicates} duplicates, {expirations_created} expirations, {runtime_ms}ms")
        
        # Complete run as success
        summary = f"Ingestion complete: {new_count} new trades, {duplicates} duplicates, {expirations_created} expirations"
        complete_run(run_id, "success", summary)
        
        return {
            "new_trades": new_count,
            "duplicates_skipped": duplicates,
            "expirations_created": expirations_created,
            "runtime_ms": runtime_ms,
            "status": "success"
        }
        
    except Exception as e:
        runtime_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        error_code = "AUTH_FAILURE" if "authentication" in error_msg.lower() else "UNKNOWN"
        
        # Emit INGESTION_ERROR (non-blocking)
        try:
            emit_ingestion_error(schedule, error_msg, error_code)
        except:
            pass
        
        logger.error(f"Ingestion failed: {error_msg}")
        
        # Complete run as failed
        complete_run(run_id, "failed", f"Ingestion failed: {error_msg}")
        
        return {
            "new_trades": 0,
            "duplicates_skipped": 0,
            "runtime_ms": runtime_ms,
            "status": "error",
            "error": error_msg
        }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 robinhood_scanner.py <midday|end_of_day|safety>")
        sys.exit(1)
    
    schedule = sys.argv[1]
    if schedule not in ("midday", "end_of_day", "safety"):
        print(f"Invalid schedule: {schedule}. Use: midday, end_of_day, or safety")
        sys.exit(1)
    
    result = run(schedule)
    
    # Exit with appropriate code
    sys.exit(0 if result["status"] == "success" else 1)
