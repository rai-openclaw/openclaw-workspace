#!/usr/bin/env python3
"""
Earnings Screener - Script-Based Version
Simple, predictable, no agent interpretation.
"""

import json
from datetime import datetime, timedelta
import os

# Configuration
ALLOWED_SECTORS = [
    'Basic Materials',
    'Consumer Cyclical', 
    'Consumer Discretionary',
    'Financials',
    'Healthcare',
    'Industrials',
    'Technology',
    'Communication Services',
    'Auto Components',
    'Software',
    'Internet Content',
    'Diversified Financials'
]

EXCLUDED_SECTORS = [
    'REITs',
    'Real Estate',
    'Real Estate Investment Trusts',
    'Utilities',
    'Electric Utilities',
    'Consumer Staples',
    'Food Products',
    'Beverages',
    'Industrials',
    'Basic Materials'
]

# Always-include list (bypass sector filter)
ALWAYS_INCLUDE = ['WMT', 'TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']

def load_weekly_schedule(filepath='weekly_earnings_schedule.json'):
    """Load the weekly earnings schedule."""
    with open(filepath) as f:
        return json.load(f)

def load_portfolio_earnings(today_date):
    """Load portfolio holdings with earnings today from cached calendar."""
    try:
        # Load cached earnings calendar
        calendar_path = os.path.expanduser("~/.openclaw/workspace/data/portfolio_earnings_calendar.json")
        if os.path.exists(calendar_path):
            with open(calendar_path) as f:
                calendar = json.load(f)
            
            # Get tickers with earnings today
            today_tickers = []
            for ticker, info in calendar.get("confirmed", {}).items():
                if info.get("date") == today_date:
                    today_tickers.append({
                        "symbol": ticker,
                        "date": today_date,
                        "time": info.get("time", "AMC"),
                        "source": "portfolio_holdings",
                        "market_cap": 0,
                        "sector": "Portfolio Holding"
                    })
            
            return today_tickers
    except Exception as e:
        print(f"Warning: Could not load portfolio earnings calendar: {e}")
    
    return []
    """Load portfolio holdings with earnings today."""
    try:
        # Try to load from Mission Control data
        mc_path = os.path.expanduser('~/mission-control/data/holdings.json')
        if os.path.exists(mc_path):
            with open(mc_path) as f:
                holdings = json.load(f)
            
            # Check if any holdings have earnings today
            portfolio_tickers = []
            for account, data in holdings.get('accounts', {}).items():
                for position in data.get('positions', []):
                    ticker = position.get('ticker')
                    if ticker and ticker not in portfolio_tickers:
                        portfolio_tickers.append(ticker)
            
            # Check Finnhub for earnings dates
            import requests
            api_key = os.environ.get('FINNHUB_API_KEY')
            portfolio_with_earnings = []
            
            for ticker in portfolio_tickers:
                try:
                    url = f"https://finnhub.io/api/v1/calendar/earnings?from={today_date}&to={today_date}&symbol={ticker}&token={api_key}"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('earningsCalendar') and len(data['earningsCalendar']) > 0:
                            earnings = data['earningsCalendar'][0]
                            portfolio_with_earnings.append({
                                'symbol': ticker,
                                'date': today_date,
                                'time': earnings.get('hour', 'AMC'),  # AMC or BMO
                                'source': 'portfolio_holdings',
                                'market_cap': 0,  # Will be fetched if needed
                                'sector': 'Portfolio Holding'
                            })
                except:
                    continue
            
            return portfolio_with_earnings
    except Exception as e:
        print(f"Warning: Could not load portfolio earnings: {e}")
    
    return []

def load_always_include_list():
    """Load always include list from JSON."""
    try:
        with open(os.path.expanduser('~/.openclaw/workspace/always_include_list.json')) as f:
            data = json.load(f)
            return data.get('always_include_earnings', [])
    except:
        return []

def filter_by_date(data, target_date):
    """Filter tickers for specific date."""
    return [s for s in data if s['date'] == target_date]

def apply_sector_filter(tickers):
    """Apply sector whitelist filter."""
    passed = []
    excluded = []
    
    for ticker in tickers:
        symbol = ticker['symbol']
        sector = ticker.get('sector', 'Unknown')
        
        # Always include check
        if symbol in ALWAYS_INCLUDE:
            passed.append({**ticker, 'status': 'always_include'})
            continue
        
        # Check if explicitly excluded
        if any(es in sector for es in EXCLUDED_SECTORS):
            excluded.append({**ticker, 'reason': f'excluded_sector: {sector}'})
            continue
        
        # Check if in allowed list
        if any(as_ in sector for as_ in ALLOWED_SECTORS):
            passed.append({**ticker, 'status': 'passed'})
        else:
            # Unknown sector - include but flag
            passed.append({**ticker, 'status': 'unknown_sector'})
    
    return passed, excluded

