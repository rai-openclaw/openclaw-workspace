"""
Ledger operations for Bob's ingestion pipeline.
Handles safe read/write to the trades ledger with duplicate detection.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def generate_trade_id(event: Dict[str, Any]) -> str:
    """Generate deterministic ID from trade parameters (excluding timestamp for duplicate detection)."""
    # Exclude timestamp - same trade executed at different times should have same ID
    event_id_input = f"{event.get('ticker', '')}{event.get('strike', '')}{event.get('expiration', '')}{event.get('contracts', '')}{event.get('price', '')}{event.get('event_type', '')}"
    return hashlib.sha1(event_id_input.encode()).hexdigest()[:16]


def load_ledger() -> Dict[str, Any]:
    """Load the ledger from disk."""
    if not LEDGER_PATH.exists():
        return {"events": []}
    
    try:
        with open(LEDGER_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"events": []}


def save_ledger(ledger: Dict[str, Any]) -> None:
    """Save the ledger to disk."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def get_existing_trade_ids() -> set:
    """Get all existing trade IDs from the ledger."""
    ledger = load_ledger()
    return {event.get("id") for event in ledger.get("events", []) if event.get("id")}


def append_trade(event: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Safely append trade to ledger with duplicate detection.
    
    Returns: (success: bool, message: str)
    """
    # Generate trade ID
    trade_id = generate_trade_id(event)
    event["id"] = trade_id
    
    # Check for duplicate
    existing_ids = get_existing_trade_ids()
    if trade_id in existing_ids:
        return False, f"Duplicate skipped: {event.get('ticker', '?')} {event.get('contracts', 0)} contracts"
    
    # Load, append, save with file locking
    try:
        with open(LEDGER_PATH, "r+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read()
                if content.strip():
                    ledger = json.loads(content)
                else:
                    ledger = {"events": []}
                
                ledger["events"].append(event)
                
                f.seek(0)
                f.truncate()
                json.dump(ledger, f, indent=2)
                
                return True, f"Added trade: {event.get('ticker', '?')} {event.get('contracts', 0)} contracts @ ${event.get('price', 0)}"
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return False, f"Write error: {str(e)}"
