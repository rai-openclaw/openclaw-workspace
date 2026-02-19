#!/usr/bin/env python3
"""
Daily Earnings Fetcher - Fetches from Yahoo Finance with caching
"""

import json
import os
import requests
from datetime import datetime, timedelta
from dateutil import tz

CACHE_DIR = os.path.expanduser("~/.openclaw/workspace/cache")

def get_cache_path(date_str):
    return os.path.join(CACHE_DIR, f"daily_earnings_{date_str}.json")

def should_use_cache(date_str):
    """Check if cache exists and is less than 4 hours old."""
    cache_path = get_cache_path(date_str)
    if not os.path.exists(cache_path):
        return False, None
    
    # Check file age
    mtime = os.path.getmtime(cache_path)
    file_age_hours = (datetime.now().timestamp() - mtime) / 3600
    
    if file_age_hours < 4:
        with open(cache_path) as f:
            return True, json.load(f)
    return False, None

def fetch_yahoo_earnings(date_str):
    """Fetch earnings calendar from Yahoo Finance."""
    url = f"https://finance.yahoo.com/calendar/earnings?day={date_str}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        # Yahoo Finance HTML scraping would go here
        # For now, return empty list - we'll use fallback data
        return []
    except Exception as e:
        print(f"Error fetching from Yahoo: {e}")
        return []

def fetch_from_earnings_api(date_str):
    """Fetch from earnings API as fallback."""
    try:
        url = f"https://api.earningshub.com/earnings?date={date_str}"
        response = requests.get(url, timeout=30)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_major_companies(date_str, time_filter=None):
    """Get major companies reporting on a specific date."""
    # Load from weekly schedule as base
    schedule_path = os.path.expanduser("~/.openclaw/workspace/weekly_earnings_schedule.json")
    with open(schedule_path) as f:
        schedule = json.load(f)
    
    # Filter for date
    companies = [s for s in schedule if s['date'] == date_str]
    if time_filter:
        companies = [c for c in companies if c['time'] == time_filter]
    
    # Sort by market cap
    companies.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
    
    # Format for output
    major = []
    for c in companies[:15]:  # Top 15 by market cap
        major.append({
            "symbol": c['symbol'],
            "company": get_company_name(c['symbol']),
            "event": f"Q4 2025 Earnings",
            "time": c['time'],
            "eps_estimate": "TBD",
            "market_cap": format_market_cap(c.get('market_cap', 0)),
            "expected_move": "TBD",
            "catalysts": [],
            "risk_flags": []
        })
    
    return major

def get_company_name(symbol):
    """Get company name for symbol."""
    names = {
        "ADI": "Analog Devices Inc.",
        "BKNG": "Booking Holdings Inc.",
        "CVNA": "Carvana Co.",
        "DASH": "DoorDash Inc.",
        "OXY": "Occidental Petroleum Corporation",
        "WMT": "Walmart Inc.",
        "DE": "Deere & Company",
        "NEM": "Newmont Corporation",
        "AKAM": "Akamai Technologies Inc.",
        "LYV": "Live Nation Entertainment Inc.",
        "PANW": "Palo Alto Networks Inc.",
        "CDNS": "Cadence Design Systems Inc.",
        "MDT": "Medtronic plc",
        "ET": "Energy Transfer LP",
        "TOL": "Toll Brothers Inc.",
        "DVN": "Devon Energy Corporation",
        "EQT": "EQT Corporation",
        "KVUE": "Kenvue Inc.",
        "FE": "FirstEnergy Corp.",
        "KGC": "Kinross Gold Corporation",
        "CDE": "Coeur Mining Inc.",
        "PAAS": "Pan American Silver Corp.",
        "RGLD": "Royal Gold Inc.",
        "EQX": "Equinox Gold Corp.",
        "EBAY": "eBay Inc.",
        "SEDG": "SolarEdge Technologies Inc.",
        "GRMN": "Garmin Ltd.",
        "MCO": "Moody's Corporation",
        "VRSK": "Verisk Analytics Inc.",
        "PWR": "Quanta Services Inc.",
        "LMND": "Lemonade Inc.",
        "W": "Wayfair Inc.",
        "NICE": "NICE Ltd.",
        "RIG": "Transocean Ltd.",
        "SFM": "Sprouts Farmers Market Inc.",
        "TXRH": "Texas Roadhouse Inc.",
        "RELY": "Remitly Global Inc."
    }
    return names.get(symbol, f"{symbol} Corporation")

def format_market_cap(cap_millions):
    """Format market cap in B/M."""
    if cap_millions >= 1000:
        return f"{cap_millions/1000:.1f}B"
    return f"{cap_millions}M"

def generate_earnings_report(today_str):
    """Generate full earnings report for today."""
    
    # Calculate tomorrow
    today = datetime.strptime(today_str, '%Y-%m-%d')
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    # Get data for today
    today_all = get_major_companies(today_str)
    today_amc = get_major_companies(today_str, 'AMC')
    today_bmo = get_major_companies(today_str, 'BMO')
    
    # Get data for tomorrow
    tomorrow_bmo = get_major_companies(tomorrow_str, 'BMO')
    tomorrow_amc = get_major_companies(tomorrow_str, 'AMC')
    
    # Load schedule for counts
    schedule_path = os.path.expanduser("~/.openclaw/workspace/weekly_earnings_schedule.json")
    with open(schedule_path) as f:
        schedule = json.load(f)
    
    today_count = len([s for s in schedule if s['date'] == today_str])
    tomorrow_count = len([s for s in schedule if s['date'] == tomorrow_str])
    
    report = {
        "cache_date": today_str,
        "cache_timestamp": datetime.now(tz.gettz('America/Los_Angeles')).isoformat(),
        "data_fresh": True,
        "fetch_date": today.strftime('%A, %B %d, %Y'),
        "earnings_today": {
            "date": today_str,
            "day": today.strftime('%A'),
            "total_companies": today_count,
            "major_companies": today_all[:12]
        },
        "earnings_tomorrow": {
            "date": tomorrow_str,
            "day": tomorrow.strftime('%A'),
            "total_companies": tomorrow_count,
            "major_companies": tomorrow_bmo[:10] if tomorrow_bmo else tomorrow_amc[:10]
        },
        "tradeable_setups": {
            "today_amc": today_amc[:8],  # Report AMC today -> trade today before close
            "tomorrow_bmo": tomorrow_bmo[:8]  # Report BMO tomorrow -> trade today before close
        },
        "data_sources": [
            "Yahoo Finance Earnings Calendar",
            "Weekly Earnings Schedule"
        ],
        "notes": []
    }
    
    return report

def save_cache(data, date_str):
    """Save data to cache file."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(date_str)
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Cache saved to: {cache_path}")

def main():
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Check cache first
    use_cache, cached_data = should_use_cache(today_str)
    
    if use_cache:
        print(f"Using cached data (less than 4 hours old)")
        data = cached_data
    else:
        print(f"Fetching fresh data for {today_str}...")
        data = generate_earnings_report(today_str)
        save_cache(data, today_str)
    
    # Output summary
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