def run_screener(today_date, schedule_file='weekly_earnings_schedule.json'):
    """Main screener function."""
    
    # Calculate tomorrow
    today = datetime.strptime(today_date, '%Y-%m-%d')
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    # Load data
    print("="*70)
    print(f"EARNINGS SCREENER - {today.strftime('%A %B %d, %Y')}")
    print("="*70)
    print()
    
    data = load_weekly_schedule(schedule_file)
    print(f"Loaded {len(data)} tickers from weekly schedule")
    
    # Load portfolio earnings (NEW)
    portfolio_earnings = load_portfolio_earnings(today_date)
    if portfolio_earnings:
        print(f"Found {len(portfolio_earnings)} portfolio holdings with earnings today")
        # Add to data
        data.extend(portfolio_earnings)
    
    # Load always include list (NEW)
    always_include_list = load_always_include_list()
    print(f"Always include list: {always_include_list}")
    
    print()
    
    # Filter by date and time
    today_amc = [s for s in data if s['date'] == today_date and s['time'] == 'AMC']
    tomorrow_bmo = [s for s in data if s['date'] == tomorrow_str and s['time'] == 'BMO']
    
    # Add always include tickers (check if they have earnings today/tomorrow)
    for ticker_symbol in always_include_list:
        # Check if already in list
        existing = [s for s in today_amc + tomorrow_bmo if s['symbol'] == ticker_symbol]
        if not existing:
            # Add with placeholder data - Bob will research
            today_amc.append({
                'symbol': ticker_symbol,
                'date': today_date,
                'time': 'AMC',  # Default to AMC
                'source': 'always_include',
                'market_cap': 0,
                'sector': 'Always Include'
            })
    
    print(f"Category A (Today AMC): {len(today_amc)} tickers")
    print(f"Category B (Tomorrow BMO): {len(tomorrow_bmo)} tickers")
    print()
    
    # Apply sector filter
    catA_passed, catA_excluded = apply_sector_filter(today_amc)
    catB_passed, catB_excluded = apply_sector_filter(tomorrow_bmo)
    
    # Output results
    print("="*70)
    print("CATEGORY 1: Today AMC (After Close)")
    print("Action: Trade today before 4 PM")
    print("="*70)
    for t in catA_passed:
        status_flag = "⭐" if t['status'] == 'always_include' else "💼" if t.get('source') == 'portfolio_holdings' else ""
        source_note = f" [{t.get('source', '')}]" if t.get('source') else ""
        print(f"  {t['symbol']:6} | ${t.get('market_cap', 0):>8,.0f}M | {t.get('sector', 'Unknown'):25} {status_flag}{source_note}")
    
    print()
    print("="*70)
    print("CATEGORY 2: Tomorrow BMO (Before Open)")
    print("Action: Trade today before 4 PM")
    print("="*70)
    for t in catB_passed:
        status_flag = "⭐" if t['status'] == 'always_include' else "💼" if t.get('source') == 'portfolio_holdings' else ""
        source_note = f" [{t.get('source', '')}]" if t.get('source') else ""
        print(f"  {t['symbol']:6} | ${t.get('market_cap', 0):>8,.0f}M | {t.get('sector', 'Unknown'):25} {status_flag}{source_note}")
    
    # Audit log
    total_processed = len(today_amc) + len(tomorrow_bmo)
    total_passed = len(catA_passed) + len(catB_passed)
    total_excluded = len(catA_excluded) + len(catB_excluded)
    
    print()
    print("="*70)
    print("AUDIT LOG")
    print("="*70)
    print(f"  Processed: {total_processed} tickers")
    print(f"  Passed: {total_passed} tickers")
    print(f"  Excluded: {total_excluded} tickers")
    if portfolio_earnings:
        print(f"  Portfolio earnings added: {[t['symbol'] for t in portfolio_earnings]}")
    if always_include_list:
        print(f"  Always include tickers: {always_include_list}")
    if catA_excluded or catB_excluded:
        print("  Excluded by sector:")
        for t in catA_excluded + catB_excluded:
            print(f"    {t['symbol']}: {t['reason']}")
    print()
    
    return {
        'category_a': catA_passed,
        'category_b': catB_passed,
        'total_passed': total_passed,
        'portfolio_earnings': [t['symbol'] for t in portfolio_earnings],
        'always_included': always_include_list
    }

if __name__ == '__main__':
    import sys
    today = datetime.now().strftime('%Y-%m-%d')
    if len(sys.argv) > 1:
        today = sys.argv[1]
    
    result = run_screener(today)
    
    # Also output JSON for automation
    output_file = f'screener_results_{today}.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Results saved to: {output_file}")
