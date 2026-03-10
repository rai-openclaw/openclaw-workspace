#!/usr/bin/env python3
"""
analysis_engine.py - Unified analysis orchestration
Orchestrates the full analysis flow using data_providers.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add core to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_providers import (
    get_price_history,
    get_basic_quote,
    get_news_timeline,
    get_options_context,
    get_schwab_fundamentals,
    get_last_earnings_event,
    get_probability_data,
    get_sector_etf,
    save_earnings_to_encyclopedia,
)

# Workspace path
WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Analysis output directory
ANALYSIS_DIR = WORKSPACE / "data" / "analysis"


def save_analysis_to_disk(result: Dict, ticker: str) -> Path:
    """
    Save full analysis result to disk.
    Path: data/analysis/YYYY-MM-DD/TICKER.json
    Overwrites same-day files.
    """
    from datetime import date
    import json

    today = date.today().isoformat()
    folder = ANALYSIS_DIR / today
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / f"{ticker.upper()}.json"

    with open(file_path, "w") as f:
        json.dump(result, f, indent=2)

    return file_path


def build_compact_response(result: Dict, ticker: str, file_path: Path) -> Dict:
    """
    Build compact response for chat session.
    Returns only summary info, not full analysis.
    """
    key_movement = result.get("key_movement", {})
    trade_desk = result.get("trade_desk_analysis", {})

    return {
        "ticker": ticker.upper(),
        "price_move": key_movement.get("magnitude"),
        "summary": trade_desk.get("trade_desk_summary"),
        "report_path": str(file_path)
    }


# =============================================================================
# ANALYSIS HELPERS
# =============================================================================

def identify_key_movement(price_timeline: List[Dict]) -> Dict:
    """Identify key price movement in data with multiple reference frames."""
    if len(price_timeline) < 2:
        return {"type": "unknown", "magnitude": 0}

    start_price = price_timeline[0]["price"]
    end_price = price_timeline[-1]["price"]
    overall_change = ((end_price - start_price) / start_price) * 100

    if abs(overall_change) > 15:
        move_type = "earnings spike" if overall_change > 0 else "major selloff"
    elif abs(overall_change) > 8:
        move_type = "strong momentum" if overall_change > 0 else "significant decline"
    elif abs(overall_change) > 3:
        move_type = "moderate move" if overall_change > 0 else "modest decline"
    else:
        move_type = "consolidation"

    # Compute multiple reference frame changes
    reference_frames = compute_price_references(price_timeline)

    return {
        "type": move_type,
        "magnitude": round(overall_change, 2),
        "reference_frames": reference_frames
    }


def compute_price_references(price_timeline: List[Dict]) -> Dict:
    """
    Compute price changes from multiple reference points.
    Returns: price_change_30d, price_change_90d, price_change_ytd, 
             price_from_52w_high, price_since_last_earnings
    """
    from datetime import date, timedelta
    
    if len(price_timeline) < 5:
        return {}
    
    # Sort by date
    sorted_timeline = sorted(price_timeline, key=lambda x: x.get("date", ""))
    
    current_price = sorted_timeline[-1]["price"]
    today = date.today()
    
    refs = {}
    
    # 30-day change
    if len(sorted_timeline) >= 30:
        price_30d_ago = sorted_timeline[-30]["price"]
        if price_30d_ago and price_30d_ago > 0:
            refs["price_change_30d"] = round(((current_price - price_30d_ago) / price_30d_ago) * 100, 1)
    
    # 90-day change (or max available)
    if len(sorted_timeline) >= 90:
        price_90d_ago = sorted_timeline[-90]["price"]
    else:
        price_90d_ago = sorted_timeline[0]["price"]
    
    if price_90d_ago and price_90d_ago > 0:
        refs["price_change_90d"] = round(((current_price - price_90d_ago) / price_90d_ago) * 100, 1)
    
    # YTD change
    try:
        year_start = date(today.year, 1, 1)
        for item in reversed(sorted_timeline):
            item_date = datetime.strptime(item.get("date", ""), "%Y-%m-%d").date()
            if item_date >= year_start:
                price_ytd = item["price"]
                if price_ytd and price_ytd > 0:
                    refs["price_change_ytd"] = round(((current_price - price_ytd) / price_ytd) * 100, 1)
                break
    except:
        pass
    
    # 52-week high
    try:
        one_year_ago = today - timedelta(days=365)
        prices_52w = [item["price"] for item in sorted_timeline 
                      if datetime.strptime(item.get("date", ""), "%Y-%m-%d").date() >= one_year_ago]
        if prices_52w:
            high_52w = max(prices_52w)
            if high_52w and high_52w > 0:
                refs["price_from_52w_high"] = round(((current_price - high_52w) / high_52w) * 100, 1)
    except:
        pass
    
    # Estimate price since last earnings (look for largest gap/move)
    # This is approximate - find biggest price swing
    if len(sorted_timeline) >= 10:
        max_price = max(item["price"] for item in sorted_timeline)
        min_price = min(item["price"] for item in sorted_timeline)
        # Use the move from recent low or high as proxy
        refs["price_since_recent_extreme"] = round(((current_price - min_price) / min_price) * 100, 1) if min_price > 0 else None
    
    return refs


def detect_price_based_event(price_timeline: List[Dict]) -> Optional[Dict]:
    """Fallback: detect large price movements."""
    if len(price_timeline) < 3:
        return None

    timeline = []
    for item in price_timeline:
        try:
            d = datetime.strptime(item.get("date", ""), "%Y-%m-%d")
            timeline.append((d, item.get("price")))
        except ValueError:
            continue

    if len(timeline) < 3:
        return None

    timeline.sort(key=lambda x: x[0])

    best_magnitude = 0
    best_date = None
    best_before = None
    best_after = None

    # Single-day moves
    for i in range(1, len(timeline)):
        date, price = timeline[i]
        before_price = timeline[i-1][1]

        if before_price and before_price > 0:
            magnitude = abs(price - before_price) / before_price * 100
            if magnitude > best_magnitude:
                best_magnitude = magnitude
                best_date = date
                best_before = before_price
                best_after = price

    # Two-day moves
    for i in range(2, len(timeline)):
        date, price = timeline[i]
        before_price = timeline[i-2][1]

        if before_price and before_price > 0:
            magnitude = abs(price - before_price) / before_price * 100
            if magnitude > best_magnitude:
                best_magnitude = magnitude
                best_date = date
                best_before = before_price
                best_after = price

    if best_magnitude >= 10 and best_date:
        return {
            "date": best_date.strftime("%Y-%m-%d"),
            "price_before": round(best_before, 2),
            "price_after": round(best_after, 2),
            "reaction_percent": round(best_magnitude, 2),
            "method": "price_spike_detection"
        }

    return None


def analyze_earnings_event(ticker: str, price_timeline: List[Dict]) -> Optional[Dict]:
    """Analyze earnings event from encyclopedia or price detection."""
    # Try encyclopedia first
    earnings = get_last_earnings_event(ticker)

    if not earnings:
        return detect_price_based_event(price_timeline)

    earnings_date = earnings.get("report_date")
    if not earnings_date:
        return detect_price_based_event(price_timeline)

    # Check if earnings date is in price timeline
    try:
        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
    except ValueError:
        return detect_price_based_event(price_timeline)

    timeline_dates = []
    for item in price_timeline:
        try:
            d = datetime.strptime(item.get("date", ""), "%Y-%m-%d")
            timeline_dates.append((d, item.get("price")))
        except ValueError:
            continue

    if not timeline_dates:
        return detect_price_based_event(price_timeline)

    timeline_dates.sort(key=lambda x: x[0])
    first_date = timeline_dates[0][0]
    last_date = timeline_dates[-1][0]

    if not (first_date <= earnings_dt <= last_date):
        return detect_price_based_event(price_timeline)

    # Find price before/after
    price_before = None
    for d, p in timeline_dates:
        if d < earnings_dt and (earnings_dt - d).days <= 3:
            price_before = p
            break

    price_after = None
    for d, p in timeline_dates:
        if d > earnings_dt and (d - earnings_dt).days <= 5:
            price_after = p
            break

    if price_before is None or price_after is None:
        return detect_price_based_event(price_timeline)

    reaction_percent = ((price_after - price_before) / price_before) * 100

    return {
        "report_date": earnings_date,
        "report_time": earnings.get("report_time", "UNKNOWN"),
        "expected_move": earnings.get("expected_move"),
        "price_before": price_before,
        "price_after": price_after,
        "reaction_percent": round(reaction_percent, 2),
        "is_earnings_driven": abs(reaction_percent) >= 10
    }


def technical_analysis(closes: List[float]) -> Dict:
    """Perform technical analysis on price data."""
    if len(closes) < 20:
        return {"trend": "neutral", "support_levels": [], "resistance_levels": []}

    current = closes[-1]
    sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current
    sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20

    recent_low = min(closes[-20:])
    recent_high = max(closes[-20:])

    if sma_20 > sma_50:
        trend = "bullish"
    elif sma_20 < sma_50:
        trend = "bearish"
    else:
        trend = "neutral"

    return {
        "support_levels": [round(recent_low, 2)],
        "resistance_levels": [round(recent_high, 2)],
        "trend": trend,
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2) if len(closes) >= 50 else None,
        "current_price": round(current, 2)
    }


def filter_material_events(news_items: List[Dict], ticker: str = "") -> List[Dict]:
    """
    Filter news for material events - company-specific only.
    
    Rules:
    - For CEO/Management news: require ticker in headline
    - For earnings/guidance news: allow if ticker in relatedTickers
    - Exclude generic market language
    """
    keyword_categories = {
        "sale": ["explores selling", "explores sale", "to sell", "for sale", "selling entire"],
        "acquisition": ["acquire", "acquisition", "buys", "purchase deal"],
        "earnings": ["earnings", "q1 ", "q2 ", "q3 ", "q4 ", "quarterly", "to report", "fiscal"],
        "guidance": ["guidance", "forecast", "outlook", "expects"],
        "downgrade": ["downgrade", "downgraded", "rating cut"],
        "upgrade": ["upgrade", "upgraded", "buy rating"],
        "ceo": ["ceo ", "chief executive", "new ceo", "executive"],
    }

    # Exclude generic market language
    exclude_keywords = [
        "what to watch", "Cramer", "opinion", "valuation",
        "tech stocks today", "market roundup", "AI sector", "chip stocks",
        "market update", "stocks to watch", "today's market", 
        "morning brief", "market pulse", "daily wrap"
    ]

    # Generic market phrases that require ticker to be first related ticker
    generic_phrases = [
        "tech stocks today", "market roundup", "AI sector", "chip stocks",
        "market update", "stocks to watch", "today's market",
        "morning brief", "market pulse", "daily wrap", "wall street",
        "stock market", "market rally", "market selloff", "trading day",
        "pre-market", "after hours", "market futures"
    ]
    
    ticker_upper = ticker.upper() if ticker else ""
    
    material = []
    for item in news_items:
        title = (item.get("title") or item.get("headline") or "").lower()
        title_upper = (item.get("title") or item.get("headline") or "")
        
        # Get related tickers from metadata
        related_tickers = item.get("relatedTickers", [])
        related_upper = [t.upper() for t in related_tickers] if related_tickers else []
        
        # Check if ticker mentioned in headline
        ticker_in_headline = ticker_upper in title_upper.upper() if ticker_upper else False
        
        # Get related tickers as set for faster lookup
        ticker_in_related = ticker_upper in related_upper if ticker_upper else True
        
        # Skip excluded keywords
        skip = False
        for ex in exclude_keywords:
            if ex.lower() in title:
                skip = True
                break
        if skip:
            continue
        
        # Check if headline contains generic market phrase
        has_generic_phrase = any(phrase in title for phrase in generic_phrases)
        if has_generic_phrase:
            # For generic headlines, require ticker to be FIRST related ticker
            if related_upper and ticker_upper != related_upper[0]:
                continue
            # Also require ticker in headline for generic headlines
            if not ticker_in_headline:
                continue

        # Check for material keywords and determine category
        matched_category = None
        for category, keywords in keyword_categories.items():
            for kw in keywords:
                if kw in title:
                    matched_category = category
                    break
            if matched_category:
                break
        
        if not matched_category:
            continue
        
        # For CEO/Management news, require ticker in headline (not just relatedTickers)
        if matched_category in ["ceo"]:
            if not ticker_in_headline:
                continue
        
        # For earnings news, require ticker in headline (not just relatedTickers)
        # This prevents market-wide earnings stories from being included
        if matched_category in ["earnings"]:
            if not ticker_in_headline:
                continue
        
        # For guidance/acquisition/sale news, allow if ticker in relatedTickers
        if matched_category in ["guidance", "acquisition", "sale"]:
            if not (ticker_in_headline or ticker_in_related):
                continue
        
        # For other categories, require ticker in headline or related
        if not (ticker_in_headline or ticker_in_related):
            continue
        
        material.append({
            "date": item.get("date"),
            "headline": item.get("title") or item.get("headline"),
            "reason": matched_category
        })

    return material[:5]


def get_analyst_activity(news_items: List[Dict]) -> List[Dict]:
    """Extract analyst signals from news."""
    keywords = {
        "upgrade": [" upgrade ", "upgraded to", "buy rating", "overweight"],
        "downgrade": [" downgrade ", "downgraded to", "sell rating", "underweight"],
        "price_target": ["price target", "pt ", "raises price target"],
    }

    exclude = ["what to watch", " Cramer ", "opinion"]

    activity = []
    for item in news_items:
        title = (item.get("title") or item.get("headline") or "").lower()

        skip = any(ex.lower() in title for ex in exclude)
        if skip:
            continue

        for atype, kws in keywords.items():
            for kw in kws:
                if kw in title:
                    activity.append({
                        "date": item.get("date"),
                        "headline": item.get("title") or item.get("headline"),
                        "type": atype
                    })
                    break

    return activity[:5]


# =============================================================================
# SECTOR RELATIVE PERFORMANCE
# =============================================================================

def compute_sector_relative_performance(data: Dict) -> Dict:
    """
    Compute sector-relative performance analysis.
    Uses existing price history function - no new APIs.
    """
    ticker = data.get("ticker", "").upper()
    sector_etf = data.get("sector_etf", "SPY")

    # Get 30-day price history for stock
    stock_timeline = get_price_history(ticker, days=30)

    if not stock_timeline or len(stock_timeline) < 5:
        return {
            "stock_return_30d": None,
            "sector_return_30d": None,
            "relative_performance": None,
            "interpretation": "insufficient data"
        }

    # Get 30-day price history for sector ETF
    sector_timeline = get_price_history(sector_etf, days=30)

    # Calculate stock return
    stock_start = stock_timeline[0].get("price")
    stock_end = stock_timeline[-1].get("price")

    if not stock_start or not stock_end or stock_start == 0:
        return {
            "stock_return_30d": None,
            "sector_return_30d": None,
            "relative_performance": None,
            "interpretation": "insufficient stock data"
        }

    stock_return_30d = ((stock_end - stock_start) / stock_start) * 100

    # Calculate sector return
    if sector_timeline and len(sector_timeline) >= 2:
        sector_start = sector_timeline[0].get("price")
        sector_end = sector_timeline[-1].get("price")

        if sector_start and sector_end and sector_start != 0:
            sector_return_30d = ((sector_end - sector_start) / sector_start) * 100
        else:
            sector_return_30d = 0.0
    else:
        sector_return_30d = 0.0

    # Relative performance
    relative_performance = stock_return_30d - sector_return_30d

    # Interpretation
    if relative_performance > 5:
        interpretation = "company-specific"
    elif relative_performance < -5:
        interpretation = "sector-driven"
    else:
        interpretation = "in-line with sector"

    return {
        "stock_return_30d": round(stock_return_30d, 2),
        "sector_return_30d": round(sector_return_30d, 2),
        "relative_performance": round(relative_performance, 2),
        "interpretation": interpretation,
        "sector_etf": sector_etf
    }


# =============================================================================
# PEER RELATIVE PERFORMANCE
# =============================================================================

def compute_peer_context(data: Dict) -> Dict:
    """
    Compute peer/sector-relative performance classification.
    Uses different thresholds than sector_context.
    """
    ticker = data.get("ticker", "").upper()
    sector_etf = data.get("sector_etf", "SPY")

    # Get 30-day price history
    stock_timeline = get_price_history(ticker, days=30)
    sector_timeline = get_price_history(sector_etf, days=30)

    if not stock_timeline or len(stock_timeline) < 5:
        return {"classification": "insufficient data"}

    # Stock return
    stock_start = stock_timeline[0].get("price")
    stock_end = stock_timeline[-1].get("price")
    if not stock_start or not stock_end or stock_start == 0:
        return {"classification": "insufficient stock data"}

    stock_return_30d = ((stock_end - stock_start) / stock_start) * 100

    # Sector return
    if sector_timeline and len(sector_timeline) >= 2:
        sector_start = sector_timeline[0].get("price")
        sector_end = sector_timeline[-1].get("price")
        if sector_start and sector_end and sector_start != 0:
            sector_return_30d = ((sector_end - sector_start) / sector_start) * 100
        else:
            sector_return_30d = 0.0
    else:
        sector_return_30d = 0.0

    relative_performance = stock_return_30d - sector_return_30d

    # Classification based on thresholds
    if abs(relative_performance) < 3:
        classification = "sector driven move"
    elif relative_performance < -5:
        classification = "company specific weakness"
    elif relative_performance > 5:
        classification = "company specific strength"
    else:
        classification = "in-line with sector"

    return {
        "stock_return_30d": round(stock_return_30d, 2),
        "sector_return_30d": round(sector_return_30d, 2),
        "relative_performance": round(relative_performance, 2),
        "classification": classification
    }


# =============================================================================
# EARNINGS REACTION INTERPRETATION
# =============================================================================

def compute_earnings_price_interpretation(data: Dict) -> Dict:
    """
    Interpret whether earnings reaction is consistent with earnings outcome.
    Uses material_events to detect earnings signal and compares to price movement.
    """
    material = data.get("material_events", [])
    key_movement = data.get("key_movement", {})

    # Find earnings-related events
    earnings_signal = None

    for event in material:
        reason = event.get("reason", "").lower()
        headline = event.get("headline", "").lower()

        # Determine earnings signal
        if "beat" in headline or "exceeds" in headline or "top" in headline:
            earnings_signal = "beat"
            break
        elif "miss" in headline or "below" in headline or "disappoint" in headline:
            earnings_signal = "miss"
            break
        elif "raises guidance" in headline or "raises outlook" in headline or "boosts outlook" in headline:
            earnings_signal = "guidance_raise"
            break
        elif "cuts guidance" in headline or "lowers outlook" in headline or "reduces outlook" in headline:
            earnings_signal = "guidance_cut"
            break

    if not earnings_signal:
        return {
            "earnings_signal": None,
            "price_move": None,
            "interpretation": "no earnings signal detected"
        }

    price_move = key_movement.get("magnitude", 0)

    # Interpret based on signal + price movement
    if earnings_signal == "beat" and price_move < 0:
        interpretation = "negative reaction to positive earnings (market questioning quality)"
    elif earnings_signal == "miss" and price_move > 0:
        interpretation = "positive reaction despite earnings miss (expectations were lower)"
    elif earnings_signal == "beat" and price_move > 0:
        interpretation = "earnings confirmation rally"
    elif earnings_signal == "miss" and price_move < 0:
        interpretation = "earnings disappointment confirmed"
    elif earnings_signal == "guidance_raise" and price_move > 0:
        interpretation = "guidance raise rewarded by market"
    elif earnings_signal == "guidance_raise" and price_move < 0:
        interpretation = "guidance raise rejected - other concerns outweigh"
    elif earnings_signal == "guidance_cut" and price_move < 0:
        interpretation = "guidance cut punished by market"
    elif earnings_signal == "guidance_cut" and price_move > 0:
        interpretation = "guidance cut absorbed - better than feared"
    else:
        interpretation = "earnings signal detected but price action unclear"

    return {
        "earnings_signal": earnings_signal,
        "price_move": round(price_move, 2),
        "interpretation": interpretation
    }


# =============================================================================
# CONTRADICTION DIAGNOSTICS
# =============================================================================

def compute_contradiction_diagnostics(data: Dict) -> Dict:
    """
    Detect contradictions between earnings signals and price movement.
    Triggered when positive signal + negative price OR negative signal + positive price.
    """
    earnings_price = data.get("earnings_price_interpretation", {})
    sector_context = data.get("sector_context", {})
    options_context = data.get("options_context", {})
    historical = data.get("historical_volatility", {})
    technical = data.get("technical_analysis", {})

    earnings_signal = earnings_price.get("earnings_signal")
    price_move = earnings_price.get("price_move", 0)

    # Check if contradiction exists
    contradiction_detected = False

    positive_signal = earnings_signal in ["beat", "guidance_raise"]
    negative_signal = earnings_signal in ["miss", "guidance_cut"]

    if positive_signal and price_move < -3:
        contradiction_detected = True
    elif negative_signal and price_move > 3:
        contradiction_detected = True

    if not contradiction_detected:
        return {
            "contradiction_detected": False,
            "possible_drivers": []
        }

    # Run diagnostics
    possible_drivers = []

    # 1. Sell-the-news check
    stock_return_30d = sector_context.get("stock_return_30d", 0) or 0
    if stock_return_30d > 10:
        possible_drivers.append("sell_the_news")

    # 2. Sector pressure
    sector_return_30d = sector_context.get("sector_return_30d", 0) or 0
    if sector_return_30d < -5:
        possible_drivers.append("sector_pressure")

    # 3. Elevated volatility
    implied_move = options_context.get("implied_move", 0) or 0
    median_move = historical.get("median_move", 0) or 0
    if median_move > 0 and implied_move > median_move * 2:
        possible_drivers.append("options_volatility_unwind")

    # 4. Technical momentum
    trend = technical.get("trend", "neutral")
    if trend == "bearish":
        possible_drivers.append("momentum_breakdown")

    return {
        "contradiction_detected": contradiction_detected,
        "possible_drivers": possible_drivers
    }


# =============================================================================
# EARNINGS EXPECTATION GAP ANALYSIS
# =============================================================================

def compute_earnings_expectation_gap(data: Dict) -> Dict:
    """
    Compute earnings expectation gap analysis.
    Compares actual price reaction to expected move.
    Uses historical_volatility.median_move as fallback if expected_move is None.
    """
    earnings_event = data.get("earnings_event", {})
    historical = data.get("historical_volatility", {})

    if not earnings_event:
        return {
            "expected_move": None,
            "actual_move": None,
            "surprise_factor": None,
            "expected_move_source": None,
            "interpretation": "no earnings data"
        }

    expected_move = earnings_event.get("expected_move")
    actual_move = earnings_event.get("reaction_percent")
    expected_move_source = None

    # Use historical median_move as fallback
    if expected_move is None and historical:
        median_move = historical.get("median_move")
        if median_move:
            expected_move = median_move * 100  # Convert from decimal to percent
            expected_move_source = "historical_proxy"

    if expected_move is None or actual_move is None:
        return {
            "expected_move": expected_move,
            "actual_move": actual_move,
            "surprise_factor": None,
            "expected_move_source": expected_move_source,
            "interpretation": "insufficient data"
        }

    # Calculate surprise factor (actual / expected)
    if expected_move > 0:
        surprise_factor = abs(actual_move) / expected_move
    else:
        surprise_factor = 1.0

    # Interpretation
    if surprise_factor > 3:
        interpretation = "extreme surprise"
    elif surprise_factor > 1.5:
        interpretation = "large surprise"
    else:
        interpretation = "normal reaction"

    return {
        "expected_move": round(expected_move, 2),
        "actual_move": round(actual_move, 2),
        "surprise_factor": round(surprise_factor, 2),
        "expected_move_source": expected_move_source or "options_implied",
        "interpretation": interpretation
    }


# =============================================================================
# TRADE DESK INTERPRETATION LAYER
# =============================================================================

def determine_dominant_driver(data: Dict) -> str:
    """
    Classify the stock into a dominant market regime.
    Uses only existing fields - no new API calls.

    Priority order (checked in sequence):
    1. post_earnings_reversal
    2. earnings_runup
    3. technical_breakdown
    4. sector_momentum
    5. volatility_event
    6. news_catalyst (only if ticker explicitly mentioned)
    """
    key_movement = data.get("key_movement", {})
    earnings_event = data.get("earnings_event", {})
    options_context = data.get("options_context", {})
    tech = data.get("technical_analysis", {})
    material = data.get("material_events", [])
    ticker = data.get("ticker", "").upper()

    magnitude = abs(key_movement.get("magnitude", 0))
    move_type = key_movement.get("type", "")
    trend = tech.get("trend", "neutral")
    implied = options_context.get("implied_move", 0) if options_context else 0

    # 1. post_earnings_reversal
    if earnings_event:
        reaction = earnings_event.get("reaction_percent", 0)
        # Large reaction that has reversed?
        if abs(reaction) > 20 and magnitude < abs(reaction) * 0.5:
            return "post_earnings_reversal"

    # 2. earnings_runup
    if implied > 15:
        return "earnings_runup"

    # 3. technical_breakdown
    if trend == "bearish" and magnitude > 10:
        return "technical_breakdown"

    # 4. sector_momentum
    if trend == "bullish" and magnitude > 5:
        return "sector_momentum"

    # 5. volatility_event
    if implied > 12:
        return "volatility_event"

    # 6. news_catalyst - ONLY if ticker explicitly mentioned in headline
    if material:
        for event in material:
            headline = event.get("headline", "").upper()
            # Must explicitly contain ticker symbol or company name pattern
            if ticker and ticker in headline:
                return "news_catalyst"

    return "neutral_consolidation"


def build_trade_desk_analysis(data: Dict) -> Dict:
    """
    Build interpretative trade desk analysis from existing data.
    Uses only fields already collected - no new API calls.
    """
    key_movement = data.get("key_movement", {})
    earnings_event = data.get("earnings_event", {})
    options_context = data.get("options_context", {})
    tech = data.get("technical_analysis", {})
    historical = data.get("historical_volatility", {})
    material = data.get("material_events", [])
    
    # Extract additional context for summary synthesis
    reaction_diagnostics = data.get("reaction_diagnostics", {})
    sector_context = data.get("sector_context", {})
    peer_context = data.get("peer_context", {})
    dominant_driver = data.get("dominant_driver", "neutral_consolidation")

    # --- movement_diagnosis ---
    move_type = key_movement.get("type", "unknown")
    magnitude = key_movement.get("magnitude", 0)

    if abs(magnitude) > 20:
        if magnitude > 0:
            movement_diagnosis = f"EXTREME RALLY: {magnitude:+.1f}% move - likely post-earnings spike or catalyst"
        else:
            movement_diagnosis = f"EXTREME CORRECTION: {magnitude:.1f}% decline - possible breakdown or negative catalyst"
    elif abs(magnitude) > 10:
        if magnitude > 0:
            movement_diagnosis = f"STRONG MOMENTUM: {magnitude:+.1f}% move - trending in direction of move"
        else:
            movement_diagnosis = f"SIGNIFICANT WEAKNESS: {magnitude:.1f}% decline - downtrend established"
    elif abs(magnitude) > 5:
        movement_diagnosis = f"MODERATE MOVE: {magnitude:+.1f}% - directional bias present"
    else:
        movement_diagnosis = f"RANGE BOUND: {magnitude:+.1f}% - consolidation phase"

    # --- sentiment_regime ---
    trend = tech.get("trend", "neutral")
    material = data.get("material_events", [])

    has_negative_news = any(e.get("reason") in ["sale", "layoffs", "bankruptcy", "downgrade"] for e in material)
    has_positive_news = any(e.get("reason") in ["acquisition", "upgrade"] for e in material)

    if trend == "bearish" and has_negative_news:
        sentiment_regime = "BEARISH REGIME: Downtrend + negative catalysts - avoid long exposure"
    elif trend == "bearish":
        sentiment_regime = "DEFENSIVE BIAS: Bearish technicals but no immediate catalyst"
    elif trend == "bullish" and has_positive_news:
        sentiment_regime = "BULLISH REGIME: Uptrend + positive catalysts - favorable for longs"
    elif trend == "bullish":
        sentiment_regime = "GROWTH BIAS: Bullish technicals but no clear catalyst"
    else:
        sentiment_regime = "NEUTRAL: No clear directional bias - wait for setup"

    # --- earnings_reaction_quality ---
    if earnings_event:
        reaction = earnings_event.get("reaction_percent", 0)
        method = earnings_event.get("method", "unknown")

        if method == "encyclopedia":
            if reaction > 15:
                earnings_reaction_quality = f"VOLATILE BEAT: {reaction:+.1f}% post-earnings move - high expectations mismatch"
            elif reaction > 5:
                earnings_reaction_quality = f"MODERATE REACTION: {reaction:+.1f}% - normal earnings response"
            elif reaction > -5:
                earnings_reaction_quality = f"FLAT RESPONSE: {reaction:+.1f}% - in-line with expectations"
            else:
                earnings_reaction_quality = f"MISS REACTION: {reaction:.1f}% - disappointed expectations"
        else:
            earnings_reaction_quality = f"PRICE-DETECTED EVENT: {reaction:+.1f}% move detected (no earnings data)"
    else:
        earnings_reaction_quality = "NO RECENT EARNINGS DATA"

    # --- csp_viability ---
    if options_context:
        implied = options_context.get("implied_move", 0)
        vol_comparison = options_context.get("volatility_comparison", "")

        down_1x = historical.get("down_1x", 0.5) or 0.5
        down_2x = historical.get("down_2x", 0.2) or 0.2

        if implied > 20:
            csp_viability = f"HIGH VOLATILITY: {implied:.0f}% implied - CSP requires wide strike"
        elif implied > 10:
            if "MORE" in vol_comparison:
                csp_viability = f"ELEVATED VOL: {implied:.0f}% implied vs historical - CSP pricing rich"
            elif "LESS" in vol_comparison:
                csp_viability = f"ATTRACTIVE VOL: {implied:.0f}% implied vs historical - CSP favorable"
            else:
                csp_viability = f"MODERATE VOL: {implied:.0f}% implied - standard CSP width"
        else:
            csp_viability = f"LOW VOLATILITY: {implied:.0f}% implied - narrow CSP possible"

        if down_2x > 0.8:
            csp_viability += f" | WARNING: {down_2x*100:.0f}% prob >50% loss"
        elif down_1x > 0.9:
            csp_viability += f" | ELEVATED RISK: {down_1x*100:.0f}% prob assignment"
    else:
        csp_viability = "NO OPTIONS DATA - cannot assess CSP"

    # --- trade_desk_summary ---
    # Generate regime-aware summary based on dominant driver
    ticker_symbol = data.get("ticker", "UNKNOWN")
    regime = determine_dominant_driver(data)

    if regime == "news_catalyst":
        # Reference actual event from material_events
        if material:
            # Get most recent material event
            latest_event = material[0]  # Already sorted newest first
            event_date = latest_event.get("date", "recently")
            event_headline = latest_event.get("headline", "material news")
            event_reason = latest_event.get("reason", "development")

            # Truncate headline if too long
            if len(event_headline) > 60:
                event_headline = event_headline[:57] + "..."

            trade_desk_summary = (
                f"On {event_date}, reports emerged that {ticker_symbol.upper()} is {event_reason}: \"{event_headline}\". "
                f"The stock has moved {magnitude:+.1f}% since as investors react to the development. "
                f"Assess the strategic implications before taking positions."
            )
        else:
            trade_desk_summary = (
                f"{ticker_symbol.upper()} is driven by material news. "
                f"The {magnitude:+.1f}% price move reflects immediate market reaction. "
                f"Wait for the news to settle before entering positions."
            )
    elif regime == "post_earnings_reversal":
        reaction = earnings_event.get("reaction_percent", 0) if earnings_event else 0
        trade_desk_summary = (
            f"{ticker_symbol.upper()} experienced a {reaction:+.1f}% earnings reaction that has since reversed. "
            f"Currently {magnitude:+.1f}% from the peak - the market has re-priced expectations. "
            f"Watch for mean reversion or continued weakness."
        )
    elif regime == "earnings_runup":
        implied = options_context.get("implied_move", 0) if options_context else 0
        trade_desk_summary = (
            f"{ticker_symbol.upper()} is in an earnings runup with {implied:.0f}% implied volatility. "
            f"Options are pricing a significant move. "
            f"Wait for post-earnings IV crush or take directional bets with defined risk."
        )
    elif regime == "technical_breakdown":
        trade_desk_summary = (
            f"{ticker_symbol.upper()} is in a technical breakdown, down {magnitude:.1f}% with bearish trend. "
            f"No fundamental catalyst identified - pure technical failure. "
            f"Short positions favored; avoid long exposure."
        )
    elif regime == "sector_momentum":
        trade_desk_summary = (
            f"{ticker_symbol.upper()} is riding sector momentum, up {magnitude:+.1f}% in a bullish trend. "
            f"Technicals support continued strength. "
            f"Momentum trades favored; watch for sector rotation."
        )
    elif regime == "volatility_event":
        implied = options_context.get("implied_move", 0) if options_context else 0
        trade_desk_summary = (
            f"{ticker_symbol.upper()} is experiencing elevated volatility at {implied:.0f}% implied move. "
            f"Price has moved {magnitude:+.1f}% but without clear fundamental driver. "
            f"Options are expensive - consider volatility arbitrage or wait for normalization."
        )
    else:  # neutral_consolidation
        trade_desk_summary = (
            f"{ticker_symbol.upper()} is in a {magnitude:+.1f}% consolidation phase with neutral technicals. "
            f"No clear catalyst or regime identified. "
            f"Wait for a clear setup before committing capital."
        )

    return {
        "movement_diagnosis": movement_diagnosis,
        "sentiment_regime": sentiment_regime,
        "earnings_reaction_quality": earnings_reaction_quality,
        "csp_viability": csp_viability,
        "trade_desk_summary": generate_trade_desk_summary(data)
    }


# =============================================================================
# NEW NARRATIVE GENERATION (Synthesized Summary)
# =============================================================================

def summarize_event(context: Dict) -> str:
    """
    Generate event description with earnings timing context.
    Returns one of:
    - "reports earnings this week/tomorrow/on [date]"
    - "reports earnings today" 
    - "recently reported earnings"
    - "moved following recent news developments." (only if material_events with reason exists)
    - "has been trading without a clear near-term catalyst."
    """
    from datetime import date, datetime
    
    ticker = context.get("ticker", "UNKNOWN")
    earnings_event = context.get("earnings_event", {})
    material_events = context.get("material_events", [])
    
    # Check if material_events has categorized catalysts (events with 'reason' field)
    has_news_catalyst = any(e.get("reason") for e in material_events)
    
    # First check: upcoming earnings from research pipeline (report field)
    report_info = context.get("report", {})
    if report_info:
        report_date_str = report_info.get("date")
        if report_date_str:
            try:
                report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
                today = date.today()
                days_until = (report_date - today).days
                
                if days_until > 0:
                    # Upcoming earnings - prioritize this over news
                    if days_until == 1:
                        return f"{ticker} reports earnings tomorrow."
                    elif days_until <= 7:
                        return f"{ticker} reports earnings this week."
                    else:
                        return f"{ticker} reports earnings on {report_date_str}."
                elif days_until == 0:
                    return f"{ticker} reports earnings today."
                else:
                    return f"{ticker} recently reported earnings."
            except (ValueError, TypeError):
                pass
    
    # Second check: detected earnings event from price analysis
    if earnings_event:
        report_date_str = earnings_event.get("report_date")
        if report_date_str:
            try:
                report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
                today = date.today()
                days_until = (report_date - today).days
                
                if days_until > 0:
                    if days_until == 1:
                        return f"{ticker} reports earnings tomorrow."
                    elif days_until <= 7:
                        return f"{ticker} reports earnings this week."
                    else:
                        return f"{ticker} reports earnings on {report_date_str}."
                elif days_until == 0:
                    return f"{ticker} reports earnings today."
                else:
                    return f"{ticker} recently reported earnings."
            except (ValueError, TypeError):
                pass
    
    # Only mention news if material_events has categorized catalysts
    if has_news_catalyst:
        return f"{ticker} moved following recent news developments."
    
    # No catalyst - return empty string to avoid redundancy
    return ""


def summarize_reaction(context: Dict) -> str:
    """
    Generate options expectations description.
    Compares implied_move vs historical_volatility.median_move.
    """
    options = context.get("options_context", {})
    historical = context.get("historical_volatility", {})
    
    implied = options.get("implied_move", 0)
    hist_median = historical.get("median_move", 0)
    
    # Convert historical from decimal to percentage if needed
    if hist_median and hist_median < 1:
        hist_median_pct = hist_median * 100
    else:
        hist_median_pct = hist_median
    
    if implied and implied > 0 and hist_median_pct and hist_median_pct > 0:
        if implied > hist_median_pct * 1.3:
            return f"Options imply a ~{implied:.0f}% move versus a historical median earnings move of ~{hist_median_pct:.0f}%."
        elif implied < hist_median_pct * 0.7:
            return f"Options imply a ~{implied:.0f}% move versus a historical median earnings move of ~{hist_median_pct:.0f}%."
        else:
            return f"Options pricing (~{implied:.0f}%) is roughly in line with historical median (~{hist_median_pct:.0f}%)."
    
    if implied and implied > 0:
        return f"Options imply a ~{implied:.0f}% move for the upcoming earnings event."
    
    return ""


def summarize_trend(context: Dict) -> str:
    """
    Generate trend context based on longer-term price movement.
    Uses specific reference frames (52w high, 90d, YTD) for precision.
    """
    key_movement = context.get("key_movement", {})
    tech = context.get("technical_analysis", {})
    
    magnitude = key_movement.get("magnitude", 0)
    reference_frames = key_movement.get("reference_frames", {})
    
    # Priority order for references:
    # 1. 52-week high (for severe drawdowns)
    # 2. 90-day change (for multi-month trends)
    # 3. YTD (for year-to-date performance)
    
    price_from_52w_high = reference_frames.get("price_from_52w_high")
    price_change_90d = reference_frames.get("price_change_90d")
    price_change_ytd = reference_frames.get("price_change_ytd")
    price_change_30d = reference_frames.get("price_change_30d")
    
    # Priority 1: If down >30% from 52w high, mention the drawdown
    if price_from_52w_high and price_from_52w_high < -30:
        return f"The stock is down roughly {abs(price_from_52w_high):.0f}% from its 52-week high."
    
    # Priority 2: If 90-day move is significant (>20%), mention it
    if price_change_90d and abs(price_change_90d) > 20:
        direction = "up" if price_change_90d > 0 else "down"
        return f"The stock has declined about {abs(price_change_90d):.0f}% over the past three months." if price_change_90d < 0 else f"The stock has rallied about {abs(price_change_90d):.0f}% over the past three months."
    
    # Priority 3: If down >10% from 52w high
    if price_from_52w_high and price_from_52w_high < -10:
        return f"The stock is down roughly {abs(price_from_52w_high):.0f}% from its 52-week high."
    
    # Priority 4: YTD performance if notable
    if price_change_ytd and abs(price_change_ytd) > 10:
        direction = "up" if price_change_ytd > 0 else "down"
        return f"The stock is {direction} roughly {abs(price_change_ytd):.0f}% year-to-date."
    
    # Priority 5: 30-day move if notable
    if price_change_30d and abs(price_change_30d) > 10:
        direction = "up" if price_change_30d > 0 else "down"
        return f"The stock has moved {direction} about {abs(price_change_30d):.0f}% over the past 30 days."
    
    # Fallback to generic description for smaller moves
    if magnitude < -10:
        return f"The stock has been drifting lower in recent weeks."
    elif magnitude > 10:
        return f"The stock has been trending higher in recent weeks."
    elif magnitude >= 3:
        direction = "up" if magnitude > 0 else "down"
        return f"Shares have moved modestly {direction} in recent weeks."
    
    return "The price action has been relatively stable."


def interpret_move(context: Dict) -> str:
    """Generate interpretation combining implied volatility + trend + sector context."""
    options = context.get("options_context", {})
    historical = context.get("historical_volatility", {})
    tech = context.get("technical_analysis", {})
    sector_ctx = context.get("sector_context", {})
    
    implied = options.get("implied_move", 0)
    hist_median = historical.get("median_move", 0)
    
    if hist_median and hist_median < 1:
        hist_median_pct = hist_median * 100
    else:
        hist_median_pct = hist_median
    
    trend = tech.get("trend", "neutral")
    
    # Build interpretation based on implied vs historical
    if implied and implied > 0 and hist_median_pct and hist_median_pct > 0:
        ratio = implied / hist_median_pct
        if ratio > 1.3:
            vol_interpretation = "Elevated implied volatility suggests earnings risk is being priced aggressively."
        elif ratio < 0.7:
            vol_interpretation = "Options pricing suggests lower-than-normal earnings risk."
        else:
            vol_interpretation = "Implied volatility is roughly in line with historical norms."
    else:
        vol_interpretation = ""
    
    # Add trend context
    if trend == "bearish":
        trend_interpretation = " Technicals remain bearish."
    elif trend == "bullish":
        trend_interpretation = " Technicals remain bullish."
    else:
        trend_interpretation = ""
    
    # Add sector context
    sector_interp = sector_ctx.get("interpretation", "")
    
    parts = [p for p in [vol_interpretation, trend_interpretation, sector_interp] if p]
    return " ".join(parts)


def interpret_move(context: Dict) -> str:
    """Synthesize interpretation from diagnostics and context."""
    diagnostics = context.get("reaction_diagnostics", {})
    classification = context.get("peer_context", {}).get("classification")
    trend = context.get("technical_analysis", {}).get("trend")
    
    # Priority 1: Check for contradiction diagnostics
    if diagnostics.get("contradiction_detected"):
        return "Despite mixed signals across catalysts and price action, the market response suggests uncertainty in investor expectations."
    
    # Priority 2: Check peer_context classification
    if classification == "company specific weakness":
        return "The move appears driven by company-specific weakness rather than sector pressure."
    if classification == "company specific strength":
        return "The move appears driven by company-specific strength rather than broader sector momentum."
    if classification == "sector driven move":
        return "The price action appears consistent with broader sector weakness."
    
    # Priority 3: Fallback to sector_context interpretation
    sector_context = context.get("sector_context", {})
    sector_interpretation = sector_context.get("interpretation")
    if sector_interpretation:
        return sector_interpretation
    
    # Priority 4: Technical trend fallback
    if trend == "bearish":
        return "The decline reinforces an existing bearish momentum trend."
    if trend == "bullish":
        return "The move aligns with the broader bullish trend."
    
    return "Price action does not currently point to a clear structural driver."


def trade_implication(context: Dict) -> str:
    """Generate trade implication based on trend."""
    trend = context.get("technical_analysis", {}).get("trend")
    
    if trend == "bearish":
        return "Until momentum stabilizes, downside risk likely remains elevated."
    if trend == "bullish":
        return "The broader trend remains constructive despite recent volatility."
    
    return "Further price stabilization will be needed before a clear directional bias emerges."


def detect_positioning_effects(context: Dict) -> Optional[str]:
    """Detect positioning effects such as volatility crush or sell-the-news."""
    options = context.get("options_context", {})
    earnings = context.get("earnings_context", {})
    key_movement = context.get("key_movement", {})
    
    implied_move = options.get("implied_move")
    iv = options.get("atm_iv")
    actual_move = abs(key_movement.get("magnitude", 0))
    
    if not implied_move:
        return None
    
    ratio = actual_move / implied_move if implied_move else None
    
    # Check for muted reaction despite elevated IV (volatility crush)
    if ratio and ratio < 0.6 and iv and iv > 12:
        return "The muted reaction despite elevated pre-earnings volatility suggests positioning unwind following the event."
    
    # Check for outsized reaction with elevated IV (under-positioned)
    if ratio and ratio > 1.5 and iv and iv > 12:
        return "The outsized reaction relative to implied expectations suggests investors were under-positioned for the move."
    
    # Check for muted reaction after earnings
    earnings_event = earnings.get("earnings_event") if earnings else None
    if earnings_event and ratio and actual_move < implied_move * 0.7:
        return "Despite the earnings catalyst, the price reaction was muted relative to expectations."
    
    return None


def generate_trade_desk_summary(context: Dict) -> str:
    """Generate synthesized trade desk summary from diagnostics."""
    # Combine interpretation with positioning detection
    interpretation = interpret_move(context)
    positioning = detect_positioning_effects(context)
    if positioning:
        interpretation = interpretation + " " + positioning
    
    parts = [
        summarize_event(context),
        summarize_reaction(context),
        summarize_trend(context),
        interpret_move(context),
        trade_implication(context)
    ]
    
    # Filter out empty parts to avoid redundancy
    parts = [p for p in parts if p]
    
    return " ".join(parts)


# =============================================================================
# MAIN ANALYSIS FUNCTIONS
# =============================================================================

def analyze_single(ticker: str, save_to_disk: bool = True) -> Dict:
    """
    Perform full analysis on a single ticker.
    Returns comprehensive analysis dict.
    
    Args:
        ticker: Stock ticker symbol
        save_to_disk: If True, save analysis to disk and return compact response.
                      If False, return full analysis dict (used by analyze_batch).
    """
    ticker = ticker.upper()

    # 1. Get price history
    price_timeline = get_price_history(ticker, days=90)

    if not price_timeline:
        return {"error": "Could not fetch price data", "ticker": ticker}

    # 2. Get options context
    options_context = get_options_context(ticker)
    if options_context is None:
        options_context = {}

    # 3. Get historical volatility
    historical = get_probability_data(ticker)
    if historical is None:
        historical = {}

    # 4. Add volatility comparison
    if options_context and historical:
        implied = options_context.get("implied_move", 0)
        hist_median = historical.get("median_move", 0) * 100 if historical.get("median_move") else 0

        if implied and hist_median:
            ratio = implied / hist_median
            if ratio > 1.2:
                comp = f"Options market pricing {ratio:.0%} MORE volatility than historical ({hist_median:.1f}%)"
            elif ratio < 0.8:
                comp = f"Options market pricing {ratio:.0%} LESS volatility than historical ({hist_median:.1f}%)"
            else:
                comp = f"Options market pricing IN LINE with historical ({hist_median:.1f}%)"
            options_context["volatility_comparison"] = comp

    # 5. Get news
    news = get_news_timeline(ticker)
    material_events = filter_material_events(news, ticker)
    analyst_activity = get_analyst_activity(news)

    # 6. Get fundamentals
    fundamentals = get_schwab_fundamentals(ticker)

    # 7. Analyze price movement
    closes = [item["price"] for item in price_timeline]
    key_movement = identify_key_movement(price_timeline)
    tech_analysis = technical_analysis(closes)
    earnings_event = analyze_earnings_event(ticker, price_timeline)

    # 7b. Save earnings event to encyclopedia if detected via price
    if earnings_event and earnings_event.get("method") == "price_spike_detection":
        # Only save if it has significant reaction
        reaction = earnings_event.get("reaction_percent", 0)
        if abs(reaction) > 10:
            save_earnings_to_encyclopedia(earnings_event, ticker, source="price_detection")

    # 8. Sector comparison
    sector_etf = get_sector_etf(ticker)

    # 9. Compute sector relative performance
    sector_data = {
        "ticker": ticker,
        "sector_etf": sector_etf
    }
    sector_context = compute_sector_relative_performance(sector_data)

    # 10. Compute peer context
    peer_data = {
        "ticker": ticker,
        "sector_etf": sector_etf
    }
    peer_context = compute_peer_context(peer_data)

    # 11. Compute earnings expectation gap
    earnings_data = {
        "earnings_event": earnings_event,
        "historical_volatility": historical
    }
    earnings_context = compute_earnings_expectation_gap(earnings_data)

    # 11b. Compute earnings price interpretation
    earnings_price_data = {
        "material_events": material_events,
        "key_movement": key_movement
    }
    earnings_price_interpretation = compute_earnings_price_interpretation(earnings_price_data)

    # 11c. Compute contradiction diagnostics
    contradiction_data = {
        "earnings_price_interpretation": earnings_price_interpretation,
        "sector_context": sector_context,
        "options_context": options_context,
        "historical_volatility": historical,
        "technical_analysis": tech_analysis
    }
    reaction_diagnostics = compute_contradiction_diagnostics(contradiction_data)

    # 12. Build trade desk analysis
    analysis_data = {
        "ticker": ticker,
        "key_movement": key_movement,
        "earnings_event": earnings_event,
        "options_context": options_context,
        "technical_analysis": tech_analysis,
        "historical_volatility": historical,
        "material_events": material_events,
        "reaction_diagnostics": reaction_diagnostics,
        "sector_context": sector_context,
        "peer_context": peer_context,
        "dominant_driver": determine_dominant_driver({
            "ticker": ticker,
            "key_movement": key_movement,
            "earnings_event": earnings_event,
            "options_context": options_context,
            "technical_analysis": tech_analysis,
            "material_events": material_events
        })
    }
    trade_desk_analysis = build_trade_desk_analysis(analysis_data)

    # Build full result
    full_result = {
        "ticker": ticker,
        "analysis_date": datetime.now().isoformat(),
        "price_timeline": price_timeline[-30:],
        "key_movement": key_movement,
        "earnings_event": earnings_event,
        "options_context": options_context,
        "historical_volatility": historical,
        "fundamentals": fundamentals,
        "news_timeline": news[:20],
        "material_events": material_events,
        "analyst_activity": analyst_activity,
        "technical_analysis": tech_analysis,
        "sector_etf": sector_etf,
        "sector_context": sector_context,
        "peer_context": peer_context,
        "earnings_context": earnings_context,
        "earnings_price_interpretation": earnings_price_interpretation,
        "trade_desk_analysis": trade_desk_analysis
    }

    # Save to disk if requested (for CLI usage), otherwise caller handles it
    if save_to_disk:
        file_path = save_analysis_to_disk(full_result, ticker)
        return build_compact_response(full_result, ticker, file_path)
    
    return full_result


def analyze_batch(tickers: List[str], candidates: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Perform analysis on a batch of tickers.
    Used by run_pipeline.py
    
    Args:
        tickers: List of ticker symbols
        candidates: Optional list of candidate dicts with original fields (market, options, report)
                   If provided, these fields are preserved in the output for downstream consumers.
    """
    # Build lookup for original candidate data
    candidate_lookup = {}
    if candidates:
        for c in candidates:
            ticker = c.get("ticker", "").upper()
            candidate_lookup[ticker] = c
    
    results = []

    for ticker in tickers:
        try:
            result = analyze_single(ticker, save_to_disk=False)
            
            # Preserve original candidate fields for pipeline compatibility
            if ticker.upper() in candidate_lookup:
                original = candidate_lookup[ticker.upper()]
                # Keep fields needed by bob_research_overlay.py
                if "market" in original:
                    result["market"] = original["market"]
                if "options" in original:
                    result["options"] = original["options"]
                if "report" in original:
                    result["report"] = original["report"]
                if "sector_etf" in original:
                    result["sector_etf"] = original["sector_etf"]
                # Preserve any other top-level fields from original
                for key in original:
                    if key not in result and key != "ticker":
                        result[key] = original[key]
                
                # Save to disk AFTER adding preserved fields
                file_path = save_analysis_to_disk(result, ticker)
                result["report_path"] = str(file_path)
            
            results.append(result)
        except Exception as e:
            results.append({
                "ticker": ticker.upper(),
                "error": str(e)
            })

    return results
