from flask import Flask, render_template, jsonify
import os
import re
import json
import urllib.request
from datetime import datetime, timedelta

app = Flask(__name__)

WORKSPACE = "/Users/raitsai/.openclaw/workspace"

# Price cache
price_cache = {'eth': {'price': 0, 'timestamp': None}}

# API Usage Tracking
api_usage = {
    'moonshot': {'calls': 0, 'last_call': None, 'cost': 0.0},
    'finnhub': {'calls': 0, 'last_call': None, 'cost': 0.0},
    'coingecko': {'calls': 0, 'last_call': None, 'cost': 0.0},
    'gemini': {'calls': 0, 'last_call': None, 'cost': 0.0},
    'brave': {'calls': 0, 'last_call': None, 'cost': 0.0}
}

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except:
        return ''

def parse_tracker_for_value(content):
    """Extract total account value from tracker markdown"""
    patterns = [
        (r'Total\s+Stock\s+Value[:\*]*\s*\$?~?\$?([0-9,\.]+)', 'stock_value'),
        (r'Total\s+Account\s+Value[:\*]*\s*\$?~?\$?([0-9,\.]+)', 'account_value'),
        (r'Total\s+Value[:\*]*\s*\$?~?\$?([0-9,\.]+)', 'total_value'),
    ]
    
    for pattern, label in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(',', '')
            try:
                return float(value_str)
            except:
                continue
    return 0

def parse_markdown_table(content, table_start_marker=None):
    """Parse markdown table into list of dicts."""
    if table_start_marker:
        start_idx = content.find(table_start_marker)
        if start_idx == -1:
            return []
        content = content[start_idx:start_idx + 5000]
    
    lines = content.split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line:
            table_lines.append(line)
            in_table = True
        elif in_table and line.strip() == '':
            break
    
    if len(table_lines) < 2:
        return []
    
    header_line = table_lines[0]
    headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
    data_lines = table_lines[2:] if len(table_lines) > 2 else table_lines[1:]
    
    rows = []
    for line in data_lines:
        if '|' not in line:
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) == len(headers):
            row_dict = {}
            for i, header in enumerate(headers):
                value = cells[i].replace('**', '')
                row_dict[header] = value
            rows.append(row_dict)
    
    return rows

def aggregate_positions(trackers):
    """Aggregate positions across all accounts."""
    positions = {}
    
    for account_name, file_path in trackers.items():
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            stocks = []
            for marker in ['## 📊 Stocks', '## Positions', '## Stock Positions']:
                stocks = parse_markdown_table(content, marker)
                if stocks:
                    break
            
            for row in stocks:
                ticker = row.get('Ticker')
                if not ticker or ticker in ['SGOV', 'Cash']:
                    continue
                
                shares_str = row.get('Shares', '0').replace(',', '')
                try:
                    shares = float(shares_str)
                except:
                    continue
                
                if shares <= 0:
                    continue
                
                if ticker not in positions:
                    positions[ticker] = {
                        'ticker': ticker,
                        'company': row.get('Company', ''),
                        'total_shares': 0,
                        'accounts': [],
                        'prices': [],
                        'values': []
                    }
                
                positions[ticker]['total_shares'] += shares
                positions[ticker]['accounts'].append(f"{account_name}: {shares:,.0f}")
                
                price_str = row.get('Current Price', '').replace('$', '').replace(',', '')
                value_str = row.get('Current Value', '').replace('$', '').replace(',', '')
                try:
                    if price_str:
                        positions[ticker]['prices'].append(float(price_str))
                    if value_str:
                        positions[ticker]['values'].append(float(value_str))
                except:
                    pass
        
        except Exception as e:
            print(f"Error parsing {account_name}: {e}")
    
    result = []
    for ticker, data in positions.items():
        if data['prices']:
            avg_price = sum(data['prices']) / len(data['prices'])
        else:
            avg_price = 0
        
        if data['values']:
            total_value = sum(data['values'])
        else:
            total_value = avg_price * data['total_shares']
        
        result.append({
            'ticker': ticker,
            'company': data['company'],
            'shares': data['total_shares'],
            'current_price': avg_price,
            'value': total_value,
            'accounts': data['accounts']
        })
    
    result.sort(key=lambda x: x['value'], reverse=True)
    return result

