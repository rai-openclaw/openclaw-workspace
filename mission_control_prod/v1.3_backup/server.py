#!/usr/bin/env python3
"""
Mission Control Dashboard - Portfolio Tracking v2.0
Clean data model with manual price refresh
"""

import os
import re
import json
import time
from datetime import datetime
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Configuration
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICE_CACHE_FILE = os.path.join(WORKSPACE, 'portfolio', 'price_cache.json')
PORTFOLIO_FILE = os.path.join(WORKSPACE, 'portfolio', 'unified_portfolio_tracker.md')

# Price cache in memory
price_cache = {}
price_cache_time = 0
PRICE_CACHE_TTL = 300  # 5 minutes

# API Keys
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', 'd68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0')


def load_price_cache():
    """Load price cache from disk"""
    global price_cache, price_cache_time
    try:
        with open(PRICE_CACHE_FILE, 'r') as f:
            data = json.load(f)
            price_cache = data.get('prices', {})
            price_cache_time = datetime.fromisoformat(data.get('last_updated', '2026-01-01T00:00:00Z').replace('Z', '+00:00')).timestamp()
    except:
        price_cache = {}
        price_cache_time = 0


def save_price_cache():
    """Save price cache to disk"""
    data = {
        'version': '2.0',
        'last_updated': datetime.now().isoformat(),
        'prices': price_cache
    }
    with open(PRICE_CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def fetch_finnhub_price(ticker):
    """Fetch price from Finnhub"""
    try:
        import urllib.request
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('c', 0)  # Current price
    except:
        return 0


def fetch_yahoo_finance_price(ticker):
    """Fetch price from Yahoo Finance for mutual funds"""
    try:
        import urllib.request
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            result = data.get('chart', {}).get('result', [{}])[0]
            return result.get('meta', {}).get('regularMarketPrice', 0)
    except:
        return 0


def fetch_coingecko_price(asset):
    """Fetch price from CoinGecko for crypto"""
    try:
        import urllib.request
        # Map asset names to CoinGecko IDs
        asset_map = {'ETH': 'ethereum', 'BTC': 'bitcoin'}
        asset_id = asset_map.get(asset, asset.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get(asset_id, {}).get('usd', 0)
    except:
        return 0


def refresh_all_prices(tickers, misc_assets):
    """Refresh prices from all sources"""
    global price_cache, price_cache_time
    
    results = {}
    
    # Categorize tickers
    mutual_funds = ['VSEQX', 'VTCLX', 'VTMSX']
    crypto = ['ETH', 'BTC']
    
    for ticker in tickers:
        if ticker in mutual_funds:
            # Try Yahoo Finance first
            price = fetch_yahoo_finance_price(ticker)
            if price > 0:
                price_cache[ticker] = {
                    'price': price,
                    'source': 'yahoo_finance',
                    'note': None,
                    'last_updated': datetime.now().isoformat()
                }
                results[ticker] = {'success': True, 'source': 'yahoo_finance'}
            else:
                # Fallback to cached
                cached = price_cache.get(ticker, {}).get('price', 0)
                price_cache[ticker] = {
                    'price': cached or 39.46,  # Default fallback
                    'source': 'cached',
                    'note': 'Using cached price - Yahoo Finance unavailable',
                    'last_updated': datetime.now().isoformat()
                }
                results[ticker] = {'success': False, 'source': 'cached', 'note': 'Yahoo Finance unavailable'}
        else:
            # Try Finnhub
            price = fetch_finnhub_price(ticker)
            if price > 0:
                price_cache[ticker] = {
                    'price': price,
                    'source': 'finnhub',
                    'note': None,
                    'last_updated': datetime.now().isoformat()
                }
                results[ticker] = {'success': True, 'source': 'finnhub'}
            else:
                # Fallback to cached
                cached = price_cache.get(ticker, {}).get('price', 0)
                price_cache[ticker] = {
                    'price': cached or 100.0,
                    'source': 'cached',
                    'note': 'Using cached price - Finnhub unavailable',
                    'last_updated': datetime.now().isoformat()
                }
                results[ticker] = {'success': False, 'source': 'cached', 'note': 'Finnhub unavailable'}
    
    # Fetch crypto prices
    for asset in misc_assets:
        if asset in crypto:
            price = fetch_coingecko_price(asset)
            if price > 0:
                price_cache[asset] = {
                    'price': price,
                    'source': 'coingecko',
                    'note': None,
                    'last_updated': datetime.now().isoformat()
                }
                results[asset] = {'success': True, 'source': 'coingecko'}
            else:
                cached = price_cache.get(asset, {}).get('price', 0)
                price_cache[asset] = {
                    'price': cached or 1900.0,
                    'source': 'cached',
                    'note': 'Using cached price - CoinGecko unavailable',
                    'last_updated': datetime.now().isoformat()
                }
                results[asset] = {'success': False, 'source': 'cached', 'note': 'CoinGecko unavailable'}
    
    price_cache_time = time.time()
    save_price_cache()
    
    return results



def parse_markdown_table_v2(content, section_header):
    """Parse a markdown table from a section"""
    lines = content.split('\n')
    in_section = False
    headers = []
    rows = []
    
    for line in lines:
        if section_header in line:
            in_section = True
            continue
        
        if in_section:
            # Check for next section
            if line.startswith('###') and section_header not in line:
                break
            if line.startswith('---'):
                break
            
            # Parse header row
            if '|' in line and not headers and '---' not in line:
                headers = [h.strip() for h in line.split('|') if h.strip()]
                continue
            
            # Skip separator row
            if '|' in line and '---' in line:
                continue
            
            # Parse data row
            if '|' in line and headers:
                values = [v.strip() for v in line.split('|') if v.strip()]
                if values:
                    row = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            row[header] = values[i]
                    rows.append(row)
    
    return rows


def parse_unified_tracker_v2(filepath):
    """Parse v2 format unified portfolio tracker"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    accounts = {}
    
    # Split by account sections
    sections = content.split('## Account: ')
    
    for section in sections[1:]:  # Skip header
        lines = section.strip().split('\n')
        account_name = lines[0].strip()
        
        # Parse stocks
        stocks = []
        stock_rows = parse_markdown_table_v2(section, '### Stocks & ETFs')
        for row in stock_rows:
            try:
                ticker = row.get('Ticker', '')
                if ticker and ticker not in ['Ticker', '—']:
                    shares_str = row.get('Shares', '0').replace(',', '').replace('$', '')
                    cost_basis_str = row.get('Cost Basis', '0').replace(',', '').replace('$', '').replace('—', '0')
                    stocks.append({
                        'ticker': ticker,
                        'shares': float(shares_str) if shares_str else 0,
                        'cost_basis': float(cost_basis_str) if cost_basis_str else 0,
                        'notes': row.get('Notes', '')
                    })
            except:
                continue
        
        # Parse options
        options = []
        option_rows = parse_markdown_table_v2(section, '### Options Positions')
        for row in option_rows:
            try:
                ticker = row.get('Ticker', '')
                if ticker and ticker not in ['Ticker', '—']:
                    contracts_str = row.get('Contracts', '0')
                    premium_str = row.get('Entry Premium', '0').replace('$', '')
                    options.append({
                        'ticker': ticker,
                        'type': row.get('Type', ''),
                        'strike': row.get('Strike', ''),
                        'expiration': row.get('Expiration', ''),
                        'contracts': int(contracts_str) if contracts_str else 0,
                        'entry_premium': float(premium_str) if premium_str else 0
                    })
            except:
                continue
        
        # Parse cash
        cash = []
        cash_rows = parse_markdown_table_v2(section, '### Cash & Cash Equivalents')
        for row in cash_rows:
            try:
                asset = row.get('Asset', '')
                if asset and asset not in ['Asset', '—']:
                    quantity_str = row.get('Quantity', '0').replace(',', '').replace('$', '')
                    cost_basis_str = row.get('Cost Basis', '0').replace(',', '').replace('$', '').replace('—', '0')
                    category = row.get('Category', 'cash')
                    cash.append({
                        'asset': asset,
                        'quantity': float(quantity_str) if quantity_str else 0,
                        'cost_basis': float(cost_basis_str) if cost_basis_str else 0,
                        'category': category
                    })
            except:
                continue
        
        # Parse misc
        misc = []
        misc_rows = parse_markdown_table_v2(section, '### Misc')
        for row in misc_rows:
            try:
                asset = row.get('Asset', '')
                if asset and asset not in ['Asset', '—']:
                    amount_str = row.get('Amount', '0').replace(',', '')
                    cost_basis_str = row.get('Cost Basis', '0').replace(',', '').replace('$', '')
                    misc.append({
                        'asset': asset,
                        'amount': float(amount_str) if amount_str else 0,
                        'type': row.get('Type', ''),
                        'cost_basis': float(cost_basis_str) if cost_basis_str else 0
                    })
            except:
                continue
        
        accounts[account_name] = {
            'stocks': stocks,
            'options': options,
            'cash': cash,
            'misc': misc
        }
    
    return accounts



def build_stocks_view(accounts, prices):
    """Build aggregated stocks view with account attribution"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            ticker = stock['ticker']
            
            # Skip cash equivalents (they're in Cash section)
            if ticker in ['SGOV', 'Cash']:
                continue
            
            if ticker not in aggregated:
                price_data = prices.get(ticker, {})
                aggregated[ticker] = {
                    'ticker': ticker,
                    'total_shares': 0,
                    'total_cost_basis': 0,
                    'accounts': [],
                    'price': price_data.get('price', 0),
                    'price_source': price_data.get('source', 'unknown'),
                    'price_note': price_data.get('note')
                }
            
            shares = stock['shares']
            cost_basis = stock['cost_basis']
            price = aggregated[ticker]['price']
            value = shares * price
            return_val = value - cost_basis
            return_pct = (return_val / cost_basis * 100) if cost_basis else 0
            
            aggregated[ticker]['total_shares'] += shares
            aggregated[ticker]['total_cost_basis'] += cost_basis
            aggregated[ticker]['accounts'].append({
                'account': account_name,
                'shares': shares,
                'cost_basis': cost_basis,
                'value': value,
                'return': return_val,
                'return_pct': return_pct
            })
    
    # Calculate totals
    for ticker, data in aggregated.items():
        data['total_value'] = data['total_shares'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['total_return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] else 0
    
    return sorted(list(aggregated.values()), key=lambda x: x['total_value'], reverse=True)


def build_options_view(accounts):
    """Build aggregated options view with account attribution"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for opt in data['options']:
            key = f"{opt['ticker']}_{opt['type']}_{opt['strike']}"
            
            if key not in aggregated:
                aggregated[key] = {
                    'ticker': opt['ticker'],
                    'type': opt['type'],
                    'strike': opt['strike'],
                    'expiration': opt['expiration'],
                    'total_contracts': 0,
                    'total_entry_value': 0,
                    'accounts': []
                }
            
            contracts = opt['contracts']
            premium = opt['entry_premium']
            entry_value = contracts * premium * 100  # 100 shares per contract
            
            aggregated[key]['total_contracts'] += contracts
            aggregated[key]['total_entry_value'] += entry_value
            aggregated[key]['accounts'].append({
                'account': account_name,
                'contracts': contracts,
                'entry_premium': premium,
                'entry_value': entry_value
            })
    
    # Options show entry value (current value requires live options API)
    for key, data in aggregated.items():
        data['current_value'] = data['total_entry_value']  # Fallback to entry value
        data['note'] = 'Current value = Entry value (live options pricing requires upgrade)'
    
    return sorted(list(aggregated.values()), key=lambda x: x['current_value'], reverse=True)


def build_cash_view(accounts, prices):
    """Build aggregated cash view with account attribution"""
    aggregated = {
        'Cash': {'total': 0, 'accounts': []},
        'SGOV': {'total': 0, 'total_shares': 0, 'price': 0, 'accounts': []}
    }
    
    for account_name, data in accounts.items():
        for cash in data['cash']:
            asset = cash['asset']
            quantity = cash['quantity']
            
            if asset == 'Cash':
                value = quantity  # Already a dollar value
                aggregated['Cash']['total'] += value
                aggregated['Cash']['accounts'].append({
                    'account': account_name,
                    'value': value
                })
            elif asset == 'SGOV':
                price_data = prices.get('SGOV', {})
                price = price_data.get('price', 100.52)
                value = quantity * price
                aggregated['SGOV']['total'] += value
                aggregated['SGOV']['total_shares'] += quantity
                aggregated['SGOV']['price'] = price
                aggregated['SGOV']['accounts'].append({
                    'account': account_name,
                    'shares': quantity,
                    'value': value
                })
    
    return aggregated


def build_misc_view(accounts, prices):
    """Build aggregated misc view with account attribution"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for misc in data['misc']:
            asset = misc['asset']
            
            if asset not in aggregated:
                price_data = prices.get(asset, {})
                aggregated[asset] = {
                    'asset': asset,
                    'type': misc['type'],
                    'total_amount': 0,
                    'total_cost_basis': 0,
                    'price': price_data.get('price', 0),
                    'price_source': price_data.get('source', 'unknown'),
                    'accounts': []
                }
            
            amount = misc['amount']
            cost_basis = misc['cost_basis']
            price = aggregated[asset]['price']
            value = amount * price
            return_val = value - cost_basis
            return_pct = (return_val / cost_basis * 100) if cost_basis else 0
            
            aggregated[asset]['total_amount'] += amount
            aggregated[asset]['total_cost_basis'] += cost_basis
            aggregated[asset]['accounts'].append({
                'account': account_name,
                'amount': amount,
                'cost_basis': cost_basis,
                'value': value,
                'return': return_val,
                'return_pct': return_pct
            })
    
    # Calculate totals
    for asset, data in aggregated.items():
        data['total_value'] = data['total_amount'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['total_return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] else 0
    
    return sorted(list(aggregated.values()), key=lambda x: x['total_value'], reverse=True)


def build_totals(stocks, options, cash, misc):
    """Calculate category totals"""
    stocks_total = sum(s['total_value'] for s in stocks)
    options_total = sum(o['current_value'] for o in options)
    cash_total = cash['Cash']['total'] + cash['SGOV']['total']
    misc_total = sum(m['total_value'] for m in misc)
    
    return {
        'stocks_etfs': stocks_total,
        'options': options_total,
        'cash_equivalents': cash_total,
        'misc': misc_total,
        'grand_total': stocks_total + options_total + cash_total + misc_total
    }



@app.route('/api/portfolio')
def api_portfolio():
    """Return complete portfolio data"""
    # Load price cache
    load_price_cache()
    
    # Parse source data
    accounts = parse_unified_tracker_v2(PORTFOLIO_FILE)
    
    # Collect all tickers and assets
    all_tickers = set()
    misc_assets = set()
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                all_tickers.add(stock['ticker'])
        for misc in data['misc']:
            misc_assets.add(misc['asset'])
    
    # Add SGOV to tickers for cash calculation
    all_tickers.add('SGOV')
    
    # Get prices
    prices = {}
    for ticker in all_tickers:
        if ticker in price_cache:
            prices[ticker] = price_cache[ticker]
        else:
            prices[ticker] = {'price': 0, 'source': 'unknown', 'note': 'Price not available'}
    
    for asset in misc_assets:
        if asset in price_cache:
            prices[asset] = price_cache[asset]
        else:
            prices[asset] = {'price': 0, 'source': 'unknown', 'note': 'Price not available'}
    
    # Build all views
    stocks = build_stocks_view(accounts, prices)
    options = build_options_view(accounts)
    cash = build_cash_view(accounts, prices)
    misc = build_misc_view(accounts, prices)
    totals = build_totals(stocks, options, cash, misc)
    
    # Calculate last refresh time
    last_refresh = datetime.fromtimestamp(price_cache_time).isoformat() if price_cache_time else 'Never'
    
    return jsonify({
        'last_price_refresh': last_refresh,
        'stocks': stocks,
        'options': options,
        'cash': cash,
        'misc': misc,
        'totals': totals
    })


@app.route('/api/refresh-prices', methods=['POST'])
def api_refresh_prices():
    """Refresh all prices from APIs"""
    # Load price cache first
    load_price_cache()
    
    # Parse source data to get tickers
    accounts = parse_unified_tracker_v2(PORTFOLIO_FILE)
    
    all_tickers = set()
    misc_assets = set()
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                all_tickers.add(stock['ticker'])
        for misc in data['misc']:
            misc_assets.add(misc['asset'])
    
    all_tickers.add('SGOV')
    
    # Refresh prices
    results = refresh_all_prices(list(all_tickers), list(misc_assets))
    
    return jsonify({
        'success': True,
        'results': results,
        'last_updated': datetime.now().isoformat()
    })


@app.route('/')
def dashboard():
    """Render dashboard"""
    return render_template('dashboard.html')


if __name__ == '__main__':
    # Load price cache on startup
    load_price_cache()
    app.run(host='0.0.0.0', port=8080, debug=True)
