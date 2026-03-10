#!/usr/bin/env python3
"""
analyze_stock.py - Single ticker analysis CLI
Usage: python analyze_stock.py TICKER
"""

import json
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from analysis_engine import analyze_single


def build_causal_explanation(result: dict) -> str:
    """Build causal explanation from analysis result."""
    ticker = result.get("ticker", "")
    key_movement = result.get("key_movement", {})
    earnings_event = result.get("earnings_event", {})
    options = result.get("options_context", {})
    material = result.get("material_events", [])
    tech = result.get("technical_analysis", {})
    
    lines = [f"## {ticker} Stock Analysis", ""]
    
    # Price summary
    lines.append(f"### Price Movement Summary")
    lines.append(f"Over the past 90 days, {ticker} has experienced **{key_movement.get('type', 'unknown')}** with a **{key_movement.get('magnitude', 0):+.2f}%** change.")
    lines.append("")
    
    # Earnings event
    if earnings_event:
        if earnings_event.get("method") == "price_spike_detection":
            lines.append("### Detected Price Event")
            lines.append(f"- Date: {earnings_event.get('date')}")
            lines.append(f"- Price Before: ${earnings_event.get('price_before')}")
            lines.append(f"- Price After: ${earnings_event.get('price_after')}")
            lines.append(f"- Reaction: {earnings_event.get('reaction_percent'):+.2f}%")
        else:
            lines.append("### Earnings Event")
            lines.append(f"- Date: {earnings_event.get('report_date')} ({earnings_event.get('report_time')})")
            lines.append(f"- Expected Move: {earnings_event.get('expected_move')}%")
            lines.append(f"- Reaction: {earnings_event.get('reaction_percent'):+.2f}%")
        lines.append("")
    
    # Material events
    if material:
        lines.append("### Material Events")
        for e in material:
            lines.append(f"- {e.get('date')}: [{e.get('reason')}] {e.get('headline')[:60]}...")
        lines.append("")
    
    # Options context
    if options:
        lines.append("### Options Context")
        lines.append(f"- Implied Move: {options.get('implied_move')}%")
        if options.get("volatility_comparison"):
            lines.append(f"- {options.get('volatility_comparison')}")
        lines.append("")
    
    # Technical
    lines.append("### Technical Analysis")
    lines.append(f"- Trend: {tech.get('trend', 'unknown').upper()}")
    support = tech.get("support_levels", [])
    resistance = tech.get("resistance_levels", [])
    lines.append(f"- Support: {', '.join(map(str, support[:3])) or 'None'}")
    lines.append(f"- Resistance: {', '.join(map(str, resistance[:3])) or 'None'}")
    lines.append("")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_stock.py TICKER")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    result = analyze_single(ticker)
    
    if result.get("error"):
        print(f"Error: {result.get('error')}")
        sys.exit(1)
    
    # Print compact summary (no full JSON)
    print(f"Ticker: {result.get('ticker')}")
    print(f"Price move: {result.get('price_move')}")
    print(f"Summary: {result.get('summary')}")
    print(f"Report: {result.get('report_path')}")


if __name__ == "__main__":
    main()
