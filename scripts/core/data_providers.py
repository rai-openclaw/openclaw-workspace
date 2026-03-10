#!/usr/bin/env python3
"""
data_providers.py - Unified data access layer
All API calls (Yahoo, Schwab, Nasdaq) go through this module.
"""

import json
import subprocess
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load .env from workspace root (override shell env)
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

# Workspace path
WORKSPACE = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# TOKEN MANAGEMENT
# =============================================================================

def get_schwab_token() -> Optional[str]:
    """Get access token from token manager."""
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from token_manager import get_access_token
        return get_access_token()
    except Exception:
        return None


# =============================================================================
# YAHOO FINANCE (via curl)
# =============================================================================

def get_price_history(ticker: str, days: int = 90) -> List[Dict]:
    """
    Fetch price history from Yahoo Finance using curl.
    Returns list of {date, price, change%} dicts.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={days}d&interval=1d"
    
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
        quote = result_data[0].get("indicators", {}).get("quote", [{}])[0]
        closes = quote.get("close", [])
        
        if not timestamps or not closes:
            return []
        
        prices = []
        prev_close = None
        
        for ts, close in zip(timestamps, closes):
            if close is not None:
                date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                change_pct = 0.0
                if prev_close is not None and prev_close > 0:
                    change_pct = ((close - prev_close) / prev_close) * 100
                
                prices.append({
                    "date": date,
                    "price": round(close, 2),
                    "change%": round(change_pct, 2)
                })
                prev_close = close
        
        return prices
        
    except Exception:
        return []


def get_basic_quote(ticker: str) -> Dict:
    """Get current quote for a ticker."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=10
        )
        
        data = json.loads(result.stdout)
        meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
        
        price = meta.get("regularMarketPrice")
        
        if price:
            return {
                "price": float(price),
                "symbol": ticker
            }
    except Exception:
        pass
    
    return {}


def get_news_timeline(ticker: str, days_back: int = 90) -> List[Dict]:
    """
    Retrieve news headlines using Yahoo Finance search endpoint.
    """
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        
        data = json.loads(result.stdout)
        news_items = data.get("news", [])
        
        if not news_items:
            return []
        
        timeline = []
        
        for item in news_items:
            title = item.get("title", "")
            publisher = item.get("publisher", "Unknown")
            pub_time = item.get("providerPublishTime", 0) or item.get("datetime", 0)
            related_tickers = item.get("relatedTickers", [])
            
            if not pub_time or not title:
                continue
            
            try:
                pub_date = datetime.fromtimestamp(pub_time)
            except (ValueError, OSError):
                continue
            
            timeline.append({
                "date": pub_date.strftime("%Y-%m-%d"),
                "headline": title,
                "publisher": publisher,
                "relatedTickers": related_tickers
            })
        
        timeline.sort(key=lambda x: x.get("date", ""), reverse=True)
        return timeline[:20]
        
    except Exception:
        return []


# =============================================================================
# SCHWAB API
# =============================================================================

SCHWAB_OPTIONS_URL = "https://api.schwabapi.com/marketdata/v1/chains"
SCHWAB_INSTRUMENTS_URL = "https://api.schwabapi.com/v1/instruments"


