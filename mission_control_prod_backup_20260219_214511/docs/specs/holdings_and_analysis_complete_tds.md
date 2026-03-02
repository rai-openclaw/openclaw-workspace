# Technical Design Spec: Mission Control v2.0 - Holdings + Stock Analysis Archive

**Version:** 2.0 (Complete Rebuild - 2 Tabs)  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed  

---

## Part 1: Data Model Deep Dive

### 1.1 Source Files

**File 1: `portfolio/unified_portfolio_tracker.md`**
```
Purpose: Master source of truth for ALL portfolio data
Format: Markdown with tables
Updates: Manual (you edit when making trades)
```

**File 2: `portfolio/price_cache.json`**
```
Purpose: Cached prices from APIs
Format: JSON
Updates: Manual via "Refresh Prices" button only
Structure:
{
  "prices": {
    "AAPL": {"price": 150.00, "source": "finnhub", "last_updated": "2026-02-15T21:00:00Z"},
    "ETH": {"price": 1900.00, "source": "coingecko", "last_updated": "2026-02-15T21:00:00Z"}
  }
}
```

**File 3: `portfolio/portfolio_tracker.md`** (for Analysis Archive)
```
Purpose: Stock analysis write-ups
Format: Markdown sections per ticker
Structure:
## RKT Detailed Analysis
...analysis content...

## AAPL Detailed Analysis  
...analysis content...
```

---

## Part 2: Holdings Tab - Complete Specification

### 2.1 Overview
**Purpose:** Show complete portfolio breakdown with live prices
**Sections:** 5 (Stocks, Options, Cash, Misc, Total)
**Refresh:** Manual button only (no auto-refresh)

### 2.2 Data Flow

```
User Opens Holdings Tab
    ↓
Frontend: fetch('/api/portfolio')
    ↓
Backend: parse_unified_tracker(DATA_FILE)
    ↓
Backend: load_price_cache()
    ↓
Backend: build_stocks_view(accounts, prices)
         build_options_view(accounts)
         build_cash_view(accounts, prices)
         build_misc_view(accounts, prices)
    ↓
Backend: Return JSON with all 4 views + totals
    ↓
Frontend: Render 5 sections with tables
```

### 2.3 Section 1: Stocks & ETFs

**Purpose:** Show all stock and ETF holdings aggregated across accounts

**Columns:**
| # | Column Name | Data Source | Calculation | Format | Example |
|---|-------------|-------------|-------------|--------|---------|
| 1 | Ticker | `stock.ticker` | Direct from source | Text | "RKT" |
| 2 | Shares | `stock.total_shares` | Sum across all accounts | Integer | "4,700" |
| 3 | Price | `prices[ticker].price` | From price cache | Currency | "$18.68" |
| 4 | Cost/Share | `total_cost_basis / total_shares` | Calculated | Currency | "$13.99" |
| 5 | Value | `total_shares * price` | Calculated | Currency | "$87,796" |
| 6 | P/L % | `(total_value - total_cost_basis) / total_cost_basis * 100` | Calculated | Percentage | "+14.5%" |
| 7 | Accounts | `stock.accounts` array | Dropdown expansion | Text | "▼ 3 accounts" |

**Column 1 - Ticker:**
- Source: `unified_portfolio_tracker.md` → `### Stocks & ETFs` table → `Ticker` column
- Extraction: Direct string value
- Filter: Exclude tickers marked as `cash_equivalent` in Cash section (prevents SGOV duplication)

**Column 2 - Shares:**
- Source: Parsed from all accounts
- Aggregation: `sum(account.shares for account in ticker.accounts)`
- Example: Robinhood (1,400) + SEP-IRA (2,500) + Roth IRA (800) = 4,700 total

**Column 3 - Price:**
- Source: `price_cache.json` → `prices[ticker].price`
- Fallback: If not in cache, show 0 with asterisk
- Refresh: Only updated when user clicks "Refresh Prices" button
- API Sources:
  - Finnhub: Regular stocks (AAPL, TSLA, etc.)
  - Yahoo Finance: Mutual funds (VSEQX, VTCLX, VTMSX)
  - Cached: Previous value if API fails

**Column 4 - Cost/Share:**
- Formula: `total_cost_basis / total_shares`
- Source Data:
  - `total_cost_basis`: From `unified_portfolio_tracker.md` → `Cost Basis` column
  - `total_shares`: Aggregated sum (see Column 2)
- Example: $65,759 / 4,700 shares = $13.99 per share

**Column 5 - Value:**
- Formula: `total_shares * current_price`
- Real-time calculation on every page load
- Uses cached price (not live API call)

