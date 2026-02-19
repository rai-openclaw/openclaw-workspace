# Technical Design Spec: Mission Control v2.0 - Complete Rebuild

**Version:** 2.0 (Final)  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed  

---

## 1. Architecture Overview

### System Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Mission Control v2.0                     │
├─────────────────────────────────────────────────────────────┤
│  Data Layer          │  portfolio/unified_portfolio_tracker.md
│                      │  portfolio/price_cache.json
├─────────────────────────────────────────────────────────────┤
│  Backend (Flask)     │  server.py
│  - Parser            │    Parse v2 markdown
│  - Price Fetcher     │    Finnhub/Yahoo/CoinGecko
│  - API Endpoints     │    /api/portfolio, /api/refresh-prices
│                      │    + all other tabs
├─────────────────────────────────────────────────────────────┤
│  Frontend            │  templates/dashboard.html
│  - Holdings Tab      │    5 sections with proper columns
│  - Other Tabs        │    Earnings, Analysis, Ideas, etc.
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Model

### 2.1 Source Data: `portfolio/unified_portfolio_tracker.md`

**Format:**
```markdown
# Unified Portfolio Tracker

## Account: {AccountName}
**Type:** {AccountType}  
**Broker:** {BrokerName}

### Stocks & ETFs
| Ticker | Shares | Cost Basis | Notes |
|--------|--------|------------|-------|
| AAPL   | 100    | $15,000    |       |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| PYPL   | PUT  | $45.00 | 2026-02-20 | -10       | $4.50         |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis | Category        |
|-------|----------|------------|-----------------|
| Cash  | $11,432  | —          | cash            |
| SGOV  | 201.20   | $20,224.62 | cash_equivalent |

### Misc
| Asset | Amount | Type   | Cost Basis |
|-------|--------|--------|------------|
| ETH   | 11.43  | crypto | $28,575    |

---
```

**Key Rules:**
- Only raw data (no calculated values)
- Cost basis = total dollars paid (not per share)
- Cash equivalents marked with `Category: cash_equivalent`
- One account per section, separated by `---`

### 2.2 Price Cache: `portfolio/price_cache.json`

**Format:**
```json
{
  "version": "2.0",
  "last_updated": "2026-02-15T21:00:00Z",
  "prices": {
    "AAPL": {
      "price": 150.00,
      "source": "finnhub",
      "last_updated": "2026-02-15T21:00:00Z"
    },
    "VSEQX": {
      "price": 39.46,
      "source": "yahoo_finance",
      "last_updated": "2026-02-15T21:00:00Z"
    },
    "ETH": {
      "price": 1900.00,
      "source": "coingecko",
      "last_updated": "2026-02-15T21:00:00Z"
    }
  }
}
```

---

## 3. Backend Implementation

### 3.1 File: `server.py` (Complete New File)

**Dependencies:**
- Flask
- Python standard library only (urllib, json, re, datetime, os)

