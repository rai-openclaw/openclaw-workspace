#!/usr/bin/env python3
"""
Mission Control v2.0 - Portfolio Dashboard
Complete rebuild - Holdings + Stock Analysis Archive tabs
"""

import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Configuration
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE, 'portfolio', 'unified_portfolio_tracker.md')
PRICE_FILE = os.path.join(WORKSPACE, 'portfolio', 'price_cache.json')
ANALYSIS_FILE = os.path.join(WORKSPACE, 'portfolio', 'portfolio_tracker.md')
EARNINGS_FILE = os.path.join(WORKSPACE, 'daily_earnings_research.md')
IDEAS_FILE = os.path.join(WORKSPACE, 'ideas', 'NOTES.md')
SCHEDULE_FILE = os.path.join(WORKSPACE, 'son_schedule.md')
CORPORATE_FILE = os.path.join(WORKSPACE, 'mission_control', 'corporate_structure.md')
SPEC_FILE = os.path.join(WORKSPACE, 'mission_control', 'docs', 'specs', 'mission_control_spec.md')

# API Keys
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', 'd68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0')

# API Usage Tracking (in-memory for now, could persist to file)
api_usage_data = {
    'Moonshot': {
        'name': 'Moonshot AI',
        'purpose': 'Primary LLM for analysis and reasoning',
        'status': 'Active',
        'tier': 'Paid',
        'limit': 'Unlimited',
        'calls_this_month': 0,
        'cost': 0.0,
        'billing_url': 'https://platform.moonshot.cn',
        'key': 'Environment variable'
    },
    'Finnhub': {
        'name': 'Finnhub',
        'purpose': 'Stock prices and financial data',
        'status': 'Active',
        'tier': 'Free',
        'limit': '60 calls/minute',
        'calls_this_month': 0,
        'cost': 0.0,
        'billing_url': 'https://finnhub.io',
        'key': 'Environment variable'
    },
    'Gemini': {
        'name': 'Google Gemini',
        'purpose': 'Backup LLM and image analysis',
        'status': 'Active',
        'tier': 'Free',
        'limit': '60 requests/minute',
        'calls_this_month': 0,
        'cost': 0.0,
        'billing_url': 'https://ai.google.dev',
        'key': 'Environment variable'
    },
    'Brave': {
        'name': 'Brave Search',
        'purpose': 'Web search for research',
        'status': 'Active',
        'tier': 'Free',
        'limit': '2000 queries/month',
        'calls_this_month': 0,
        'cost': 0.0,
        'billing_url': 'https://brave.com/search/api',
        'key': 'Environment variable'
    },
    'CoinGecko': {
        'name': 'CoinGecko',
        'purpose': 'Cryptocurrency prices',
        'status': 'Active',
        'tier': 'Free',
        'limit': '10-30 calls/minute',
        'calls_this_month': 0,
        'cost': 0.0,
        'billing_url': 'https://www.coingecko.com/api',
        'key': 'Environment variable'
    }
}

# ============================================================================
# DATA PARSING
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
                values = [v.strip() for v in line.split('|')]
                while values and values[0] == '':
                    values.pop(0)
                while len(values) > len(headers) and values and values[-1] == '':
                    values.pop()
                if values and len(values) >= len(headers) - 1:
                    row = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            row[header] = values[i]
                        else:
                            row[header] = ''
                    rows.append(row)
    
    return rows


