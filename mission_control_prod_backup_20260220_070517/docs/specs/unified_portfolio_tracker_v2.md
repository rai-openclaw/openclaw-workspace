# Technical Design Spec: Unified Portfolio Tracker v2.0

**Version:** 2.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Overview

Complete redesign of portfolio tracking system with clean data model, manual price refresh, and dynamic calculations.

---

## Core Principles

1. **Source Data = Raw Static Data Only**
   - Ticker, shares, cost basis
   - No calculated values
   - No prices (cached separately)

2. **Prices = Cached & Manual Refresh**
   - Price cache file updated only on user action
   - No automatic API calls
   - Dashboard shows "Last Updated" timestamp

3. **Calculations = Always Dynamic**
   - Position value = shares × cached_price
   - Totals = sum of components
   - Recalculated on every page load

4. **Two Display Views**
   - **Stocks & ETFs Tab:** Aggregated across all accounts
   - **Accounts Tab:** Per-account breakdown

---

## Data Model

### File: `portfolio/unified_portfolio_tracker.md`

```markdown
# Unified Portfolio Tracker

## Account: Robinhood
**Type:** Taxable Brokerage  
**Broker:** Robinhood

### Stocks & ETFs
| Ticker | Shares | Cost Basis | Notes |
|--------|--------|------------|-------|
| RKT    | 1,400  | $18,435    |       |
| AAPL   | 100    | $12,000    |       |
| SHOP   | 440    | $41,300    |       |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| PYPL   | PUT  | $45.00 | 2026-02-20 | -10       | $4.50         |

### Cash & Cash Equivalents
| Asset    | Quantity     | Cost Basis |
|----------|--------------|------------|
| Cash     | $11,432.00   | —          |
| SGOV     | 201.20       | $20,224.62 |

### Misc
| Asset | Amount | Type   | Cost Basis |
|-------|--------|--------|------------|
| ETH   | 11.43  | Crypto | $28,575    |

---

## Account: SEP-IRA
**Type:** Retirement (SEP-IRA)  
**Broker:** Schwab

### Stocks & ETFs
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| RKT    | 2,500  | $35,964    |
| AAPL   | 50     | $3,750     |
| HOOD   | 700    | $32,750    |
| VSEQX  | 5,860.559 | $231,573 |
| VTCLX  | 446.53 | $157,219   |
| VTMSX  | 2,514.233 | $269,576 |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| SOFI   | CALL | $20.00 | 2026-03-20 | 3         | $2.10         |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis |
|-------|----------|------------|
| Cash  | $2,572   | —          |
| SGOV  | 350      | $35,182    |

### Misc
| Asset | Amount | Type | Cost Basis |
|-------|--------|------|------------|
| —     | —      | —    | —          |

---

## Account: Schwab CSP
**Type:** Taxable (Margin)  
**Broker:** Schwab

### Stocks & ETFs
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| ELF    | 200    | $16,294    |
| TTD    | 600    | $15,492    |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| ELF    | PUT  | $110.00| 2026-02-26 | -6        | $29.225       |
| AMD    | PUT  | $220.00| 2026-02-26 | -4        | $14.275       |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis |
|-------|----------|------------|
| SGOV  | 65.7288  | $6,607     |

### Misc
| Asset | Amount | Type | Cost Basis |
|-------|--------|------|------------|
| —     | —      | —    | —          |

---

## Account: Schwab #2
**Type:** Taxable (Margin)  
**Broker:** Schwab

### Stocks & ETFs
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| CRM    | 320    | $60,710    |
| AMZN   | 265    | $52,722    |
| GOOG   | 170    | $52,020    |
| MSFT   | 115.39 | $46,180    |

### Options Positions
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium |
|--------|------|--------|------------|-----------|---------------|
| AMD    | PUT  | $200.00| 2026-03-26 | -1        | $7.33         |
| ELF    | PUT  | $105.00| 2026-03-26 | -2        | $25.00        |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis |
|-------|----------|------------|
| SGOV  | 65.7288  | $6,607     |

### Misc
| Asset | Amount | Type | Cost Basis |
|-------|--------|------|------------|
| —     | —      | —    | —          |

---

## Account: Roth IRA
**Type:** Retirement (Roth IRA)  
**Broker:** Schwab

### Stocks & ETFs
| Ticker | Shares | Cost Basis |
|--------|--------|------------|
| RKT    | 800    | $14,944    |
| CRM    | 60     | $11,383    |
| AMD    | 100    | $15,574    |
| NKE    | 100    | $6,300     |
| PYPL   | 100    | $4,036     |
| FUBO   | 4,000  | $5,360     |

### Options Positions
| — | — | — | — | — | — |

### Cash & Cash Equivalents
| Asset | Quantity | Cost Basis |
|-------|----------|------------|
| SGOV  | 65.7288  | $6,607     |

### Misc
| Asset | Amount | Type | Cost Basis |
|-------|--------|------|------------|
| —     | —      | —    | —          |
```

