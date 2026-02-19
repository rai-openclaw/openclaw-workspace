# Mission Control Technical Design Specification

## Document Purpose
Single source of truth for Mission Control architecture, data contracts, and implementation plan. **DO NOT implement without confirming this design first.**

---

## 1. Goals

### Primary Goal
Provide Rai with a unified dashboard that aggregates all portfolio data, trading research, schedule, and API usage tracking in one interface.

### Functional Goals
1. **Portfolio Aggregation**: Combine 5 brokerage accounts (Robinhood, SEP-IRA, Schwab CSP, Schwab #2, Roth IRA) into unified view
2. **Real-time Prices**: Display current stock prices via Finnhub API integration
3. **Options Tracking**: Show CSP positions across all accounts with strike/expiry details
4. **Cash Management**: Track SGOV + cash positions per account
5. **Stock Analysis**: Link to detailed research on individual tickers
6. **Earnings Calendar**: Upcoming earnings dates for portfolio holdings
7. **API Usage Tracking**: Monitor API costs and limits
8. **Team Structure**: Display corporate hierarchy (Dave, Bob, Rai)
9. **Ideas & Notes**: Searchable repository

### Non-Functional Goals
1. **Data Accuracy**: No estimates — exact values from tracker files only
2. **Performance**: Load time < 2 seconds for portfolio view
3. **Reliability**: Server managed by launchd, auto-restart on crash
4. **Maintainability**: Single source of truth (tracker files), no duplicated data

---

## 2. Current State Analysis

### Working Components
- ✅ Flask server running on port 8080 via launchd
- ✅ Basic API endpoints: `/api/portfolio`, `/api/usage`
- ✅ HTML template with sidebar navigation
- ✅ API usage tracking display

### Broken Components
- ❌ Portfolio endpoint only returns account totals, not positions
- ❌ Options positions not being parsed from tracker files
- ❌ Stock table expects `positions` array that doesn't exist in API response
- ❌ Cash/SGOV breakdown not calculated correctly
- ❌ ETH price not being fetched

### Missing Components
- ❌ `/api/stock/<ticker>` analysis endpoint
- ❌ `/api/analysis-archive` full content
- ❌ `/api/earnings-research` Bob's research
- ❌ `/api/schedule` endpoint
- ❌ `/api/ideas` endpoint
- ❌ Real-time price fetching via Finnhub

---

## 3. Affected Files

### Server-Side Files
| File | Purpose | Changes Needed |
|------|---------|----------------|
| `~/.openclaw/workspace/mission_control/server.py` | Flask application | Complete rewrite of data parsing logic |
| `~/.openclaw/workspace/mission_control/mc.sh` | Control script | No changes (working) |
| `~/.openclaw/workspace/mission_control/templates/dashboard.html` | Frontend | Minor updates for data field names |

### Data Source Files (Read-Only)
| File | Format | Contains |
|------|--------|----------|
| `~/.openclaw/workspace/portfolio/robinhood_tracker.md` | Markdown table | 13 stocks, ETH, cash, options |
| `~/.openclaw/workspace/portfolio/sep_ira_tracker.md` | Markdown table | 17 stocks, options, SGOV, cash |
| `~/.openclaw/workspace/portfolio/schwab_csp_tracker.md` | Markdown table | 2 stocks, 3 index funds, 2 CSP positions |
| `~/.openclaw/workspace/portfolio/schwab_secondary_tracker.md` | Markdown table | 4 stocks, 2 CSP positions |
| `~/.openclaw/workspace/portfolio/roth_ira_tracker.md` | Markdown table | 6 stocks, SGOV |
| `~/.openclaw/workspace/portfolio/portfolio_tracker.md` | Markdown | Analysis archive |
| `~/.openclaw/workspace/daily_earnings_research.md` | Markdown | Bob's research |
| `~/.openclaw/workspace/ideas/NOTES.md` | Markdown | Ideas repository |
| `~/.openclaw/workspace/son_schedule.md` | Markdown | Schedule data |

### Configuration Files
| File | Purpose |
|------|---------|
| `~/.openclaw/workspace/.gemini_api_key` | Gemini API key |
| `~/.openclaw/openclaw.json` | Moonshot API config |

---

## 4. API Contract

### GET `/api/portfolio`
**Current Response (BROKEN):**
```json
{
  "account_total": 300124.0,
  "account_totals": {"Robinhood": 300124, ...},
  "last_updated": "2026-02-15T..."
}
```

**Required Response:**
```json
{
  "account_total": 1652728.35,
  "account_totals": {
    "Robinhood": 290555.71,
    "SEP-IRA": 393728.73,
    "Schwab CSP": 687464.15,
    "Schwab #2": 211632.15,
    "Roth IRA": 69307.26
  },
  "positions": [
    {
      "ticker": "RKT",
      "company": "Rocket Companies",
      "shares": 3900,
      "current_price": 18.68,
      "value": 72892.00,
      "return_pct": 42.0,
      "return": 15716.60,
      "has_analysis": true,
      "accounts": ["Robinhood: 1,400", "SEP-IRA: 2,500"]
    }
  ],
  "options": [
    {
      "ticker": "ELF",
      "type": "PUT (Short)",
      "strike": 110.00,
      "expiration": "Feb 26, 2026",
      "quantity": -6,
      "price": 29.225,
      "value": -17535.00,
      "account": "Schwab CSP"
    }
  ],
  "cash_sg": {
    "total_cash": 14004.00,
    "total_sgov": 91993.68,
    "accounts": [
      {"name": "Robinhood", "cash": 11432.00, "sgov": 20224.62},
      {"name": "SEP-IRA", "cash": 2572.00, "sgov": 35182.00},
      {"name": "Roth IRA", "cash": 0, "sgov": 6607.06}
    ]
  },
  "eth_value": 32004.00,
  "total_value": 1536730.67,
  "total_return": 29712.00,
  "last_price_update": "2026-02-15 14:30 PST"
}
```

### GET `/api/stock/<ticker>`
**Response:**
```json
{
  "ticker": "RKT",
  "analysis": "markdown content from portfolio_tracker.md"
}
```

### GET `/api/analysis-archive`
**Response:**
```json
{
  "analyses": [
    {"ticker": "RKT", "date": "2026-02-13", "title": "...", "grade": "A"}
  ]
}
```

### GET `/api/earnings-research`
**Response:**
```json
{
  "date": "2026-02-15",
  "research": "markdown content from daily_earnings_research.md"
}
```

---

## 5. Data Parsing Strategy

### Markdown Table Parser
All tracker files use markdown tables with slightly different formats. Create a unified parser that:

1. Extracts "Total Value" from header (regex: `Total.*Value:?\*?\*?	?
?	?
?:?	?
?\$?([0-9,.]+)`)
2. Parses position tables (regex: `\|\s*(\w+)\s*\|\s*([^|]+)\|\s*([0-9,.]+)\s*\|\s*\$?([0-9,.]+)\s*\|\s*\$?([0-9,.]+)`)
3. Parses options tables separately (different format)
4. Aggregates positions across accounts by ticker

### Price Fetching Strategy
1. Cache Finnhub prices for 5 minutes
2. Batch API calls (60/min limit)
3. Store cache in memory only (not persistent)
4. Track API usage for dashboard display

### Aggregation Logic
1. Read all 5 tracker files
2. Parse positions from each
3. Merge positions with same ticker:
   - Sum shares
   - Calculate weighted avg price
   - List accounts in breakdown
4. Aggregate options separately (don't merge)
5. Sum cash/SGOV across accounts

---

## 6. Step-by-Step Implementation Plan

### Phase 1: Data Parsing Infrastructure
**Step 1:** Create markdown table parser function
- Function: `parse_markdown_table(content, table_name)`
- Returns: List of dicts with column names as keys
- Test: Parse robinhood_tracker.md stocks table

**Step 2:** Create account value extractor
- Function: `extract_account_value(content)`
- Returns: Float (total value from header)
- Test: Extract $300,124 from robinhood_tracker.md

**Step 3:** Create position aggregator
- Function: `aggregate_positions(trackers)`
- Input: Dict of tracker contents by account name
- Output: Merged positions list with account breakdown
- Test: RKT should show 3,900 shares across RH+SEP

### Phase 2: API Response Construction
**Step 4:** Build `/api/portfolio` response structure
- Add `positions` array with all required fields
- Add `options` array with CSP positions
- Add `cash_sg` breakdown
- Test: Verify response matches contract

**Step 5:** Implement `/api/stock/<ticker>`
- Read portfolio_tracker.md
- Extract analysis section for ticker
- Return markdown content
- Test: /api/stock/RKT returns analysis

**Step 6:** Implement remaining endpoints
- `/api/analysis-archive`
- `/api/earnings-research`
- `/api/schedule`
- `/api/ideas`

### Phase 3: Price Integration
**Step 7:** Add Finnhub price fetching
- Function: `get_stock_price(ticker)`
- Cache results for 5 minutes
- Track API calls in `api_usage['finnhub']`
- Test: VAW price matches Finnhub

**Step 8:** Integrate prices into portfolio endpoint
- Fetch prices for all held tickers
- Calculate current values
- Update return metrics
- Test: Portfolio values match real-time

### Phase 4: Frontend Integration
**Step 9:** Update dashboard.html
- Ensure field names match API response
- Test: Stocks table renders correctly
- Test: Options table renders correctly
- Test: Cash/SGOV section renders

**Step 10:** Add error handling
- Handle missing tracker files
- Handle API failures gracefully
- Show "last updated" timestamp
- Test: Works with partial data

---

## 7. Testing Checklist

- [ ] `/api/portfolio` returns all 5 account totals
- [ ] `/api/portfolio` returns merged positions (RKT = 3,900 shares)
- [ ] `/api/portfolio` returns options positions
- [ ] `/api/portfolio` returns cash/SGOV breakdown
- [ ] `/api/stock/RKT` returns analysis content
- [ ] `/api/analysis-archive` returns list of analyses
- [ ] Dashboard renders without JavaScript errors
- [ ] Stocks table shows correct data
- [ ] Options table shows correct data
- [ ] API usage displays correctly
- [ ] Price refresh button works

---

## 8. Open Questions

1. **Price Updates**: Should prices auto-refresh on page load, or only on manual refresh?
2. **Earnings Calendar**: Should this be hardcoded or parsed from a file?
3. **Analysis Archive**: Parse structured data from portfolio_tracker.md, or just return raw markdown?
4. **Schedule Integration**: Parse son_schedule.md or integrate with calendar API?

**DO NOT PROCEED WITH IMPLEMENTATION until these questions are answered.**

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Finnhub API rate limit (60/min) | Cache prices for 5 minutes, batch requests |
| Tracker file format changes | Use flexible regex parsers, log parsing errors |
| Server crash | launchd KeepAlive=true auto-restarts |
| Data inconsistency | Single source of truth: tracker files only |
| Port conflicts | mc.sh checks port before starting |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-15
**Status:** Awaiting Review
