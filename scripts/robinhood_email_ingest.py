"""
Robinhood Email Trade Ingestion Script
Parses Robinhood trade confirmation emails and adds them to the ledger.
"""
import re
import hashlib
import json
import fcntl
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, Any

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def parse_robinhood_email(body: str) -> Optional[Dict[str, Any]]:
    """
    Extract option trade data from Robinhood email body.
    
    Example email:
    Your limit order to buy 3 contracts of ROST $175.00 Put 3/6 executed 
    at an average price of $5.00 per contract on March 4, 2026 at 9:44 AM ET
    
    Returns: dict with trade event or None if parsing fails
    """
    # Match: buy/sell N contracts of TICKER $STRIKE PUT/CALL MM/DD
    trade_match = re.search(
        r"(buy|sell)\s+(\d+)\s+contracts?\s+of\s+([A-Z]+)\s+\$?([\d.]+)\s+(Put|Call)\s+(\d+/\d+)",
        body,
        re.IGNORECASE
    )
    
    if not trade_match:
        print("⚠️ Could not find trade pattern in email")
        return None
    
    side = trade_match.group(1).lower()
    contracts = int(trade_match.group(2))
    ticker = trade_match.group(3)
    strike = float(trade_match.group(4))
    option_type = trade_match.group(5).upper()
    expiration_raw = trade_match.group(6)
    
    # Extract price per contract
    price_match = re.search(r"average price of \$?([\d.]+)", body)
    price = float(price_match.group(1)) if price_match else None
    
    if price is None:
        print("⚠️ Could not extract price from email")
        return None
    
    # Extract timestamp
    timestamp_match = re.search(
        r"on ([A-Za-z]+ \d{1,2},? \d{4}) at (\d{1,2}:\d{2} [AP]M)",
        body
    )
    
    if not timestamp_match:
        print("⚠️ Could not extract timestamp from email")
        return None
    
    dt_string = f"{timestamp_match.group(1)} {timestamp_match.group(2)}"
    # Handle optional comma after date
    dt_string = dt_string.replace(",", "")
    
    try:
        timestamp = datetime.strptime(dt_string, "%B %d %Y %I:%M %p")
    except ValueError:
        try:
            timestamp = datetime.strptime(dt_string, "%B %d, %Y %I:%M %p")
        except ValueError as e:
            print(f"⚠️ Could not parse timestamp '{dt_string}': {e}")
            return None
    
    # Handle partial fills - check if this is a partial execution
    partial_match = re.search(r"So Far, (\d+) of (\d+) contracts", body)
    if partial_match:
        contracts = int(partial_match.group(1))
    
    # Parse expiration date
    try:
        month, day = expiration_raw.split("/")
        # Use the year from the timestamp
        expiration = date(timestamp.year, int(month), int(day))
    except ValueError as e:
        print(f"⚠️ Could not parse expiration '{expiration_raw}': {e}")
        return None
    
    # Determine event type
    # Buy = BUY_TO_CLOSE (closing a short position)
    # Sell = SELL_TO_OPEN (opening a new short position)
    if side == "buy":
        event_type = "BUY_TO_CLOSE"
    else:
        event_type = "SELL_TO_OPEN"
    
    # Create event
    event = {
        "timestamp": timestamp.isoformat(),
        "ticker": ticker,
        "option_type": option_type,
        "strike": strike,
        "expiration": expiration.isoformat(),
        "contracts": contracts,
        "price": price,
        "event_type": event_type,
        "account": "Robinhood",
        "source": "email_ingest"
    }
    
    # Generate deterministic ID
    event_id_input = f"{event['timestamp']}{ticker}{strike}{expiration}{contracts}{price}{event_type}"
    event["id"] = hashlib.sha1(event_id_input.encode()).hexdigest()[:16]
    
    return event


def append_trade(event: dict) -> bool:
    """
    Safely append a trade to the ledger, preventing duplicates.
    Uses file locking for concurrent write safety.
    
    Returns: True if appended, False if duplicate
    """
    # Ensure ledger directory exists
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Create ledger if it doesn't exist
    if not LEDGER_PATH.exists():
        with open(LEDGER_PATH, "w") as f:
            json.dump({"events": []}, f, indent=2)
    
    # Use file locking for concurrent write safety
    with open(LEDGER_PATH, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        try:
            # Read current data
            f.seek(0)
            data = json.load(f)
            
            if "events" not in data:
                data["events"] = []
            
            # Check for duplicates using ID
            existing_ids = {e.get("id") for e in data["events"]}
            
            if event["id"] in existing_ids:
                print(f"⚠️ Duplicate trade ignored: {event['ticker']} {event['contracts']} contracts @ ${event['price']}")
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            
            # Append new event
            data["events"].append(event)
            
            # Write back
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            
            print(f"✅ Added trade: {event['ticker']} {event['contracts']} {event['option_type']} ${event['strike']} @ ${event['price']}")
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    return True


def process_email(body: str) -> bool:
    """
    Process a Robinhood email and add to ledger if valid.
    
    Returns: True if trade was added, False otherwise
    """
    event = parse_robinhood_email(body)
    
    if event:
        return append_trade(event)
    
    return False


if __name__ == "__main__":
    # Test with example email
    test_email = """Your limit order to sell 10 contracts of OKTA $59.00 Put 3/6 
    executed at an average price of $31.00 per contract on March 4, 2026 at 3:24 PM ET."""
    
    event = parse_robinhood_email(test_email)
    if event:
        print(json.dumps(event, indent=2))
        append_trade(event)
