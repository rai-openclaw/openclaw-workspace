#!/usr/bin/env python3
"""
load_analysis_report.py - Load saved analysis reports from disk
"""

from datetime import date
from pathlib import Path
from typing import Optional
import json


def load_analysis_report(ticker: str, report_date: Optional[str] = None, section: Optional[str] = None) -> dict:
    """
    Load a saved analysis report from disk.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "HPE")
        report_date: Optional YYYY-MM-DD. Defaults to today.
        section: Optional key to return only part of the report.
                 e.g., "trade_desk_analysis", "news_timeline", "key_movement"
    
    Returns:
        Full analysis report dict, section dict, or error dict if not found.
    """
    if report_date is None:
        report_date = date.today().isoformat()
    
    # Get workspace path
    workspace = Path(__file__).resolve().parent.parent.parent
    path = workspace / "data" / "analysis" / report_date / f"{ticker.upper()}.json"
    
    if not path.exists():
        return {
            "error": "analysis report not found",
            "ticker": ticker.upper(),
            "date": report_date,
            "path_attempted": str(path)
        }
    
    with open(path) as f:
        data = json.load(f)
    
    if section:
        return data.get(section, {"error": "section not found", "section": section})
    
    return data


# For direct CLI testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_analysis_report.py TICKER [YYYY-MM-DD] [SECTION]")
        print("  SECTION: optional key like trade_desk_analysis, news_timeline, key_movement")
        sys.exit(1)
    
    ticker = sys.argv[1]
    report_date = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None
    section = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = load_analysis_report(ticker, report_date, section)
    print(json.dumps(result, indent=2))
