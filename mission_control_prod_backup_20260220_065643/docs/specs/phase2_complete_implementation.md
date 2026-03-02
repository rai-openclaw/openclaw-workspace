# Technical Design Spec: Mission Control Portfolio v2.0 - Complete Implementation

**Version:** 2.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Overview

Complete implementation of portfolio tracking system with:
- Clean data model (v2 format)
- Manual price refresh only
- Account attribution for ALL sections
- Yahoo Finance fallback for mutual funds
- Clear UI indicators for data quality

---

## 1. Data Model

### Source File: `portfolio/unified_portfolio_tracker.md`

Format already created in Phase 1. Key structure:

```markdown
## Account: Robinhood
### Stocks & ETFs
| Ticker | Shares | Cost Basis | Notes |
|--------|--------|------------|-------|
| RKT    | 1,400  | $18,435    |       |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| PYPL   | PUT  | $45.00 | 2026-02-20 | -10       | $4.50         |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis | Category        |
|-------|----------|------------|-----------------|
| Cash  | $11,432  | —          | cash            |
| SGOV  | 201.20   | $20,224.62 | cash_equivalent |

### Misc
| Asset | Amount | Type   | Cost Basis |
|-------|--------|--------|------------|
| ETH   | 11.43  | crypto | $28,575    |
```

**Note:** Added `Category` column to Cash section for filtering.

---

## 2. Price Cache System

### File: `portfolio/price_cache.json`

```json
{
  "version": "2.0",
  "last_updated": "2026-02-15T20:00:00Z",
  "prices": {
    "RKT": {
      "price": 18.68,
      "name": "Rocket Companies",
      "source": "finnhub",
      "last_updated": "2026-02-15T20:00:00Z"
    },
    "VSEQX": {
      "price": 39.46,
      "name": "Vanguard Extended Market",
      "source": "cached",
      "note": "Manual update required - Yahoo Finance unavailable",
      "last_updated": "2026-02-15T20:00:00Z"
    },
    "ETH": {
      "price": 1900.00,
      "name": "Ethereum",
      "source": "coingecko",
      "last_updated": "2026-02-15T20:00:00Z"
    }
  }
}
```

**Price Sources:**
- `finnhub` - Stocks and ETFs
- `coingecko` - Crypto (ETH)
- `yahoo_finance` - Mutual funds (fallback)
- `cached` - Manual/static price (last resort)

---

## 3. Price Fetching Implementation

### Function: `fetch_all_prices(tickers)`

**Logic:**
```python
def fetch_all_prices(tickers):
    """Fetch prices from multiple sources"""
    prices = {}
    
    # Categorize tickers
    stocks = [t for t in tickers if t not in ['VSEQX', 'VTCLX', 'VTMSX', 'ETH']]
    mutual_funds = [t for t in tickers if t in ['VSEQX', 'VTCLX', 'VTMSX']]
    crypto = [t for t in tickers if t == 'ETH']
    
    # 1. Fetch stock prices from Finnhub
    for ticker in stocks:
        try:
            price = fetch_finnhub(ticker)
            prices[ticker] = {
                'price': price,
                'source': 'finnhub',
                'note': None
            }
        except:
            # Fallback to cached price
            prices[ticker] = get_cached_price(ticker)
    
    # 2. Fetch mutual funds from Yahoo Finance
    for ticker in mutual_funds:
        try:
            price = fetch_yahoo_finance(ticker)
            prices[ticker] = {
                'price': price,
                'source': 'yahoo_finance',
                'note': None
            }
        except:
            # Fallback to cached with note
            prices[ticker] = get_cached_price(ticker)
            prices[ticker]['note'] = 'Using cached price - Yahoo Finance unavailable'
    
    # 3. Fetch crypto from CoinGecko
    for ticker in crypto:
        try:
            price = fetch_coingecko(ticker)
            prices[ticker] = {
                'price': price,
                'source': 'coingecko',
                'note': None
            }
        except:
            prices[ticker] = get_cached_price(ticker)
    
    return prices
```

### Yahoo Finance API

**Endpoint:** `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}`

**Example:**
```bash
curl "https://query1.finance.yahoo.com/v8/finance/chart/VSEQX"
```

