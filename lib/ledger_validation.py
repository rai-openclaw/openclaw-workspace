"""
Ledger Validation
Detects issues in the trades ledger without modifying it.
"""
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

LEDGER_PATH = Path("~/.openclaw/workspace/data/options/trades.json").expanduser()


def load_ledger() -> dict:
    """Load the ledger data."""
    if not LEDGER_PATH.exists():
        return {"events": []}
    
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def validate_ledger() -> dict:
    """
    Validate the ledger and return a report of issues.
    
    Returns dict with:
    - orphan_buy_to_close: list of BUY_TO_CLOSE without matching SELL_TO_OPEN
    - orphan_expire_worthless: list of EXPIRE_WORTHLESS without position
    - negative_balances: list of positions with negative contract counts
    """
    data = load_ledger()
    events = data.get("events", [])
    
    # Track positions: key -> {sells: int, buys: int, opens: int, closes: int}
    positions = defaultdict(lambda: {"sells": 0, "buys": 0, "opens": 0, "closes": 0})
    
    # First pass: categorize events
    for event in events:
        key = _make_key(event)
        
        if event.get("event_type") == "SELL_TO_OPEN":
            positions[key]["sells"] += event.get("contracts", 0)
            positions[key]["opens"] += event.get("contracts", 0)
        elif event.get("event_type") == "BUY_TO_CLOSE":
            positions[key]["buys"] += event.get("contracts", 0)
            positions[key]["closes"] += event.get("contracts", 0)
        elif event.get("event_type") == "SELL_TO_CLOSE":
            positions[key]["sells"] += event.get("contracts", 0)
            positions[key]["closes"] += event.get("contracts", 0)
        elif event.get("event_type") == "BUY_TO_OPEN":
            positions[key]["buys"] += event.get("contracts", 0)
            positions[key]["opens"] += event.get("contracts", 0)
    
    # Second pass: find orphan BUY_TO_CLOSE events
    orphan_buy_to_close = []
    for event in events:
        if event.get("event_type") != "BUY_TO_CLOSE":
            continue
        
        key = _make_key(event)
        position = positions[key]
        
        # If we have more closes than opens for this position, it's an orphan
        if position["closes"] > position["opens"]:
            orphan_buy_to_close.append({
                "ticker": event.get("ticker"),
                "strike": event.get("strike"),
                "expiration": event.get("expiration"),
                "option_type": event.get("option_type"),
                "contracts": event.get("contracts"),
                "timestamp": event.get("timestamp"),
                "account": event.get("account"),
                "id": event.get("id")
            })
    
    # Find orphan EXPIRE_WORTHLESS (position never opened)
    orphan_expire_worthless = []
    for event in events:
        if event.get("event_type") != "EXPIRE_WORTHLESS":
            continue
        
        key = _make_key(event)
        position = positions[key]
        
        # If no opens for this position, it's an orphan
        if position["opens"] == 0:
            orphan_expire_worthless.append({
                "ticker": event.get("ticker"),
                "strike": event.get("strike"),
                "expiration": event.get("expiration"),
                "option_type": event.get("option_type"),
                "contracts": event.get("contracts"),
                "timestamp": event.get("timestamp"),
                "account": event.get("account"),
                "id": event.get("id")
            })
    
    # Find negative balances
    negative_balances = []
    for key, position in positions.items():
        # Net position = sells - buys (for shorts) or buys - sells (for longs)
        # A negative balance means we closed more than we opened
        net = position["sells"] - position["buys"]
        if net < 0:
            ticker, strike, expiration, account = key.split("|")
            negative_balances.append({
                "ticker": ticker,
                "strike": float(strike),
                "expiration": expiration,
                "account": account,
                "net_contracts": net
            })
    
    return {
        "orphan_buy_to_close": orphan_buy_to_close,
        "orphan_expire_worthless": orphan_expire_worthless,
        "negative_balances": negative_balances,
        "total_events": len(events)
    }


def _make_key(event: dict) -> str:
    """Create a unique key for a position."""
    return f"{event.get('ticker')}|{event.get('strike')}|{event.get('expiration')}|{event.get('account', 'Unknown')}"


def print_validation_report():
    """Print a human-readable validation report."""
    report = validate_ledger()
    
    print("=" * 60)
    print("LEDGER VALIDATION REPORT")
    print("=" * 60)
    print(f"Total events: {report['total_events']}")
    print()
    
    # Orphan BUY_TO_CLOSE
    print("-" * 60)
    if report["orphan_buy_to_close"]:
        print(f"⚠️  ORPHAN BUY_TO_CLOSE: {len(report['orphan_buy_to_close'])} found")
        for e in report["orphan_buy_to_close"]:
            print(f"   Ticker: {e['ticker']}")
            print(f"   Strike: ${e['strike']}")
            print(f"   Expiration: {e['expiration']}")
            print(f"   Contracts: {e['contracts']}")
            print()
    else:
        print("✅ No orphan BUY_TO_CLOSE events")
    print()
    
    # Orphan EXPIRE_WORTHLESS
    print("-" * 60)
    if report["orphan_expire_worthless"]:
        print(f"⚠️  ORPHAN EXPIRE_WORTHLESS: {len(report['orphan_expire_worthless'])} found")
        for e in report["orphan_expire_worthless"][:10]:  # Limit output
            print(f"   Ticker: {e['ticker']} ${e['strike']} {e['option_type']} x{e['contracts']}")
        if len(report["orphan_expire_worthless"]) > 10:
            print(f"   ... and {len(report['orphan_expire_worthless']) - 10} more")
        print()
    else:
        print("✅ No orphan EXPIRE_WORTHLESS events")
    print()
    
    # Negative balances
    print("-" * 60)
    if report["negative_balances"]:
        print(f"⚠️  NEGATIVE BALANCES: {len(report['negative_balances'])} found")
        for e in report["negative_balances"]:
            print(f"   {e['ticker']} ${e['strike']} {e['expiration']}: {e['net_contracts']} contracts")
        print()
    else:
        print("✅ No negative contract balances")
    print()
    
    print("=" * 60)


if __name__ == "__main__":
    print_validation_report()
