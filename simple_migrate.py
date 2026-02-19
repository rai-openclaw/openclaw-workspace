#!/usr/bin/env python3
"""
Simple migration script to convert markdown trading journals to JSON format.
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

def extract_table_from_markdown(content, start_marker, end_marker=None):
    """Extract table data from markdown between markers"""
    lines = content.split('\n')
    in_table = False
    headers = []
    rows = []
    
    for i, line in enumerate(lines):
        # Check for start marker
        if start_marker in line:
            in_table = True
            continue
        
        # Check for end marker
        if end_marker and end_marker in line and in_table:
            break
        
        if in_table:
            # Skip separator lines
            if '---' in line and '|' in line:
                continue
            
            # Parse header row
            if '|' in line and not headers and any(h in line for h in ['Ticker', 'Account', 'Date']):
                headers = [h.strip() for h in line.split('|') if h.strip()]
                continue
            
            # Parse data rows
            if '|' in line and headers and line.strip().startswith('|'):
                # Clean the line
                line = line.strip()
                if line.startswith('|'):
                    line = line[1:]
                if line.endswith('|'):
                    line = line[:-1]
                
                values = [v.strip() for v in line.split('|')]
                
                # Skip total rows
                if values and values[0] and 'TOTAL' in values[0]:
                    continue
                
                # Create row dictionary
                if len(values) >= len(headers) - 1:  # Allow for missing last column
                    row = {}
                    for j, header in enumerate(headers):
                        if j < len(values):
                            row[header] = values[j]
                        else:
                            row[header] = ''
                    rows.append(row)
    
    return headers, rows

def clean_numeric(value):
    """Clean and convert numeric values"""
    if not value:
        return None
    
    # Remove bold markers, $ signs, commas, and other non-numeric characters
    value = re.sub(r'[\*\$\+,]', '', value)
    
    # Remove emojis and special characters
    value = re.sub(r'[★⚠️%]', '', value)
    
    # Remove text like "day", "days"
    value = re.sub(r'\s*(day|days)\s*', '', value, flags=re.IGNORECASE)
    
    value = value.strip()
    
    if not value or value == '-':
        return None
    
    try:
        # Check if it's a float
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except:
        return None

def create_trade_from_realized_row(row):
    """Create trade object from realized P&L row"""
    try:
        ticker = row.get('Ticker', '').replace('**', '').strip()
        if not ticker or ticker == 'Ticker':
            return None
        
        # Parse dates
        open_date = row.get('Open Date', '').strip()
        close_date = row.get('Close Date', '').strip()
        
        # Convert 2/17 to 2026-02-17
        if '/' in open_date:
            month, day = open_date.split('/')
            open_date_iso = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            open_date_iso = "2026-02-17"
        
        if '/' in close_date:
            month, day = close_date.split('/')
            close_date_iso = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            close_date_iso = "2026-02-18"
        
        # Parse numeric values
        entry_premium = clean_numeric(row.get('Entry', ''))
        exit_premium = clean_numeric(row.get('Exit', ''))
        contracts = clean_numeric(row.get('Contracts', ''))
        realized_pnl = clean_numeric(row.get('Realized P&L', ''))
        
        # Calculate total credit/debit
        total_credit = entry_premium * contracts * 100 if entry_premium and contracts else None
        total_debit = exit_premium * contracts * 100 if exit_premium and contracts else None
        
        return {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{open_date_iso}T09:30:00",
            "date": open_date_iso,
            "account": "Robinhood",  # Default for realized trades
            "broker": "Robinhood",
            "ticker": ticker,
            "strategy": "CSP",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": contracts or 0,
            "strike": None,  # Not in realized table
            "expiration": "2026-02-20",
            "option_type": "PUT",
            "entry_premium": entry_premium,
            "exit_premium": exit_premium,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "realized_pnl": realized_pnl,
            "fees": 0.0,
            "days_held": 1,  # All are 1 day
            "status": "CLOSED",
            "close_date": close_date_iso,
            "notes": f"Closed {ticker} CSP",
            "related_trade_id": None
        }
    except Exception as e:
        print(f"Error creating trade from realized row: {e}")
        return None

def create_trade_from_open_row(row, expiration_date="2026-02-20"):
    """Create trade object from open position row"""
    try:
        account = row.get('Account', '').replace('**', '').strip()
        if not account or account == 'Account':
            return None
        
        ticker = row.get('Ticker', '').replace('**', '').strip()
        if not ticker:
            return None
        
        broker = "Schwab" if "SEP-IRA" in account else "Robinhood"
        
        # Parse numeric values
        strike = clean_numeric(row.get('Strike', ''))
        quantity = clean_numeric(row.get('Qty', '')) or clean_numeric(row.get('Quantity', ''))
        credit = clean_numeric(row.get('Credit', ''))
        
        # Calculate entry premium
        entry_premium = credit / (quantity * 100) if credit and quantity else 0
        
        # Get grade and EM
        grade = row.get('Grade', '').replace('**', '').strip()
        em = row.get('↓1.5x EM', '').replace('**', '').strip()
        
        # Check for open date (for prior days positions)
        open_date_str = row.get('Open Date', '').strip()
        if '/' in open_date_str:
            month, day = open_date_str.split('/')
            trade_date = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            trade_date = "2026-02-18"  # Default
        
        return {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{trade_date}T09:30:00",
            "date": trade_date,
            "account": account,
            "broker": broker,
            "ticker": ticker,
            "strategy": "CSP",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": quantity or 0,
            "strike": strike,
            "expiration": expiration_date,
            "option_type": "PUT",
            "entry_premium": entry_premium,
            "exit_premium": None,
            "total_credit": credit,
            "total_debit": None,
            "realized_pnl": None,
            "fees": 0.0,
            "days_held": None,
            "status": "OPEN",
            "close_date": None,
            "notes": f"Grade {grade}, {em} ↓1.5x EM" if grade else f"Open {ticker} CSP",
            "related_trade_id": None
        }
    except Exception as e:
        print(f"Error creating trade from open row: {e}")
        return None

def create_trade_from_older_row(row):
    """Create trade object from older journal row"""
    try:
        date_str = row.get('Date', '').strip()
        if not date_str or not date_str.startswith('2026'):
            return None
        
        ticker = row.get('Ticker', '').strip()
        if not ticker:
            return None
        
        strategy = row.get('Strategy', '').strip()
        outcome = row.get('Outcome', '').strip()
        notes = row.get('Notes', '')
        
        # Determine status
        if "OPEN" in outcome.upper():
            status = "OPEN"
        elif "CLOSED" in outcome.upper():
            status = "CLOSED"
        else:
            status = "OPEN"
        
        # Parse P&L
        pnl = clean_numeric(row.get('P&L', ''))
        
        # Extract contract details from notes
        contracts = 1
        strike = None
        entry_premium = None
        
        # Try to parse contracts
        contract_match = re.search(r'(\d+)\s*contracts?', notes, re.IGNORECASE)
        if contract_match:
            contracts = int(contract_match.group(1))
        
        # Try to parse strike
        strike_match = re.search(r'\$(\d+(?:\.\d+)?)\s*strike', notes, re.IGNORECASE)
        if strike_match:
            strike = float(strike_match.group(1))
        
        # Try to parse premium
        premium_match = re.search(r'@\s*\$?(\d+(?:\.\d+)?)', notes)
        if premium_match:
            entry_premium = float(premium_match.group(1))
        
        # Determine option type
        if "PUT" in strategy.upper():
            option_type = "PUT"
        elif "CALL" in strategy.upper():
            option_type = "CALL"
        else:
            option_type = "PUT"
        
        return {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{date_str}T09:30:00",
            "date": date_str,
            "account": "Robinhood",  # Default
            "broker": "Robinhood",
            "ticker": ticker,
            "strategy": "CSP" if "Cash-Secured Put" in strategy else "CC" if "Covered Call" in strategy else "Spread",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": contracts,
            "strike": strike,
            "expiration": "2026-02-20",  # Default
            "option_type": option_type,
            "entry_premium": entry_premium,
            "exit_premium": None,
            "total_credit": entry_premium * contracts * 100 if entry_premium else None,
            "total_debit": None,
            "realized_pnl": pnl,
            "fees": 0.0,
            "days_held": None,
            "status": status,
            "close_date": date_str if status == "CLOSED" else None,
            "notes": notes,
            "related_trade_id": None
        }
    except Exception as e:
        print(f"Error creating trade from older row: {e}")
        return None

def main():
    """Main migration function"""
    workspace = Path.home() / ".openclaw" / "workspace"
    
    # Read markdown files
    journal_2026_path = workspace / "trading_journal_2026.md"
    journal_older_path = workspace / "trading_journal.md"
    
    if not journal_2026_path.exists():
        print(f"Error: {journal_2026_path} not found")
        return
    
    with open(journal_2026_path, 'r') as f:
        content_2026 = f.read()
    
    all_trades = []
    
    # Parse realized trades from 2026 journal
    print("Parsing realized trades...")
    _, realized_rows = extract_table_from_markdown(content_2026, "Realized P&L Detail", "## Open Positions")
    for row in realized_rows:
        trade = create_trade_from_realized_row(row)
        if trade:
            all_trades.append(trade)
            print(f"  Added realized trade: {trade['ticker']} ${trade.get('realized_pnl', 0):.2f}")
    
    # Parse open positions expiring Feb 20
    print("\nParsing open positions (Feb 20 expiration)...")
    _, open_rows_feb20 = extract_table_from_markdown(content_2026, "Expiring Friday, February 20", "### Open from Prior Days")
    for row in open_rows_feb20:
        trade = create_trade_from_open_row(row, "2026-02-20")
        if trade:
            all_trades.append(trade)
            print(f"  Added open trade: {trade['ticker']} {trade['strike']}PUT")
    
    # Parse open positions from prior days
    print("\nParsing open positions (prior days)...")
    _, open_rows_prior = extract_table_from_markdown(content_2026, "Open from Prior Days", "**Total Open Credit Exposure:**")
    for row in open_rows_prior:
        trade = create_trade_from_open_row(row, "2026-02-20")
        if trade:
            all_trades.append(trade)
            print(f"  Added prior open trade: {trade['ticker']} {trade['strike']}PUT")
    
    # Parse older trades if file exists
    if journal_older_path.exists():
        print("\nParsing older trades...")
        with open(journal_older_path, 'r') as f:
            content_older = f.read()
        
        _, older_rows = extract_table_from_markdown(content_older, "Trades Log", "---")
        for row in older_rows:
            trade = create_trade_from_older_row(row)
            if trade:
                all_trades.append(trade)
                print(f"  Added older trade: {trade['ticker']} {trade['status']}")
    
    # Remove duplicates - include entry premium for realized trades
    unique_trades = []
    seen = set()
    for trade in all_trades:
        # For realized trades, include entry premium to distinguish between trades with same ticker/date
        if trade.get('status') == 'CLOSED' and trade.get('entry_premium'):
            key = (trade['ticker'], trade['date'], trade.get('entry_premium'), trade.get('quantity'))
        else:
            key = (trade['ticker'], trade['date'], trade.get('strike'), trade.get('quantity'), trade.get('status'))
        
        if key not in seen:
            seen.add(key)
            unique_trades.append(trade)
        else:
            print(f"  Skipping duplicate: {trade['ticker']} {trade['date']}")
    
    # Calculate summary
    total_trades = len(unique_trades)
    open_positions = sum(1 for t in unique_trades if t.get('status') == 'OPEN')
    ytd_realized_pnl = sum(t.get('realized_pnl', 0) or 0 for t in unique_trades)
    ytd_premium_collected = sum(t.get('total_credit', 0) or 0 for t in unique_trades)
    
    summary = {
        "total_trades": total_trades,
        "open_positions": open_positions,
        "ytd_realized_pnl": ytd_realized_pnl,
        "ytd_premium_collected": ytd_premium_collected
    }
    
    # Create final JSON structure
    trades_json = {
        "schema_version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "trades": unique_trades,
        "summary": summary
    }
    
    # Save to file
    output_path = workspace / "data" / "trades.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(trades_json, f, indent=2)
    
    print(f"\n✅ Migration complete!")
    print(f"   Total trades migrated: {total_trades}")
    print(f"   Open positions: {open_positions}")
    print(f"   YTD Realized P&L: ${ytd_realized_pnl:.2f}")
    print(f"   YTD Premium Collected: ${ytd_premium_collected:.2f}")
    print(f"   Output file: {output_path}")
    
    # Validate
    expected_pnl = 721
    if abs(ytd_realized_pnl - expected_pnl) > 10:
        print(f"\n⚠️  WARNING: Realized P&L mismatch!")
        print(f"   Expected: ${expected_pnl:.2f}")
        print(f"   Actual: ${ytd_realized_pnl:.2f}")

if __name__ == "__main__":
    main()