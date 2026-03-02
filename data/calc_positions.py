#!/usr/bin/env python3
"""
calc_positions.py - Calculate positions, P&L, and grades from trades.json

Reads: trades.json
Writes: positions.json, pnl_summary.json, trade_grades.json
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE_DATA = Path("/Users/raitsai/.openclaw/workspace/data")
TRADES_FILE = WORKSPACE_DATA / "options" / "trades.json"
POSITIONS_FILE = WORKSPACE_DATA / "positions.json"
PNL_SUMMARY_FILE = WORKSPACE_DATA / "pnl_summary.json"
TRADE_GRADES_FILE = WORKSPACE_DATA / "trade_grades.json"


def load_trades():
    """Load trades from trades.json"""
    with open(TRADES_FILE, 'r') as f:
        return json.load(f)


def calculate_positions(trades):
    """Calculate open positions (net > 0)"""
    positions = {}
    
    for trade in trades:
        # Key includes account to separate positions by account
        key = f"{trade['ticker']}_{trade['strike']}_{trade['expiration']}_{trade.get('account', 'Unknown')}"
        
        if key not in positions:
            positions[key] = {
                "ticker": trade['ticker'],
                "strike": trade['strike'],
                "expiration": trade['expiration'],
                "option_type": trade.get('option_type', 'PUT'),
                "net_quantity": 0,
                "total_premium": 0,
                "open_date": trade['date'],
                "days_open": 0,
                "account": trade.get('account', 'Unknown')
            }
        
        action = trade['action']
        qty = trade['quantity']
        
        if action == 'SELL_TO_OPEN':
            positions[key]['net_quantity'] += qty
            # Premium is now in decimal format (e.g., 0.65 = $65 per share = $65 per contract)
            positions[key]['total_premium'] += trade['premium'] * qty * 100
            if positions[key]['open_date'] == "" or positions[key]['open_date'] > trade['date']:
                positions[key]['open_date'] = trade['date']
        elif action == 'BUY_TO_CLOSE':
            positions[key]['net_quantity'] -= qty
        elif action == 'BUY_TO_OPEN':
            positions[key]['net_quantity'] -= qty
        elif action == 'SELL_TO_CLOSE':
            positions[key]['net_quantity'] += qty
    
    # Filter to only open positions (net > 0)
    open_positions = [p for p in positions.values() if p['net_quantity'] > 0]
    
    # Calculate days open
    today = datetime.now().strftime("%Y-%m-%d")
    for p in open_positions:
        try:
            open_date = datetime.strptime(p['open_date'], "%Y-%m-%d")
            today_date = datetime.strptime(today, "%Y-%m-%d")
            p['days_open'] = (today_date - open_date).days
        except:
            p['days_open'] = 0
    
    return open_positions


def calculate_pnl_and_grades(trades):
    """Calculate P&L by period and trade grades"""
    
    # Group by ticker
    ticker_stats = {}
    trade_grades = []
    
    # Get current date info
    now = datetime.now()
    today = now.date()
    
    # Start of week (Monday)
    week_start = today - timedelta(days=today.weekday())
    # Start of month
    month_start = today.replace(day=1)
    # Start of year
    year_start = today.replace(month=1, day=1)
    
    ytd_pnl = 0
    month_pnl = 0
    week_pnl = 0
    closed_trades = []
    
    for trade in trades:
        ticker = trade['ticker']
        
        # Initialize ticker stats if needed
        if ticker not in ticker_stats:
            ticker_stats[ticker] = {
                "ticker": ticker,
                "total_pnl": 0,
                "trades": 0,
                "wins": 0,
                "win_rate": 0,
                "premium_collected": 0,
                "largest_win": 0,
                "largest_loss": 0,
                "open_now": False,
                "grade": "C"
            }
        
        ticker_stats[ticker]["trades"] += 1
        
        # Track premium collected (premium in decimal, convert to dollars)
        if trade['action'] == 'SELL_TO_OPEN':
            ticker_stats[ticker]["premium_collected"] += trade['premium'] * trade['quantity'] * 100
        
        # Process closed trades (have exit premium)
        if trade['action'] in ['BUY_TO_CLOSE', 'SELL_TO_CLOSE'] or trade['action'] == 'EXPIRED':
            # Calculate P&L
            # For SELL_TO_OPEN: entry - exit
            # For EXPIRED: full premium kept
            
            # Find matching open
            open_trades = [t for t in trades if 
                          t['ticker'] == trade['ticker'] and 
                          t['strike'] == trade['strike'] and
                          t['expiration'] == trade['expiration'] and
                          t['action'] == 'SELL_TO_OPEN']
            
            if open_trades and trade['action'] != 'EXPIRED':
                entry_premium = open_trades[0]['premium']
                exit_premium = trade['premium']
                # Premium in decimal, convert to dollars
                pnl = (entry_premium - exit_premium) * trade['quantity'] * 100
            elif trade['action'] == 'EXPIRED':
                pnl = trade['premium'] * trade['quantity'] * 100
            else:
                pnl = 0
            
            # Calculate grade
            if trade['action'] == 'EXPIRED':
                grade = 'A'
            elif open_trades:
                entry = open_trades[0]['premium']
                if entry > 0:
                    pnl_pct = (entry - trade['premium']) / entry * 100
                    if pnl_pct >= 90:
                        grade = 'A'
                    elif pnl_pct >= 50:
                        grade = 'B'
                    elif pnl_pct >= 0:
                        grade = 'C'
                    elif pnl_pct >= -50:
                        grade = 'D'
                    else:
                        grade = 'F'
                else:
                    grade = 'C'
            else:
                grade = 'C'
            
            # Add to trade grades
            trade_grades.append({
                "ticker": trade['ticker'],
                "date": trade['date'],
                "action": trade['action'],
                "quantity": trade['quantity'],
                "strike": trade['strike'],
                "expiration": trade['expiration'],
                "entry_premium": open_trades[0]['premium'] if open_trades else 0,
                "exit_premium": trade['premium'],
                "realized_pnl": pnl,
                "grade": grade
            })
            
            # Update ticker stats
            ticker_stats[ticker]["total_pnl"] += pnl
            
            # Count as win if pnl > 0 (profitable close)
            if pnl > 0:
                ticker_stats[ticker]["wins"] += 1
                if pnl > ticker_stats[ticker]["largest_win"]:
                    ticker_stats[ticker]["largest_win"] = pnl
            elif pnl < 0:
                if pnl < ticker_stats[ticker]["largest_loss"]:
                    ticker_stats[ticker]["largest_loss"] = pnl
            
            # Count total closed trades (including wins and losses)
            ticker_stats[ticker]["closed_trades"] = ticker_stats[ticker].get("closed_trades", 0) + 1
            
            # Add to period P&L
            try:
                trade_date = datetime.strptime(trade['date'], "%Y-%m-%d").date()
                if trade_date >= year_start:
                    ytd_pnl += pnl
                if trade_date >= month_start:
                    month_pnl += pnl
                if trade_date >= week_start:
                    week_pnl += pnl
            except:
                pass
    
    # Check for open positions per ticker
    positions = calculate_positions(trades)
    for p in positions:
        ticker_stats[p['ticker']]["open_now"] = True
    
    # Calculate win rates (based on closed trades only)
    for ticker, stats in ticker_stats.items():
        closed = stats.get("closed_trades", stats["trades"])
        if closed > 0:
            stats["win_rate"] = round((stats["wins"] / closed) * 100)
        # Determine grade based on win rate
        if stats["win_rate"] >= 80:
            stats["grade"] = "A"
        elif stats["win_rate"] >= 60:
            stats["grade"] = "B"
        elif stats["win_rate"] >= 40:
            stats["grade"] = "C"
        elif stats["win_rate"] >= 20:
            stats["grade"] = "D"
        else:
            stats["grade"] = "F"
    
    # Sort by total P&L descending
    by_ticker = sorted(ticker_stats.values(), key=lambda x: x['total_pnl'], reverse=True)
    
    return {
        "ytd_pnl": ytd_pnl,
        "month_pnl": month_pnl,
        "week_pnl": week_pnl,
        "by_ticker": by_ticker,
        "trade_grades": trade_grades
    }


def main():
    print("Loading trades...")
    data = load_trades()
    trades = data.get('trades', [])
    print(f"Loaded {len(trades)} trades")
    
    # Calculate positions
    print("Calculating open positions...")
    positions = calculate_positions(trades)
    print(f"Found {len(positions)} open positions")
    
    # Calculate P&L and grades
    print("Calculating P&L and grades...")
    pnl_data = calculate_pnl_and_grades(trades)
    
    # Build summary
    total_wins = sum(1 for t in pnl_data['by_ticker'] if t['wins'] > 0)
    total_trades = sum(t['trades'] for t in pnl_data['by_ticker'])
    win_rate = round((total_wins / total_trades) * 100) if total_trades > 0 else 0
    
    summary = {
        "ytd_pnl": pnl_data['ytd_pnl'],
        "month_pnl": pnl_data['month_pnl'],
        "week_pnl": pnl_data['week_pnl'],
        "win_rate": win_rate,
        "total_trades": total_trades,
        "open_positions": len(positions)
    }
    
    # Save positions.json
    positions_output = {
        "last_updated": datetime.now().isoformat(),
        "positions": positions
    }
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions_output, f, indent=2)
    print(f"Saved {len(positions)} positions to {POSITIONS_FILE}")
    
    # Save pnl_summary.json
    pnl_output = {
        "last_updated": datetime.now().isoformat(),
        "summary": summary,
        "by_ticker": pnl_data['by_ticker']
    }
    with open(PNL_SUMMARY_FILE, 'w') as f:
        json.dump(pnl_output, f, indent=2)
    print(f"Saved P&L summary to {PNL_SUMMARY_FILE}")
    
    # Save trade_grades.json
    grades_output = {
        "last_updated": datetime.now().isoformat(),
        "trades": pnl_data['trade_grades']
    }
    with open(TRADE_GRADES_FILE, 'w') as f:
        json.dump(grades_output, f, indent=2)
    print(f"Saved {len(pnl_data['trade_grades'])} graded trades to {TRADE_GRADES_FILE}")
    
    print("\n=== Summary ===")
    print(f"YTD P&L: ${summary['ytd_pnl']}")
    print(f"Month P&L: ${summary['month_pnl']}")
    print(f"Week P&L: ${summary['week_pnl']}")
    print(f"Win Rate: {summary['win_rate']}%")
    print(f"Open Positions: {summary['open_positions']}")


if __name__ == "__main__":
    main()