**Response:**
```json
{
  "chart": {
    "result": [{
      "meta": {
        "regularMarketPrice": 39.46
      }
    }]
  }
}
```

**Implementation:**
```python
def fetch_yahoo_finance(ticker):
    """Fetch price from Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    response = requests.get(url, timeout=10)
    data = response.json()
    return data['chart']['result'][0]['meta']['regularMarketPrice']
```

---

## 4. Parser Implementation

### Parse Source Data

```python
def parse_unified_tracker_v2(filepath):
    """Parse v2 format markdown"""
    with open(filepath) as f:
        content = f.read()
    
    accounts = {}
    sections = content.split('## Account: ')
    
    for section in sections[1:]:  # Skip header
        lines = section.strip().split('\n')
        account_name = lines[0].strip()
        
        accounts[account_name] = {
            'stocks': parse_stocks_table(section),
            'options': parse_options_table(section),
            'cash': parse_cash_table(section),
            'misc': parse_misc_table(section)
        }
    
    return accounts
```

### Build Views

**Stocks View (Aggregated):**
```python
def build_stocks_view(accounts, prices):
    """Build aggregated stocks view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            ticker = stock['ticker']
            
            # Skip cash equivalents (they're in Cash section)
            if ticker in ['SGOV', 'Cash']:
                continue
            
            if ticker not in aggregated:
                price_data = prices.get(ticker, {})
                aggregated[ticker] = {
                    'ticker': ticker,
                    'total_shares': 0,
                    'total_cost_basis': 0,
                    'accounts': [],
                    'price': price_data.get('price', 0),
                    'price_source': price_data.get('source', 'unknown'),
                    'price_note': price_data.get('note')
                }
            
            shares = stock['shares']
            cost_basis = stock['cost_basis']
            price = aggregated[ticker]['price']
            value = shares * price
            
            aggregated[ticker]['total_shares'] += shares
            aggregated[ticker]['total_cost_basis'] += cost_basis
            aggregated[ticker]['accounts'].append({
                'account': account_name,
                'shares': shares,
                'cost_basis': cost_basis,
                'value': value
            })
    
    # Calculate totals and returns
    for ticker, data in aggregated.items():
        data['total_value'] = data['total_shares'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] else 0
    
    return list(aggregated.values())
```

**Options View (Aggregated):**
```python
def build_options_view(accounts):
    """Build aggregated options view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for opt in data['options']:
            key = f"{opt['ticker']}_{opt['type']}_{opt['strike']}"
            
            if key not in aggregated:
                aggregated[key] = {
                    'ticker': opt['ticker'],
                    'type': opt['type'],
                    'strike': opt['strike'],
                    'expiration': opt['expiration'],
                    'total_contracts': 0,
                    'avg_premium': 0,
                    'accounts': []
                }
            
            contracts = opt['contracts']
            premium = opt['entry_premium']
            entry_value = contracts * premium * 100  # 100 shares per contract
            
            aggregated[key]['total_contracts'] += contracts
            aggregated[key]['accounts'].append({
                'account': account_name,
                'contracts': contracts,
                'entry_premium': premium,
                'entry_value': entry_value
            })
    
    # Options show entry value (current value requires live options API)
    for key, data in aggregated.items():
        data['total_entry_value'] = data['total_contracts'] * data['avg_premium'] * 100
        data['current_value'] = data['total_entry_value']  # Fallback to entry value
        data['note'] = 'Current value = Entry value (live options pricing requires upgrade)'
    
    return list(aggregated.values())
```

**Cash View (Aggregated):**
```python
def build_cash_view(accounts, prices):
    """Build aggregated cash view"""
    aggregated = {
        'Cash': {'total': 0, 'accounts': []},
        'SGOV': {'total': 0, 'shares': 0, 'accounts': []}
    }
    
    for account_name, data in accounts.items():
        for cash in data['cash']:
            asset = cash['asset']
            quantity = cash['quantity']
            
            if asset == 'Cash':
                value = quantity
                aggregated['Cash']['total'] += value
                aggregated['Cash']['accounts'].append({
                    'account': account_name,
                    'value': value
                })
            elif asset == 'SGOV':
                price = prices.get('SGOV', {}).get('price', 100.52)
                value = quantity * price
                aggregated['SGOV']['total'] += value
                aggregated['SGOV']['shares'] += quantity
                aggregated['SGOV']['accounts'].append({
                    'account': account_name,
                    'shares': quantity,
                    'value': value
                })
    
    return aggregated
```

