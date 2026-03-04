#!/usr/bin/env python3
"""
Mission Control v3.0 - Portfolio Dashboard with JSON Data Layer
Uses clean JSON data sources with schema validation
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, jsonify, render_template, request

# Import performance cache module
try:
    from lib.performanceCache import get_performance_cache, set_performance_cache, clear_performance_cache, get_quote_timestamp, generate_cache_key
    USE_PERF_CACHE = True
except ImportError:
    USE_PERF_CACHE = False
    # Fallback functions if cache module not available
    def get_performance_cache(key): return None
    def set_performance_cache(key, data): pass
    def clear_performance_cache(): pass
    def get_quote_timestamp(): return datetime.now().isoformat()
    def generate_cache_key(context, start_date=None, end_date=None, month_offset=0, week_offset=0): 
        if context == 'weekly' and week_offset != 0:
            # Calculate start date for this week offset
            from datetime import date, timedelta
            today = date.today()
            current_week_start = today - timedelta(days=today.weekday())
            target_week_start = current_week_start - timedelta(days=week_offset * 7)
            return f"weekly-{target_week_start.isoformat()}"
        return context

# Add mission_control to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import data layer, fallback to inline if not available
try:
    from data_layer import load_holdings, load_analyses, load_earnings, load_schedule, load_ideas, load_team
    USE_DATA_LAYER = True
    print("✅ Using new JSON data layer")
except ImportError as e:
    USE_DATA_LAYER = False
    print(f"⚠️ Data layer not available ({e}), using fallback")

app = Flask(__name__)

# Configuration
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE, 'portfolio', 'data', 'holdings.json')
ANALYSES_DIR = os.path.join(WORKSPACE, 'portfolio', 'data', 'analyses')
PRICE_FILE = os.path.join(WORKSPACE, 'portfolio', 'price_cache.json')

# Fallback markdown files (for backward compatibility)
MD_DATA_FILE = os.path.join(WORKSPACE, 'portfolio', 'unified_portfolio_tracker.md')
MD_ANALYSIS_FILE = os.path.join(WORKSPACE, 'portfolio', 'portfolio_tracker.md')

# API Keys
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', 'd68o369r01qq5rjg8lcgd68o369r01qq5rjg8ld0')

# ============================================================================
# DATA PARSING (Legacy - for fallback)
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
                values = [v for v in values if v or v == '']
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

# ============================================================================
# API ENDPOINTS
# ============================================================================

def transform_holdings_for_dashboard(data):
    """Transform JSON holdings data to dashboard format"""
    accounts = data.get('accounts', [])
    
    # Aggregate stocks across accounts
    stocks_map = {}
    options_list = []
    cash_data = {'Cash': {'total': 0, 'accounts': []}, 'SGOV': {'total': 0, 'total_shares': 0, 'accounts': [], 'price': 100.0}}
    misc_total = 0
    
    # Load prices from cache if available
    prices = {}
    try:
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, 'r') as f:
                price_data = json.load(f)
                # Handle nested structure: {"prices": {"TICKER": {"price": 123}}}
                if isinstance(price_data, dict) and 'prices' in price_data:
                    prices = {ticker: data.get('price', 100.0) for ticker, data in price_data['prices'].items()}
                else:
                    prices = price_data
    except Exception as e:
        print(f"Error loading prices: {e}")
        pass
    
    for account in accounts:
        account_name = account.get('name', 'Unknown')
        
        # Process stocks
        for stock in account.get('stocks_etfs', []):
            ticker = stock.get('Ticker', '')
            shares = stock.get('Shares', 0)
            cost_basis = stock.get('Cost Basis', 0)
            
            if ticker not in stocks_map:
                stocks_map[ticker] = {
                    'ticker': ticker,
                    'total_shares': 0,
                    'total_cost_basis': 0,
                    'total_value': 0,
                    'price': prices.get(ticker, 100.0),
                    'accounts': []
                }
            
            stocks_map[ticker]['total_shares'] += shares
            stocks_map[ticker]['total_cost_basis'] += cost_basis
            stocks_map[ticker]['accounts'].append({
                'account': account_name,
                'shares': shares,
                'cost_basis': cost_basis
            })
        
        # Process options - preserve sign for short positions
        for opt in account.get('options', []):
            contracts = opt.get('Contracts', 0)  # Don't use abs() - preserve sign
            premium = opt.get('Entry Premium', 0)
            # For short options (negative contracts), value is negative (obligation)
            # For long options (positive contracts), value is positive (asset)
            notional_value = contracts * premium * 100
            options_list.append({
                'ticker': opt.get('Ticker', ''),
                'type': opt.get('Type', 'PUT'),
                'strike': opt.get('Strike', 0),
                'expiration': opt.get('Expiration', ''),
                'total_contracts': contracts,  # Preserve negative for short
                'total_entry_value': notional_value,
                'current_value': notional_value,  # Simplified - should use current option price
                'accounts': [{'account': account_name, 'contracts': contracts, 'entry_premium': premium}],
                'note': f"{contracts} contracts @ ${premium}"
            })
        
        # Process cash
        for cash_item in account.get('cash', []):
            asset = cash_item.get('Asset', 'Cash')
            qty = cash_item.get('Quantity', 0)
            if asset == 'Cash':
                cash_data['Cash']['total'] += qty
                cash_data['Cash']['accounts'].append({'account': account_name, 'value': qty})
            elif asset == 'SGOV':
                cash_data['SGOV']['total'] += qty * 100  # Assuming $100/share
                cash_data['SGOV']['total_shares'] += qty
                cash_data['SGOV']['accounts'].append({'account': account_name, 'value': qty * 100})
        
    # Process misc assets (crypto, etc.) with live prices
    misc_list = []
    for account in accounts:
        account_name = account.get('name', 'Unknown')
        for misc in account.get('misc', []):
            asset = misc.get('Asset', '')
            amount = misc.get('Amount', 0)
            cost_basis = misc.get('Cost Basis', 0)
            asset_type = misc.get('Type', 'Other')
            
            # Get live price if available
            price = prices.get(asset, 0)
            current_value = amount * price if price > 0 else cost_basis
            
            misc_list.append({
                'asset': asset,
                'type': asset_type,
                'amount': amount,
                'price': price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'account': account_name
            })
    
    misc_total = sum(m['current_value'] for m in misc_list)
    
    # Calculate stock values and returns
    stocks_list = []
    for stock in stocks_map.values():
        stock['total_value'] = stock['total_shares'] * stock['price']
        cost_per_share = stock['total_cost_basis'] / stock['total_shares'] if stock['total_shares'] > 0 else 0
        stock['total_return_pct'] = ((stock['price'] - cost_per_share) / cost_per_share * 100) if cost_per_share > 0 else 0
        stocks_list.append(stock)
    
    # Calculate totals
    stocks_total = sum(s['total_value'] for s in stocks_list)
    options_total = sum(o['current_value'] for o in options_list)
    cash_total = cash_data['Cash']['total'] + cash_data['SGOV']['total']
    
    return {
        'stocks': stocks_list,
        'options': options_list,
        'cash': cash_data,
        'misc': misc_list,
        'totals': {
            'stocks_etfs': stocks_total,
            'options': options_total,
            'cash_equivalents': cash_total,
            'misc': misc_total,
            'grand_total': stocks_total + options_total + cash_total + misc_total
        },
        'last_price_refresh': data.get('last_updated', datetime.now().isoformat())
    }

@app.route('/api/portfolio')
def api_portfolio():
    """Return complete portfolio data for Holdings tab"""
    try:
        if USE_DATA_LAYER:
            data = load_holdings(use_markdown_fallback=True)
            # Transform to dashboard format
            transformed = transform_holdings_for_dashboard(data)
            return jsonify(transformed)
        else:
            # Fallback to old parsing
            return jsonify({'error': 'Data layer not available'}), 500
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

def fetch_yahoo_price(ticker):
    """Fetch mutual fund price from Yahoo Finance"""
    try:
        import urllib.request
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            result = data.get('chart', {}).get('result', [{}])[0]
            return result.get('meta', {}).get('regularMarketPrice', 0)
    except Exception as e:
        print(f"Yahoo error for {ticker}: {e}")
        return 0

def fetch_coingecko_price(asset):
    """Fetch crypto price from CoinGecko"""
    try:
        import urllib.request
        asset_map = {'ETH': 'ethereum', 'BTC': 'bitcoin', 'SOL': 'solana'}
        asset_id = asset_map.get(asset, asset.lower())
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get(asset_id, {}).get('usd', 0)
    except Exception as e:
        print(f"CoinGecko error for {asset}: {e}")
        return 0

@app.route('/api/refresh-prices', methods=['POST'])
def refresh_prices():
    """Refresh all prices from APIs"""
    try:
        import requests
        
        # Get all tickers and misc assets from holdings
        data = load_holdings(use_markdown_fallback=True)
        stock_tickers = set()
        misc_assets = set()
        
        for account in data.get('accounts', []):
            for stock in account.get('stocks_etfs', []):
                ticker = stock.get('Ticker', '')
                if ticker and ticker not in ['SGOV', 'Cash']:
                    stock_tickers.add(ticker)
            for misc in account.get('misc', []):
                asset = misc.get('Asset', '')
                if asset:
                    misc_assets.add(asset)
        stock_tickers.add('SGOV')
        
        prices = {'version': '2.0', 'last_updated': datetime.now().isoformat(), 'prices': {}}
        
        # Fetch stock prices (Finnhub for most, Yahoo for mutual funds)
        mutual_funds = ['VSEQX', 'VTCLX', 'VTMSX', 'VIG', 'VYM', 'VXUS']
        
        for ticker in stock_tickers:
            if not ticker:
                continue
            try:
                if ticker in mutual_funds:
                    # Use Yahoo Finance for mutual funds
                    price = fetch_yahoo_price(ticker)
                    source = 'yahoo_finance'
                else:
                    # Use Finnhub for regular stocks
                    url = f'https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}'
                    resp = requests.get(url, timeout=5)
                    price = 0
                    if resp.status_code == 200:
                        data = resp.json()
                        price = data.get('c', 0)
                    source = 'finnhub'
                
                if price > 0:
                    prices['prices'][ticker] = {
                        'price': price,
                        'source': source,
                        'last_updated': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                continue
        
        # Fetch crypto prices from CoinGecko
        for asset in misc_assets:
            try:
                price = fetch_coingecko_price(asset)
                if price > 0:
                    prices['prices'][asset] = {
                        'price': price,
                        'source': 'coingecko',
                        'last_updated': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Error fetching {asset}: {e}")
                continue
        
        # Save to cache
        with open(PRICE_FILE, 'w') as f:
            json.dump(prices, f, indent=2)
        
        return jsonify({
            'success': True, 
            'prices_updated': len(prices['prices']),
            'stocks': len([p for p in prices['prices'].values() if p.get('source') != 'coingecko']),
            'crypto': len([p for p in prices['prices'].values() if p.get('source') == 'coingecko'])
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/analysis-archive')
def api_analysis_archive():
    """Return stock analysis archive for Analysis Archive tab"""
    try:
        if USE_DATA_LAYER:
            analyses = load_analyses(use_markdown_fallback=True)
            return jsonify(analyses)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/earnings-research')
def api_earnings_research():
    """Return earnings research for Earnings Research tab"""
    try:
        if USE_DATA_LAYER:
            earnings = load_earnings()
            return jsonify(earnings)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ideas')
def api_ideas():
    """Return ideas for Ideas & Notes tab"""
    try:
        if USE_DATA_LAYER:
            ideas = load_ideas()
            return jsonify(ideas)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue-idea', methods=['POST'])
def queue_idea():
    """Queue an idea for execution - sends notification to user"""
    try:
        data = request.get_json()
        idea_id = data.get('idea_id')
        idea_title = data.get('idea_title', 'Unknown Idea')
        
        if not idea_id:
            return jsonify({'success': False, 'error': 'No idea_id provided'}), 400
        
        # Load the full idea details
        ideas_data = load_ideas()
        ideas_list = ideas_data.get('ideas', []) if isinstance(ideas_data, dict) else ideas_data
        
        idea = None
        for i in ideas_list:
            if i.get('id') == idea_id:
                idea = i
                break
        
        if not idea:
            return jsonify({'success': False, 'error': 'Idea not found'}), 404
        
        # Update status to in_progress if it's approved
        if idea.get('status') == 'approved':
            idea['status'] = 'in_progress'
            # Save updated ideas
            from pathlib import Path
            import json
            ideas_file = Path(WORKSPACE) / 'portfolio' / 'data' / 'ideas.json'
            with open(ideas_file, 'w') as f:
                json.dump({'ideas': ideas_list, 'last_updated': datetime.now().isoformat()}, f, indent=2)
        
        # Add to queue file for notification
        try:
            sys.path.insert(0, WORKSPACE)
            from queue_manager import add_to_queue
            added, msg = add_to_queue(idea_id, idea_title, idea.get('context', ''))
        except Exception as queue_err:
            print(f"Queue error: {queue_err}")
            added, msg = False, str(queue_err)
        
        return jsonify({
            'success': True, 
            'message': "Idea queued successfully. You'll receive a Telegram notification within 30 minutes.",
            'idea_id': idea_id,
            'new_status': idea.get('status'),
            'queued': added
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/queue-status')
def queue_status():
    """Get current queue status (for heartbeat checks)"""
    try:
        sys.path.insert(0, WORKSPACE)
        from queue_manager import get_pending_ideas
        pending = get_pending_ideas()
        return jsonify({
            'pending_count': len(pending),
            'pending_ids': [i['id'] for i in pending]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule')
def api_schedule():
    """Return schedule for Schedule tab"""
    try:
        if USE_DATA_LAYER:
            schedule = load_schedule()
            return jsonify(schedule)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/corporate')
def api_corporate():
    """Return corporate structure for Corporate tab"""
    try:
        if USE_DATA_LAYER:
            corporate = load_team()
            return jsonify(corporate)
        else:
            # Fallback: load directly from JSON
            import json
            corporate_file = os.path.join(WORKSPACE, 'portfolio', 'data', 'corporate.json')
            if os.path.exists(corporate_file):
                with open(corporate_file, 'r') as f:
                    return jsonify(json.load(f))
            return jsonify({'team': [], 'departments': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usage')
def api_usage():
    """Return API usage for API Usage tab"""
    try:
        api_usage_data = {
            'Moonshot': {
                'name': 'Moonshot AI',
                'purpose': 'Primary LLM',
                'status': 'Active',
                'tier': 'Paid',
                'limit': 'Unlimited',
                'calls_this_month': 0,
                'cost': 0.0
            },
            'Finnhub': {
                'name': 'Finnhub',
                'purpose': 'Stock prices',
                'status': 'Active',
                'tier': 'Free',
                'limit': '60/min',
                'calls_this_month': 0,
                'cost': 0.0
            }
        }
        return jsonify({'apis': api_usage_data, 'total_cost': 0.0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades')
def api_trades():
    """Return all trades for Trading tab"""
    try:
        import json
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
                return jsonify(trades_data)
        return jsonify({'trades': [], 'summary': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/summary')
def api_trades_summary():
    """Return P&L summary + by_ticker for Trading tab"""
    try:
        import json
        pnl_file = os.path.join(WORKSPACE, 'data', 'pnl_summary.json')
        if os.path.exists(pnl_file):
            with open(pnl_file, 'r') as f:
                pnl_data = json.load(f)
                return jsonify(pnl_data)
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/positions')
def api_trades_positions():
    """Return current trade positions for Trading tab"""
    try:
        import json
        positions_file = os.path.join(WORKSPACE, 'data', 'positions.json')
        if os.path.exists(positions_file):
            with open(positions_file, 'r') as f:
                positions_data = json.load(f)
                return jsonify(positions_data)
        return jsonify({'positions': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades/add', methods=['POST'])
def api_trades_add():
    """
    Add a new trade event.
    Clears performance cache on successful add.
    
    Request body:
        {
            "ticker": "AAPL",
            "date": "2026-03-04",
            "action": "BUY/SELL",
            "premium": 100.00,
            "realized_pnl": 50.00,
            ...
        }
    """
    try:
        import json
        from datetime import datetime
        
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        
        # Load existing trades
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
        else:
            trades_data = {'trades': []}
        
        # Get trade data from request
        trade_data = request.get_json()
        if not trade_data:
            return jsonify({'error': 'No trade data provided'}), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in trade_data:
            trade_data['timestamp'] = datetime.now().isoformat()
        
        # Add trade to list
        trades_data['trades'].append(trade_data)
        
        # Save trades
        with open(trades_file, 'w') as f:
            json.dump(trades_data, f, indent=2)
        
        # Clear performance cache
        clear_performance_cache()
        
        return jsonify({
            'success': True, 
            'message': 'Trade added successfully',
            'trade': trade_data
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/trades/delete', methods=['DELETE'])
def api_trades_delete():
    """
    Delete a trade event by index or trade ID.
    Clears performance cache on successful delete.
    
    Query params:
        index: Trade array index to delete
        id: Trade ID to delete
    """
    try:
        import json
        
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        
        if not os.path.exists(trades_file):
            return jsonify({'error': 'Trades file not found'}), 404
        
        with open(trades_file, 'r') as f:
            trades_data = json.load(f)
        
        trades = trades_data.get('trades', [])
        
        # Get delete criteria
        trade_index = request.args.get('index', type=int)
        trade_id = request.args.get('id')
        
        if trade_index is not None:
            if 0 <= trade_index < len(trades):
                deleted_trade = trades.pop(trade_index)
            else:
                return jsonify({'error': 'Invalid trade index'}), 400
        elif trade_id:
            # Find and remove trade by ID
            found = False
            for i, trade in enumerate(trades):
                if trade.get('id') == trade_id:
                    deleted_trade = trades.pop(i)
                    found = True
                    break
            if not found:
                return jsonify({'error': 'Trade not found'}), 404
        else:
            return jsonify({'error': 'Must provide index or id'}), 400
        
        # Save updated trades
        trades_data['trades'] = trades
        with open(trades_file, 'w') as f:
            json.dump(trades_data, f, indent=2)
        
        # Clear performance cache
        clear_performance_cache()
        
        return jsonify({
            'success': True,
            'message': 'Trade deleted successfully',
            'deleted': deleted_trade
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/trades/bulk-delete', methods=['POST'])
def api_trades_bulk_delete():
    """
    Bulk delete trade events.
    Clears performance cache on successful delete.
    
    Request body:
        {
            "indices": [0, 2, 5],  // Array of indices to delete
            "ids": ["trade-id-1", "trade-id-2"]  // Or array of trade IDs
        }
    """
    try:
        import json
        
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        
        if not os.path.exists(trades_file):
            return jsonify({'error': 'Trades file not found'}), 404
        
        with open(trades_file, 'r') as f:
            trades_data = json.load(f)
        
        trades = trades_data.get('trades', [])
        
        # Get delete criteria
        delete_data = request.get_json() or {}
        indices = delete_data.get('indices', [])
        ids = delete_data.get('ids', [])
        
        if not indices and not ids:
            return jsonify({'error': 'Must provide indices or ids'}), 400
        
        # Track deleted trades
        deleted_trades = []
        
        # Delete by indices (process in reverse order to maintain correct indices)
        if indices:
            indices_to_delete = set(indices)
            trades = [t for i, t in enumerate(trades) if i not in indices_to_delete]
            deleted_trades.extend(indices)
        
        # Delete by IDs
        if ids:
            ids_to_delete = set(ids)
            trades = [t for t in trades if t.get('id') not in ids_to_delete]
            deleted_trades.extend(ids)
        
        # Save updated trades
        trades_data['trades'] = trades
        with open(trades_file, 'w') as f:
            json.dump(trades_data, f, indent=2)
        
        # Clear performance cache
        clear_performance_cache()
        
        return jsonify({
            'success': True,
            'message': f'Deleted {len(deleted_trades)} trades',
            'deleted': deleted_trades
        })
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/portfolio/positions')
def api_portfolio_positions():
    """Return current portfolio positions"""
    try:
        import json
        portfolio_file = os.path.join(WORKSPACE, 'data', 'portfolio_positions.json')
        if os.path.exists(portfolio_file):
            with open(portfolio_file, 'r') as f:
                portfolio_data = json.load(f)
                return jsonify(portfolio_data)
        return jsonify({'accounts': {}, 'totals': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/performance-v2')
def api_trades_performance_v2():
    """
    Performance v2 - Canonical context model for trading performance.
    Uses server-side caching for improved performance.
    
    Query params:
        context: lifetime | daily | weekly | monthly | yearly | custom
        start: Start date for custom range (YYYY-MM-DD)
        end: End date for custom range (YYYY-MM-DD)
        month: Month offset for monthly context (0 = current month, 1 = last month, etc.)
        
    Returns:
        - summary: totalRealizedPl, winRate, totalTrades
        - tickerBreakdown: per-ticker realized P/L, wins, losses, winRate
        - quoteTimestamp: timestamp from quote cache
    """
    try:
        from datetime import datetime, date
        import json
        
        # Parse context parameter
        context = request.args.get('context', 'lifetime').lower()
        valid_contexts = ['lifetime', 'daily', 'weekly', 'monthly', 'yearly', 'custom']
        if context not in valid_contexts:
            return jsonify({'error': f'Invalid context. Use: {", ".join(valid_contexts)}'}), 400
        
        # Parse date range parameters
        start_date = None
        end_date = None
        month_offset = 0
        week_offset = 0
        
        if context == 'custom':
            start_str = request.args.get('start')
            end_str = request.args.get('end')
            if start_str and end_str:
                try:
                    start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        elif context == 'monthly':
            try:
                month_offset = int(request.args.get('month', '0'))
            except ValueError:
                month_offset = 0
        elif context == 'weekly':
            try:
                week_offset = int(request.args.get('weekOffset', '0'))
            except ValueError:
                week_offset = 0
            # Ensure week_offset is not negative (no future weeks)
            week_offset = max(0, week_offset)
        
        # Generate cache key
        cache_key = generate_cache_key(
            context, 
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None,
            month_offset,
            week_offset
        )
        
        # Check cache first
        cached_data = get_performance_cache(cache_key)
        if cached_data:
            # Add quote timestamp to cached response
            cached_data['quoteTimestamp'] = get_quote_timestamp()
            return jsonify(cached_data)
        
        # Load trades (compute if not cached)
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        if not os.path.exists(trades_file):
            return jsonify({
                'context': context, 
                'summary': {}, 
                'tickerBreakdown': [],
                'quoteTimestamp': get_quote_timestamp()
            })
        
        with open(trades_file, 'r') as f:
            trades_data = json.load(f)
        
        all_trades = trades_data.get('trades', [])
        
        # Determine date range based on context
        today = date.today()
        
        if context == 'daily':
            start_date = today
            end_date = today
        elif context == 'weekly':
            # Get start of week (Monday) with weekOffset support
            # week_offset=0 is current week, week_offset=1 is last week, etc.
            today = date.today()
            current_week_start = today - timedelta(days=today.weekday())
            target_week_start = current_week_start - timedelta(days=week_offset * 7)
            start_date = target_week_start
            end_date = start_date + timedelta(days=6)
        elif context == 'monthly':
            # Calculate target month based on offset
            target_month = today.month - month_offset
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            start_date = date(target_year, target_month, 1)
            # Last day of month
            if target_month == 12:
                end_date = date(target_year, 12, 31)
            else:
                end_date = date(target_year, target_month + 1, 1) - timedelta(days=1)
        elif context == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        # lifetime: no date filter
        
        # Filter trades by date
        filtered_trades = []
        for trade in all_trades:
            trade_date_str = trade.get('date') or trade.get('timestamp', '')[:10]
            try:
                trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()
                
                if start_date and end_date:
                    if not (start_date <= trade_date <= end_date):
                        continue
                elif start_date and trade_date < start_date:
                    continue
                    
                filtered_trades.append(trade)
            except (ValueError, TypeError):
                # If date parsing fails, include the trade (default to lifetime behavior)
                filtered_trades.append(trade)
        
        # Aggregate: Group by ticker
        ticker_stats = {}
        for trade in filtered_trades:
            ticker = trade.get('ticker', 'UNKNOWN')
            if ticker not in ticker_stats:
                ticker_stats[ticker] = {
                    'ticker': ticker,
                    'realizedPl': 0.0,
                    'wins': 0,
                    'losses': 0,
                    'total': 0
                }
            
            # Get trade P/L (prefer realized_pnl, fall back to premium for CSP logic)
            pnl = trade.get('realized_pnl')
            if pnl is None:
                # For CSP: premium collected = credit, loss = assignment
                # Use premium as the base P/L indicator
                pnl = trade.get('premium', 0) or 0
            
            ticker_stats[ticker]['realizedPl'] += pnl
            ticker_stats[ticker]['total'] += 1
            
            if pnl > 0:
                ticker_stats[ticker]['wins'] += 1
            elif pnl < 0:
                ticker_stats[ticker]['losses'] += 1
            # pnl == 0 is neither win nor loss
        
        # Calculate totals
        total_realized_pl = sum(t.get('realizedPl', 0) for t in ticker_stats.values())
        total_trades = len(filtered_trades)
        total_wins = sum(t.get('wins', 0) for t in ticker_stats.values())
        total_losses = sum(t.get('losses', 0) for t in ticker_stats.values())
        
        win_rate = round((total_wins / total_trades * 100), 2) if total_trades > 0 else 0.0
        
        # Build ticker breakdown with winRate
        ticker_breakdown = []
        for ticker, stats in ticker_stats.items():
            ticker_win_rate = round((stats['wins'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0.0
            ticker_breakdown.append({
                'ticker': ticker,
                'realizedPl': round(stats['realizedPl'], 2),
                'wins': stats['wins'],
                'losses': stats['losses'],
                'winRate': ticker_win_rate
            })
        
        # Sort by realizedPl descending
        ticker_breakdown.sort(key=lambda x: x['realizedPl'], reverse=True)
        
        # Build response
        response_data = {
            'context': context,
            'dateRange': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'summary': {
                'totalRealizedPl': round(total_realized_pl, 2),
                'winRate': win_rate,
                'totalTrades': total_trades
            },
            'tickerBreakdown': ticker_breakdown,
            'openPositions': [],  # Placeholder for future open positions data
            'equityCurve': []  # Placeholder for future equity curve data
        }
        
        # Store in cache
        set_performance_cache(cache_key, response_data)
        
        # Add quote timestamp
        response_data['quoteTimestamp'] = get_quote_timestamp()
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/research/results')
def api_research_results():
    """Return research calibration data"""
    try:
        import json
        research_file = os.path.join(WORKSPACE, 'data', 'research_results.json')
        if os.path.exists(research_file):
            with open(research_file, 'r') as f:
                research_data = json.load(f)
                return jsonify(research_data)
        return jsonify({'results': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/')
def dashboard():
    """Render dashboard"""
    return render_template('dashboard.html')

@app.route('/corporate-test')
def corporate_test():
    """Standalone corporate tab test"""
    return render_template('corporate_test_standalone.html')

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