---

## Price Cache

### File: `portfolio/price_cache.json`

```json
{
  "version": "2.0",
  "last_updated": "2026-02-15T19:55:00Z",
  "prices": {
    "RKT": {"price": 18.68, "name": "Rocket Companies"},
    "AAPL": {"price": 150.00, "name": "Apple Inc."},
    "SHOP": {"price": 112.70, "name": "Shopify"},
    "VSEQX": {"price": 39.46, "name": "Vanguard Extended Market"},
    "VTCLX": {"price": 352.09, "name": "Vanguard Tax-Managed Capital"},
    "VTMSX": {"price": 107.22, "name": "Vanguard Tax-Managed Small Cap"},
    "ETH": {"price": 2800.00, "name": "Ethereum"}
  }
}
```

---

## Parser Logic

### Step 1: Parse Source Data

```python
def parse_unified_tracker(filepath):
    """Parse markdown into structured data"""
    accounts = {}
    
    # Parse each account section
    for account_section in split_by_account(content):
        account_name = extract_account_name(account_section)
        
        accounts[account_name] = {
            'type': extract_type(account_section),
            'broker': extract_broker(account_section),
            'stocks': parse_table(account_section, '### Stocks & ETFs'),
            'options': parse_table(account_section, '### Options Positions'),
            'cash': parse_table(account_section, '### Cash & Cash Equivalents'),
            'misc': parse_table(account_section, '### Misc')
        }
    
    return accounts
```

### Step 2: Load Price Cache

```python
def load_price_cache():
    """Load cached prices"""
    with open('portfolio/price_cache.json') as f:
        cache = json.load(f)
    return cache['prices'], cache['last_updated']
```

### Step 3: Calculate View - Accounts Tab

```python
def calculate_accounts_view(accounts, prices):
    """Calculate per-account totals"""
    result = {}
    
    for account_name, data in accounts.items():
        account_total = 0
        positions = []
        
        # Stocks & ETFs
        for stock in data['stocks']:
            ticker = stock['ticker']
            shares = stock['shares']
            cost_basis = stock['cost_basis']
            price = prices.get(ticker, {}).get('price', 0)
            value = shares * price
            
            positions.append({
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'value': value,
                'cost_basis': cost_basis,
                'return': value - cost_basis,
                'return_pct': ((value - cost_basis) / cost_basis * 100) if cost_basis else 0
            })
            account_total += value
        
        # Cash (dollar value directly)
        for cash in data['cash']:
            asset = cash['asset']
            quantity = cash['quantity']
            if asset == 'Cash':
                value = quantity  # Already a dollar value
            else:  # SGOV, etc.
                price = prices.get(asset, {}).get('price', 0)
                value = quantity * price
            account_total += value
        
        # Misc (crypto, etc.)
        for misc in data['misc']:
            asset = misc['asset']
            amount = misc['amount']
            price = prices.get(asset, {}).get('price', 0)
            value = amount * price
            account_total += value
        
        result[account_name] = {
            'total_value': account_total,
            'positions': positions
        }
    
    return result
```

### Step 4: Calculate View - Stocks & ETFs Tab (Aggregated)

```python
def calculate_stocks_view(accounts, prices):
    """Aggregate positions across all accounts"""
    aggregated = {}
    
    for account_name, data in accounts.items():
        for stock in data['stocks']:
            ticker = stock['ticker']
            shares = stock['shares']
            cost_basis = stock['cost_basis']
            
            if ticker not in aggregated:
                aggregated[ticker] = {
                    'ticker': ticker,
                    'total_shares': 0,
                    'total_cost_basis': 0,
                    'accounts': [],
                    'price': prices.get(ticker, {}).get('price', 0)
                }
            
            aggregated[ticker]['total_shares'] += shares
            aggregated[ticker]['total_cost_basis'] += cost_basis
            aggregated[ticker]['accounts'].append({
                'account': account_name,
                'shares': shares,
                'cost_basis': cost_basis
            })
    
    # Calculate aggregated values
    for ticker, data in aggregated.items():
        data['total_value'] = data['total_shares'] * data['price']
        data['total_return'] = data['total_value'] - data['total_cost_basis']
        data['return_pct'] = ((data['total_return'] / data['total_cost_basis']) * 100) if data['total_cost_basis'] else 0
    
    return list(aggregated.values())
```

