#!/usr/bin/env python3
"""
pull_earnings_today.py - Deterministic earnings candidate fetcher
Fetches today's and tomorrow's earnings from Nasdaq, applies timing filter,
outputs candidate tickers to JSON.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# === TEST MODE ===
# Set to a specific date string (YYYY-MM-DD) to force that date
# Example: TEST_DATE = "2026-02-25"
# Set to None for production (uses current date)
TEST_DATE = None
# ===============

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_DIR = WORKSPACE / "config"
DATA_DIR = WORKSPACE / "data"
CACHE_FILE = DATA_DIR / "cache" / "todays_candidates.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

# Ensure directories exist
(DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)

def log(msg):
    """Append to pipeline log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] PULL_EARNINGS: {msg}\n")
    print(f"[{timestamp}] {msg}")

def load_config(filename):
    """Load JSON config file"""
    path = CONFIG_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def fetch_nasdaq_earnings():
    """Fetch earnings calendar from Nasdaq"""
    log("Fetching earnings calendar from Nasdaq...")
    
    # Apply TEST_DATE override if set
    if TEST_DATE:
        today = datetime.strptime(TEST_DATE, "%Y-%m-%d")
    else:
        today = datetime.now()
    
    all_earnings = []
    
    # Fetch 4 days for Wednesday simulation, otherwise just today+tomorrow
    if TEST_DATE:
        dates = [today + timedelta(days=i) for i in range(4)]
    else:
        dates = [today, today + timedelta(days=1)]
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        log(f"  Fetching {date_str}...")
        
        url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"
        
        try:
            result = subprocess.run(
                ["curl", "-s", "-H", f"User-Agent: {headers['User-Agent']}", 
                 "-H", f"Accept: {headers['Accept']}",
                 "--max-time", "30", url],
                capture_output=True,
                text=True,
                timeout=35
            )
            
            if result.returncode != 0:
                log(f"  Nasdaq fetch failed for {date_str}: {result.stderr[:100]}")
                continue
            
            # Parse JSON response
            try:
                data = json.loads(result.stdout)
                
                # Nasdaq structure: data -> rows[]
                if "data" in data:
                    rows = data["data"].get("rows", [])
                    log(f"  Got {len(rows)} earnings for {date_str}")
                    # Tag each row with the API date since Nasdaq returns null
                    for row in rows:
                        row['_api_date'] = date_str
                    all_earnings.extend(rows)
                else:
                    log(f"  Data structure: {list(data.keys())}")
                    
            except json.JSONDecodeError as e:
                log(f"  JSON parse error for {date_str}: {e}")
                continue
                
        except Exception as e:
            log(f"  Error fetching {date_str}: {e}")
            continue
    
    if not all_earnings:
        log("No earnings data from Nasdaq")
        return None
        
    log(f"Total earnings fetched: {len(all_earnings)}")
    return all_earnings