**Misc View (Aggregated):**
```python
def build_misc_view(accounts, prices):
    """Build aggregated misc view"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for misc in data['misc']:
            asset = misc['asset']
            amount = misc['amount']
            cost_basis = misc['cost_basis']
            
            if asset not in aggregated:
                price = prices.get(asset, {}).get('price', 0)
                aggregated[asset] = {
                    'asset': asset,
                    'type': misc['type'],
                    'total_amount': 0,
                    'total_cost_basis': 0,
                    'price': price,
                    'accounts': []
                }
            
            price = aggregated[asset]['price']
            value = amount * price
            
            aggregated[asset]['total_amount'] += amount
            aggregated[asset]['total_cost_basis'] += cost_basis
            aggregated[asset]['accounts'].append({
                'account': account_name,
                'amount': amount,
                'cost_basis': cost_basis,
                'value': value
            })
    
    # Calculate returns
    for asset, data in aggregated.items():
        data['total_value'] = data['total_amount'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['return_pct'] = (data['total_return'] / data['total_cost_basis'] * 100) if data['total_cost_basis'] else 0
    
    return list(aggregated.values())
```

**Total Section:**
```python
def build_total_section(stocks, options, cash, misc):
    """Calculate category totals"""
    return {
        'stocks_etfs': sum(s['total_value'] for s in stocks),
        'options': sum(o['current_value'] for o in options),
        'cash_equivalents': cash['Cash']['total'] + cash['SGOV']['total'],
        'misc': sum(m['total_value'] for m in misc),
        'grand_total': sum([
            sum(s['total_value'] for s in stocks),
            sum(o['current_value'] for o in options),
            cash['Cash']['total'] + cash['SGOV']['total'],
            sum(m['total_value'] for m in misc)
        ])
    }
```

---

## 5. API Endpoints

### GET `/api/portfolio`

**Response:**
```json
{
  "last_price_refresh": "2026-02-15T20:00:00Z",
  "stocks": [
    {
      "ticker": "RKT",
      "total_shares": 4700,
      "total_value": 87796.00,
      "total_return": 11123.00,
      "return_pct": 14.5,
      "price": 18.68,
      "price_source": "finnhub",
      "price_note": null,
      "accounts": [
        {"account": "Robinhood", "shares": 1400, "value": 26152.00},
        {"account": "SEP-IRA", "shares": 2500, "value": 46700.00},
        {"account": "Roth IRA", "shares": 800, "value": 14944.00}
      ]
    }
  ],
  "options": [
    {
      "ticker": "PYPL",
      "type": "PUT",
      "strike": 45.00,
      "total_contracts": -10,
      "entry_value": -45000.00,
      "current_value": -45000.00,
      "note": "Current value = Entry value (live options pricing requires upgrade)",
      "accounts": [
        {"account": "Robinhood", "contracts": -10, "entry_value": -45000.00}
      ]
    }
  ],
  "cash": {
    "Cash": {
      "total": 14004.00,
      "accounts": [
        {"account": "Robinhood", "value": 11432.00},
        {"account": "SEP-IRA", "value": 2572.00}
      ]
    },
    "SGOV": {
      "total": 91994.68,
      "shares": 916.46,
      "price": 100.52,
      "accounts": [
        {"account": "Robinhood", "shares": 201.20, "value": 20224.62},
        {"account": "SEP-IRA", "shares": 350.00, "value": 35182.00}
      ]
    }
  },
  "misc": [
    {
      "asset": "ETH",
      "type": "crypto",
      "total_amount": 11.43,
      "total_value": 21717.00,
      "price": 1900.00,
      "price_source": "coingecko",
      "accounts": [
        {"account": "Robinhood", "amount": 11.43, "value": 21717.00}
      ]
    }
  ],
  "totals": {
    "stocks_etfs": 1559644.00,
    "options": -43950.00,
    "cash_equivalents": 105998.68,
    "misc": 21717.00,
    "grand_total": 1642409.68
  }
}
```

### POST `/api/refresh-prices`

