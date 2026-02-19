#!/usr/bin/env python3
"""
Fix data_layer.py by adding trade functions at the end
"""

from pathlib import Path

def fix_data_layer():
    """Add trade functions to data_layer.py"""
    workspace = Path.home() / ".openclaw" / "workspace"
    data_layer_path = workspace / "mission_control_dev" / "data_layer.py"
    
    if not data_layer_path.exists():
        print(f"Error: {data_layer_path} not found")
        return
    
    with open(data_layer_path, 'r') as f:
        content = f.read()
    
    # Check if load_trades already exists
    if 'def load_trades' in content:
        print("load_trades function already exists in data_layer.py")
        return
    
    # Find the test section and insert before it
    test_marker = 'if __name__ == "__main__":'
    test_pos = content.find(test_marker)
    
    if test_pos == -1:
        # Add at the end
        test_pos = len(content)
    
    # New functions to add
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
    
    # Insert the new functions
    new_content = content[:test_pos] + new_functions + '\n' + content[test_pos:]
    
    # Write updated content
    with open(data_layer_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Fixed data_layer.py with trade functions")

def main():
    """Main function"""
    print("Fixing data_layer.py...")
    fix_data_layer()

if __name__ == "__main__":
    main()