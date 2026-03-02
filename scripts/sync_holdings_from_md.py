#!/usr/bin/env python3
"""
sync_holdings_from_md.py - Sync holdings from unified_portfolio_tracker.md to JSON
"""
import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MD_FILE = WORKSPACE / "portfolio" / "unified_portfolio_tracker.md"
OUTPUT_FILE = WORKSPACE / "data" / "portfolio" / "holdings.json"

def parse_holdings_md():
    """Parse unified_portfolio_tracker.md and extract tickers by account"""
    
    if not MD_FILE.exists():
        print(f"Source file not found: {MD_FILE}")
        return None
    
    with open(MD_FILE) as f:
        content = f.read()
    
    # Find all account sections
    accounts = {
        "robinhood": [],
        "schwab_sep_ira": [],
        "schwab_csp": [],
        "roth_ira": [],
        "other": []
    }
    
    # Map account names to keys
    account_map = {
        "Robinhood": "robinhood",
        "SEP-IRA": "schwab_sep_ira",
        "CSP": "schwab_csp",
        "Roth IRA": "roth_ira",
        "Roth-IRA": "roth_ira",
    }
    
    current_account = "other"
    
    for line in content.split("\n"):
        # Check for account headers
        if "## Account:" in line:
            for name, key in account_map.items():
                if name.lower() in line.lower():
                    current_account = key
                    break
            else:
                current_account = "other"
        
        # Extract tickers from table rows (| TICKER | ...)
        if line.startswith("|") and "|" in line[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                ticker = parts[1].upper()
                # Valid ticker: 1-5 uppercase letters
                if ticker and re.match(r"^[A-Z]{1,5}$", ticker) and ticker not in ["TICKER", "SHARES", "COST", "NOTES", "TYPE", "STRIKE", "EXPIRATION", "CONTRACTS", "PREMIUM", "ENTRY", "ASSET", "AMOUNT", "QUANTITY"]:
                    if ticker not in accounts[current_account]:
                        accounts[current_account].append(ticker)
    
    return accounts

def main():
    print("=== Syncing holdings from MD ===")
    
    accounts = parse_holdings_md()
    
    if not accounts:
        print("Failed to parse holdings")
        return
    
    # Load existing
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
    else:
        data = {"accounts": {}, "last_synced": None}
    
    # Update
    data["accounts"] = accounts
    data["last_synced"] = datetime.now().isoformat()
    
    # Write
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Synced {sum(len(v) for v in accounts.values())} holdings")
    for acc, tickers in accounts.items():
        if tickers:
            print(f"  {acc}: {tickers}")
    
    print(f"Written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