def parse_unified_tracker(filepath):
    """Parse v2 unified tracker into structured data"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    accounts = {}
    sections = content.split('## Account: ')
    
    for section in sections[1:]:
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
                    contracts = int(row.get('Contracts', '0'))
                    premium = float(row.get('Entry Premium', '0').replace('$', ''))
                    accounts[account_name]['options'].append({
                        'ticker': ticker,
                        'type': row.get('Type', ''),
                        'strike': row.get('Strike', ''),
                        'expiration': row.get('Expiration', ''),
                        'contracts': contracts,
                        'entry_premium': premium
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
                    category = row.get('Category', 'cash')
                    accounts[account_name]['cash'].append({
                        'asset': asset,
                        'quantity': float(quantity) if quantity else 0,
                        'cost_basis': float(cost_basis) if cost_basis else 0,
                        'category': category
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
# PRICE MANAGEMENT
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


# ============================================================================
# VIEW BUILDERS
# ============================================================================

def build_stocks_view(accounts, prices):
    """Build aggregated stocks view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            ticker = stock['ticker']
            
            if ticker in ['SGOV', 'Cash']:
                continue
            
            if ticker not in aggregated:
                price_data = prices.get(ticker, {'price': 0, 'source': 'unknown', 'last_updated': ''})
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
        data['current_value'] = data['total_entry_value']
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
# ANALYSIS ARCHIVE
# ============================================================================

def parse_analysis_archive(filepath):
    """Parse stock analysis from portfolio_tracker.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return []
    
    import re
    analyses = []
    
    pattern = r'^## ([^#].*?)(?=\n## [^#]|\Z)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for section in matches:
        if 'Detailed Analysis' in section:
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            header = lines[0]
            ticker = header.split()[0] if header else ''
            
            summary_lines = []
            for line in lines[1:20]:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('|') and not stripped.startswith('---'):
                    summary_lines.append(stripped)
                if len(summary_lines) >= 3:
                    break
            
            summary = ' '.join(summary_lines) if summary_lines else 'Analysis available'
            
            analyses.append({
                'ticker': ticker,
                'summary': summary[:200],
                'full_text': '\n'.join(lines[1:]) if len(lines) > 1 else ''
            })
    
    return analyses


# ============================================================================
# EARNINGS RESEARCH PARSER
# ============================================================================

def parse_earnings_research(filepath):
    """Parse earnings research from daily_earnings_research.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return []
    
    entries = []
    lines = content.split('\n')
    current_entry = None
    
    for line in lines:
        line = line.strip()
        
        # Date headers
        if line.startswith('## '):
            current_date = line.replace('## ', '').strip()
            continue
        
        # Stock ticker headers (### TICKER)
        if line.startswith('### ') and len(line) > 4:
            if current_entry:
                entries.append(current_entry)
            ticker = line.replace('### ', '').strip()
            current_entry = {
                'ticker': ticker,
                'date': current_date if 'current_date' in locals() else '',
                'grade': '',
                'action': '',
                'expected_move': '',
                'iv_rank': '',
                'historical_accuracy': '',
                'news_summary': [],
                'risk_flags': [],
                'setup_notes': []
            }
            continue
        
        if not current_entry:
            continue
        
        # Parse fields
        if line.startswith('**Grade:**'):
            current_entry['grade'] = line.replace('**Grade:**', '').strip()
        elif line.startswith('**Action:**'):
            current_entry['action'] = line.replace('**Action:**', '').strip()
        elif line.startswith('**Expected Move:**'):
            current_entry['expected_move'] = line.replace('**Expected Move:**', '').strip()
        elif line.startswith('**IV Rank:**'):
            current_entry['iv_rank'] = line.replace('**IV Rank:**', '').strip()
        elif line.startswith('**Historical Accuracy:**'):
            current_entry['historical_accuracy'] = line.replace('**Historical Accuracy:**', '').strip()
        elif line.startswith('- ') and 'news' in str(current_entry.get('parsing_section', '')).lower():
            current_entry['news_summary'].append(line.replace('- ', '').strip())
        elif line.startswith('- ') and 'risk' in str(current_entry.get('parsing_section', '')).lower():
            current_entry['risk_flags'].append(line.replace('- ', '').strip())
        elif line.startswith('**News Summary:**'):
            current_entry['parsing_section'] = 'news'
        elif line.startswith('**Risk Flags:**'):
            current_entry['parsing_section'] = 'risk'
        elif line.startswith('**Setup Notes:**'):
            current_entry['parsing_section'] = 'setup'
        elif line.startswith('- ') and current_entry.get('parsing_section') == 'setup':
            current_entry['setup_notes'].append(line.replace('- ', '').strip())
    
    if current_entry:
        entries.append(current_entry)
    
    return entries


