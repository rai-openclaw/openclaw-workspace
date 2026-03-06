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
        }
        
        return event
        
    except Exception as e:
        logger.debug(f"Parse error: {e}")
        return None


def run(schedule: str) -> Dict[str, Any]:
    """
    Main ingestion runner.
    
    Args:
        schedule: One of 'midday', 'end_of_day', 'safety'
    
    Returns:
        Scan result dict
    """
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
        runtime_ms = int((time.time() - start_time) * 1000)
        
        # 6. Emit LEDGER_UPDATED (non-blocking)
        try:
            emit_ledger_updated(schedule, new_count, duplicates, runtime_ms)
        except Exception as e:
            logger.warning(f"Event emission failed: {e}")
        
        logger.info(f"Ingestion complete: {new_count} new, {duplicates} duplicates, {runtime_ms}ms")
        
        return {
            "new_trades": new_count,
            "duplicates_skipped": duplicates,
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
