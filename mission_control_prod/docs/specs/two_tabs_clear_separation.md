# TDS: Two Tabs - Holdings + Stock Analysis Archive

**Clear separation of the TWO tabs being built**

---

## TAB 1: HOLDINGS

**Purpose:** Show portfolio value, positions, breakdown by account
**Data Source:** `unified_portfolio_tracker.md` + `price_cache.json`
**Sections:** 5 (Stocks, Options, Cash, Misc, Total)

### Holdings - API Endpoints
```
GET /api/portfolio       → Returns all holdings data
POST /api/refresh-prices → Updates price_cache.json
```

### Holdings - Section 1: Stocks & ETFs

**Columns:**
| Column | Where Data Comes From | Calculation | Example |
|--------|----------------------|-------------|---------|
| Ticker | `unified_portfolio_tracker.md` → Stocks table → Ticker column | Direct | "RKT" |
| Shares | Sum across all accounts in `unified_portfolio_tracker.md` | Robinhood(1,400) + SEP(2,500) + Roth(800) = 4,700 | "4,700" |
| Price | `price_cache.json` → prices[ticker].price | From Finnhub/Yahoo API (cached) | "$18.68" |
| Cost/Share | `total_cost_basis / total_shares` | $65,759 / 4,700 = $13.99 | "$13.99" |
| Value | `shares * price` | 4,700 * $18.68 = $87,796 | "$87,796" |
| P/L % | `(value - cost_basis) / cost_basis * 100` | ($87,796 - $65,759) / $65,759 = +33.5% | "+33.5%" |
| Accounts | Dropdown | Shows dollar value per account (see below) | "▼ 3 accounts" |

**Account Breakdown (dropdown when clicked):**
- Shows: "{AccountName}: ${dollarValue}"
- Dollar value = `account_shares * current_price`
- Example: "Robinhood: $26,152" NOT "Robinhood: 1,400 shares"

### Holdings - Section 2: Options Positions

**Columns:** Ticker | Type | Strike | Expiration | Contracts | Entry Premium | Value | Accounts

**Entry Premium Calculation:** `total_entry_value / total_contracts / 100`
- Example: -$45,000 / -10 contracts / 100 = $4.50 per share

**Note:** Current value = Entry value (live options pricing needs paid API)

### Holdings - Section 3: Cash & Cash Equivalents

**Rows:**
1. **Cash** - Direct dollar amounts
2. **SGOV** - Shares × price (SGOV is an ETF but treated as cash equivalent)

### Holdings - Section 4: Misc

**Columns:** Same as Stocks (Asset | Amount | Price | Cost/Unit | Value | P/L % | Accounts)
- For crypto like ETH
- Price from CoinGecko

### Holdings - Section 5: Total

**Display:** 4 cards + Grand Total
- Stocks & ETFs: $X
- Options: $X  
- Cash & Equivalents: $X
- Misc: $X
- **Grand Total: $X**

### Holdings - Refresh Prices Button

**Location:** Top right of Holdings tab
**Behavior:**
1. Call `POST /api/refresh-prices`
2. APIs fired:
   - Finnhub (stocks): `https://finnhub.io/api/v1/quote?symbol={TICKER}&token={KEY}`
   - Yahoo Finance (mutual funds): `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}`
   - CoinGecko (crypto): `https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd`
3. Update `price_cache.json`
4. Reload Holdings display

**NO AUTOMATIC API CALLS** - Only when button clicked

---

## TAB 2: STOCK ANALYSIS ARCHIVE

**Purpose:** Read and search stock research write-ups
**Data Source:** `portfolio/portfolio_tracker.md` (different file!)
**Sections:** 1 (Searchable cards)

### Analysis Archive - API Endpoint
```
GET /api/analysis-archive → Returns array of analysis objects
```

### Analysis Archive - Data Parsing

**Source File:** `portfolio/portfolio_tracker.md`
**Format:**
```markdown
## RKT Detailed Analysis (Updated Feb 13, 2026)

### Current Status
- **Entry:** ~$10
- **Current:** $18.68 (+87%)
...

## AAPL Detailed Analysis
...
```

