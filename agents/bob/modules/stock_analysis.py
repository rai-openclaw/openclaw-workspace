#!/usr/bin/env python3
"""
stock_analysis.py - Bob agent module wrapper
Delegates to scripts/core/analysis_engine.py
"""

import sys
from pathlib import Path

# Add scripts to path
WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "scripts"))

# Import from core analysis engine
from core.analysis_engine import analyze_single


def analyze_stock(ticker: str) -> dict:
    """
    Provide structured causal analysis of stock price movements.
    Delegates to unified analysis_engine.
    
    Args:
        ticker: Stock symbol to analyze
        
    Returns:
        Dict with full analysis
    """
    return analyze_single(ticker)


# For direct CLI execution
if __name__ == "__main__":
    import json
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = analyze_stock(ticker)
    print(json.dumps(result, indent=2))
