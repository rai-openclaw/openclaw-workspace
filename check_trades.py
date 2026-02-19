#!/usr/bin/env python3
"""
Check trades.json file
"""

import json
from pathlib import Path

workspace = Path.home() / ".openclaw" / "workspace"
trades_path = workspace / "data" / "trades.json"

with open(trades_path, 'r') as f:
    data = json.load(f)

print("All trades in trades.json:")
print("-" * 80)
for i, trade in enumerate(data['trades']):
    pnl = trade.get('realized_pnl')
    strike = trade.get('strike')
    
    pnl_str = f"${pnl:.2f}" if pnl is not None else "N/A"
    strike_str = f"{strike:.2f}" if strike is not None else "N/A"
    
    print(f"{i:2d}. {trade['ticker']:6s} {trade['status']:8s} "
          f"P&L: {pnl_str:>8} Strike: {strike_str:>6} "
          f"Qty: {trade['quantity']:>3d} Date: {trade['date']}")

print("\n" + "=" * 80)
print(f"Summary from JSON:")
print(f"  Total trades: {data['summary']['total_trades']}")
print(f"  Open positions: {data['summary']['open_positions']}")
print(f"  YTD Realized P&L: ${data['summary']['ytd_realized_pnl']:.2f}")
print(f"  YTD Premium Collected: ${data['summary']['ytd_premium_collected']:.2f}")

# Calculate manually
realized_pnl = sum(t.get('realized_pnl', 0) or 0 for t in data['trades'])
premium_collected = sum(t.get('total_credit', 0) or 0 for t in data['trades'])

print(f"\nManual calculation:")
print(f"  Realized P&L: ${realized_pnl:.2f}")
print(f"  Premium Collected: ${premium_collected:.2f}")

print(f"\nExpected from markdown: $721.00")
print(f"Difference: ${realized_pnl - 721:.2f}")