---

## API Endpoints

### GET `/api/portfolio`

**Response:**
```json
{
  "last_price_update": "2026-02-15T19:55:00Z",
  "accounts": {
    "Robinhood": {
      "total_value": 255200.37,
      "positions": [...]
    },
    "SEP-IRA": {
      "total_value": 393728.73,
      "positions": [...]
    },
    ...
  },
  "stocks_aggregated": [
    {
      "ticker": "RKT",
      "total_shares": 4700,
      "total_value": 87896.00,
      "accounts": [
        {"account": "Robinhood", "shares": 1400, "value": 26152.00},
        {"account": "SEP-IRA", "shares": 2500, "value": 46700.00},
        {"account": "Roth IRA", "shares": 800, "value": 15044.00}
      ]
    },
    ...
  ],
  "grand_total": 1662256.29
}
```

### POST `/api/refresh-prices`

**Action:**
1. Collect all tickers from source data
2. Call Finnhub API for each ticker
3. Update `price_cache.json`
4. Return updated prices

**No automatic calls.** Only triggered by user clicking "Refresh Prices" button.

---

## Dashboard UI

### Accounts Tab
```
┌─────────────────────────────────────────────────────┐
│ Accounts                                            │
├─────────────────────────────────────────────────────┤
│ Robinhood                    $255,200.37           │
│   AAPL: 100 shares × $150 = $15,000                │
│   RKT:  1,400 shares × $18.68 = $26,152            │
│   ...                                               │
├─────────────────────────────────────────────────────┤
│ SEP-IRA                      $393,728.73           │
│   ...                                               │
├─────────────────────────────────────────────────────┤
│ Grand Total                  $1,662,256.29         │
└─────────────────────────────────────────────────────┘
Last price update: 2026-02-15 7:55 PM
[Refresh Prices] button
```

### Stocks & ETFs Tab
```
┌─────────────────────────────────────────────────────┐
│ Stocks & ETFs (Aggregated)                          │
├─────────────────────────────────────────────────────┤
│ Ticker │ Shares │ Price │ Value │ Return │ Return % │
├─────────────────────────────────────────────────────┤
│ RKT    │ 4,700  │ $18.68│ $87,796│ +$12,227│ +16.2% │
│   └─ Robinhood: $26,152 (1,400 shares)             │
│   └─ SEP-IRA:   $46,700 (2,500 shares)             │
│   └─ Roth IRA:  $14,944 (800 shares)               │
├─────────────────────────────────────────────────────┤
│ AAPL   │ 150    │ $150  │ $22,500│ +$2,750 │ +14.0% │
│   └─ Robinhood: $15,000 (100 shares)               │
│   └─ SEP-IRA:   $7,500 (50 shares)                 │
└─────────────────────────────────────────────────────┘
```

---

## Migration Plan

### Step 1: Extract Raw Data
- Use OCR tool on all brokerage screenshots
- Extract: ticker, shares, cost basis (or calculate from total return)

### Step 2: Create New Unified Tracker
- Write clean markdown with 4 sections per account
- Store only raw data

### Step 3: Calculate Missing Cost Basis
- For Robinhood: `Cost Basis = (Shares × Price) - Total Return`
- Store calculated cost basis in new tracker

### Step 4: Create Price Cache
- Initialize with current prices
- Empty cache is valid (shows $0 until first refresh)

### Step 5: Update Parser
- Read new markdown format
- Calculate views dynamically

### Step 6: Update Dashboard
- Add "Refresh Prices" button
- Show last update timestamp
- Display both views

---

## Affected Files

| File | Action |
|------|--------|
| `portfolio/unified_portfolio_tracker.md` | Rewrite with new format |
| `portfolio/price_cache.json` | Create new |
| `server.py` | Rewrite parser for new format |
| `templates/dashboard.html` | Add refresh button, show timestamp |

---

## Verification Checklist

- [ ] All raw data extracted from screenshots
- [ ] Cost basis calculated for all positions
- [ ] New markdown format validates
- [ ] Price cache loads/saves correctly
- [ ] Accounts tab shows correct per-account totals
- [ ] Stocks tab shows correct aggregated view
- [ ] Refresh Prices button works
- [ ] Last updated timestamp displays
- [ ] No automatic API calls
- [ ] All totals add up correctly

---

**Awaiting Proceed.**
