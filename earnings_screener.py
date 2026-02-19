#!/usr/bin/env python3
"""
Earnings Screener - Script-Based Version
Simple, predictable, no agent interpretation.
"""

import json
from datetime import datetime, timedelta

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
    print()
    
    # Filter by date and time
    today_amc = [s for s in data if s['date'] == today_date and s['time'] == 'AMC']
    tomorrow_bmo = [s for s in data if s['date'] == tomorrow_str and s['time'] == 'BMO']
    
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
        status_flag = "⭐" if t['status'] == 'always_include' else ""
        print(f"  {t['symbol']:6} | ${t.get('market_cap', 0):>8,.0f}M | {t.get('sector', 'Unknown'):25} {status_flag}")
    
    print()
    print("="*70)
    print("CATEGORY 2: Tomorrow BMO (Before Open)")
    print("Action: Trade today before 4 PM")
    print("="*70)
    for t in catB_passed:
        status_flag = "⭐" if t['status'] == 'always_include' else ""
        print(f"  {t['symbol']:6} | ${t.get('market_cap', 0):>8,.0f}M | {t.get('sector', 'Unknown'):25} {status_flag}")
    
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
    if catA_excluded or catB_excluded:
        print("  Excluded by sector:")
        for t in catA_excluded + catB_excluded:
            print(f"    {t['symbol']}: {t['reason']}")
    print()
    
    return {
        'category_a': catA_passed,
        'category_b': catB_passed,
        'total_passed': total_passed
    }

if __name__ == '__main__':
    import sys
    
    today = sys.argv[1] if len(sys.argv) > 1 else '2026-02-18'
    result = run_screener(today)
    
    print(f"Final tradable list: {result['total_passed']} stocks")
