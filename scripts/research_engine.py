#!/usr/bin/env python3
"""
research_engine.py - Deterministic earnings research engine
Fetches real options data from Schwab API, computes actual expected moves.
Now includes visible progress tracking.
"""

import json
import subprocess
import sys
import requests
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.options_provider_schwab import get_earnings_snapshot
from scripts.token_manager import get_access_token


# ===============================
# PATHS
# ===============================

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_DIR = WORKSPACE / "config"
DATA_DIR = WORKSPACE / "data"
CACHE_FILE = DATA_DIR / "cache" / "todays_candidates.json"
OUTPUT_FILE = DATA_DIR / "analysis" / "analysis_raw.json"
LOG_FILE = DATA_DIR / "logs" / "pipeline.log"

(DATA_DIR / "analysis").mkdir(parents=True, exist_ok=True)


# ===============================
# LOGGING
# ===============================

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] RESEARCH: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ===============================
# HELPERS
# ===============================

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def load_holdings():
    holdings_file = DATA_DIR / "portfolio" / "holdings.json"
    if holdings_file.exists():
        with open(holdings_file) as f:
            data = json.load(f)

        all_holdings = []
        for account_tickers in data.get("accounts", {}).values():
            all_holdings.extend(account_tickers)

        return list(set(all_holdings))
    return []


def get_basic_quote(symbol: str):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True,
            text=True,
            timeout=10
        )

        data = json.loads(result.stdout)
        meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        volume = meta.get("regularMarketVolume")

        if price:
            return {
                "price": float(price),
                "volume": int(volume) if volume else None,
                "market_cap": None
            }
    except Exception as e:
        log(f"Quote error {symbol}: {e}")

    return {}


def get_schwab_fundamentals(symbol: str):
    try:
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://api.schwabapi.com/v1/instruments"
        params = {"symbol": symbol, "projection": "fundamental"}

        resp = requests.get(url, headers=headers, params=params, timeout=10)

        if resp.status_code != 200:
            log(f"Fundamentals failed {symbol}: {resp.status_code}")
            return {}

        data = resp.json()
        instruments = data.get("instruments", {})
        return instruments.get(symbol, {})

    except Exception as e:
        log(f"Fundamentals error {symbol}: {e}")
        return {}


def is_excluded_healthcare(industry: str):
    if not industry:
        return False

    risky_keywords = [
        "Biotechnology",
        "Drug",
        "Pharmaceutical",
        "Therapeutic",
        "Clinical",
        "Life Sciences",
        "Genomics"
    ]

    return any(word.lower() in industry.lower() for word in risky_keywords)


# ===============================
# MAIN
# ===============================

def main():
    log("=== Starting research_engine.py ===")

    if not CACHE_FILE.exists():
        log("Candidates file not found")
        return

    with open(CACHE_FILE) as f:
        candidates = json.load(f)

    include_list = load_json(CONFIG_DIR / "include_list.json")
    exclude_list = load_json(CONFIG_DIR / "exclude_list.json")
    holdings = load_holdings()

    log(f"Raw earnings candidates: {len(candidates)}")

    # Track filter statistics
    filtered_no_weekly = 0
    filtered_options_unavailable = 0

    # -----------------------------
    # QUOTE FETCH
    # -----------------------------

    ticker_list = list(set([c.get("ticker") for c in candidates]))
    log(f"Fetching quotes for {len(ticker_list)} tickers...")

    ticker_quotes = {}

    for idx, ticker in enumerate(ticker_list, 1):
        log(f"[QUOTE {idx}/{len(ticker_list)}] {ticker}")
        quote = get_basic_quote(ticker)
        ticker_quotes[ticker] = quote if isinstance(quote, dict) else {}

    ticker_prices = {
        t: ticker_quotes.get(t, {}).get("price")
        for t in ticker_list
    }

    log("Quote fetch complete")

    # -----------------------------
    # BASE FILTERS
    # -----------------------------

    candidates = [c for c in candidates if c.get("ticker") not in exclude_list]

    candidates = [
        c for c in candidates
        if ticker_prices.get(c.get("ticker"))
        and ticker_prices.get(c.get("ticker")) > 15
    ]

    log(f"After base filters: {len(candidates)}")

    # -----------------------------
    # RANKING
    # -----------------------------

    ranked = []

    for c in candidates:
        ticker = c.get("ticker")
        quote = ticker_quotes.get(ticker, {})

        score = (
            (10000 if ticker in holdings else 0)
            + (1000 if ticker in include_list else 0)
            + (quote.get("volume") or 0)
        )

        ranked.append((score, c))

    ranked.sort(key=lambda x: -x[0])
    candidates = [c for score, c in ranked][:20]

    log(f"Top ranked selection: {len(candidates)}")

    # -----------------------------
    # HEALTHCARE FILTER
    # -----------------------------

    filtered = []

    for idx, c in enumerate(candidates, 1):
        ticker = c.get("ticker")
        log(f"[FUNDAMENTALS {idx}/{len(candidates)}] {ticker}")

        if ticker in include_list:
            filtered.append(c)
            continue

        fundamentals = get_schwab_fundamentals(ticker)
        industry = fundamentals.get("industry")

        if is_excluded_healthcare(industry):
            log(f"Excluded {ticker} — healthcare subclass ({industry})")
            continue

        filtered.append(c)

    candidates = filtered
    log(f"After healthcare filter: {len(candidates)}")

    # -----------------------------
    # OPTIONS SNAPSHOT
    # -----------------------------

    results = []

    for idx, c in enumerate(candidates, 1):
        ticker = c.get("ticker")
        report_date = c.get("report_date")
        report_time = c.get("report_time", "AMC")

        log(f"[OPTIONS {idx}/{len(candidates)}] {ticker}")

        snapshot = get_earnings_snapshot(ticker, report_date)

        if snapshot.get("status") == "options_unavailable":
            log(f"{ticker} skipped — options unavailable")
            filtered_options_unavailable += 1
            continue

        # Filter: only weekly earnings options (DTE within earnings cycle: 0-10 days)
        dte = snapshot.get("dte", 0)
        if dte < 0 or dte > 10:
            log(f"{ticker} skipped — no weekly earnings options available (dte={dte})")
            filtered_no_weekly += 1
            continue

        result = {
            "ticker": ticker,
            "report": {"date": report_date, "time": report_time},
            "market": {
                "price": snapshot.get("price"),
                "atm_strike": snapshot.get("atm_strike"),
                "expiration": snapshot.get("expiration"),
            },
            "options": {
                "straddle": snapshot.get("straddle"),
                "em_percent": snapshot.get("em_percent"),
            },
            "probabilities": {
                "down_1x": None,
                "down_1_5x": None,
                "down_2x": None,
            },
            "grading": {
                "grade": None,
                "score_total": None,
                "data_ready": True,
            },
            "meta": {
                "status": "ok",
                "tags": ["HOLDING"] if ticker in holdings else ["TRADE"],
            },
        }

        results.append(result)

    results.sort(
        key=lambda x: x.get("options", {}).get("em_percent") or 0,
        reverse=True,
    )

    # Build output with metadata
    from datetime import datetime
    output_data = {
        "metadata": {
            "pipeline_run_time": datetime.now().isoformat(),
            "total_candidates": len(candidates),
            "filtered_no_weekly_options": filtered_no_weekly,
            "filtered_options_unavailable": filtered_options_unavailable,
            "tradeable_candidates": len(results)
        },
        "candidates": results
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)

    log(f"Wrote {len(results)} final research results")
    log("=== Completed ===")


if __name__ == "__main__":
    main()