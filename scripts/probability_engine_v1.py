#!/usr/bin/env python3
"""
probability_engine_v1.py - B-lite probability engine
Calculates downside probabilities based on historical earnings moves.
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_raw.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_with_probs.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] PROB: {msg}\n")
    print(f"[{timestamp}] PROB: {msg}")

def load_analysis():
    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return [], {}
    with open(INPUT_FILE) as f:
        data = json.load(f)
    
    # Handle both old format (array) and new format (object with metadata)
    if isinstance(data, dict) and "candidates" in data:
        return data.get("candidates", []), data.get("metadata", {})
    return data, {}

def get_price_history(ticker):
    """Fetch price history from Yahoo to find earnings dates"""
    # Get last 90 days of daily data
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1d"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        
        data = json.loads(result.stdout)
        result_data = data.get("chart", {}).get("result", [])
        
        if not result_data:
            return []
        
        timestamps = result_data[0].get("timestamp", [])
        close_prices = result_data[0]["indicators"]["quote"][0].get("close", [])
        
        if not timestamps or not close_prices:
            return []
        
        # Build price series
        prices = []
        for i, (ts, close) in enumerate(zip(timestamps, close_prices)):
            if close is not None:
                prices.append({
                    "date": datetime.fromtimestamp(ts),
                    "close": close
                })
        
        return prices
        
    except Exception as e:
        log(f"  Error fetching {ticker}: {e}")
        return []

def find_earnings_moves(prices, ticker):
    """
    Estimate earnings moves by looking for large gap-downs.
    This is a simplified approach since we don't have actual earnings dates.
    """
    # Look for the largest single-day drops in recent history
    # These are likely earnings-related
    
    if len(prices) < 10:
        return []
    
    moves = []
    for i in range(1, len(prices)):
        prev_close = prices[i-1]["close"]
        curr_close = prices[i]["close"]
        
        if prev_close > 0:
            pct_change = (curr_close - prev_close) / prev_close
            
            # Large single-day drops (>3%) are likely earnings
            if abs(pct_change) > 0.03:
                moves.append(abs(pct_change))
    
    return moves

def calculate_probabilities(down_moves, em_percent):
    """Calculate probability of staying within EM thresholds"""
    if not down_moves:
        return None, None, None, None, None
    
    # Compute stats
    median_move = sorted(down_moves)[len(down_moves) // 2]
    max_move = max(down_moves)
    
    # Convert EM from percentage (10.26) to decimal (0.1026) for comparison with moves
    em_decimal = em_percent / 100
    
    em_1x = em_decimal
    em_1_5x = em_decimal * 1.5
    em_2x = em_decimal * 2.0
    
    total = len(down_moves)
    
    down_1x = sum(1 for m in down_moves if m <= em_1x) / total
    down_1_5x = sum(1 for m in down_moves if m <= em_1_5x) / total
    down_2x = sum(1 for m in down_moves if m <= em_2x) / total
    
    return round(down_1x, 2), round(down_1_5x, 2), round(down_2x, 2), median_move, max_move

def process_tickers(analysis_data):
    """Process each ticker and calculate probabilities"""
    
    calculated = 0
    skipped = 0
    
    results = []
    
    for item in analysis_data:
        ticker = item.get("ticker")
        
        # Check if EM exists
        options = item.get("options", {})
        em = options.get("em_percent")
        
        if em is None:
            # No EM yet - skip
            skipped += 1
            results.append(item)
            continue
        
        # Fetch price history
        log(f"Processing {ticker}...")
        prices = get_price_history(ticker)
        
        if not prices:
            log(f"  No price data for {ticker}")
            skipped += 1
            results.append(item)
            continue
        
        # Find estimated earnings moves
        down_moves = find_earnings_moves(prices, ticker)
        
        if not down_moves:
            log(f"  No earnings-like moves found for {ticker}")
            skipped += 1
            results.append(item)
            continue
        
        # Calculate probabilities
        print(f"DEBUG PROB INPUT: {ticker} - em={em}, down_moves_count={len(down_moves)}")
        p1, p1_5, p2, median_move, max_move = calculate_probabilities(down_moves, em)
        
        if p1 is None:
            skipped += 1
            results.append(item)
            continue
        
        # Update item with probabilities
        item["probabilities"] = {
            "down_1x": p1,
            "down_1_5x": p1_5,
            "down_2x": p2,
            "median_move": round(median_move, 4),
            "max_move": round(max_move, 4)
        }
        
        log(f"  {ticker}: EM={em:.2f}%, median={median_move:.2%}, max={max_move:.2%}, samples={len(down_moves)}, P(↓1x)={p1:.0%}, P(↓1.5x)={p1_5:.0%}, P(↓2x)={p2:.0%}")
        
        calculated += 1
        results.append(item)
    
    return results, calculated, skipped

def main():
    log("=== Starting probability_engine_v1.py ===")
    
    # Load analysis
    analysis_data, metadata = load_analysis()
    
    # Always write output file, even if empty - prevents stale data bug
    if not analysis_data:
        log("No candidates — writing empty probability output")
        output_data = {
            "metadata": metadata,
            "candidates": []
        }
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f, indent=2)
        log(f"Wrote empty output to {OUTPUT_FILE}")
        log("=== Completed ===")
        return
    
    log(f"Loaded {len(analysis_data)} tickers")
    
    # Process
    results, calculated, skipped = process_tickers(analysis_data)
    
    # Write output with metadata preserved
    output_data = {
        "metadata": metadata,
        "candidates": results
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)
    
    log(f"Calculated probabilities for {calculated} tickers")
    log(f"Skipped {skipped} tickers (no EM yet)")
    log(f"Wrote to {OUTPUT_FILE}")
    
    # Print sample
    print("\n=== Sample Output ===")
    for item in results[:3]:
        ticker = item.get("ticker")
        probs = item.get("probabilities", {})
        print(f"{ticker}: {probs}")
    
    log("=== Completed ===")
    return calculated

if __name__ == "__main__":
    main()
