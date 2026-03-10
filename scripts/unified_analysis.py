#!/usr/bin/env python3
"""
unified_analysis.py - Uses core/analysis_engine.py for batch analysis
Replaces the individual analysis scripts with a single unified call.
"""

import json
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from analysis_engine import analyze_batch


def main():
    # Load candidates
    candidates_path = Path("data/cache/todays_candidates.json")
    
    if not candidates_path.exists():
        print("Error: todays_candidates.json not found")
        sys.exit(1)
    
    with open(candidates_path) as f:
        candidates = json.load(f)
    
    if not candidates:
        print("No candidates to analyze")
        return
    
    tickers = [c.get("ticker") for c in candidates if c.get("ticker")]
    print(f"Analyzing {len(tickers)} tickers: {tickers}")
    
    # Run unified analysis
    results = analyze_batch(tickers)
    
    # Write results
    output_path = Path("data/analysis/analysis_unified.json")
    with open(output_path, "w") as f:
        json.dump({"candidates": results}, f, indent=2)
    
    print(f"Wrote {len(results)} results to {output_path}")


if __name__ == "__main__":
    main()
