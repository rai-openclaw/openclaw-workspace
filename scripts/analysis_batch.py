#!/usr/bin/env python3
"""
analysis_batch.py - Direct call to analyze_batch()
Calls analysis_engine.analyze_batch() directly (not via subprocess).
Must be called from run_pipeline.py with Schwab token in environment.
"""

import json
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "core"))

from analysis_engine import analyze_batch


def main():
    # Load candidates after research_engine filtering
    candidates_path = Path("data/analysis/analysis_raw.json")
    
    if not candidates_path.exists():
        print("Error: analysis_raw.json not found")
        print("Run research_engine.py first to filter candidates")
        sys.exit(1)
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    candidates = data.get("candidates", [])
    
    if not candidates:
        print("No candidates to analyze")
        return
    
    tickers = [c.get("ticker") for c in candidates if c.get("ticker")]
    print(f"Analyzing {len(tickers)} filtered tickers: {tickers}")
    
    # Run unified analysis (direct call, not subprocess)
    # Pass candidates to preserve original fields for downstream pipeline consumers
    results = analyze_batch(tickers, candidates=candidates)
    
    # Write results - overwrites analysis_raw.json with enriched data
    with open(candidates_path, "w") as f:
        json.dump({"candidates": results}, f, indent=2)
    
    print(f"Wrote {len(results)} enriched results to analysis_raw.json")


if __name__ == "__main__":
    main()