**Structure:**
```python
#!/usr/bin/env python3
"""Mission Control v2.0 - Portfolio Dashboard"""

import os
import json
import re
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Configuration
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE, 'portfolio', 'unified_portfolio_tracker.md')
PRICE_FILE = os.path.join(WORKSPACE, 'portfolio', 'price_cache.json')

# API Keys (use environment variables in production)
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', 'd68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0')

# ============================================================================
# SECTION 1: Data Parsing
# ============================================================================

def parse_markdown_table(content, section_marker):
    """Extract table data from markdown section"""
    lines = content.split('\n')
    in_section = False
    headers = []
    rows = []
    
    for line in lines:
        if section_marker in line:
            in_section = True
            continue
        
        if in_section:
            if line.startswith('###') or line.startswith('---'):
                break
            
            if '|' in line and not headers:
                headers = [h.strip() for h in line.split('|') if h.strip()]
                continue
            
            if '|' in line and '---' not in line and headers:
                values = [v.strip() for v in line.split('|') if v.strip()]
                if values:
                    row = dict(zip(headers, values))
                    rows.append(row)
    
    return rows

def parse_unified_tracker(filepath):
    """Parse v2 unified tracker into structured data"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    accounts = {}
    sections = content.split('## Account: ')
    
    for section in sections[1:]:  # Skip header
        lines = section.strip().split('\n')
        account_name = lines[0].strip()
        
        accounts[account_name] = {
            'stocks': [],
            'options': [],
            'cash': [],
            'misc': []
        }
        
        # Parse Stocks
        for row in parse_markdown_table(section, '### Stocks & ETFs'):
            try:
                ticker = row.get('Ticker', '')
                if ticker and ticker not in ['Ticker', '—']:
                    shares = float(row.get('Shares', '0').replace(',', ''))
                    cost_basis = float(row.get('Cost Basis', '0').replace('$', '').replace(',', ''))
                    accounts[account_name]['stocks'].append({
                        'ticker': ticker,
                        'shares': shares,
                        'cost_basis': cost_basis
                    })
            except:
                continue
        
        # Parse Options
        for row in parse_markdown_table(section, '### Options Positions'):
            try:
                ticker = row.get('Ticker', '')
                if ticker and ticker not in ['Ticker', '—']:
                    accounts[account_name]['options'].append({
                        'ticker': ticker,
                        'type': row.get('Type', ''),
                        'strike': row.get('Strike', ''),
                        'expiration': row.get('Expiration', ''),
                        'contracts': int(row.get('Contracts', '0')),
                        'entry_premium': float(row.get('Entry Premium', '0').replace('$', ''))
                    })
            except:
                continue
        
        # Parse Cash
        for row in parse_markdown_table(section, '### Cash & Cash Equivalents'):
            try:
                asset = row.get('Asset', '')
                if asset and asset not in ['Asset', '—']:
                    quantity = row.get('Quantity', '0').replace(',', '').replace('$', '')
                    cost_basis = row.get('Cost Basis', '0').replace('$', '').replace(',', '').replace('—', '0')
                    accounts[account_name]['cash'].append({
                        'asset': asset,
                        'quantity': float(quantity) if quantity else 0,
                        'cost_basis': float(cost_basis) if cost_basis else 0,
                        'category': row.get('Category', 'cash')
                    })
            except:
                continue
        
        # Parse Misc
        for row in parse_markdown_table(section, '### Misc'):
            try:
                asset = row.get('Asset', '')
                if asset and asset not in ['Asset', '—']:
                    amount = float(row.get('Amount', '0').replace(',', ''))
                    cost_basis = float(row.get('Cost Basis', '0').replace('$', '').replace(',', ''))
                    accounts[account_name]['misc'].append({
                        'asset': asset,
                        'amount': amount,
                        'type': row.get('Type', ''),
                        'cost_basis': cost_basis
                    })
            except:
                continue
    
    return accounts

# ============================================================================
# SECTION 2: Price Management
# ============================================================================

def load_price_cache():
    """Load price cache from disk"""
    try:
        with open(PRICE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('prices', {}), data.get('last_updated', '')
    except:
        return {}, ''

def save_price_cache(prices, last_updated):
    """Save price cache to disk"""
    data = {
        'version': '2.0',
        'last_updated': last_updated,
        'prices': prices
    }
    with open(PRICE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_finnhub_price(ticker):
    """Fetch stock price from Finnhub"""
    try:
        import urllib.request
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('c', 0)
    except:
        return 0

def fetch_yahoo_price(ticker):
    """Fetch mutual fund price from Yahoo Finance"""
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
    """Fetch crypto price from CoinGecko"""
    try:
        import urllib.request
        asset_map = {'ETH': 'ethereum', 'BTC': 'bitcoin'}
        asset_id = asset_map.get(asset, asset.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get(asset_id, {}).get('usd', 0)
    except:
        return 0

def refresh_prices(accounts):
    """Refresh all prices from APIs"""
    prices, _ = load_price_cache()
    now = datetime.now().isoformat()
    
    # Collect tickers
    stock_tickers = set()
    misc_assets = set()
    
    for account in accounts.values():
        for stock in account['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                stock_tickers.add(stock['ticker'])
        for item in account['misc']:
            misc_assets.add(item['asset'])
    
    # Add SGOV
    stock_tickers.add('SGOV')
    
    # Fetch stock prices (Finnhub)
    for ticker in stock_tickers:
        if ticker in ['VSEQX', 'VTCLX', 'VTMSX']:
            # Mutual funds - try Yahoo Finance
            price = fetch_yahoo_price(ticker)
            source = 'yahoo_finance'
        else:
            price = fetch_finnhub_price(ticker)
            source = 'finnhub'
        
        if price > 0:
            prices[ticker] = {
                'price': price,
                'source': source,
                'last_updated': now
            }
    
    # Fetch crypto prices
    for asset in misc_assets:
        price = fetch_coingecko_price(asset)
        if price > 0:
            prices[asset] = {
                'price': price,
                'source': 'coingecko',
                'last_updated': now
            }
    
    save_price_cache(prices, now)
    return prices

# ============================================================================
# SECTION 3: View Builders
# ============================================================================

def build_stocks_view(accounts, prices):
    """Build aggregated stocks view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            ticker = stock['ticker']
            
            # Skip cash equivalents
            if ticker in ['SGOV', 'Cash']:
                continue
            
            if ticker not in aggregated:
                price_data = prices.get(ticker, {'price': 0, 'source': 'unknown'})
                aggregated[ticker] = {
                    'ticker': ticker,
                    'total_shares': 0,
                    'total_cost_basis': 0,
                    'accounts': [],
                    'price': price_data['price'],
                    'price_source': price_data.get('source', 'unknown'),
                    'price_updated': price_data.get('last_updated', '')
                }
            
            shares = stock['shares']
            cost_basis = stock['cost_basis']
            price = aggregated[ticker]['price']
            value = shares * price
            
            aggregated[ticker]['total_shares'] += shares
            aggregated[ticker]['total_cost_basis'] += cost_basis
            aggregated[ticker]['accounts'].append({
                'account': account_name,
                'shares': shares,
                'cost_basis': cost_basis,
                'value': value
            })
    
    # Calculate derived values
    for ticker, data in aggregated.items():
        data['cost_per_share'] = data['total_cost_basis'] / data['total_shares'] if data['total_shares'] > 0 else 0
        data['total_value'] = data['total_shares'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['total_return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] > 0 else 0
    
    return sorted(list(aggregated.values()), key=lambda x: x['total_value'], reverse=True)

def build_options_view(accounts):
    """Build aggregated options view"""
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
            entry_value = contracts * premium * 100
            
            aggregated[key]['total_contracts'] += contracts
            aggregated[key]['total_entry_value'] += entry_value
            aggregated[key]['accounts'].append({
                'account': account_name,
                'contracts': contracts,
                'entry_premium': premium,
                'entry_value': entry_value
            })
    
    for key, data in aggregated.items():
        data['current_value'] = data['total_entry_value']  # Fallback
        data['note'] = 'Current value = Entry value (live options pricing requires upgrade)'
    
    return sorted(list(aggregated.values()), key=lambda x: x['current_value'], reverse=True)

def build_cash_view(accounts, prices):
    """Build aggregated cash view"""
    aggregated = {
        'Cash': {'total': 0, 'accounts': []},
        'SGOV': {'total': 0, 'total_shares': 0, 'price': 0, 'accounts': []}
    }
    
    for account_name, data in accounts.items():
        for cash in data['cash']:
            asset = cash['asset']
            
            if asset == 'Cash':
                value = cash['quantity']
                aggregated['Cash']['total'] += value
                aggregated['Cash']['accounts'].append({
                    'account': account_name,
                    'value': value
                })
            elif asset == 'SGOV':
                price_data = prices.get('SGOV', {'price': 100.52})
                price = price_data['price']
                value = cash['quantity'] * price
                aggregated['SGOV']['total'] += value
                aggregated['SGOV']['total_shares'] += cash['quantity']
                aggregated['SGOV']['price'] = price
                aggregated['SGOV']['accounts'].append({
                    'account': account_name,
                    'shares': cash['quantity'],
                    'value': value
                })
    
    return aggregated

def build_misc_view(accounts, prices):
    """Build aggregated misc view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for item in data['misc']:
            asset = item['asset']
            
            if asset not in aggregated:
                price_data = prices.get(asset, {'price': 0})
                aggregated[asset] = {
                    'asset': asset,
                    'type': item['type'],
                    'total_amount': 0,
                    'total_cost_basis': 0,
                    'price': price_data['price'],
                    'accounts': []
                }
            
            amount = item['amount']
            cost_basis = item['cost_basis']
            price = aggregated[asset]['price']
            value = amount * price
            
            aggregated[asset]['total_amount'] += amount
            aggregated[asset]['total_cost_basis'] += cost_basis
            aggregated[asset]['accounts'].append({
                'account': account_name,
                'amount': amount,
                'cost_basis': cost_basis,
                'value': value
            })
    
    for asset, data in aggregated.items():
        data['cost_per_unit'] = data['total_cost_basis'] / data['total_amount'] if data['total_amount'] > 0 else 0
        data['total_value'] = data['total_amount'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['total_return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] > 0 else 0
    
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

# ============================================================================
# SECTION 4: API Endpoints
# ============================================================================

@app.route('/api/portfolio')
def api_portfolio():
    """Return complete portfolio data"""
    accounts = parse_unified_tracker(DATA_FILE)
    prices, last_updated = load_price_cache()
    
    stocks = build_stocks_view(accounts, prices)
    options = build_options_view(accounts)
    cash = build_cash_view(accounts, prices)
    misc = build_misc_view(accounts, prices)
    totals = build_totals(stocks, options, cash, misc)
    
    return jsonify({
        'last_price_refresh': last_updated,
        'stocks': stocks,
        'options': options,
        'cash': cash,
        'misc': misc,
        'totals': totals
    })

@app.route('/api/refresh-prices', methods=['POST'])
def api_refresh_prices():
    """Refresh all prices"""
    accounts = parse_unified_tracker(DATA_FILE)
    prices = refresh_prices(accounts)
    return jsonify({'success': True, 'prices_updated': len(prices)})

# Additional endpoints for other tabs
@app.route('/api/analysis-archive')
def api_analysis_archive():
    """Return stock analysis"""
    try:
        with open(os.path.join(WORKSPACE, 'portfolio', 'portfolio_tracker.md'), 'r') as f:
            content = f.read()
        
        analyses = []
        sections = content.split('##')
        for section in sections:
            if 'Detailed Analysis' in section:
                lines = section.strip().split('\n')
                ticker = lines[0].split()[0] if lines else ''
                analyses.append({
                    'ticker': ticker,
                    'summary': 'Analysis available',
                    'full_text': section
                })
        return jsonify(analyses)
    except:
        return jsonify([])

@app.route('/api/earnings-research')
def api_earnings_research():
    """Return earnings research"""
    try:
        filepath = os.path.join(WORKSPACE, 'daily_earnings_research.md')
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    except:
        return jsonify({'content': 'No research available'})

@app.route('/api/ideas')
def api_ideas():
    """Return ideas"""
    try:
        filepath = os.path.join(WORKSPACE, 'ideas', 'NOTES.md')
        ideas = []
        with open(filepath, 'r') as f:
            content = f.read()
        # Simple parsing
        lines = content.split('\n')
        category = ''
        for line in lines:
            if line.startswith('###'):
                category = line.replace('###', '').strip()
            elif line.strip().startswith('- Idea:'):
                ideas.append({
                    'category': category,
                    'content': line.replace('- Idea:', '').strip()
                })
        return jsonify(ideas)
    except:
        return jsonify([])

@app.route('/api/schedule')
def api_schedule():
    """Return schedule"""
    return jsonify([
        {'date': 'Feb 18', 'event': 'Market Open', 'time': '6:30 AM'},
        {'date': 'Feb 25', 'event': 'CRM Earnings', 'time': 'After Close'},
        {'date': 'Feb 26', 'event': 'RKT Earnings', 'time': 'After Close'}
    ])

@app.route('/api/corporate')
def api_corporate():
    """Return corporate structure"""
    return jsonify({
        'team': [
            {'name': 'Dave', 'role': 'Chief Briefer'},
            {'name': 'Bob', 'role': 'Senior Earnings Analyst'},
            {'name': 'EA', 'role': 'Executive Assistant'}
        ]
    })

@app.route('/api/usage')
def api_usage():
    """Return API usage"""
    return jsonify({'apis': {}})

@app.route('/api/system/spec')
def api_system_spec():
    """Return system spec"""
    return jsonify({'version': '2.0'})

@app.route('/')
def dashboard():
    """Render dashboard"""
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

---

## 4. Frontend Implementation

### 4.1 File: `templates/dashboard.html` (Complete New File)

**Key Features:**
- Clean, single-file implementation
- No external dependencies
- Responsive design
- Dark theme

**Holdings Tab - 5 Sections:**

**Section 1: Stocks & ETFs**
```
Columns: Ticker | Shares | Price | Cost/Share | Value | P/L % | Accounts
```

**Section 2: Options Positions**
```
Columns: Ticker | Type | Strike | Expiration | Contracts | Entry Premium | Value | Accounts
```

**Section 3: Cash & Cash Equivalents**
```
Columns: Asset | Total | Details | Accounts
```

**Section 4: Misc**
```
Columns: Asset | Type | Amount | Price | Cost/Unit | Value | P/L % | Accounts
```

**Section 5: Total Portfolio**
```
Shows: Stocks | Options | Cash | Misc | Grand Total
```

**Color Coding:**
- Green (`#10b981`) for positive P/L
- Red (`#ef4444`) for negative P/L

