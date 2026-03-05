"""
Expiration Checker
Detects expired worthless options and creates close events.
"""
import json
import fcntl
import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def load_ledger() -> dict:
    """Load the ledger data."""
    if not LEDGER_PATH.exists():
        return {"events": []}
    
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(data: dict):
    """Save the ledger data."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_open_positions() -> List[Dict]:
    """
    Get current open positions from the ledger.
    Tracks position state by computing net contracts.
    
    NOTE: This tracks the CURRENT state based on SELL_TO_OPEN/BUY_TO_CLOSE events.
    It does NOT automatically expire positions - use detect_expired_positions() for that.
    """
    data = load_ledger()
    events = data.get("events", [])
    
    # Track positions: key -> {ticker, strike, expiration, option_type, contracts, account, ...}
    positions = {}
    
    for event in events:
        if event.get("event_type") in ["EXPIRE_WORTHLESS", "EXERCISED", "ASSIGNED"]:
            # These events close positions
            key = _make_position_key(event)
            if key in positions:
                del positions[key]
            continue
        
        contracts = event.get("contracts", 0)
        key = _make_position_key(event)
        
        if key not in positions:
            positions[key] = {
                "ticker": event["ticker"],
                "strike": event["strike"],
                "expiration": event["expiration"],
                "option_type": event["option_type"],
                "contracts": 0,
                "account": event.get("account", "Robinhood"),
                "opened_at": event.get("timestamp"),
                "entry_price": event.get("price"),
            }
        
        # Update contract count based on event type
        if event["event_type"] in ["SELL_TO_OPEN", "SELL_TO_CLOSE"]:
            delta = contracts if event["event_type"] == "SELL_TO_OPEN" else -contracts
        elif event["event_type"] in ["BUY_TO_OPEN", "BUY_TO_CLOSE"]:
            delta = contracts if event["event_type"] == "BUY_TO_OPEN" else -contracts
        else:
            delta = 0
        
        positions[key]["contracts"] += delta
        
        # Remove if closed
        if positions[key]["contracts"] <= 0:
            del positions[key]
    
    return list(positions.values())


def _make_position_key(event: Dict) -> str:
    """Create a unique key for a position."""
    return f"{event['ticker']}_{event['strike']}_{event['expiration']}_{event.get('account', 'Robinhood')}"


def detect_expired_positions(as_of_date: date = None, account_filter: str = None) -> List[Dict]:
    """
    Detect options that have expired without being closed.
    Creates EXPIRE_WORTHLESS events for remaining open contracts.
    
    Args:
        as_of_date: Date to check against. Defaults to today.
        account_filter: Only process this account. If None, process all.
        
    Returns: List of expired position dicts ready for EXPIRE_WORTHLESS events
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    data = load_ledger()
    events = data.get("events", [])
    
    # Track positions with remaining contracts
    positions = {}
    
    for event in events:
        # Skip if doesn't match account filter
        if account_filter and event.get('account') != account_filter:
            continue
        
        # Skip EXPIRE_WORTHLESS - already handled
        if event.get("event_type") == "EXPIRE_WORTHLESS":
            continue
            
        key = _make_position_key(event)
        contracts = event.get("contracts", 0)
        
        if key not in positions:
            positions[key] = {
                "ticker": event["ticker"],
                "strike": event["strike"],
                "expiration": event["expiration"],
                "option_type": event.get("option_type", "PUT"),
                "contracts": 0,
                "account": event.get("account", "Robinhood"),
            }
        
        # Track net position
        if event["event_type"] in ["SELL_TO_OPEN", "SELL_TO_CLOSE"]:
            delta = contracts if event["event_type"] == "SELL_TO_OPEN" else -contracts
        elif event["event_type"] in ["BUY_TO_OPEN", "BUY_TO_CLOSE"]:
            delta = contracts if event["event_type"] == "BUY_TO_OPEN" else -contracts
        else:
            delta = 0
        
        positions[key]["contracts"] += delta
    
    # Find expired positions with remaining contracts
    expired = []
    
    for key, pos in positions.items():
        if pos["contracts"] <= 0:
            continue
            
        exp_date = date.fromisoformat(pos["expiration"]) if isinstance(pos["expiration"], str) else pos["expiration"]
        
        if exp_date < as_of_date:
            expired.append({
                "ticker": pos["ticker"],
                "strike": pos["strike"],
                "expiration": pos["expiration"],
                "option_type": pos["option_type"],
                "contracts": pos["contracts"],  # Remaining contracts to expire
                "account": pos["account"],
            })
    
    return expired


def create_expire_worthless_event(position: Dict, expire_date: date = None) -> Dict:
    """
    Create an EXPIRE_WORTHLESS event for a position.
    
    Args:
        position: Position dict from get_open_positions()
        expire_date: Date the option expired. Defaults to position's expiration.
        
    Returns: Event dict ready to append to ledger
    """
    if expire_date is None:
        expire_date = date.fromisoformat(position["expiration"]) if isinstance(position["expiration"], str) else position["expiration"]
    
    # Use market close time (16:00) for expiration timestamp
    timestamp = datetime.combine(expire_date, datetime.strptime("16:00", "%H:%M").time()).isoformat()
    
    event = {
        "timestamp": timestamp,
        "ticker": position["ticker"],
        "option_type": position.get("option_type", "PUT"),
        "strike": position["strike"],
        "expiration": position["expiration"],
        "contracts": position["contracts"],
        "price": 0,  # Worthless = $0
        "event_type": "EXPIRE_WORTHLESS",
        "account": position["account"],
        "source": "expiration_checker"
    }
    
    # Generate deterministic ID
    event_id_input = f"{event['timestamp']}{position['ticker']}{position['strike']}{position['expiration']}{position['contracts']}EXPIRE_WORTHLESS"
    event["id"] = hashlib.sha1(event_id_input.encode()).hexdigest()[:16]
    
    return event


def append_expire_worthless_events(events: List[Dict]) -> int:
    """
    Append EXPIRE_WORTHLESS events to the ledger.
    
    Args:
        events: List of event dicts
        
    Returns: Number of events appended
    """
    if not events:
        return 0
    
    with open(LEDGER_PATH, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        try:
            data = json.load(f)
            if "events" not in data:
                data["events"] = []
            
            existing_ids = {e.get("id") for e in data["events"]}
            
            appended = 0
            for event in events:
                if event["id"] not in existing_ids:
                    data["events"].append(event)
                    appended += 1
            
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    return appended


def run_expiration_check(as_of_date: date = None) -> int:
    """
    Main function to run expiration check.
    Detects expired positions and creates EXPIRE_WORTHLESS events.
    
    Args:
        as_of_date: Date to check against. Defaults to today.
        
    Returns: Number of expired positions processed
    """
    expired_positions = detect_expired_positions(as_of_date)
    
    if not expired_positions:
        print("No expired positions found.")
        return 0
    
    events = [create_expire_worthless_event(pos) for pos in expired_positions]
    
    appended = append_expire_worthless_events(events)
    
    if appended > 0:
        print(f"✅ Created {appended} EXPIRE_WORTHLESS events for expired positions:")
        for pos in expired_positions:
            print(f"   - {pos['ticker']} ${pos['strike']} {pos['option_type']} x{pos['contracts']}")
    
    return appended


if __name__ == "__main__":
    # Test
    run_expiration_check()
