#!/usr/bin/env python3
"""
Update server.py with new API endpoints for trades and portfolio
"""

import os
from pathlib import Path

def update_server_file():
    """Update server.py with new endpoints"""
    workspace = Path.home() / ".openclaw" / "workspace"
    server_path = workspace / "mission_control_dev" / "server.py"
    
    if not server_path.exists():
        print(f"Error: {server_path} not found")
        return
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Find where to add new endpoints - look for the last API endpoint
    # We'll add them after the /api/usage endpoint
    
    # First, let's check if endpoints already exist
    if '@app.route(\'/api/trades\')' in content:
        print("Trades endpoints already exist in server.py")
        return
    
    # Find the /api/usage endpoint and add after it
    usage_endpoint_pos = content.find('@app.route(\'/api/usage\')')
    if usage_endpoint_pos == -1:
        print("Could not find /api/usage endpoint")
        return
    
    # Find the end of the /api/usage function
    # Look for the next @app.route or end of file
    next_route_pos = content.find('@app.route', usage_endpoint_pos + 1)
    if next_route_pos == -1:
        next_route_pos = len(content)
    
    # Insert new endpoints before the next route
    new_endpoints = '''
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
    """Return P&L summary for Trading tab"""
    try:
        import json
        trades_file = os.path.join(WORKSPACE, 'data', 'trades.json')
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
                return jsonify(trades_data.get('summary', {}))
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
'''
    
    # Insert the new endpoints
    new_content = content[:next_route_pos] + new_endpoints + content[next_route_pos:]
    
    # Create backup
    backup_path = server_path.with_suffix('.py.backup.' + os.path.basename(server_path))
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Write updated content
    with open(server_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated server.py with new API endpoints")
    print(f"   Backup created at: {backup_path}")
    
    # Also update data_layer.py to include load_trades function
    update_data_layer()

def update_data_layer():
    """Update data_layer.py with trade loading functions"""
    workspace = Path.home() / ".openclaw" / "workspace"
    data_layer_path = workspace / "mission_control_dev" / "data_layer.py"
    
    if not data_layer_path.exists():
        print(f"Warning: {data_layer_path} not found")
        return
    
    with open(data_layer_path, 'r') as f:
        content = f.read()
    
    # Check if load_trades already exists
    if 'def load_trades' in content:
        print("load_trades function already exists in data_layer.py")
        return
    
    # Find where to add new functions - look for the end of existing functions
    # We'll add them before the last return statement or at the end
    
    # Add new functions before the last line (which should be empty or the end)
    new_functions = '''
def load_trades():
    """Load trades from JSON file"""
    trades_file = DATA_DIR / "trades.json"
    if not trades_file.exists():
        return {"trades": [], "summary": {}}
    
    with open(trades_file, 'r') as f:
        return json.load(f)

def save_trade(trade_data):
    """Save a new trade to JSON file"""
    trades_file = DATA_DIR / "trades.json"
    
    # Load existing trades
    if trades_file.exists():
        with open(trades_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"schema_version": "1.0", "trades": [], "summary": {}}
    
    # Add new trade
    data["trades"].append(trade_data)
    data["last_updated"] = datetime.now().isoformat()
    
    # Recalculate summary
    total_trades = len(data["trades"])
    open_positions = sum(1 for t in data["trades"] if t.get("status") == "OPEN")
    ytd_realized_pnl = sum(t.get("realized_pnl", 0) or 0 for t in data["trades"])
    ytd_premium_collected = sum(t.get("total_credit", 0) or 0 for t in data["trades"])
    
    data["summary"] = {
        "total_trades": total_trades,
        "open_positions": open_positions,
        "ytd_realized_pnl": ytd_realized_pnl,
        "ytd_premium_collected": ytd_premium_collected
    }
    
    # Save
    with open(trades_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return True

def calculate_pnl(trades):
    """Calculate P&L from trades"""
    realized_pnl = sum(t.get("realized_pnl", 0) or 0 for t in trades)
    open_premium = sum(t.get("total_credit", 0) or 0 for t in trades if t.get("status") == "OPEN")
    
    return {
        "realized_pnl": realized_pnl,
        "open_premium": open_premium,
        "total_trades": len(trades),
        "open_positions": sum(1 for t in trades if t.get("status") == "OPEN")
    }

def get_open_positions(trades):
    """Get open positions from trades"""
    return [t for t in trades if t.get("status") == "OPEN"]
'''
    
    # Find a good place to insert - before the last line
    lines = content.split('\n')
    
    # Find the last function definition
    last_func_line = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            last_func_line = i
    
    if last_func_line != -1:
        # Insert after the last function
        insert_line = last_func_line + 1
        # Find the end of that function (next empty line or end of file)
        for i in range(insert_line, len(lines)):
            if lines[i].strip() == '':
                insert_line = i
                break
        
        lines.insert(insert_line, new_functions)
        new_content = '\n'.join(lines)
        
        # Create backup
        backup_path = data_layer_path.with_suffix('.py.backup.' + os.path.basename(data_layer_path))
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Write updated content
        with open(data_layer_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated data_layer.py with trade functions")
        print(f"   Backup created at: {backup_path}")
    else:
        print("Could not find a good place to insert functions in data_layer.py")

def main():
    """Main function"""
    print("Updating Mission Control files...")
    update_server_file()

if __name__ == "__main__":
    main()