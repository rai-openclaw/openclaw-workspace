#!/usr/bin/env python3
"""
Migration script to convert markdown trading journals to JSON format.
"""

import json
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path

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
        
        if in_realized_section and "|" in line and "Ticker" in line and "Strategy" in line:
            # Found the header row
            headers = [h.strip() for h in line.split('|') if h.strip()]
            continue
        
        if in_realized_section and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [v.strip() for v in line.split('|')]
            values = [v for v in values if v or v == '']
            
            # Clean up values
            while values and values[0] == '':
                values.pop(0)
            while len(values) > len(headers) and values and values[-1] == '':
                values.pop()
            
            if len(values) >= len(headers) - 1 and values[0] != "TOTAL":
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
        # Parse dates
        open_date_str = row.get('Open Date', '').strip()
        close_date_str = row.get('Close Date', '').strip()
        
        # Convert month/day format to proper date (assuming 2026)
        if open_date_str and '/' in open_date_str:
            month, day = open_date_str.split('/')
            open_date = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            open_date = "2026-02-17"  # Default
        
        if close_date_str and '/' in close_date_str:
            month, day = close_date_str.split('/')
            close_date = f"2026-{int(month):02d}-{int(day):02d}"
        else:
            close_date = "2026-02-18"  # Default
        
        # Parse entry/exit premiums (remove $ sign)
        entry_premium = float(row.get('Entry', '').replace('$', '').strip())
        exit_premium = float(row.get('Exit', '').replace('$', '').strip())
        
        # Parse contracts and P&L
        contracts = int(row.get('Contracts', '0').strip())
        realized_pnl = float(row.get('Realized P&L', '').replace('$', '').replace('+', '').strip())
        
        # Determine if this is a CSP (all are CSP in current data)
        strategy = "CSP"
        
        # Determine direction (SELL for opening CSP)
        direction = "SELL"
        
        # Calculate total credit/debit
        total_credit = entry_premium * contracts * 100 if entry_premium > 0 else None
        total_debit = exit_premium * contracts * 100 if exit_premium > 0 else None
        
        # Determine account (need to infer from context - most are Robinhood based on journal)
        account = "Robinhood"
        
        # Create trade object
        trade = {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{open_date}T09:30:00",  # Default market open time
            "date": open_date,
            "account": account,
            "broker": "Robinhood",
            "ticker": row.get('Ticker', '').strip(),
            "strategy": strategy,
            "action": "OPEN",
            "direction": direction,
            "quantity": contracts,
            "strike": None,  # Not available in realized table
            "expiration": "2026-02-20",  # Based on journal context
            "option_type": "PUT",
            "entry_premium": entry_premium,
            "exit_premium": exit_premium,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "realized_pnl": realized_pnl,
            "fees": 0.0,
            "days_held": int(row.get('Days Held', '1').replace(' day', '').strip()),
            "status": "CLOSED",
            "close_date": close_date,
            "notes": f"Closed early for profit" if realized_pnl > 0 else "Closed early for loss",
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
    headers = []
    
    for i, line in enumerate(lines):
        if "Open Positions (Unrealized)" in line:
            in_open_section = True
            continue
        
        if in_open_section and "Expiring Friday, February 20" in line:
            # Skip the subheader
            continue
        
        if in_open_section and "|" in line and "Account" in line and "Ticker" in line:
            # Found the header row
            headers = [h.strip() for h in line.split('|') if h.strip()]
            continue
        
        if in_open_section and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [v.strip() for v in line.split('|')]
            values = [v for v in values if v or v == '']
            
            # Clean up values
            while values and values[0] == '':
                values.pop(0)
            while len(values) > len(headers) and values and values[-1] == '':
                values.pop()
            
            if len(values) >= len(headers) - 1 and values[0] != "TOTAL":
                row = {}
                for j, header in enumerate(headers):
                    if j < len(values):
                        row[header] = values[j]
                    else:
                        row[header] = ''
                
                # Convert to trade object
                if row.get('Ticker') and row.get('Ticker') != '':
                    trade = parse_open_position_row(row)
                    if trade:
                        trades.append(trade)
    
    return trades

def parse_open_position_row(row):
    """Convert an open position row to JSON format"""
    try:
        # Parse account
        account = row.get('Account', '').strip()
        broker = "Schwab" if "SEP-IRA" in account else "Robinhood"
        
        # Parse ticker
        ticker = row.get('Ticker', '').strip()
        
        # Parse strike (remove $ sign)
        strike_str = row.get('Strike', '').replace('$', '').strip()
        strike = float(strike_str) if strike_str else None
        
        # Parse quantity
        qty_str = row.get('Qty', '').strip()
        quantity = int(qty_str) if qty_str else 0
        
        # Parse credit (remove $ sign)
        credit_str = row.get('Credit', '').replace('$', '').strip()
        credit = float(credit_str) if credit_str else 0
        
        # Calculate entry premium (credit per contract)
        entry_premium = credit / (quantity * 100) if quantity > 0 else 0
        
        # Parse grade and EM
        grade = row.get('Grade', '').strip()
        em = row.get('↓1.5x EM', '').strip()
        
        # Create trade object
        trade = {
            "trade_id": str(uuid.uuid4()),
            "timestamp": "2026-02-18T09:30:00",  # Assuming opened on Feb 18
            "date": "2026-02-18",
            "account": account,
            "broker": broker,
            "ticker": ticker,
            "strategy": "CSP",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": quantity,
            "strike": strike,
            "expiration": "2026-02-20",
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
            headers = [h.strip() for h in line.split('|') if h.strip()]
            continue
        
        if in_table and headers and "|" in line and "---" not in line:
            # Parse data row
            values = [v.strip() for v in line.split('|')]
            values = [v for v in values if v or v == '']
            
            # Clean up values
            while values and values[0] == '':
                values.pop(0)
            while len(values) > len(headers) and values and values[-1] == '':
                values.pop()
            
            if len(values) >= len(headers) - 1 and values[0] and "2026" in values[0]:
                row = {}
                for j, header in enumerate(headers):
                    if j < len(values):
                        row[header] = values[j]
                    else:
                        row[header] = ''
                
                # Convert to trade object
                if row.get('Ticker') and row.get('Ticker') != '':
                    trade = parse_older_trade_row(row)
                    if trade:
                        trades.append(trade)
    
    return trades

def parse_older_trade_row(row):
    """Convert an older trade row to JSON format"""
    try:
        # Parse date
        date_str = row.get('Date', '').strip()
        date = date_str if date_str else "2026-02-17"
        
        # Parse ticker
        ticker = row.get('Ticker', '').strip()
        
        # Parse strategy
        strategy = row.get('Strategy', '').strip()
        
        # Parse entry/exit from notes
        notes = row.get('Notes', '')
        
        # Determine if OPEN or CLOSED
        status = "OPEN" if "OPEN" in row.get('Outcome', '') else "CLOSED"
        
        # Parse P&L if available
        pnl_str = row.get('P&L', '').replace('$', '').replace('+', '').strip()
        realized_pnl = float(pnl_str) if pnl_str and pnl_str != '' else None
        
        # Extract contract details from notes
        contracts = 1
        strike = None
        entry_premium = None
        
        # Try to parse from notes
        if "contracts" in notes.lower():
            import re
            contract_match = re.search(r'(\d+)\s*contracts', notes)
            if contract_match:
                contracts = int(contract_match.group(1))
        
        if "strike" in notes.lower():
            import re
            strike_match = re.search(r'\$(\d+(?:\.\d+)?)\s*strike', notes)
            if strike_match:
                strike = float(strike_match.group(1))
        
        if "@" in notes:
            import re
            premium_match = re.search(r'@\s*\$?(\d+(?:\.\d+)?)', notes)
            if premium_match:
                entry_premium = float(premium_match.group(1))
        
        # Create trade object
        trade = {
            "trade_id": str(uuid.uuid4()),
            "timestamp": f"{date}T09:30:00",
            "date": date,
            "account": "Robinhood",  # Default
            "broker": "Robinhood",
            "ticker": ticker,
            "strategy": "CSP" if "Cash-Secured Put" in strategy else "CC" if "Covered Call" in strategy else "Spread",
            "action": "OPEN",
            "direction": "SELL",
            "quantity": contracts,
            "strike": strike,
            "expiration": "2026-02-20",  # Default
            "option_type": "PUT" if "Put" in strategy else "CALL",
            "entry_premium": entry_premium,
            "exit_premium": None,
            "total_credit": entry_premium * contracts * 100 if entry_premium else None,
            "total_debit": None,
            "realized_pnl": realized_pnl,
            "fees": 0.0,
            "days_held": None,
            "status": status,
            "close_date": date if status == "CLOSED" else None,
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
    realized_trades = parse_realized_trades_2026(content_2026)
    open_trades = parse_open_positions_2026(content_2026)
    
    # Parse older trades if file exists
    older_trades = []
    if journal_older_path.exists():
        with open(journal_older_path, 'r') as f:
            content_older = f.read()
        older_trades = parse_older_trades(content_older)
    
    # Combine all trades
    all_trades = realized_trades + open_trades + older_trades
    
    # Remove duplicates (based on ticker, date, and strike)
    unique_trades = []
    seen = set()
    for trade in all_trades:
        key = (trade['ticker'], trade['date'], trade.get('strike'))
        if key not in seen:
            seen.add(key)
            unique_trades.append(trade)
    
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
    
    print(f"✅ Migration complete!")
    print(f"   Total trades migrated: {len(unique_trades)}")
    print(f"   Open positions: {summary['open_positions']}")
    print(f"   YTD Realized P&L: ${summary['ytd_realized_pnl']:.2f}")
    print(f"   YTD Premium Collected: ${summary['ytd_premium_collected']:.2f}")
    print(f"   Output file: {output_path}")

if __name__ == "__main__":
    main()