def get_schwab_fundamentals(symbol: str) -> Dict:
    """Get fundamental data from Schwab."""
    token = get_schwab_token()
    if not token:
        return {}
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "symbol": symbol,
        "projection": "fundamental"
    }
    
    try:
        resp = requests.get(SCHWAB_INSTRUMENTS_URL, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            instruments = data.get("instruments", [])
            if instruments:
                return instruments[0]
    except Exception:
        pass
    
    return {}


def get_options_chain(symbol: str) -> Optional[Dict]:
    """Fetch options chain from Schwab API."""
    token = get_schwab_token()
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"symbol": symbol, "includeQuotes": "true"}
    
    try:
        response = requests.get(SCHWAB_OPTIONS_URL, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    return None


def get_options_context(ticker: str) -> Optional[Dict]:
    """
    Get options market context using Schwab API.
    Returns implied move, ATM IV, call/put skew.
    """
    chain = get_options_chain(ticker)
    if not chain:
        return None
    
    underlying_price = chain.get("underlyingPrice")
    if not underlying_price:
        return None
    
    call_map = chain.get("callExpDateMap", {})
    if not call_map:
        return None
    
    expirations = list(call_map.keys())
    if not expirations:
        return None
    
    expirations.sort(key=lambda x: x.split(":")[0] if ":" in x else x)
    nearest_exp = expirations[0]
    
    exp_calls = call_map.get(nearest_exp, {})
    strikes = list(exp_calls.keys())
    if not strikes:
        return None
    
    # Find ATM strike
    atm_strike = None
    min_diff = float('inf')
    
    for strike_str in strikes:
        try:
            strike = float(strike_str)
            diff = abs(strike - underlying_price)
            if diff < min_diff:
                min_diff = diff
                atm_strike = strike
        except ValueError:
            continue
    
    if atm_strike is None:
        return None
    
    call_data = exp_calls.get(str(atm_strike), [{}])[0] if exp_calls.get(str(atm_strike)) else {}
    put_data = chain.get("putExpDateMap", {}).get(nearest_exp, {}).get(str(atm_strike), [{}])[0]
    
    # Calculate implied move
    call_mark = call_data.get("mark", 0) or 0
    put_mark = put_data.get("mark", 0) or 0 if put_data else 0
    straddle = call_mark + put_mark
    
    if underlying_price > 0 and straddle > 0:
        implied_move_pct = (straddle / underlying_price) * 100
    else:
        implied_move_pct = None
    
    # Get ATM IV - Schwab API uses "volatility" field as percentage (e.g., 150 = 150%)
    call_iv = call_data.get("volatility", 0) or 0
    put_iv = put_data.get("volatility", 0) or 0 if put_data else 0
    atm_iv = (call_iv + put_iv) / 2 if (call_iv and put_iv) else (call_iv or put_iv or 0)
    
    # Calculate call/put skew
    if put_mark > 0 and call_mark > 0:
        call_put_skew = (call_mark - put_mark) / put_mark * 100
    else:
        call_put_skew = 0
    
    # Extract DTE
    dte = 0
    if ":" in nearest_exp:
        try:
            dte = int(nearest_exp.split(":")[1])
        except (ValueError, IndexError):
            dte = 0
    
    # Build interpretation
    if implied_move_pct:
        interpretation = f"Options market expects a +/-{implied_move_pct:.1f}% move for the next {dte} days."
    else:
        interpretation = "Unable to calculate implied move."
    
    return {
        "implied_move": round(implied_move_pct, 2) if implied_move_pct else None,
        "atm_iv": round(atm_iv, 1) if atm_iv else None,
        "call_put_skew": round(call_put_skew, 1),
        "underlying_price": underlying_price,
        "dte": dte,
        "expiration": nearest_exp.split(":")[0] if ":" in nearest_exp else nearest_exp,
        "interpretation": interpretation
    }


# =============================================================================
# NASDAQ API
# =============================================================================

def fetch_nasdaq_earnings(date_str: str = None) -> List[Dict]:
    """Fetch earnings calendar from Nasdaq."""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_str}"
    
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"User-Agent: {headers['User-Agent']}", 
             "-H", f"Accept: {headers['Accept']}", "--max-time", "30", url],
            capture_output=True, text=True, timeout=35
        )
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        
        if "data" in data:
            rows = data["data"].get("rows", [])
            return rows
    except Exception:
        pass
    
    return []


# =============================================================================
# LOCAL DATA FILES
# =============================================================================

def get_earnings_encyclopedia() -> List[Dict]:
    """Load earnings encyclopedia entries."""
    path = WORKSPACE / "data" / "earnings" / "earnings_encyclopedia.json"
    
    if not path.exists():
        return []
    
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("entries", [])
    except Exception:
        return []