**Action:**
1. Collect all tickers from source data
2. Fetch prices from Finnhub (stocks), Yahoo Finance (mutual funds), CoinGecko (ETH)
3. Update price_cache.json
4. Return updated prices with sources and notes

---

## 6. Dashboard UI

### Holdings Tab Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│ HOLDINGS                                                            │
├─────────────────────────────────────────────────────────────────────┤
│ Last price refresh: Feb 15, 2026 8:00 PM (3 hours ago)  [Refresh]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STOCKS & ETFs                                           $1,559,644  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Ticker  Shares  Price    Value      Return   Return%   Accounts   │
│ ────────────────────────────────────────────────────────────────────│
│ RKT     4,700   $18.68*  $87,796   +$11,235  +14.5%   ▼ 3 accts  │
│   └─ Robinhood: $26,152 (1,400 shares)                             │
│   └─ SEP-IRA:   $46,700 (2,500 shares)                             │
│   └─ Roth IRA:  $14,944 (800 shares)                               │
│ AAPL    150     $150.00  $22,500   +$2,750   +14.0%   ▼ 2 accts  │
│   └─ Robinhood: $15,000 (100 shares)                               │
│   └─ SEP-IRA:   $7,500 (50 shares)                                 │
│ VSEQX   5,861   $39.46** $231,258  -$315    -0.1%     ▼ 1 acct   │
│   └─ SEP-IRA:   $231,258 (5,861 shares)                            │
│        ** Using cached price - Yahoo Finance unavailable           │
│ ...                                                                │
│                                                                     │
│ OPTIONS POSITIONS                                         -$43,950  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Ticker  Type  Strike   Expiration  Contracts  Entry Value Accounts │
│ ────────────────────────────────────────────────────────────────────│
│ PYPL    PUT   $45.00   Feb 20      -10        -$45,000   ▼ 1 acct │
│   └─ Robinhood: -10 contracts                                     │
│   ⚠ Current value = Entry value (live options pricing unavailable) │
│ SOFI    CALL  $20.00   Mar 20      3          $393       ▼ 1 acct │
│   └─ SEP-IRA: 3 contracts                                         │
│ ...                                                                │
│                                                                     │
│ CASH & CASH EQUIVALENTS                                  $105,999  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Asset        Total           Accounts                              │
│ ────────────────────────────────────────────────────────────────────│
│ Cash         $14,004    ▼ 2 accts                                 │
│   └─ Robinhood: $11,432                                           │
│   └─ SEP-IRA:   $2,572                                            │
│ SGOV         $91,995    ▼ 5 accts (916.46 shares @ $100.52)       │
│   └─ Robinhood: $20,225 (201.20 shares)                           │
│   └─ SEP-IRA:   $35,182 (350.00 shares)                           │
│   └─ Schwab CSP: $6,607 (65.73 shares)                            │
│   └─ Schwab #2:  $6,607 (65.73 shares)                            │
│   └─ Roth IRA:   $6,607 (65.73 shares)                            │
│                                                                     │
│ MISC                                                        $21,717 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Asset   Amount    Price     Value    Return   Accounts             │
│ ────────────────────────────────────────────────────────────────────│
│ ETH     11.43     $1,900*   $21,717  -$6,858  ▼ 1 acct            │
│   └─ Robinhood: 11.43 ($21,717)                                    │
│        * Price from CoinGecko                                      │
│                                                                     │
│ TOTALS                                                     $1,642,410│
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Stocks & ETFs:        $1,559,644                                    │
│ Options:                -$43,950                                    │
│ Cash & Equivalents:     $105,999                                    │
│ Misc:                    $21,717                                    │
│ ─────────────────────────────────                                   │
│ GRAND TOTAL:          $1,642,410                                    │
│                                                                     │
│ LEGEND:                                                             │
│ * Real-time price from Finnhub                                      │
│ ** Cached price - manual update available                           │
│ ⚠ Using fallback value                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Refresh Prices Flow

1. User clicks "[Refresh Prices]" button
2. Button shows spinner: "Refreshing..."
3. POST to `/api/refresh-prices`
4. API fetches from Finnhub, Yahoo Finance, CoinGecko
5. Updates price_cache.json
6. Returns success/failure per ticker
7. Dashboard reloads with new prices
8. Shows "Last refresh: Just now"

