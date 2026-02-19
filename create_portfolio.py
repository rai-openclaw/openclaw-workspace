#!/usr/bin/env python3
"""
Create portfolio_positions.json from trades.json and portfolio tracker
"""

import json
from datetime import datetime
from pathlib import Path

def load_trades():
    """Load trades from JSON file"""
    workspace = Path.home() / ".openclaw" / "workspace"
    trades_path = workspace / "data" / "trades.json"
    
    with open(trades_path, 'r') as f:
        return json.load(f)

def parse_portfolio_markdown():
    """Parse portfolio positions from markdown file"""
    workspace = Path.home() / ".openclaw" / "workspace"
    portfolio_path = workspace / "portfolio" / "unified_portfolio_tracker.md"
    
    if not portfolio_path.exists():
        return {}
    
    with open(portfolio_path, 'r') as f:
        content = f.read()
    
    accounts = {}
    current_account = None
    current_section = None
    
    lines = content.split('\n')
    for line in lines:
        # Check for account header
        if "## Account:" in line:
            account_name = line.split(":")[1].strip()
            current_account = account_name
            accounts[current_account] = {
                "stocks": [],
                "options": [],
                "cash": 0.0,
                "cash_equivalents": []
            }
            continue
        
        # Check for section headers
        if "### Stocks & ETFs" in line:
            current_section = "stocks"
            continue
        elif "### Options Positions" in line:
            current_section = "options"
            continue
        elif "### Cash & Cash Equivalents" in line:
            current_section = "cash"
            continue
        
        # Parse table rows
        if current_account and current_section and '|' in line and '---' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            
            if current_section == "stocks" and len(parts) >= 3:
                ticker, shares_str, cost_str = parts[0], parts[1], parts[2]
                try:
                    shares = float(shares_str)
                    cost = float(cost_str.replace('$', '').replace(',', ''))
                    accounts[current_account]["stocks"].append({
                        "ticker": ticker,
                        "shares": shares,
                        "cost_basis": cost
                    })
                except:
                    pass
            
            elif current_section == "options" and len(parts) >= 6:
                ticker, option_type, strike_str, expiration, contracts_str, premium_str = parts[:6]
                try:
                    strike = float(strike_str.replace('$', ''))
                    contracts = int(contracts_str)
                    premium = float(premium_str.replace('$', ''))
                    
                    accounts[current_account]["options"].append({
                        "ticker": ticker,
                        "type": option_type.upper(),
                        "strike": strike,
                        "expiration": expiration,
                        "contracts": contracts,
                        "premium": premium
                    })
                except:
                    pass
            
            elif current_section == "cash" and len(parts) >= 2:
                asset, quantity_str = parts[0], parts[1]
                try:
                    if asset.lower() == "cash":
                        cash = float(quantity_str.replace('$', '').replace(',', ''))
                        accounts[current_account]["cash"] = cash
                    else:
                        # Cash equivalent like SGOV
                        quantity = float(quantity_str)
                        accounts[current_account]["cash_equivalents"].append({
                            "ticker": asset,
                            "shares": quantity
                        })
                except:
                    pass
    
    return accounts

def create_portfolio_json(trades_data, portfolio_accounts):
    """Create portfolio_positions.json structure"""
    
    # Map account names
    account_map = {
        "Robinhood": {
            "name": "Robinhood",
            "broker": "Robinhood",
            "type": "Taxable Brokerage"
        },
        "SEP-IRA": {
            "name": "SEP-IRA", 
            "broker": "Schwab",
            "type": "Retirement (SEP-IRA)"
        },
        "Schwab CSP": {
            "name": "Schwab CSP",
            "broker": "Schwab",
            "type": "Taxable (Margin)"
        }
    }
    
    # Start with accounts structure
    accounts = {}
    
    # Initialize accounts
    for account_key, account_info in account_map.items():
        accounts[account_info["name"]] = {
            "broker": account_info["broker"],
            "type": account_info["type"],
            "positions": [],
            "cash": 0.0
        }
    
    # Add open positions from trades
    for trade in trades_data.get("trades", []):
        if trade.get("status") == "OPEN" and trade.get("option_type") == "PUT":
            account_name = trade.get("account")
            if account_name in accounts:
                # Find or create position for this ticker
                position = None
                for pos in accounts[account_name]["positions"]:
                    if pos["ticker"] == trade["ticker"]:
                        position = pos
                        break
                
                if not position:
                    position = {
                        "ticker": trade["ticker"],
                        "shares": 0,
                        "options": []
                    }
                    accounts[account_name]["positions"].append(position)
                
                # Add option
                position["options"].append({
                    "type": trade["option_type"],
                    "strike": trade["strike"],
                    "expiration": trade["expiration"],
                    "contracts": trade["quantity"],
                    "entry_premium": trade["entry_premium"]
                })
    
    # Add stocks and cash from portfolio tracker
    for account_name, account_data in portfolio_accounts.items():
        mapped_name = account_name
        if mapped_name in accounts:
            # Add stocks
            for stock in account_data.get("stocks", []):
                accounts[mapped_name]["positions"].append({
                    "ticker": stock["ticker"],
                    "shares": stock["shares"],
                    "options": []
                })
            
            # Add cash
            accounts[mapped_name]["cash"] = account_data.get("cash", 0.0)
            
            # Add cash equivalents
            for ce in account_data.get("cash_equivalents", []):
                accounts[mapped_name]["positions"].append({
                    "ticker": ce["ticker"],
                    "shares": ce["shares"],
                    "options": []
                })
    
    # Calculate totals
    total_value = 0.0
    options_exposure = 0.0
    
    for account_name, account_data in accounts.items():
        # Calculate account value (simplified)
        account_value = account_data["cash"]
        for position in account_data["positions"]:
            # For options, calculate premium collected
            for option in position.get("options", []):
                options_exposure += option.get("entry_premium", 0) * option.get("contracts", 0) * 100
        
        total_value += account_value
    
    # Create final structure
    portfolio_json = {
        "last_updated": datetime.now().isoformat(),
        "accounts": accounts,
        "totals": {
            "total_value": total_value,
            "options_exposure": options_exposure
        }
    }
    
    return portfolio_json

def main():
    """Main function"""
    print("Creating portfolio_positions.json...")
    
    # Load data
    trades_data = load_trades()
    portfolio_accounts = parse_portfolio_markdown()
    
    # Create portfolio JSON
    portfolio_json = create_portfolio_json(trades_data, portfolio_accounts)
    
    # Save to file
    workspace = Path.home() / ".openclaw" / "workspace"
    output_path = workspace / "data" / "portfolio_positions.json"
    
    with open(output_path, 'w') as f:
        json.dump(portfolio_json, f, indent=2)
    
    print(f"✅ Portfolio created!")
    print(f"   Accounts: {len(portfolio_json['accounts'])}")
    print(f"   Total value: ${portfolio_json['totals']['total_value']:.2f}")
    print(f"   Options exposure: ${portfolio_json['totals']['options_exposure']:.2f}")
    print(f"   Output file: {output_path}")
    
    # Print summary
    print("\nAccount summary:")
    for account_name, account_data in portfolio_json["accounts"].items():
        positions_count = len(account_data["positions"])
        options_count = sum(len(p.get("options", [])) for p in account_data["positions"])
        print(f"  {account_name}: {positions_count} positions ({options_count} options), Cash: ${account_data['cash']:.2f}")

if __name__ == "__main__":
    main()