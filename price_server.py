# FastAPI Price Server - Data Driven Multi-API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import time

app = FastAPI(title="Mission Control Price API")

# Enable CORS for GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/portfolio/data")
HOLDINGS_FILE = os.path.join(DATA_DIR, "holdings.json")
CACHE_FILE = os.path.join(DATA_DIR, "price_cache.json")

# API Keys from environment
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")

# Cache settings
CACHE_DURATION = 60

def load_holdings() -> Dict:
    try:
        with open(HOLDINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading holdings: {e}")
        return {"accounts": []}

def get_portfolio_tickers() -> Dict[str, List[str]]:
    data = load_holdings()
    stocks = set()
    crypto = set()
    
    for account in data.get('accounts', []):
        for stock in account.get('stocks_etfs', []):
            ticker = stock.get('Ticker', '').strip().upper()
            if ticker and ticker not in ['CASH', 'SGOV']:
                stocks.add(ticker)
        
        for opt in account.get('options', []):
            ticker = opt.get('Ticker', '').strip().upper()
            if ticker:
                stocks.add(ticker)
        
        for misc in account.get('misc', []):
            if misc.get('Type', '').upper() == 'CRYPTO':
                asset = misc.get('Asset', '').strip().upper()
                if asset:
                    crypto.add(asset)
    
    return {"stocks": sorted(list(stocks)), "crypto": sorted(list(crypto))}

def fetch_finnhub(tickers: List[str]) -> Dict[str, Dict]:
    results = {}
    if not FINNHUB_KEY:
        return results
    
    for ticker in tickers:
        try:
            response = requests.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": ticker},
                headers={"X-Finnhub-Token": FINNHUB_KEY},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('c'):
                    results[ticker] = {
                        "price": data['c'],
                        "change": data.get('d', 0),
                        "change_percent": data.get('dp', 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "finnhub"
                    }
        except Exception as e:
            print(f"Error fetching {ticker} from Finnhub: {e}")
    return results

def fetch_yahoo(tickers: List[str]) -> Dict[str, Dict]:
    results = {}
    for ticker in tickers:
        try:
            response = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                params={"interval": "1d", "range": "1d"},
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                data = response.json()
                meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price:
                    prev_close = meta.get("previousClose", price)
                    change = price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    results[ticker] = {
                        "price": price,
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2),
                        "timestamp": datetime.now().isoformat(),
                        "source": "yahoo"
                    }
        except Exception as e:
            print(f"Error fetching {ticker} from Yahoo: {e}")
    return results

def fetch_coingecko(cryptos: List[str]) -> Dict[str, Dict]:
    results = {}
    if not cryptos:
        return results
    
    ticker_to_id = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "ADA": "cardano", "DOT": "polkadot", "AVAX": "avalanche-2",
        "MATIC": "matic-network", "LINK": "chainlink"
    }
    
    ids = [ticker_to_id.get(c, c.lower()) for c in cryptos]
    
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ",".join(ids), "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            for crypto in cryptos:
                cg_id = ticker_to_id.get(crypto, crypto.lower())
                if cg_id in data:
                    results[crypto] = {
                        "price": data[cg_id].get("usd"),
                        "change_24h_percent": data[cg_id].get("usd_24h_change", 0),
                        "timestamp": datetime.now().isoformat(),
                        "source": "coingecko"
                    }
    except Exception as e:
        print(f"Error fetching from CoinGecko: {e}")
    return results

def save_cache(prices: Dict):
    try:
        cache_data = {"timestamp": datetime.now().isoformat(), "prices": prices}
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        cache_time = datetime.fromisoformat(cache["timestamp"])
        age = (datetime.now() - cache_time).total_seconds()
        if age < CACHE_DURATION:
            return cache["prices"]
    except:
        pass
    return None

@app.get("/")
def root():
    return {"name": "Mission Control Price API", "version": "1.0"}

@app.get("/health")
def health_check():
    tickers = get_portfolio_tickers()
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "stocks": len(tickers["stocks"]),
        "crypto": len(tickers["crypto"]),
        "finnhub_configured": bool(FINNHUB_KEY)
    }

@app.get("/api/tickers")
def list_tickers():
    return get_portfolio_tickers()

@app.get("/api/prices")
def get_all_prices(force_refresh: bool = False):
    if not force_refresh:
        cached = load_cache()
        if cached:
            return {"cached": True, "timestamp": datetime.now().isoformat(), "prices": cached}
    
    tickers = get_portfolio_tickers()
    results = {"stocks": {}, "crypto": {}, "timestamp": datetime.now().isoformat(), "cached": False}
    
    if tickers["stocks"]:
        finnhub_results = fetch_finnhub(tickers["stocks"])
        results["stocks"].update(finnhub_results)
        
        missing = set(tickers["stocks"]) - set(finnhub_results.keys())
        if missing:
            yahoo_results = fetch_yahoo(list(missing))
            results["stocks"].update(yahoo_results)
    
    if tickers["crypto"]:
        crypto_results = fetch_coingecko(tickers["crypto"])
        results["crypto"].update(crypto_results)
    
    save_cache(results)
    return results

@app.get("/api/prices/{ticker}")
def get_single_price(ticker: str):
    ticker = ticker.strip().upper()
    
    results = fetch_finnhub([ticker])
    if ticker in results:
        return results[ticker]
    
    results = fetch_yahoo([ticker])
    if ticker in results:
        return results[ticker]
    
    results = fetch_coingecko([ticker])
    if ticker in results:
        return results[ticker]
    
    raise HTTPException(status_code=404, detail=f"Price not found for {ticker}")

@app.post("/api/refresh")
def refresh_all_prices():
    return get_all_prices(force_refresh=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