---

## 7. Implementation Steps

### Step 1: Update Parser (server.py)
- [ ] Rewrite `parse_unified_tracker()` for v2 format
- [ ] Add `build_stocks_view()` with cash equivalent filtering
- [ ] Add `build_options_view()` with account attribution
- [ ] Add `build_cash_view()` with account attribution
- [ ] Add `build_misc_view()` with account attribution
- [ ] Add `build_total_section()`
- [ ] Add price fetching functions (Finnhub, Yahoo, CoinGecko)
- [ ] Update `/api/portfolio` endpoint
- [ ] Create `/api/refresh-prices` endpoint

### Step 2: Update Dashboard (templates/dashboard.html)
- [ ] Redesign Holdings tab with 5 sections
- [ ] Add account attribution columns (expandable)
- [ ] Add price source indicators (*, **, ⚠)
- [ ] Add "Refresh Prices" button with spinner state
- [ ] Show last refresh timestamp
- [ ] Add legend for price sources
- [ ] Test all sections render correctly

### Step 3: Testing
- [ ] Verify all stocks aggregate correctly
- [ ] Verify SGOV only shows in Cash (not Stocks)
- [ ] Verify options show entry values
- [ ] Verify mutual funds attempt Yahoo Finance
- [ ] Verify ETH fetches from CoinGecko
- [ ] Verify manual refresh updates all prices
- [ ] Verify last updated timestamp displays
- [ ] Verify account attribution expands/collapses
- [ ] Verify totals add up correctly

### Step 4: Documentation
- [ ] Update README with new data model
- [ ] Document how to make trades (edit markdown, click refresh)
- [ ] Document price source limitations

---

## 8. Future-Proofing for Trades

### When You Make a Trade:

**Example: Buy 100 AAPL in Robinhood at $150**

1. **You tell me** the trade details
2. **I update** `unified_portfolio_tracker.md`:
   ```markdown
   ### Stocks & ETFs
   | Ticker | Shares | Cost Basis | Notes |
   |--------|--------|------------|-------|
   | AAPL   | 100    | $15,000    | NEW   |
   ```
3. **Update Cash** (if needed):
   ```markdown
   ### Cash & Cash Equivalents
   | Asset | Quantity | Cost Basis | Category |
   |-------|----------|------------|----------|
   | Cash  | $X-15,000| —          | cash     |
   ```
4. **You click** "Refresh Prices"
5. **System** fetches AAPL price, recalculates everything
6. **Result** - New position appears with live P/L

**No code changes. Only markdown edits.**

---

## 9. Error Handling & Edge Cases

### Yahoo Finance Unavailable
- **Fallback**: Use cached price
- **UI**: Show "**" and note: "Using cached price - Yahoo Finance unavailable"
- **Action**: Manual price update button available

### Finnhub Rate Limit
- **Fallback**: Use cached price
- **UI**: Show warning: "Rate limit hit - using cached prices"
- **Action**: Wait 1 minute, retry

### CoinGecko Unavailable
- **Fallback**: Use cached ETH price
- **UI**: Show note: "ETH price may be stale"

### Missing Cost Basis
- **Calculation**: If cost_basis = 0, show "—" for return
- **UI**: Gray out return columns

---

## 10. Files to Modify

| File | Changes |
|------|---------|
| `mission_control/server.py` | Complete rewrite of parser and API endpoints |
| `mission_control/templates/dashboard.html` | Redesign Holdings tab with 5 sections |
| `portfolio/price_cache.json` | Created with current prices |
| `portfolio/unified_portfolio_tracker.md` | Already in v2 format |

---

## 11. Verification Checklist

Before declaring complete:

- [ ] All 5 sections display correctly
- [ ] Account attribution shows in all sections
- [ ] SGOV only in Cash (not Stocks)
- [ ] Options show entry values with note
- [ ] Mutual funds attempt Yahoo Finance
- [ ] ETH fetches from CoinGecko  
- [ ] Refresh button works
- [ ] Last updated timestamp shows
- [ ] Price source indicators visible (*, **, ⚠)
- [ ] Totals add up correctly
- [ ] No errors in console
- [ ] Server restarts successfully

---

**Awaiting Proceed for Phase 2 Implementation.**