# ============================================================================
# IDEAS PARSER
# ============================================================================

def parse_ideas(filepath):
    """Parse ideas from NOTES.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return []
    
    ideas = []
    lines = content.split('\n')
    current_category = ''
    
    for line in lines:
        line = line.strip()
        
        # Category headers (### Category)
        if line.startswith('### '):
            current_category = line.replace('### ', '').strip()
            continue
        
        # Idea entries
        if line.startswith('- Idea:'):
            idea_content = line.replace('- Idea:', '').strip()
            ideas.append({
                'category': current_category,
                'content': idea_content,
                'id': len(ideas)
            })
    
    return ideas


# ============================================================================
# SCHEDULE PARSER
# ============================================================================

def parse_schedule(filepath):
    """Parse schedule from son_schedule.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return []
    
    events = []
    table_rows = parse_markdown_table(content, '## 🗓️ Upcoming Events')
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for row in table_rows:
        if row.get('Date') and row['Date'] not in ['Date', '—']:
            event_date = row.get('Date', '')
            events.append({
                'date': event_date,
                'time': row.get('Time', ''),
                'event': row.get('Event', ''),
                'location': row.get('Location', ''),
                'notes': row.get('Notes', ''),
                'is_today': event_date == today
            })
    
    return events


# ============================================================================
# CORPORATE STRUCTURE PARSER
# ============================================================================