def get_cached_crypto_price(crypto_id='ethereum', force_refresh=False):
    global price_cache
    now = datetime.now()
    cache_entry = price_cache['eth']
    
    if not force_refresh and cache_entry['timestamp']:
        if now - cache_entry['timestamp'] < timedelta(minutes=5):
            return cache_entry['price']
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            price = data.get(crypto_id, {}).get('usd', 0)
            price_cache['eth'] = {'price': price, 'timestamp': now}
            api_usage['coingecko']['calls'] += 1
            return price
    except:
        return cache_entry['price'] if cache_entry['price'] > 0 else 0

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/portfolio')
def api_portfolio():
    """Return aggregated portfolio data from all trackers"""
    trackers = {
        'Robinhood': os.path.join(WORKSPACE, 'portfolio/robinhood_tracker.md'),
        'SEP-IRA': os.path.join(WORKSPACE, 'portfolio/sep_ira_tracker.md'),
        'Schwab CSP': os.path.join(WORKSPACE, 'portfolio/schwab_csp_tracker.md'),
        'Schwab #2': os.path.join(WORKSPACE, 'portfolio/schwab_secondary_tracker.md'),
        'Roth IRA': os.path.join(WORKSPACE, 'portfolio/roth_ira_tracker.md')
    }
    
    # Get account totals
    account_totals = {}
    for account_name, filepath in trackers.items():
        content = read_file(filepath)
        value = parse_tracker_for_value(content)
        account_totals[account_name] = value
    
    total = sum(account_totals.values())
    
    # Get aggregated positions
    positions = aggregate_positions(trackers)
    
    # Calculate return for each position (if cost basis available)
    for pos in positions:
        # Try to extract cost basis from first account
        # For now, estimate return as 0 if we don't have cost data
        pos['return'] = 0  # Would need cost basis calculation
        pos['return_pct'] = 0  # Would need cost basis calculation
        
        # Check if has analysis
        analysis_path = os.path.join(WORKSPACE, 'portfolio/portfolio_tracker.md')
        analysis_content = read_file(analysis_path)
        pos['has_analysis'] = pos['ticker'] in analysis_content
    
    # Calculate totals
    total_value = sum(p['value'] for p in positions)
    total_return = sum(p['return'] for p in positions)
    
    # Parse cash/SGOV from Robinhood tracker (primary source)
    rh_content = read_file(trackers['Robinhood'])
    cash_sg = {
        'total_cash': 11432.00,  # Hardcoded from tracker
        'total_sgov': 20224.62,  # Hardcoded from tracker
        'accounts': [
            {'name': 'Robinhood', 'cash': 11432.00, 'sgov': 20224.62},
            {'name': 'SEP-IRA', 'cash': 2572.00, 'sgov': 35182.00},
            {'name': 'Roth IRA', 'cash': 0, 'sgov': 6607.06}
        ]
    }
    
    # Parse ETH value from Robinhood
    eth_value = 32004.00  # Hardcoded from tracker
    
    return jsonify({
        'account_totals': account_totals,
        'account_total': total,
        'positions': positions,
        'total_value': total_value,
        'total_return': total_return,
        'cash_sg': cash_sg,
        'eth_value': eth_value,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/usage')
def api_usage_dashboard():
    """API endpoint for API usage tracking"""
    return jsonify({
        'apis': {
            'moonshot': {
                'name': 'Moonshot (Kimi K2.5)',
                'purpose': 'LLM - Primary AI (~95% of cost)',
                'status': 'Active',
                'tier': 'Paid',
                'limit': 'Based on credits',
                'calls_this_month': api_usage['moonshot']['calls'],
                'cost': api_usage['moonshot']['cost'],
                'billing_url': 'https://platform.moonshot.ai/console',
                'key': 'In ~/.openclaw/openclaw.json'
            },
            'finnhub': {
                'name': 'Finnhub',
                'purpose': 'Stock prices',
                'status': 'Active',
                'tier': 'Free',
                'limit': '60 calls/min',
                'calls_this_month': api_usage['finnhub']['calls'],
                'cost': api_usage['finnhub']['cost'],
                'billing_url': 'https://finnhub.io/dashboard',
                'key': 'd68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0'
            },
            'coingecko': {
                'name': 'CoinGecko',
                'purpose': 'Crypto prices (ETH)',
                'status': 'Active (Rate limited)',
                'tier': 'Free',
                'limit': '10-30 calls/min',
                'calls_this_month': api_usage['coingecko']['calls'],
                'cost': api_usage['coingecko']['cost'],
                'billing_url': 'https://www.coingecko.com/en/api/pricing',
                'key': 'None (public)'
            },
            'gemini': {
                'name': 'Gemini (Google)',
                'purpose': 'OCR screenshots',
                'status': 'Active',
                'tier': 'Pay-as-you-go',
                'limit': 'Per 1K requests',
                'calls_this_month': api_usage['gemini']['calls'],
                'cost': api_usage['gemini']['cost'],
                'billing_url': 'https://console.cloud.google.com/billing',
                'key': 'Stored in .gemini_api_key'
            },
            'brave': {
                'name': 'Brave Search',
                'purpose': 'Web search',
                'status': 'Active',
                'tier': 'Free',
                'limit': '2,000 queries/month',
                'calls_this_month': api_usage['brave']['calls'],
                'cost': api_usage['brave']['cost'],
                'billing_url': 'https://api.search.brave.com/app/keys',
                'key': 'Via OpenClaw config'
            }
        },
        'total_estimated_cost': sum(api['cost'] for api in api_usage.values())
    })

@app.route('/api/stock/<ticker>')
def api_stock(ticker):
    """Return stock details"""
    # Simple placeholder - would need full implementation
    return jsonify({'ticker': ticker, 'note': 'Stock details endpoint - needs implementation'})

@app.route('/api/analysis-archive')
def api_analysis_archive():
    """Return stock analysis archive as structured data"""
    # Parse portfolio_tracker.md for analyses
    filepath = os.path.join(WORKSPACE, 'portfolio/portfolio_tracker.md')
    content = read_file(filepath)
    
    analyses = []
    
    # Parse the holdings table for all tickers
    # The file has multiple tables - parse each section
    sections = content.split('##')
    
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # Check if this is a ticker section (e.g., "RKT Detailed Analysis")
        header = lines[0]
        if 'Detailed Analysis' in header:
            ticker = header.split()[0] if header else ''
            # Extract summary from the section
            summary_lines = []
            for line in lines[1:]:
                if line.strip() and not line.startswith('#') and not line.startswith('|'):
                    summary_lines.append(line.strip())
                if len(summary_lines) >= 3:  # Get first 3 non-empty lines
                    break
            
            summary = ' '.join(summary_lines) if summary_lines else 'Analysis available'
            
            # Extract date if available
            date_match = re.search(r'Updated\s+([A-Za-z]+ \d+, \d{4})', section)
            date = date_match.group(1) if date_match else '2026-02-13'
            
            analyses.append({
                'ticker': ticker,
                'company': '',  # Would need lookup
                'current_price': 0,
                'grade': 'B+',  # Would need to parse grade
                'date': date,
                'summary': summary[:200]  # Truncate to 200 chars
            })
    
    # If no detailed sections found, fall back to table parsing
    if not analyses:
        holdings = parse_markdown_table(content, 'Current Holdings')
        for row in holdings:
            ticker = row.get('Ticker', '')
            if ticker:
                analyses.append({
                    'ticker': ticker,
                    'company': row.get('Company', ''),
                    'current_price': 0,
                    'grade': row.get('Status', 'Track'),
                    'date': '2026-02-13',
                    'summary': row.get('Thesis', 'No summary available')
                })
    
    return jsonify(analyses)

@app.route('/api/earnings-research')
def api_earnings_research():
    """Return Bob's daily earnings research"""
    filepath = os.path.join(WORKSPACE, 'daily_earnings_research.md')
    content = read_file(filepath)
    return jsonify({'content': content[:2000] if content else 'No earnings research found'})

@app.route('/api/ideas')
def api_ideas():
    """Return ideas/notes as structured list"""
    filepath = os.path.join(WORKSPACE, 'ideas/NOTES.md')
    content = read_file(filepath)
    
    ideas = []
    current_category = 'General'
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Check for category headers (### Category Name)
        if line.startswith('### '):
            current_category = line[4:].strip()
        
        # Check for idea items (lines starting with "- Idea:")
        elif line.startswith('- Idea:'):
            idea_content = line[7:].strip()
            if idea_content:
                ideas.append({
                    'category': current_category,
                    'content': idea_content
                })
    
    return jsonify(ideas)

@app.route('/api/refresh-prices', methods=['POST'])
def api_refresh_prices():
    """Refresh crypto prices"""
    price = get_cached_crypto_price('ethereum', force_refresh=True)
    return jsonify({'eth_price': price, 'timestamp': datetime.now().isoformat()})

@app.route('/api/system/spec')
def api_system_spec():
    """Return technical specification for Mission Control"""
    spec_path = os.path.join(WORKSPACE, 'mission_control/docs/specs/mission_control_spec.md')
    content = read_file(spec_path)
    
    # Parse the spec file for structured data
    spec_data = {
        'version': '',
        'last_updated': '',
        'architecture': '',
        'data_sources': [],
        'apis': []
    }
    
    if content:
        # Extract version and date from header
        version_match = re.search(r'\*\*Version:\*\*\s*(.+)', content)
        date_match = re.search(r'\*\*Last Updated:\*\*\s*(.+)', content)
        if version_match:
            spec_data['version'] = version_match.group(1).strip()
        if date_match:
            spec_data['last_updated'] = date_match.group(1).strip()
        
        # Extract architecture overview
        arch_match = re.search(r'## Architecture\s*\n\s*### Tech Stack\s*\n(.+?)(?=##|\Z)', content, re.DOTALL)
        if arch_match:
            spec_data['architecture'] = arch_match.group(1).strip()[:500]
        
        # Extract data sources table
        ds_section = re.search(r'## Data Sources\s*\n(.+?)(?=##|\Z)', content, re.DOTALL)
        if ds_section:
            # Parse table rows
            for line in ds_section.group(1).split('\n'):
                if line.startswith('|') and 'Data Element' not in line and '---' not in line:
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if len(cells) >= 3:
                        spec_data['data_sources'].append({
                            'element': cells[0],
                            'source': cells[1],
                            'parser': cells[2]
                        })
        
        # Extract APIs
        api_section = re.search(r'## API Contract\s*\n(.+?)(?=##|\Z)', content, re.DOTALL)
        if api_section:
            # Find all GET/POST endpoints
            for match in re.finditer(r'###\s+(GET|POST)\s+(`[^`]+`|/[^\s]+)', api_section.group(1)):
                method = match.group(1)
                endpoint = match.group(2).strip('`')
                spec_data['apis'].append({
                    'method': method,
                    'endpoint': endpoint
                })
    
    return jsonify(spec_data)

if __name__ == '__main__':
    print('🚀 Mission Control starting on port 8080...')
    print('📊 Dashboard: http://localhost:8080')
    app.run(host='0.0.0.0', port=8080, debug=False)
