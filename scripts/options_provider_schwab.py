#!/usr/bin/env python3
"""
Schwab Options Provider

Fetches options chains from Schwab API.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime, date

# Add workspace to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
from scripts.token_manager import get_access_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schwab API configuration
SCHWAB_OPTIONS_URL = "https://api.schwabapi.com/marketdata/v1/chains"


def fetch_options_chain(symbol: str):
    """
    Fetch options chain for a given symbol from Schwab API.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'INTU')
        
    Returns:
        JSON response dict or None if failed
    """
    logger.info(f"OPTIONS: Fetching chain for {symbol}")
    
    try:
        # Get fresh access token
        access_token = get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "symbol": symbol,
            "includeQuotes": "true"
        }
        
        response = requests.get(SCHWAB_OPTIONS_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            logger.error(f"OPTIONS: Failed - Status {response.status_code}: {response.text}")
            return None
        
        logger.info("OPTIONS: Success")
        return response.json()
        
    except Exception as e:
        logger.error(f"OPTIONS: Failed - {str(e)}")
        return None


def select_earnings_expiration(chain_json: dict, earnings_date: str):
    """
    Select the best expiration date for an earnings play.
    
    Args:
        chain_json: Response from fetch_options_chain
        earnings_date: String in format 'YYYY-MM-DD'
        
    Returns:
        Expiration date string (YYYY-MM-DD) or None if no valid expiration
    """
    if not chain_json or "callExpDateMap" not in chain_json:
        logger.warning("OPTIONS: No valid expiration found - no chain data")
        return None
    
    # Parse earnings date
    try:
        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d").date()
    except ValueError:
        logger.warning("OPTIONS: No valid expiration found - invalid earnings date format")
        return None
    
    # Extract expiration dates from callExpDateMap keys
    # Keys look like: "2026-02-27:0", "2026-03-06:7"
    valid_expirations = []
    
    for key in chain_json["callExpDateMap"].keys():
        try:
            # Split key into date and DTE
            exp_str, dte_str = key.split(":")
            exp_dt = datetime.strptime(exp_str, "%Y-%m-%d").date()
            dte = int(dte_str)
            
            # Keep only expirations where: expiration >= earnings_date AND dte > 0
            if exp_dt >= earnings_dt and dte > 0:
                valid_expirations.append((exp_dt, exp_str))
        except (ValueError, IndexError):
            continue
    
    if not valid_expirations:
        logger.warning("OPTIONS: No valid expiration found")
        return None
    
    # Sort by expiration date ascending and return the first
    valid_expirations.sort(key=lambda x: x[0])
    selected = valid_expirations[0][1]
    
    logger.info(f"OPTIONS: Selected expiration {selected}")
    return selected


def select_atm_strike(chain_json: dict, expiration: str):
    """
    Select the ATM (at-the-money) strike price.
    
    Args:
        chain_json: Response from fetch_options_chain
        expiration: Expiration date string (YYYY-MM-DD)
        
    Returns:
        ATM strike as float, or None if not found
    """
    if not chain_json or "callExpDateMap" not in chain_json:
        logger.warning("OPTIONS: No ATM strike found - no chain data")
        return None
    
    # Get underlying price
    underlying_price = chain_json.get("underlyingPrice")
    if not underlying_price:
        logger.warning("OPTIONS: No ATM strike found - no underlying price")
        return None
    
    # Find the expiration map key
    exp_key = None
    for key in chain_json["callExpDateMap"].keys():
        if key.startswith(f"{expiration}:"):
            exp_key = key
            break
    
    if not exp_key:
        logger.warning(f"OPTIONS: No ATM strike found - expiration {expiration} not in chain")
        return None
    
    # Get strikes for this expiration from both call and put maps
    call_exp_map = chain_json["callExpDateMap"][exp_key]
    put_exp_map = chain_json.get("putExpDateMap", {}).get(exp_key, {})
    
    if not call_exp_map:
        logger.warning(f"OPTIONS: No ATM strike found - empty expiration map")
        return None
    
    # Collect all strikes with their distance from underlying
    strikes_with_diff = []
    for strike_str in call_exp_map.keys():
        try:
            strike = float(strike_str)
            diff = abs(strike - underlying_price)
            strikes_with_diff.append((diff, strike, strike_str))
        except ValueError:
            continue
    
    if not strikes_with_diff:
        logger.warning("OPTIONS: No ATM strike found - could not parse strikes")
        return None
    
    # Sort by distance from underlying
    strikes_with_diff.sort(key=lambda x: x[0])
    
    # Find first strike that passes liquidity check
    atm_strike = None
    atm_strike_str = None
    
    for diff, strike, strike_str in strikes_with_diff:
        # Get call and put data for this strike
        call_data = call_exp_map.get(strike_str)
        put_data = put_exp_map.get(strike_str) if put_exp_map else None
        
        if not call_data or not put_data:
            logger.info(f"OPTIONS: Liquidity check failed for strike {strike} - no data")
            continue
        
        call_option = call_data[0] if call_data else {}
        put_option = put_data[0] if put_data else {}
        
        # Check liquidity conditions
        call_bid = call_option.get("bid", 0) or 0
        put_bid = put_option.get("bid", 0) or 0
        call_ask = call_option.get("ask", 0) or 0
        put_ask = put_option.get("ask", 0) or 0
        call_oi = call_option.get("openInterest", 0) or 0
        put_oi = put_option.get("openInterest", 0) or 0
        
        if call_bid > 0 and put_bid > 0 and call_ask > 0 and put_ask > 0 and call_oi >= 50 and put_oi >= 50:
            atm_strike = strike
            atm_strike_str = strike_str
            logger.info(f"OPTIONS: Liquidity confirmed at strike {strike}")
            break
        else:
            logger.info(f"OPTIONS: Liquidity check failed for strike {strike}")
    
    if atm_strike is None:
        logger.warning("OPTIONS: No liquid ATM found")
        return None
    
    logger.info(f"OPTIONS: Selected ATM strike {atm_strike}")
    return atm_strike


def compute_atm_straddle(chain_json: dict, expiration: str, atm_strike: float):
    """
    Compute ATM straddle and expected move percentage.
    
    Args:
        chain_json: Response from fetch_options_chain
        expiration: Expiration date string (YYYY-MM-DD)
        atm_strike: ATM strike price
        
    Returns:
        Dict with straddle, em_percent, call_mark, put_mark or None if failed
    """
    if not chain_json:
        logger.warning("OPTIONS: No straddle computed - no chain data")
        return None
    
    underlying_price = chain_json.get("underlyingPrice")
    if not underlying_price:
        logger.warning("OPTIONS: No straddle computed - no underlying price")
        return None
    
    # Find expiration key in call and put maps
    call_key = None
    put_key = None
    
    for key in chain_json.get("callExpDateMap", {}).keys():
        if key.startswith(f"{expiration}:"):
            call_key = key
            break
    
    for key in chain_json.get("putExpDateMap", {}).keys():
        if key.startswith(f"{expiration}:"):
            put_key = key
            break
    
    if not call_key or not put_key:
        logger.warning("OPTIONS: No straddle computed - expiration not found in chain")
        return None
    
    # Get strike entry (strike is stored as string like "410.0")
    strike_str = str(atm_strike)
    
    call_data = chain_json["callExpDateMap"][call_key].get(strike_str)
    put_data = chain_json["putExpDateMap"][put_key].get(strike_str)
    
    if not call_data or not put_data:
        logger.warning("OPTIONS: No straddle computed - strike not found in chain")
        return None
    
    # Extract marks
    call_mark = call_data[0].get("mark")
    put_mark = put_data[0].get("mark")
    
    if call_mark is None or put_mark is None:
        logger.warning("OPTIONS: No straddle computed - no mark price available")
        return None
    
    # Compute straddle and EM%
    straddle = call_mark + put_mark
    em_percent = (straddle / underlying_price) * 100
    print(f"DEBUG EM: straddle={straddle}, price={underlying_price}, em_percent={em_percent}")
    
    logger.info(f"OPTIONS: Call mark {call_mark}")
    logger.info(f"OPTIONS: Put mark {put_mark}")
    logger.info(f"OPTIONS: Straddle {straddle}")
    logger.info(f"OPTIONS: EM% {em_percent:.2f}%")
    
    return {
        "straddle": straddle,
        "em_percent": em_percent,
        "call_mark": call_mark,
        "put_mark": put_mark
    }


def get_earnings_snapshot(symbol: str, earnings_date: str) -> dict:
    """
    Get a complete earnings snapshot for a symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'INTU')
        earnings_date: Earnings date string (YYYY-MM-DD)
        
    Returns:
        Dict with price, expiration, atm_strike, straddle, em_percent, liquidity_ok, dte
        or {"status": "options_unavailable"} if failed
    """
    logger.info(f"OPTIONS: Snapshot complete")
    
    # Fetch chain
    chain = fetch_options_chain(symbol)
    if chain is None:
        logger.warning("OPTIONS: Snapshot failed - no options chain")
        return {"status": "options_unavailable"}
    
    # Select expiration
    expiration = select_earnings_expiration(chain, earnings_date)
    if expiration is None:
        logger.warning("OPTIONS: Snapshot failed - no valid expiration")
        return {"status": "options_unavailable"}
    
    # Select liquid ATM strike
    atm_strike = select_atm_strike(chain, expiration)
    if atm_strike is None:
        logger.warning("OPTIONS: Snapshot failed - no liquid ATM strike")
        return {"status": "options_unavailable"}
    
    # Compute straddle + EM
    straddle_data = compute_atm_straddle(chain, expiration, atm_strike)
    if straddle_data is None:
        logger.warning("OPTIONS: Snapshot failed - could not compute straddle")
        return {"status": "options_unavailable"}
    
    # Extract DTE from expiration key
    dte = 0
    for key in chain.get("callExpDateMap", {}).keys():
        if key.startswith(f"{expiration}:"):
            try:
                dte = int(key.split(":")[1])
            except (IndexError, ValueError):
                dte = 0
            break
    
    return {
        "price": chain.get("underlyingPrice"),
        "expiration": expiration,
        "atm_strike": atm_strike,
        "straddle": straddle_data["straddle"],
        "em_percent": straddle_data["em_percent"],
        "liquidity_ok": True,
        "dte": dte
    }


if __name__ == "__main__":
    # Test the full snapshot function
    snapshot = get_earnings_snapshot("INTU", "2026-02-26")
    print("Snapshot:", snapshot)