def parse_corporate_structure(filepath):
    """Parse corporate structure from corporate_structure.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return {'team': [], 'departments': []}
    
    team = []
    departments = []
    lines = content.split('\n')
    current_dept = None
    current_person = None
    
    for line in lines:
        line = line.strip()
        
        # Department headers (## Department)
        if line.startswith('## ') and not line.startswith('## Current') and 'Updated' not in line:
            current_dept = line.replace('## ', '').strip()
            departments.append({
                'name': current_dept,
                'members': []
            })
            continue
        
        # Team member headers (### Name - Role)
        if line.startswith('### '):
            parts = line.replace('### ', '').split(' - ')
            name = parts[0].strip()
            role = parts[1].strip() if len(parts) > 1 else ''
            
            # Clean up emoji
            if name.startswith('👔') or name.startswith('🤵') or name.startswith('📋') or name.startswith('📊'):
                name = name[2:].strip()
            
            current_person = {
                'name': name,
                'role': role,
                'department': current_dept,
                'details': {},
                'status': 'Active'
            }
            team.append(current_person)
            if departments:
                departments[-1]['members'].append(current_person)
            continue
        
        if not current_person:
            continue
        
        # Parse details
        if line.startswith('- **Role:**'):
            current_person['role'] = line.replace('- **Role:**', '').strip()
        elif line.startswith('- **Reports To:**'):
            current_person['reports_to'] = line.replace('- **Reports To:**', '').strip()
        elif line.startswith('- **Schedule:**'):
            current_person['schedule'] = line.replace('- **Schedule:**', '').strip()
        elif line.startswith('- **Status:**'):
            status = line.replace('- **Status:**', '').strip()
            current_person['status'] = status
    
    return {'team': team, 'departments': departments}


# ============================================================================
# SYSTEM SPEC PARSER
# ============================================================================

def parse_system_spec(filepath):
    """Parse system spec from mission_control_spec.md"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return {'version': 'Unknown', 'architecture': '', 'apis': [], 'data_sources': []}
    
    spec = {
        'version': 'Unknown',
        'last_updated': '',
        'architecture': '',
        'data_sources': [],
        'apis': [],
        'full_content': content
    }
    
    lines = content.split('\n')
    
    # Extract version and date from header
    for line in lines[:20]:
        if 'Version:' in line:
            spec['version'] = line.split('Version:')[-1].strip()
        if 'Last Updated:' in line:
            spec['last_updated'] = line.split('Last Updated:')[-1].strip()
    
    # Extract architecture overview
    in_architecture = False
    architecture_lines = []
    for line in lines:
        if '## Architecture' in line:
            in_architecture = True
            continue
        if in_architecture and line.startswith('##'):
            break
        if in_architecture and line.strip():
            architecture_lines.append(line)
    spec['architecture'] = '\n'.join(architecture_lines).strip()
    
    return spec


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/portfolio')
def api_portfolio():
    """Return complete portfolio data for Holdings tab"""
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
    """Refresh all prices from APIs"""
    accounts = parse_unified_tracker(DATA_FILE)
    prices, _ = load_price_cache()
    now = datetime.now().isoformat()
    
    stock_tickers = set()
    misc_assets = set()
    
    for account in accounts.values():
        for stock in account['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                stock_tickers.add(stock['ticker'])
        for item in account['misc']:
            misc_assets.add(item['asset'])
    stock_tickers.add('SGOV')
    
    for ticker in stock_tickers:
        if ticker in ['VSEQX', 'VTCLX', 'VTMSX']:
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
        api_usage_data['Finnhub']['calls_this_month'] += 1
    
    for asset in misc_assets:
        price = fetch_coingecko_price(asset)
        if price > 0:
            prices[asset] = {
                'price': price,
                'source': 'coingecko',
                'last_updated': now
            }
        api_usage_data['CoinGecko']['calls_this_month'] += 1
    
    save_price_cache(prices, now)
    return jsonify({'success': True, 'updated': len(prices)})


@app.route('/api/analysis-archive')
def api_analysis_archive():
    """Return stock analysis archive for Analysis Archive tab"""
    analyses = parse_analysis_archive(ANALYSIS_FILE)
    return jsonify(analyses)


@app.route('/api/earnings-research')
def api_earnings_research():
    """Return earnings research for Earnings Research tab"""
    entries = parse_earnings_research(EARNINGS_FILE)
    return jsonify(entries)


@app.route('/api/ideas')
def api_ideas():
    """Return ideas for Ideas & Notes tab"""
    ideas = parse_ideas(IDEAS_FILE)
    return jsonify(ideas)


@app.route('/api/schedule')
def api_schedule():
    """Return schedule for Schedule tab"""
    events = parse_schedule(SCHEDULE_FILE)
    return jsonify(events)


@app.route('/api/corporate')
def api_corporate():
    """Return corporate structure for Corporate tab"""
    structure = parse_corporate_structure(CORPORATE_FILE)
    return jsonify(structure)


@app.route('/api/usage')
def api_usage():
    """Return API usage for API Usage tab"""
    # Calculate total cost
    total_cost = sum(api['cost'] for api in api_usage_data.values())
    return jsonify({
        'apis': api_usage_data,
        'total_estimated_cost': total_cost
    })


@app.route('/api/system/spec')
def api_system_spec():
    """Return system spec for System Spec tab"""
    spec = parse_system_spec(SPEC_FILE)
    
    # Get file structure
    file_structure = []
    base_path = os.path.join(WORKSPACE, 'mission_control')
    
    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and backups
        dirs[:] = [d for d in dirs if not d.startswith('.') and 'backup' not in d.lower()]
        
        level = root.replace(base_path, '').count(os.sep)
        indent = '  ' * level
        rel_path = os.path.relpath(root, base_path)
        if rel_path == '.':
            rel_path = 'mission_control/'
        else:
            rel_path = f'mission_control/{rel_path}/'
        
        file_structure.append(f'{indent}{rel_path}')
        
        subindent = '  ' * (level + 1)
        for file in sorted(files):
            if not file.startswith('.') and not file.endswith('.pyc'):
                file_structure.append(f'{subindent}{file}')
    
    spec['file_structure'] = '\n'.join(file_structure)
    return jsonify(spec)


@app.route('/')
def dashboard():
    """Render dashboard"""
    return render_template('dashboard.html')


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 6060
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)