def save_earnings_to_encyclopedia(earnings_event: Dict, ticker: str, source: str = "price_detection") -> bool:
    """
    Add new earnings event to encyclopedia if it doesn't already exist.
    
    Args:
        earnings_event: The earnings event dict with date, reaction, etc
        ticker: Stock ticker symbol
        source: "pipeline" or "price_detection"
    
    Returns:
        True if saved successfully, False if already exists or error
    """
    import copy
    from datetime import datetime
    
    path = WORKSPACE / "data" / "earnings" / "earnings_encyclopedia.json"
    
    # Load existing data
    try:
        if path.exists():
            with open(path) as f:
                data = json.load(f)
        else:
            data = {"version": "1.0", "last_updated": "", "entries": []}
    except Exception:
        return False
    
    entries = data.get("entries", [])
    
    # Check if entry already exists for this ticker + date
    earnings_date = earnings_event.get("report_date") or earnings_event.get("earnings_date")
    if not earnings_date:
        return False
    
    # Check for existing entry
    for existing in entries:
        if existing.get("ticker", "").upper() == ticker.upper():
            if existing.get("earnings_date") == earnings_date:
                # Already exists
                return False
    
    # Create new entry
    new_entry = {
        "ticker": ticker.upper(),
        "company": ticker.upper(),  # Would need to fetch real name
        "grade": "N/A",
        "total_score": 0,
        "expected_move": earnings_event.get("expected_move"),
        "earnings_date": earnings_date,
        "earnings_time": earnings_event.get("report_time", "UNKNOWN"),
        "sector": get_sector_etf(ticker),  # Get sector from mapping
        "price_before": earnings_event.get("price_before"),
        "price_after": earnings_event.get("price_after"),
        "reaction_percent": earnings_event.get("reaction_percent"),
        "source": source,
        "last_researched": datetime.now().strftime("%Y-%m-%d"),
        "research_history": []
    }
    
    # Add to entries
    entries.append(new_entry)
    data["entries"] = entries
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Save
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def get_last_earnings_event(ticker: str) -> Optional[Dict]:
    """Get most recent earnings event for a ticker."""
    entries = get_earnings_encyclopedia()
    
    ticker_entries = [
        e for e in entries 
        if e.get("ticker", "").upper() == ticker.upper()
    ]
    
    if not ticker_entries:
        return None
    
    ticker_entries.sort(key=lambda x: x.get("earnings_date", ""), reverse=True)
    latest = ticker_entries[0]
    
    return {
        "ticker": latest.get("ticker"),
        "report_date": latest.get("earnings_date"),
        "report_time": latest.get("earnings_time"),
        "expected_move": latest.get("expected_move"),
        "grade": latest.get("grade"),
        "sector": latest.get("sector")
    }


def get_probability_data(ticker: str) -> Optional[Dict]:
    """Load probability metrics from analysis file."""
    path = WORKSPACE / "data" / "analysis" / "analysis_with_probs.json"
    
    if not path.exists():
        return None
    
    try:
        with open(path) as f:
            data = json.load(f)
        
        candidates = data.get("candidates", [])
        
        for c in candidates:
            if c.get("ticker", "").upper() == ticker.upper():
                return c.get("probabilities", {})
    except Exception:
        pass
    
    return None


