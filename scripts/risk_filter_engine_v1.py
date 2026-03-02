#!/usr/bin/env python3
"""
risk_filter_engine_v1.py - Deterministic risk filter
Adds risk flags to each ticker based on market conditions.
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_DIR = WORKSPACE / "config"
DATA_DIR = WORKSPACE / "data"
INPUT_FILE = DATA_DIR / "analysis" / "analysis_with_probs.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_with_risk.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

# Sector mapping (ticker -> sector ETF)
SECTOR_MAP = {
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "AMD": "XLK", "INTC": "XLK",
    "UNH": "XLV", "LLY": "XLV", "PFE": "XLV", "ABBV": "XLV",
    "TSLA": "XLY", "AMZN": "XLY", "HD": "XLY", "MCD": "XLY",
    "JPM": "XLF", "BAC": "XLF", "WFC": "XLF",
    "XOM": "XLE", "CVX": "XLE",
    "BA": "XLI", "CAT": "XLI",
    "GLD": "XLI",  # commodities
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] RISK: {msg}\n")
    print(f"[{timestamp}] RISK: {msg}")

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def load_analysis():
    if not INPUT_FILE.exists():
        log(f"Input file not found: {INPUT_FILE}")
        return []
    with open(INPUT_FILE) as f:
        return json.load(f)

def get_price_change(ticker, days=10):
    """Get price change over last N days"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={days}d&interval=1d"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        
        data = json.loads(result.stdout)
        result_data = data.get("chart", {}).get("result", [])
        
        if not result_data:
            return None
        
        timestamps = result_data[0].get("timestamp", [])
        close_prices = result_data[0]["indicators"]["quote"][0].get("close", [])
        
        if len(close_prices) < 2:
            return None
        
        start_price = close_prices[0]
        end_price = close_prices[-1]
        
        if start_price and end_price:
            return (end_price - start_price) / start_price
        
        return None
        
    except Exception as e:
        return None

def get_sector_change(sector_etf, days=14):
    """Get sector ETF change over last N days"""
    return get_price_change(sector_etf, days)

def get_vix():
    """Get current VIX level"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        
        data = json.loads(result.stdout)
        result_data = data.get("chart", {}).get("result", [])
        
        if not result_data:
            return None
        
        close_prices = result_data[0]["indicators"]["quote"][0].get("close", [])
        
        if close_prices:
            return close_prices[-1]
        
        return None
        
    except:
        return None

def check_macro_events():
    """Check if any macro events within 48 hours"""
    events_file = CONFIG_DIR / "macro_events.json"
    events = load_json(events_file)
    
    if not events:
        return False
    
    now = datetime.now()
    events_list = events.get("events", [])
    
    for event in events_list:
        event_date = event.get("date", "")
        if not event_date:
            continue
        
        try:
            event_dt = datetime.strptime(event_date, "%Y-%m-%d")
            hours_until = (event_dt - now).total_seconds() / 3600
            
            if 0 <= hours_until <= 48:
                return True
        except:
            continue
    
    return False

def process_tickers(analysis_data):
    """Process each ticker and add risk flags"""
    
    # Get market conditions once
    vix = get_vix()
    log(f"VIX: {vix}")
    
    market_regime = vix and vix > 23
    macro_nearby = check_macro_events()
    
    flagged_count = 0
    
    for item in analysis_data:
        ticker = item.get("ticker")
        risk_flags = {
            "recent_drift": False,
            "sector_stress": False,
            "market_regime": False,
            "macro_event_nearby": False
        }
        
        # Recent drift check (>8% in 10 days)
        price_change = get_price_change(ticker, 10)
        if price_change and abs(price_change) > 0.08:
            risk_flags["recent_drift"] = True
        
        # Sector stress check
        sector_etf = SECTOR_MAP.get(ticker)
        if sector_etf:
            sector_change = get_sector_change(sector_etf, 14)
            if sector_change and sector_change < -0.05:
                risk_flags["sector_stress"] = True
        
        # Market regime
        if market_regime:
            risk_flags["market_regime"] = True
        
        # Macro events
        if macro_nearby:
            risk_flags["macro_event_nearby"] = True
        
        # Add to item
        item["risk_flags"] = risk_flags
        
        if any(risk_flags.values()):
            flagged_count += 1
            log(f"  {ticker}: {[k for k,v in risk_flags.items() if v]}")
    
    return analysis_data, flagged_count, market_regime, macro_nearby

def main():
    log("=== Starting risk_filter_engine_v1.py ===")
    
    # Load analysis
    analysis_data = load_analysis()
    
    if not analysis_data:
        log("No analysis data - exiting")
        return
    
    log(f"Loaded {len(analysis_data)} tickers")
    
    # Process
    results, flagged_count, market_regime, macro_nearby = process_tickers(analysis_data)
    
    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    log(f"Flagged {flagged_count} tickers")
    log(f"Market regime (VIX>23): {market_regime}")
    log(f"Macro event nearby: {macro_nearby}")
    log(f"Wrote to {OUTPUT_FILE}")
    
    # Print sample
    print("\n=== Sample Output ===")
    for item in results[:2]:
        print(f"{item.get('ticker')}: {item.get('risk_flags')}")
    
    log("=== Completed ===")
    return flagged_count

if __name__ == "__main__":
    main()