**Parsing Logic:**
1. Split file by `## ` (markdown h2 headers)
2. Find sections containing "Detailed Analysis"
3. Extract:
   - Ticker: First word of header ("RKT")
   - Summary: First 3 non-empty lines after header
   - Full Text: Everything after header

### Analysis Archive - UI

**Layout:**
```
[Search Bar: "Search by ticker or keyword..."]

[Card Grid]
┌─────────────┐ ┌─────────────┐
│ RKT      B+ │ │ AAPL     A- │
│             │ │             │
│ Entry ~$10  │ │ Strong mo-  │
│ Current     │ │ mentum.     │
│ $18.68.     │ │ Target $200 │
│ Trim before │ │             │
│ earnings.   │ │             │
│             │ │             │
│ [Read More] │ │ [Read More] │
└─────────────┘ └─────────────┘
```

**Card Fields:**
- **Ticker:** From parsed data
- **Grade:** Parsed from text (A+, B+, etc.) or default "B+"
- **Summary:** First 200 characters of analysis
- **Read More:** Opens modal with full text

**Search:**
- Filters cards by ticker OR summary text
- Real-time as user types

**Modal (when Read More clicked):**
- Full screen overlay
- Shows complete `full_text` from analysis
- Markdown rendered as HTML

---

## CLEAR SEPARATION

| Feature | Holdings Tab | Analysis Archive Tab |
|---------|--------------|---------------------|
| **Purpose** | Show what you own | Show research write-ups |
| **Data File** | `unified_portfolio_tracker.md` | `portfolio_tracker.md` |
| **API** | `/api/portfolio` | `/api/analysis-archive` |
| **APIs Called** | Finnhub, Yahoo, CoinGecko (manual only) | None (reads file directly) |
| **Sections** | 5 (Stocks, Options, Cash, Misc, Total) | 1 (Searchable cards) |
| **Columns** | 7-8 per section | 3 per card (Ticker, Grade, Summary) |
| **Calculations** | Yes (values, P/L, totals) | No (display only) |
| **Refresh** | Manual button | N/A (file-based) |

---

## FILES BEING CREATED

### Backend (`server.py`)
Functions for Holdings:
- `parse_unified_tracker()` - reads `unified_portfolio_tracker.md`
- `build_stocks_view()` - aggregates stocks
- `build_options_view()` - aggregates options
- `build_cash_view()` - aggregates cash
- `build_misc_view()` - aggregates misc
- `refresh_prices()` - calls Finnhub/Yahoo/CoinGecko
- `/api/portfolio` endpoint
- `/api/refresh-prices` endpoint

Functions for Analysis Archive:
- `parse_analysis_archive()` - reads `portfolio_tracker.md`
- `/api/analysis-archive` endpoint

### Frontend (`dashboard.html`)
Holdings Tab JavaScript:
- `loadPortfolio()` - fetches and renders all 5 sections
- `renderStocksSection()` - table with 7 columns
- `renderOptionsSection()` - table with 8 columns
- `renderCashSection()` - 2 rows (Cash + SGOV)
- `renderMiscSection()` - table with 7 columns
- `renderTotalSection()` - 4 cards + grand total
- `refreshPrices()` - button handler
- `toggleAccounts()` - dropdown expand/collapse

Analysis Archive Tab JavaScript:
- `loadAnalysisArchive()` - fetches and renders cards
- `renderAnalysisCards()` - grid layout
- `filterAnalyses()` - search functionality
- `openAnalysisModal()` - show full text

---

## SUMMARY

**Building TWO separate tabs:**

1. **HOLDINGS** = Portfolio tracking with live prices
   - Shows: What you own, how much it's worth, P/L
   - Updates: Manual refresh button
   - APIs: Finnhub (stocks), Yahoo (funds), CoinGecko (crypto)

2. **STOCK ANALYSIS ARCHIVE** = Research notes
   - Shows: Your written analysis on each stock
   - Updates: None (reads markdown file)
   - APIs: None (static content)

**Both tabs work independently. Different data files. Different purposes.**

**Proceed with building these TWO tabs?**