def filter_candidates(earnings_data):
    """Apply filters to earnings data"""
    # Load configs
    include_list = load_config("include_list.json")
    exclude_list = load_config("exclude_list.json")
    
    # Apply TEST_DATE override if set
    if TEST_DATE:
        now = datetime.strptime(TEST_DATE, "%Y-%m-%d")
    else:
        now = datetime.now()
    
    today = now.strftime("%Y-%m-%d")
    weekday = now.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
    
    # Determine target dates based on weekday
    # For selling puts into earnings, we want the next TRADABLE event
    if weekday in [0, 1, 2, 3]:  # Mon-Thu
        target_dates = [(today, "AMC"), ((now + timedelta(days=1)).strftime("%Y-%m-%d"), "BMO")]
        log(f"Selecting today AMC / tomorrow BMO")
    elif weekday == 4:  # Friday
        # Friday - today AMC (trades Monday) AND Monday BMO (trades Monday)
        monday = (now + timedelta(days=3)).strftime("%Y-%m-%d")
        target_dates = [(today, "AMC"), (monday, "BMO")]
        log(f"Today is Friday — selecting today AMC + Monday BMO")
    else:  # Weekend (Sat/Sun)
        # Weekend - next tradable is Monday BMO
        days_until_monday = 7 - weekday  # 1 for Sat, 2 for Sun
        monday = (now + timedelta(days=days_until_monday)).strftime("%Y-%m-%d")
        target_dates = [(monday, "BMO")]
        log(f"Weekend — selecting Monday BMO")
    
    # Count for logging
    raw_count = len(earnings_data)
    time_filtered_count = 0
    
    # Track timing breakdown
    timing_breakdown = {"time-not-supplied": 0, "time-after-hours": 0, "time-pre-market": 0, "unknown": 0}
    
    candidates = []
    
    # If no data from Nasdaq, use stub data for testing
    if not earnings_data:
        log("No Nasdaq data - using empty candidate list")
        return []
    
    for row in earnings_data:
        try:
            # Nasdaq format: ticker is in "symbol" field
            ticker = row.get("symbol", row.get("ticker", ""))
            if not ticker:
                continue
            
            # Get earnings date/time
            # Nasdaq format: time is "time-pre-market", "time-after-hours", "time-not-supplied"
            # Use _api_date which we set when fetching
            earnings_date = row.get("_api_date", today)
            start_time = str(row.get("time", "")).strip()
            
            # Parse time - FIXED: handle all Nasdaq time formats
            # "time-not-supplied" = AMC (after hours - unknown exact time)
            # "time-after-hours" = AMC (confirmed after hours)
            # "time-pre-market" = BMO
            if start_time == "time-not-supplied":
                report_time = "AMC"
                timing_breakdown["time-not-supplied"] += 1
            elif start_time == "time-after-hours":
                report_time = "AMC"
                timing_breakdown["time-after-hours"] += 1
            elif start_time == "time-pre-market":
                report_time = "BMO"
                timing_breakdown["time-pre-market"] += 1
            else:
                report_time = "UNKNOWN"
                timing_breakdown["unknown"] += 1
            
            # Apply date filter: target_dates (skip UNKNOWN)
            if report_time == "UNKNOWN":
                time_filtered_count += 1
                continue
            
            if (earnings_date, report_time) not in target_dates:
                time_filtered_count += 1
                continue  # Skip
            
            # Apply include list (always include)
            if ticker in include_list:
                candidates.append({
                    "ticker": ticker,
                    "report_time": report_time,
                    "report_date": earnings_date,
                    "source": "include_list"
                })
                continue
            
            # Apply exclude list
            if ticker in exclude_list:
                continue
            
            # Keep ticker
            candidates.append({
                "ticker": ticker,
                "report_time": report_time,
                "report_date": earnings_date,
                "source": "nasdaq_filtered"
            })
            
        except Exception as e:
            log(f"Error parsing row: {e}")
            continue
    
    # Final logging
    log(f"Raw earnings pulled: {raw_count}")
    log(f"Timing breakdown: time-not-supplied={timing_breakdown['time-not-supplied']} time-after-hours={timing_breakdown['time-after-hours']} time-pre-market={timing_breakdown['time-pre-market']} unknown={timing_breakdown['unknown']}")
    log(f"After timing filter: {len(candidates)}")
    log(f"Final candidates: {len(candidates)}")
    
    return candidates

def main():
    """Main execution"""
    log("=== Starting pull_earnings_today.py ===")
    
    # Fetch from Nasdaq
    earnings_data = fetch_nasdaq_earnings()
    
    # Filter candidates
    candidates = filter_candidates(earnings_data)
    
    # Write output
    with open(CACHE_FILE, "w") as f:
        json.dump(candidates, f, indent=2)
    
    log(f"Wrote {len(candidates)} candidates to {CACHE_FILE}")
    
    # Print summary
    print("\n=== Today's Earnings Candidates ===")
    if candidates:
        for c in candidates:
            print(f"  {c['ticker']} - {c['report_time']} ({c['report_date']})")
    else:
        print("  (none)")
    
    print(f"\nOutput: {CACHE_FILE}")
    log("=== Completed ===")
    
    return len(candidates)

if __name__ == "__main__":
    main()
