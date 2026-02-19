#!/usr/bin/env python3
"""
Earnings Screener Pipeline - Data Driven
Generates screened_tickers_YYYY-MM-DD.json for Bob
"""

import json
import os
from datetime import datetime, timedelta

def load_portfolio_calendar():
    """Load portfolio earnings calendar."""
    try:
        path = os.path.expanduser('~/.openclaw/workspace/data/portfolio_earnings_calendar.json')
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {'confirmed': {}}

def load_always_include():
    """Load always include list."""
    try:
        path = os.path.expanduser('~/.openclaw/workspace/always_include_list.json')
        with open(path, 'r') as f:
            return json.load(f).get('always_include_earnings', [])
    except:
        return []

def load_earnings_whispers(date_str):
    """Load Earnings Whispers data from cache."""
    try:
        path = os.path.expanduser(f'~/.openclaw/workspace/cache/daily_earnings_{date_str}.json')
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {'stocks': []}

def run_screener():
    """Main screener function."""
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    tomorrow_str = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"Earnings Screener - {today_str}")
    print("="*60)
    
    # Load all sources
    portfolio = load_portfolio_calendar()
    always_include = load_always_include()
    ew_data = load_earnings_whispers(today_str)
    
    tickers = []
    sources = {
        'earnings_whispers': [],
        'portfolio_holdings': [],
        'always_include': []
    }
    
    # Add Earnings Whispers stocks (Today AMC + Tomorrow BMO)
    for stock in ew_data.get('stocks', []):
        ticker = stock.get('ticker')
        if stock.get('date') == today_str and stock.get('time') == 'AMC':
            tickers.append({
                'ticker': ticker,
                'source': 'earnings_whispers',
                'earnings_date': today_str,
                'earnings_time': 'AMC',
                'market_cap': stock.get('market_cap', 0),
                'sector': stock.get('sector', 'Unknown'),
                'expected_move': stock.get('expected_move', 0)
            })
            sources['earnings_whispers'].append(ticker)
        elif stock.get('date') == tomorrow_str and stock.get('time') == 'BMO':
            tickers.append({
                'ticker': ticker,
                'source': 'earnings_whispers',
                'earnings_date': tomorrow_str,
                'earnings_time': 'BMO',
                'market_cap': stock.get('market_cap', 0),
                'sector': stock.get('sector', 'Unknown'),
                'expected_move': stock.get('expected_move', 0)
            })
            sources['earnings_whispers'].append(ticker)
    
    # Add portfolio holdings with earnings today
    for ticker, info in portfolio.get('confirmed', {}).items():
        if info.get('date') == today_str:
            # Check not already added
            if not any(t['ticker'] == ticker for t in tickers):
                tickers.append({
                    'ticker': ticker,
                    'source': 'portfolio_holdings',
                    'earnings_date': today_str,
                    'earnings_time': info.get('time', 'AMC'),
                    'market_cap': 0,
                    'sector': 'Portfolio Holding',
                    'expected_move': 0
                })
                sources['portfolio_holdings'].append(ticker)
    
    # Add always include tickers
    for ticker in always_include:
        if not any(t['ticker'] == ticker for t in tickers):
            tickers.append({
                'ticker': ticker,
                'source': 'always_include',
                'earnings_date': today_str,
                'earnings_time': 'AMC',
                'market_cap': 0,
                'sector': 'Always Include',
                'expected_move': 0
            })
            sources['always_include'].append(ticker)
    
    # Build output
    output = {
        'date': today_str,
        'generated_at': datetime.now().isoformat(),
        'sources': sources,
        'tickers': tickers
    }
    
    # Save to JSON
    output_path = os.path.expanduser(f'~/.openclaw/workspace/data/screened_tickers_{today_str}.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"\nSources:")
    print(f"  Earnings Whispers: {len(sources['earnings_whispers'])} tickers")
    print(f"  Portfolio Holdings: {len(sources['portfolio_holdings'])} tickers")
    print(f"  Always Include: {len(sources['always_include'])} tickers")
    print(f"\nTotal: {len(tickers)} tickers to research")
    print(f"\nSaved to: {output_path}")
    
    return output

if __name__ == '__main__':
    run_screener()