**Column 6 - P/L %:**
- Formula: `((total_value - total_cost_basis) / total_cost_basis) * 100`
- Positive = Green color (#10b981)
- Negative = Red color (#ef4444)
- Zero = Gray color

**Column 7 - Accounts:**
- Display: Dropdown button "▼ 3 accounts"
- Click Action: Expand to show per-account breakdown
- Per-Account Data: Shows **dollar value** (not shares)
  - Formula per account: `account.shares * current_price`
  - Display: "Robinhood: $26,152"
  - NOT: "Robinhood: 1,400 shares" (that's the old broken way)

**Account Breakdown Example:**
```
Row: RKT | 4,700 | $18.68 | $13.99 | $87,796 | +14.5% | ▼ 3 accounts

[Click expands to:]
  Robinhood: $26,152 (1,400 shares)
  SEP-IRA: $46,700 (2,500 shares)
  Roth IRA: $14,944 (800 shares)
```

**Asterisk Logic:**
```python
price_data = prices[ticker]
last_updated = datetime.fromisoformat(price_data['last_updated'])
hours_old = (now - last_updated).total_seconds() / 3600

if hours_old > 24:
    show_asterisk = True
    tooltip = "Price cached >24 hours ago. Click Refresh Prices."
else:
    show_asterisk = False
```

**Section Total:**
- Display: Right-aligned at top of section
- Value: `sum(stock.total_value for stock in stocks)`
- Format: "$1,559,644"

---

### 2.4 Section 2: Options Positions

**Purpose:** Show all option contracts (puts/calls) across accounts

**Columns:**
| # | Column | Data Source | Calculation | Format | Example |
|---|--------|-------------|-------------|--------|---------|
| 1 | Ticker | `option.ticker` | Direct | Text | "PYPL" |
| 2 | Type | `option.type` | Direct | Text | "PUT" or "CALL" |
| 3 | Strike | `option.strike` | Direct | Currency | "$45.00" |
| 4 | Expiration | `option.expiration` | Direct | Date | "2026-02-20" |
| 5 | Contracts | `option.total_contracts` | Sum across accounts | Integer | "-10" |
| 6 | Entry Premium | `total_entry_value / total_contracts / 100` | Calculated | Currency | "$4.500" |
| 7 | Value | `total_entry_value` | Calculated | Currency | "-$45,000" |
| 8 | Accounts | `option.accounts` array | Dropdown | Text | "▼ 1 account" |

**Column 1-5:** Direct from source data

**Column 6 - Entry Premium (per contract):**
- Formula: `total_entry_value / total_contracts / 100`
- Why /100: Options contracts represent 100 shares each
- Example: -$45,000 / -10 contracts / 100 = $4.50 per share premium

**Column 7 - Value:**
- Current limitation: Shows entry value (not live market value)
- Reason: Live options pricing requires paid API or complex scraping
- Note displayed: "Current value = Entry value (live options pricing requires upgrade)"

**Account Breakdown:**
- Shows: "{Account}: {contracts} contracts ({dollar_value})"
- Dollar value: `contracts * premium * 100`
- Example: "Robinhood: -10 contracts (-$45,000)"

**Section Total:**
- Sum of all option values
- Usually negative (liability for short options)

---

### 2.5 Section 3: Cash & Cash Equivalents

**Purpose:** Show cash and cash-like instruments (SGOV, money market)

**Columns:**
| # | Column | Data Source | Calculation | Example |
|---|--------|-------------|-------------|---------|
| 1 | Asset | Direct | "Cash" or "SGOV" | "SGOV" |
| 2 | Total | Calculated | Cash=direct, SGOV=shares*price | "$91,995" |
| 3 | Details | Varies | Cash="-", SGOV="{shares} @ ${price}" | "916.46 shares @ $100.52" |
| 4 | Accounts | Dropdown | Per-account dollar values | "▼ 5 accounts" |

**Cash Row:**
- Source: `cash['Cash']`
- Total: Direct sum of dollar values
- No price calculation needed

**SGOV Row:**
- Source: `cash['SGOV']`
- Total: `total_shares * price`
- Price: From cache (ticker "SGOV")
- Details: Shows share count and price per share

**Per-Account Display:**
- Cash: "{Account}: $11,432"
- SGOV: "{Account}: $20,225 (201.20 shares)"

---

### 2.6 Section 4: Misc

**Purpose:** Crypto and other non-standard assets

**Columns:** Same as Stocks (Ticker→Accounts)
- Ticker/Asset name
- Amount (instead of Shares)
- Price (from CoinGecko for crypto)
- Cost/Unit
- Value
- P/L %
- Accounts

**Data Source:**
- From `unified_portfolio_tracker.md` → `### Misc` table
- ETH price: CoinGecko API ( ethereum ID )

---

### 2.7 Section 5: Total Portfolio

**Layout:** Grid of 4 cards + Grand Total

**Cards:**
1. Stocks & ETFs: `$1,559,644`
2. Options: `-$43,950`
3. Cash & Equivalents: `$105,999`
4. Misc: `$21,717`

**Grand Total:**
- Formula: `stocks + options + cash + misc`
- Display: Large font, prominent
- Value: `$1,662,256`

**Verification:**
- Backend checks: `abs(calculated - reported) < 1`
- If mismatch: Log error, display warning

---

### 2.8 Refresh Prices Feature

**Button Location:** Top of Holdings tab, right side
**Button Text:** "Refresh Prices"

**Click Handler:**
```javascript
async function refreshPrices() {
    // 1. Disable button, show spinner
    button.disabled = true;
    button.textContent = "Refreshing...";
    
    // 2. Call API
    const response = await fetch('/api/refresh-prices', {method: 'POST'});
    const result = await response.json();
    
    // 3. Reload portfolio data
    await loadPortfolio();
    
    // 4. Re-enable button
    button.disabled = false;
    button.textContent = "Refresh Prices";
}
```

**Backend Handler:**
```python
@app.route('/api/refresh-prices', methods=['POST'])
def api_refresh_prices():
    accounts = parse_unified_tracker(DATA_FILE)
    
    # Collect all tickers
    stock_tickers = set()
    misc_assets = set()
    for account in accounts.values():
        for stock in account['stocks']:
            if stock['ticker'] not in ['SGOV', 'Cash']:
                stock_tickers.add(stock['ticker'])
        for misc in account['misc']:
            misc_assets.add(misc['asset'])
    stock_tickers.add('SGOV')
    
    # Fetch prices
    prices = {}
    for ticker in stock_tickers:
        if ticker in ['VSEQX', 'VTCLX', 'VTMSX']:
            price = fetch_yahoo_price(ticker)  # Mutual funds
        else:
            price = fetch_finnhub_price(ticker)  # Stocks
        if price > 0:
            prices[ticker] = {'price': price, 'source': 'api', 'last_updated': now()}
    
    for asset in misc_assets:
        price = fetch_coingecko_price(asset)  # Crypto
        if price > 0:
            prices[asset] = {'price': price, 'source': 'coingecko', 'last_updated': now()}
    
    save_price_cache(prices)
    return jsonify({'success': True, 'updated': len(prices)})
```

**APIs Called (only on manual refresh):**
- Finnhub: `/api/v1/quote?symbol={TICKER}` - 60 calls/min free tier
- Yahoo Finance: `/v8/finance/chart/{TICKER}` - No key needed
- CoinGecko: `/api/v3/simple/price?ids={ASSET}&vs_currencies=usd` - Free tier

**No Automatic Calls:** Prices only update when user clicks button

---

## Part 3: Stock Analysis Archive Tab

### 3.1 Overview
**Purpose:** Searchable archive of stock research write-ups
**Data Source:** `portfolio/portfolio_tracker.md`
**Features:** Search, filter, read full analysis

### 3.2 Data Flow

```
User Opens Analysis Archive Tab
    ↓
Frontend: fetch('/api/analysis-archive')
    ↓
Backend: Read portfolio_tracker.md
    ↓
Backend: Parse sections marked "## {TICKER} Detailed Analysis"
    ↓
Backend: Extract ticker, summary, full text
    ↓
Backend: Return array of analyses
    ↓
Frontend: Display as searchable cards
```

### 3.3 Data Structure

**Source File Parsing:**
```python
def parse_analysis_archive(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    analyses = []
    # Split by ## headers
    sections = content.split('## ')
    
    for section in sections:
        if 'Detailed Analysis' in section:
            lines = section.split('\n')
            header = lines[0]  # e.g., "RKT Detailed Analysis"
            ticker = header.split()[0]  # Extract "RKT"
            
            # Get summary (first 3 non-empty lines)
            summary_lines = []
            for line in lines[1:10]:
                if line.strip() and not line.startswith('#') and not line.startswith('|'):
                    summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break
            
            analyses.append({
                'ticker': ticker,
                'summary': ' '.join(summary_lines)[:200],
                'full_text': '\n'.join(lines[1:])  # Everything after header
            })
    
    return analyses
```

**API Response:**
```json
[
  {
    "ticker": "RKT",
    "summary": "Entry ~$10. Current $18.68 (+87%). Trim 40-50% before Feb 26 earnings...",
    "full_text": "### Current Status\n- **Entry:** ~$10..."
  },
  {
    "ticker": "AAPL",
    "summary": "Strong momentum. Target $200...",
    "full_text": "### Analysis\n..."
  }
]
```

### 3.4 UI Layout

**Search Bar:**
- Placeholder: "Search by ticker or keyword..."
- Real-time filter as user types
- Searches both ticker and summary text

**Analysis Cards Grid:**
```
┌─────────────────────────────────────────────────┐
│ Search: [____________________]                  │
├─────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│ │ RKT    B+   │  │ AAPL   A-   │  │ TSLA  C+ ││
│ │             │  │             │  │          ││
│ │ Entry ~$10  │  │ Strong      │  │ Volatile ││
│ │ Current     │  │ momentum    │  │ but      ││
│ │ $18.68      │  │             │  │ growing  ││
│ │             │  │             │  │          ││
│ │ [Read More] │  │ [Read More] │  │ [...]    ││
│ └─────────────┘  └─────────────┘  └──────────┘│
└─────────────────────────────────────────────────┘
```

**Card Fields:**
| Field | Source | Example |
|-------|--------|---------|
| Ticker | `analysis.ticker` | "RKT" |
| Grade | Parsed from summary or default "B+" | "B+" |
| Summary | `analysis.summary` | "Entry ~$10. Current..." |
| Read More | Button opens modal | "Read More →" |

**Modal (Read More):**
- Full screen overlay
- Title: "{TICKER} Analysis"
- Content: `analysis.full_text` rendered as HTML
- Close button (X) top right
- Click outside to close

**Search Implementation:**
```javascript
function filterAnalyses(searchTerm) {
    const term = searchTerm.toLowerCase();
    return analyses.filter(a => 
        a.ticker.toLowerCase().includes(term) ||
        a.summary.toLowerCase().includes(term)
    );
}
```

---

## Part 4: API Endpoints Summary

### Holdings Tab APIs
| Endpoint | Method | Purpose | Data Returned |
|----------|--------|---------|---------------|
| `/api/portfolio` | GET | Complete portfolio | stocks, options, cash, misc, totals |
| `/api/refresh-prices` | POST | Update prices | success, count updated |

### Stock Analysis Archive APIs
| Endpoint | Method | Purpose | Data Returned |
|----------|--------|---------|---------------|
| `/api/analysis-archive` | GET | All analyses | array of {ticker, summary, full_text} |

---

## Part 5: Implementation Steps

### Step 1: Create Backend
1. Create `server.py` with:
   - Data parsing functions
   - Price fetchers (Finnhub, Yahoo, CoinGecko)
   - View builders (stocks, options, cash, misc)
   - API endpoints (/api/portfolio, /api/refresh-prices, /api/analysis-archive)
   - All other tab endpoints (earnings, ideas, schedule, etc.)

### Step 2: Create Frontend - Holdings Tab
1. HTML structure with 5 sections
2. JavaScript render functions for each section
3. Table generation with all columns
4. Account dropdown functionality
5. Refresh button handler
6. Currency/percentage formatters
7. Color coding (green/red)

### Step 3: Create Frontend - Analysis Archive Tab
1. Card grid layout
2. Search/filter functionality
3. Modal for full text
4. Markdown-to-HTML rendering

### Step 4: Test Everything
1. Verify all 5 Holdings sections display
2. Verify cost/share calculations
3. Verify P/L % colors
4. Verify account dollar values
5. Verify refresh button updates prices
6. Verify Analysis Archive search works
7. Verify modal opens/closes

---

## Part 6: Data Verification Examples

### Example 1: RKT Stock
**Source Data:**
- Robinhood: 1,400 shares, cost basis $18,435
- SEP-IRA: 2,500 shares, cost basis $35,964
- Roth IRA: 800 shares, cost basis $14,944

**Aggregated:**
- Total shares: 4,700
- Total cost basis: $69,343
- Cost/share: $14.75
- Current price: $18.68
- Value: $87,796
- P/L: $18,453 (+26.6%)

**Display:**
```
RKT | 4,700 | $18.68 | $14.75 | $87,796 | +26.6% | ▼ 3 accounts
[Dropdown:]
  Robinhood: $26,152
  SEP-IRA: $46,700
  Roth IRA: $14,944
```

### Example 2: PYPL Options
**Source Data:**
- Robinhood: -10 contracts, premium $4.50

**Display:**
```
PYPL | PUT | $45.00 | 2026-02-20 | -10 | $4.500 | -$45,000 | ▼ 1 account
[Dropdown:]
  Robinhood: -10 contracts (-$45,000)
  Note: Current value = Entry value
```

---

**Proceed with building these 2 tabs with complete specification?**
