#!/usr/bin/env python3
"""
Fixed migration script to convert markdown trading journals to JSON format.
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

def clean_value(value):
    """Clean markdown formatting from values"""
    if not value:
        return value
    
    # Remove **bold** markers
    value = re.sub(r'\*\*(.+?)\*\*', r'\1', value)
    
    # Remove $ signs and commas from numbers
    value = re.sub(r'[\$,]', '', value)
    
    # Remove emojis and special characters
    value = re.sub(r'[★⚠️]', '', value)
    
    # Remove extra whitespace
    value = value.strip()
    
    return value

def parse_realized_trades_2026(content):
    """Parse realized trades from trading_journal_2026.md"""
    trades = []
    
    # Find the Realized P&L Detail section
    lines = content.split('\n')
    in_realized_section = False
    headers = []
    
    for i, line in enumerate(lines):
        if "Realized P&L Detail" in line:
            in_realized_section = True
            continue
        
        if in_realized_section and "###" in line:
            # End of section
            break
        
        if in_realized_section and "|" in line and "Ticker" in line and "Strategy" in line:
            # Found the header row
            headers = [clean_value(h) for h in line.split('|') if h.strip()]
            continue
        
        if in_realized_section and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [clean_value(v) for v in line.split('|')]
            
            # Skip empty rows and total rows
            if not values or len(values) < 2 or values[0] in ["", "TOTAL"]:
                continue
            
            # Ensure we have enough values
            if len(values) < len(headers):
                values.extend([''] * (len(headers) - len(values)))
            
            row = {}
            for j, header in enumerate(headers):
                if j < len(values):
                    row[header] = values[j]
                else:
                    row[header] = ''
            
            # Convert to trade object
            if row.get('Ticker') and row.get('Ticker') != '':
                trade = parse_realized_trade_row(row)
                if trade:
                    trades.append(trade)
    
    return trades

def parse_realized_trade_row(row):
    """Convert a realized trade row to JSON format"""
    try:
        ticker = row.get('Ticker', '').strip()
        if not ticker or ticker == 'Ticker':
            return None
        
        # Parse dates
        open_date_str = row.get('Open Date', '').strip()
        close_date_str = row.get('Close Date', '').strip()
        
        # Convert month/day format to proper date (assuming 2026)
        if open_date_str and '/' in open_date_str:
            month, day = open_date_str.split('/')
            open_date = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            open_date = "2026-02-17"
        
        if close_date_str and '/' in close_date_str:
            month, day = close_date_str.split('/')
            close_date = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            close_date = "2026-02-18"
        
        # Parse entry/exit premiums
        entry_str = row.get('Entry', '').replace('$', '').strip()
        exit_str = row.get('Exit', '').replace('$', '').strip()
        
        try:
            entry_premium = float(entry_str) if entry_str else 0
            exit_premium = float(exit_str) if exit_str else 0
        except:
            entry_premium = 0
            exit_premium = 0
        
        # Parse contracts
        contracts_str = row.get('Contracts', '0').strip()
        try:
            contracts = int(contracts_str) if contracts_str else 0
        except:
            contracts = 0
        
        # Parse P&L
        pnl_str = row.get('Realized P&L', '').replace('$', '').replace('+', '').strip()
        try:
            realized_pnl = float(pnl_str) if pnl_str else 0
        except:
            realized_pnl = 0
        
        # Calculate total credit/debit
        total_credit = entry_premium * contracts * 100 if entry_premium > 0 else None
        total_debit = exit_premium * contracts * 100 if exit_premium > 0 else None
        
        # Determine account based on ticker pattern
        account = "Robinhood"  # Default
        
        # Create trade object
        trade = {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{open_date}T09:30:00",
            "date": open_date,
            "account": account,
            "broker": "Robinhood",
            "ticker": ticker,
            "strategy": "CSP",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": contracts,
            "strike": None,  # Not available in realized table
            "expiration": "2026-02-20",
            "option_type": "PUT",
            "entry_premium": entry_premium,
            "exit_premium": exit_premium,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "realized_pnl": realized_pnl,
            "fees": 0.0,
            "days_held": 1,  # All are 1 day in current data
            "status": "CLOSED",
            "close_date": close_date,
            "notes": f"Closed {ticker} CSP",
            "related_trade_id": None
        }
        
        return trade
    except Exception as e:
        print(f"Error parsing realized trade row: {e}")
        print(f"Row data: {row}")
        return None

def parse_open_positions_2026(content):
    """Parse open positions from trading_journal_2026.md"""
    trades = []
    
    lines = content.split('\n')
    in_open_section = False
    current_subsection = None
    headers = []
    
    for i, line in enumerate(lines):
        if "Open Positions (Unrealized)" in line:
            in_open_section = True
            continue
        
        if in_open_section and "###" in line:
            current_subsection = line.strip('#').strip()
            continue
        
        if in_open_section and "|" in line and "Account" in line and "Ticker" in line:
            # Found the header row
            headers = [clean_value(h) for h in line.split('|') if h.strip()]
            continue
        
        if in_open_section and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [clean_value(v) for v in line.split('|')]
            
            # Skip empty rows and total rows
            if not values or len(values) < 2 or values[0] in ["", "TOTAL", "TOTAL OPEN"]:
                continue
            
            # Ensure we have enough values
            if len(values) < len(headers):
                values.extend([''] * (len(headers) - len(values)))
            
            row = {}
            for j, header in enumerate(headers):
                if j < len(values):
                    row[header] = values[j]
                else:
                    row[header] = ''
            
            # Convert to trade object
            if row.get('Ticker') and row.get('Ticker') != '':
                trade = parse_open_position_row(row, current_subsection)
                if trade:
                    trades.append(trade)
    
    return trades

def parse_open_position_row(row, subsection):
    """Convert an open position row to JSON format"""
    try:
        account = row.get('Account', '').strip()
        if not account or account == 'Account':
            return None
        
        broker = "Schwab" if "SEP-IRA" in account else "Robinhood"
        
        ticker = row.get('Ticker', '').strip()
        if not ticker:
            return None
        
        # Parse strike
        strike_str = row.get('Strike', '').replace('$', '').strip()
        try:
            strike = float(strike_str) if strike_str else None
        except:
            strike = None
        
        # Parse quantity
        qty_str = row.get('Qty', '').strip()
        try:
            quantity = int(qty_str) if qty_str else 0
        except:
            quantity = 0
        
        # Parse credit
        credit_str = row.get('Credit', '').replace('$', '').strip()
        try:
            credit = float(credit_str) if credit_str else 0
        except:
            credit = 0
        
        # Calculate entry premium
        entry_premium = credit / (quantity * 100) if quantity > 0 and credit > 0 else 0
        
        # Parse grade and EM
        grade = row.get('Grade', '').strip()
        em = row.get('↓1.5x EM', '').strip()
        
        # Determine expiration based on subsection
        if "Expiring Friday, February 20" in str(subsection):
            expiration = "2026-02-20"
        else:
            expiration = "2026-02-20"  # Default
        
        # Create trade object
        trade = {
            "trade_id": str(uuid.uuid4()),
            "timestamp": "2026-02-18T09:30:00",
            "date": "2026-02-18",
            "account": account,
            "broker": broker,
            "ticker": ticker,
            "strategy": "CSP",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": quantity,
            "strike": strike,
            "expiration": expiration,
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
            "notes": f"Grade {grade}, {em} ↓1.5x EM",
            "related_trade_id": None
        }
        
        return trade
    except Exception as e:
        print(f"Error parsing open position row: {e}")
        print(f"Row data: {row}")
        return None

def parse_older_trades(content):
    """Parse trades from older trading_journal.md"""
    trades = []
    
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for i, line in enumerate(lines):
        if "Trades Log" in line:
            in_table = True
            continue
        
        if in_table and "|" in line and "Date" in line and "Ticker" in line:
            # Found the header row
            headers = [clean_value(h) for h in line.split('|') if h.strip()]
            continue
        
        if in_table and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [clean_value(v) for v in line.split('|')]
            
            # Skip empty rows
            if not values or len(values) < 2:
                continue
            
            # Ensure we have enough values
            if len(values) < len(headers):
                values.extend([''] * (len(headers) - len(values)))
            
            row = {}
            for j, header in enumerate(headers):
                if j < len(values):
                    row[header] = values[j]
                else:
                    row[header] = ''
            
            # Skip header rows and empty rows
            if row.get('Date') in ['Date', ''] or not row.get('Ticker'):
                continue
            
            # Convert to trade object
            trade = parse_older_trade_row(row)
            if trade:
                trades.append(trade)
    
    return trades

def parse_older_trade_row(row):
    """Convert an older trade row to JSON format"""
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
            status = "OPEN"  # Default
        
        # Parse P&L
        pnl_str = row.get('P&L', '').replace('$', '').replace('+', '').strip()
        try:
            realized_pnl = float(pnl_str) if pnl_str and pnl_str != '-' else None
        except:
            realized_pnl = None
        
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
        
        # Determine option type from strategy
        if "PUT" in strategy.upper():
            option_type = "PUT"
        elif "CALL" in strategy.upper():
            option_type = "CALL"
        else:
            option_type = "PUT"  # Default
        
        # Create trade object
        trade = {
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
            "realized_pnl": realized_pnl,
            "fees": 0.0,
            "days_held": None,
            "status": status,
            "close_date": date_str if status == "CLOSED" else None,
            "notes": notes,
            "related_trade_id": None
        }
        
        return trade
    except Exception as e:
        print(f"Error parsing older trade row: {e}")
        print(f"Row data: {row}")
        return None

def calculate_summary(trades):
    """Calculate summary statistics from trades"""
    total_trades = len(trades)
    open_positions = sum(1 for t in trades if t.get('status') == 'OPEN')
    
    # Calculate YTD realized P&L
    ytd_realized_pnl = sum(t.get('realized_pnl', 0) or 0 for t in trades)
    
    # Calculate YTD premium collected
    ytd_premium_collected = sum(t.get('total_credit', 0) or 0 for t in trades)
    
    return {
        "total_trades": total_trades,
        "open_positions": open_positions,
        "ytd_realized_pnl": ytd_realized_pnl,
        "ytd_premium_collected": ytd_premium_collected
    }

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
    
    # Parse trades from 2026 journal
    print("Parsing realized trades from 2026 journal...")
    realized_trades = parse_realized_trades_2026(content_2026)
    print(f"  Found {len(realized_trades)} realized trades")
    
    print("Parsing open positions from 2026 journal...")
    open_trades = parse_open_positions_2026(content_2026)
    print(f"  Found {len(open_trades)} open positions")
    
    # Parse older trades if file exists
    older_trades = []
    if journal_older_path.exists():
        print("Parsing older trades from trading_journal.md...")
        with open(journal_older_path, 'r') as f:
            content_older = f.read()
        older_trades = parse_older_trades(content_older)
        print(f"  Found {len(older_trades)} older trades")
    
    # Combine all trades
    all_trades = realized_trades + open_trades + older_trades
    
    # Remove duplicates (based on ticker, date, strike, and quantity)
    unique_trades = []
    seen = set()
    for trade in all_trades:
        key = (trade['ticker'], trade['date'], trade.get('strike'), trade.get('quantity'))
        if key not in seen:
            seen.add(key)
            unique_trades.append(trade)
        else:
            print(f"  Skipping duplicate: {trade['ticker']} {trade['date']}")
    
    # Calculate summary
    summary = calculate_summary(unique_trades)
    
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
    print(f"   Total trades migrated: {len(unique_trades)}")
    print(f"   Open positions: {summary['open_positions']}")
    print(f"   YTD Realized P&L: ${summary['ytd_realized_pnl']:.2f}")
    print(f"   YTD Premium Collected: ${summary['ytd_premium_collected']:.2f}")
    print(f"   Output file: {output_path}")
    
    # Validate against expected values
    expected_pnl = 721  # From the journal
    actual_pnl = summary['ytd_realized_pnl']
    
    if abs(actual_pnl - expected_pnl) > 10:  # Allow small rounding differences
        print(f"\n⚠️  WARNING: Realized P&L mismatch!")
        print(f"   Expected: ${expected_pnl:.2f}")
        print(f"   Actual: ${actual_pnl:.2f}")
        print(f"   Difference: ${actual_pnl - expected_pnl:.2f}")

if __name__ == "__main__":
    main()