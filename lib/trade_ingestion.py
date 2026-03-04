"""
Trade Ingestion Library
Provides safe, idempotent trade appending to the ledger.
"""
import json
import fcntl
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def ensure_ledger_exists():
    """Create ledger file if it doesn't exist."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if not LEDGER_PATH.exists():
        with open(LEDGER_PATH, "w") as f:
            json.dump({"events": []}, f, indent=2)


def generate_trade_id(event: dict) -> str:
    """Generate deterministic ID from trade parameters."""
    event_id_input = f"{event['timestamp']}{event.get('ticker', '')}{event.get('strike', '')}{event.get('expiration', '')}{event.get('contracts', '')}{event.get('price', '')}{event.get('event_type', '')}"
    return hashlib.sha1(event_id_input.encode()).hexdigest()[:16]


def append_trade(event: dict, ledger_path: Path = None) -> bool:
    """
    Safely append a trade to the ledger, preventing duplicates.
    Uses file locking for concurrent write safety.
    
    Args:
        event: Trade event dict with required fields
        ledger_path: Optional custom ledger path
        
    Returns: True if appended, False if duplicate
    """
    path = ledger_path or LEDGER_PATH
    ensure_ledger_exists()
    
    # Generate ID if not present
    if "id" not in event:
        event["id"] = generate_trade_id(event)
    
    # Use file locking for concurrent write safety
    with open(path, "r+") as f:
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
                return False
            
            # Append new event
            data["events"].append(event)
            
            # Write back
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    return True


def get_all_trades(ledger_path: Path = None) -> list:
    """Read all trades from the ledger."""
    path = ledger_path or LEDGER_PATH
    
    if not path.exists():
        return []
    
    with open(path, "r") as f:
        data = json.load(f)
        return data.get("events", [])


def find_trade_by_id(trade_id: str, ledger_path: Path = None) -> Optional[dict]:
    """Find a trade by its ID."""
    trades = get_all_trades(ledger_path)
    for trade in trades:
        if trade.get("id") == trade_id:
            return trade
    return None


def get_open_positions(ledger_path: Path = None) -> list:
    """Get current open positions from the ledger."""
    trades = get_all_trades(ledger_path)
    
    # Track positions by key (ticker, strike, expiration, account)
    positions = {}
    
    for trade in trades:
        key = f"{trade['ticker']}_{trade['strike']}_{trade['expiration']}_{trade.get('account', 'Robinhood')}"
        
        contracts = trade.get('contracts', 0)
        
        if trade['event_type'] in ['SELL_TO_OPEN', 'SELL_TO_CLOSE']:
            # Selling opens or closes a position
            if trade['event_type'] == 'SELL_TO_OPEN':
                # Opening a short position
                if key not in positions:
                    positions[key] = {
                        'ticker': trade['ticker'],
                        'strike': trade['strike'],
                        'expiration': trade['expiration'],
                        'option_type': trade['option_type'],
                        'contracts': contracts,
                        'account': trade.get('account', 'Robinhood'),
                        'opened_at': trade['timestamp'],
                        'entry_price': trade['price']
                    }
                else:
                    positions[key]['contracts'] += contracts
            else:
                # Closing a short position
                if key in positions:
                    positions[key]['contracts'] -= contracts
                    if positions[key]['contracts'] <= 0:
                        del positions[key]
        
        elif trade['event_type'] in ['BUY_TO_OPEN', 'BUY_TO_CLOSE']:
            # Buying opens or closes a position
            if trade['event_type'] == 'BUY_TO_OPEN':
                # Opening a long position
                if key not in positions:
                    positions[key] = {
                        'ticker': trade['ticker'],
                        'strike': trade['strike'],
                        'expiration': trade['expiration'],
                        'option_type': trade['option_type'],
                        'contracts': contracts,
                        'account': trade.get('account', 'Robinhood'),
                        'opened_at': trade['timestamp'],
                        'entry_price': trade['price']
                    }
                else:
                    positions[key]['contracts'] += contracts
            else:
                # Closing a long position
                if key in positions:
                    positions[key]['contracts'] -= contracts
                    if positions[key]['contracts'] <= 0:
                        del positions[key]
    
    return list(positions.values())


if __name__ == "__main__":
    # Test
    ensure_ledger_exists()
    trades = get_all_trades()
    print(f"Ledger has {len(trades)} trades")
    
    open_positions = get_open_positions()
    print(f"Open positions: {len(open_positions)}")