**Asterisk Logic:**
- Show `*` next to price if `last_updated` > 24 hours ago
- Legend explains: "* Price cached more than 24 hours ago"

**Account Attribution:**
- Expandable dropdown showing dollar values per account
- Example: "Robinhood: $26,152" not "Robinhood: 1,400 shares"

---

## 5. Implementation Checklist

### Phase 1: Create Files
- [ ] Create `server.py` with all code above
- [ ] Create `dashboard.html` with complete UI
- [ ] Ensure `unified_portfolio_tracker.md` and `price_cache.json` exist

### Phase 2: Test Backend
- [ ] Parse data file without errors
- [ ] Load price cache
- [ ] Build all 4 views (stocks, options, cash, misc)
- [ ] Calculate totals correctly
- [ ] All API endpoints respond

### Phase 3: Test Frontend
- [ ] Dashboard loads
- [ ] Holdings tab shows all 5 sections
- [ ] Cost per share displayed
- [ ] P/L % with colors
- [ ] Account breakdown shows dollar values
- [ ] Refresh button works
- [ ] Other tabs (Earnings, Analysis, Ideas) work

### Phase 4: Verify Data
- [ ] Grand total adds up
- [ ] SGOV only in Cash (not Stocks)
- [ ] No duplicate entries
- [ ] Prices cached correctly

---

## 6. Maintenance Guide

### Adding a New Account
1. Add new `## Account:` section to `unified_portfolio_tracker.md`
2. Fill in all 4 subsections (even if empty)
3. Click "Refresh Prices" in dashboard
4. New account automatically included in totals

### Making a Trade
1. Edit `unified_portfolio_tracker.md`
2. Update shares and cost basis
3. Update cash if needed
4. Click "Refresh Prices"

### Updating Prices Manually
1. Edit `price_cache.json`
2. Update price and timestamp
3. Refresh dashboard

---

**Proceed with complete rebuild?**