def get_sector_etf(ticker: str) -> str:
    """
    Map stock to sector ETF.
    Uses ticker-specific mapping + sector-based fallback.
    """
    # Ticker-specific ETF mapping
    ticker_map = {
        # Consumer Discretionary
        "KSS": "XRT", "WMT": "XLY", "TGT": "XLY", "BBY": "XLY",
        "AMZN": "XLY", "TSLA": "XLY", "NKE": "XLY", "HD": "XLY",
        "MCD": "XLY", "SBUX": "XLY",
        
        # Consumer Staples
        "CPB": "XLP", "KO": "XLP", "PEP": "XLP", "PG": "XLP",
        "COST": "XLP", "WBA": "XLP", "MDLZ": "XLP", "GIS": "XLP",
        "K": "XLP", "HSY": "XLP", "STZ": "XLP", "CL": "XLP",
        
        # Technology
        "AAPL": "XLK", "MSFT": "XLK", "NVDA": "SMH", "AMD": "SMH",
        "INTC": "XLK", "CRM": "XLK", "ORCL": "XLK", "ADBE": "XLK",
        "AVAV": "ITA",  # AeroVironment - Aerospace & Defense
        
        # Healthcare
        "JNJ": "XLV", "PFE": "XLV", "UNH": "XLV", "MRK": "XLV",
        "LLY": "XLV", "ABBV": "XLV", "TMO": "XLV", "DHR": "XLV",
        "CVS": "XLV", "CI": "XLV", "HUM": "XLV",
        
        # Financials
        "JPM": "XLF", "BAC": "XLF", "WFC": "XLF", "GS": "XLF",
        "MS": "XLF", "C": "XLF", "BLK": "XLF", "SCHW": "XLF",
        
        # Energy
        "XOM": "XLE", "CVX": "XLE", "COP": "XLE", "SLB": "XLE",
        "EOG": "XLE", "MPC": "XLE", "PSX": "XLE", "VLO": "XLE",
        
        # Industrials
        "BA": "XLI", "CAT": "XLI", "UNP": "XLI", "HON": "XLI",
        "GE": "XLI", "MMM": "XLI", "LMT": "XLI", "RTX": "XLI",
        
        # Materials
        "LIN": "XLB", "APD": "XLB", "SHW": "XLB", "FCX": "XLB",
        "NEM": "XLB", "GOLD": "XLB",
        
        # Real Estate
        "PLD": "XLRE", "AMT": "XLRE", "EQIX": "XLRE", "SPG": "XLRE",
        
        # Utilities
        "NEE": "XLU", "DUK": "XLU", "SO": "XLU", "D": "XLU",
        
        # Communications
        "META": "XLC", "GOOG": "XLC", "GOOGL": "XLC", "NFLX": "XLC",
        "DIS": "XLC", "CMCSA": "XLC", "VZ": "XLC", "TMUS": "XLC",
    }
    
    # Check ticker-specific mapping first
    if ticker.upper() in ticker_map:
        return ticker_map[ticker.upper()]
    
    # Try to get sector from fundamentals
    fundamentals = get_schwab_fundamentals(ticker)
    sector = fundamentals.get("sector", "")
    industry = fundamentals.get("industry", "")
    
    # Sector to ETF mapping
    sector_etf_map = {
        "Technology": "XLK",
        "Information Technology": "XLK",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Healthcare": "XLV",
        "Financials": "XLF",
        "Financial Services": "XLF",
        "Energy": "XLE",
        "Industrials": "XLI",
        "Basic Materials": "XLB",
        "Materials": "XLB",
        "Real Estate": "XLRE",
        "Utilities": "XLU",
        "Communication Services": "XLC",
        "Communications": "XLC",
    }
    
    # Industry keywords for more precise mapping
    industry_keywords = {
        "semiconductor": "SMH",
        "software": "XLK",
        "hardware": "XLK",
        "bank": "XLF",
        "insurance": "XLF",
        "oil": "XLE",
        "gas": "XLE",
        "aerospace": "ITA",
        "defense": "ITA",
        "retail": "XLY",
        "pharma": "XLV",
        "biotech": "XLV",
        "hospital": "XLV",
    }
    
    # Check sector
    if sector and sector in sector_etf_map:
        return sector_etf_map[sector]
    
    # Check industry keywords
    search_text = (sector + " " + industry).lower()
    for keyword, etf in industry_keywords.items():
        if keyword in search_text:
            return etf
    
    # Default to broad market
    return "SPY"
