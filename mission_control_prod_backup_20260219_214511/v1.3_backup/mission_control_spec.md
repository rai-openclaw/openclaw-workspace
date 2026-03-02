# Mission Control Technical Specification
**Version:** V1.1  
**Last Updated:** 2026-02-15 (V1.1)  
**Status:** Baseline Complete  

---

## Overview

Mission Control is a unified personal dashboard that aggregates portfolio data, trading research, scheduling, and API usage tracking into a single interface. All data is file-driven with no hardcoded values.

---

## Architecture

### Tech Stack
- **Backend:** Flask (Python 3.9)
- **Frontend:** Vanilla HTML/CSS/JS
- **Server:** Port 8080, managed by launchd
- **Data Storage:** Markdown files (human-readable, version controllable)

### File Structure
```
mission_control/
├── server.py                  # Flask application
├── templates/
│   └── dashboard.html         # Single-page frontend
├── mc.sh                      # Control script
├── docs/
│   └── specs/
│       └── mission_control_spec.md    # This file
├── v1_backup/                 # Baseline backup
└── server.log                 # Runtime logs
```

---

## Data Sources

| Data Element | Source File | Parsed By |
|--------------|-------------|-----------|
| Account Values | `../portfolio/unified_portfolio_tracker.md` | `parse_unified_tracker()` | `parse_tracker_for_value()` |
| Stock Positions | `../portfolio/unified_portfolio_tracker.md` | `parse_unified_tracker()` | `aggregate_positions()` |
| Options Positions | `../portfolio/{account}_tracker.md` options tables | `parse_markdown_table()` |
| Cash & SGOV | `../portfolio/{account}_tracker.md` cash sections | `parse_cash_positions()` |
| ETH Holdings | `../portfolio/robinhood_tracker.md` crypto table | `parse_crypto_holdings()` |
| Ideas | `../ideas/NOTES.md` | `api_ideas()` |
| Stock Analysis | `../portfolio/portfolio_tracker.md` sections | `api_analysis_archive()` |
| Earnings Research | `../daily_earnings_research.md` | `api_earnings_research()` |
| Schedule | `../son_schedule.md` | `api_schedule()` |
| API Usage | Runtime tracking in `api_usage` dict | `api_usage_dashboard()` |

---

## API Contract

### GET `/api/portfolio`
**Data Sources:**
- Account totals: Parsed from 5 tracker file headers
- Positions: Aggregated from stock tables across all trackers
- Cash/SGOV: Parsed from cash sections in each tracker
- ETH: Parsed from crypto table in robinhood_tracker.md

**Response Schema:**
```json
{
  "account_total": "<sum of all account values>",
  "account_totals": {
    "<account_name>": "<parsed value from header>"
  },
  "positions": [
    {
      "ticker": "<from table>",
      "company": "<from table>",
      "shares": "<aggregated across accounts>",
      "current_price": "<from table or API>",
      "value": "<calculated>",
      "return": "<calculated from cost basis>",
      "return_pct": "<calculated>",
      "has_analysis": "<boolean: ticker in portfolio_tracker.md>",
      "accounts": ["<account>: <shares>"]
    }
  ],
  "total_value": "<sum of position values>",
  "total_return": "<sum of position returns>",
  "cash_sg": {
    "total_cash": "<sum across accounts>",
    "total_sgov": "<sum across accounts>",
    "accounts": [{"name": "<account>", "cash": "<value>", "sgov": "<value>"}]
  },
  "eth_value": "<from crypto table>",
  "last_updated": "<ISO timestamp>"
}
```

### GET `/api/usage`
**Data Source:** Runtime tracking in `api_usage` dictionary

**Response Schema:**
```json
{
  "apis": {
    "<api_name>": {
      "name": "<display name>",
      "purpose": "<description>",
      "status": "<Active|Inactive>",
      "tier": "<Free|Paid>",
      "limit": "<rate limit>",
      "calls_this_month": "<counter>",
      "cost": "<accumulated cost>",
      "billing_url": "<URL from config>",
      "key": "<location from config>"
    }
  },
  "total_estimated_cost": "<sum of all costs>"
}
```

### GET `/api/ideas`
**Data Source:** `../ideas/NOTES.md`

**Response Schema:**
```json
[
  {
    "category": "<### header text>",
    "content": "<text after '- Idea:'>"
  }
]
```

### GET `/api/analysis-archive`
**Data Source:** `../portfolio/portfolio_tracker.md` (ticker sections)

**Response Schema:**
```json
[
  {
    "ticker": "<from ## Ticker header>",
    "company": "<from holdings table>",
    "current_price": "<from API or table>",
    "grade": "<parsed from Status column>",
    "date": "<parsed from 'Updated' text>",
    "summary": "<first 200 chars of section>"
  }
]
```

### GET `/api/earnings-research`
**Data Source:** `../daily_earnings_research.md`

**Response Schema:**
```json
{
  "content": "<full markdown content>"
}
```

### GET `/api/stock/<ticker>`
**Data Source:** `../portfolio/portfolio_tracker.md` (ticker-specific section)

**Response Schema:**
```json
{
  "ticker": "<requested ticker>",
  "analysis": "<section content for ticker>",
  "note": "<status message>"
}
```

### POST `/api/refresh-prices`
**Data Source:** CoinGecko API (cached for 5 minutes)

**Response Schema:**
```json
{
  "eth_price": "<from CoinGecko API>",
  "timestamp": "<ISO timestamp>"
}
```

### GET `/api/system/spec`
**Data Source:** `docs/specs/mission_control_spec.md` (this file)

**Response Schema:**
```json
{
  "version": "<from header>",
  "last_updated": "<from header>",
  "architecture": "<overview section>",
  "data_sources": [{"element": "<name>", "source": "<file>", "parser": "<function>"}],
  "apis": [{"endpoint": "<path>", "source": "<data source>", "schema": "<description>"}]
}
```

---

## Frontend Views

| View | Data Endpoint | Description |
|------|---------------|-------------|
| Portfolio | `/api/portfolio` | Aggregated holdings, options, cash breakdown |
| Earnings Calendar | Hardcoded (needs data file) | Upcoming earnings dates |
| Analysis Archive | `/api/analysis-archive` | Searchable stock research cards |
| Earnings Research | `/api/earnings-research` | Bob's daily CSP research |
| Schedule | Placeholder | Events and reminders |
| Ideas | `/api/ideas` | Categorized ideas list |
| Corporate | Hardcoded JS | Team hierarchy structure |
| API Usage | `/api/usage` | API tracking dashboard |
| System Spec | `/api/system/spec` | This technical specification |

---

## Key Functions

### Data Parsing
| Function | Purpose | Data Sources |
|----------|---------|--------------|
| `parse_markdown_table()` | Parse markdown tables into dicts | All `*_tracker.md` files |
| `parse_tracker_for_value()` | Extract account value from headers | `*_tracker.md` headers |
| `aggregate_positions()` | Merge positions across accounts | 5 tracker files |
| `parse_cash_positions()` | Extract cash/SGOV data | Cash sections in trackers |
| `parse_crypto_holdings()` | Extract ETH amount and value | `robinhood_tracker.md` |
| `read_file()` | Safe file reading | All markdown sources |

### Price Fetching
| Function | Purpose | Data Source |
|----------|---------|-------------|
| `get_cached_crypto_price()` | Fetch ETH price | CoinGecko API |

---

## Control Commands

```bash
cd ~/.openclaw/workspace/mission_control
./mc.sh start    # Start server on port 8080
./mc.sh stop     # Stop server
./mc.sh restart  # Restart server
./mc.sh status   # Check if running
```

---

## Development Protocol

### Before Implementing Features
1. **Create TDS** in `docs/specs/[feature-name].md`
2. **Specify data sources** - Which files will drive the feature
3. **Define API contract** - Request/response schemas
4. **List affected files** - Full paths to all modified files
5. **Step-by-step plan** - 5-10 implementation steps
6. **Wait for "Proceed"** - No code until confirmed

### Contract-First Coding
- No breaking changes to existing APIs
- If signature change required, update all references
- Test after every file edit

### State Sync (every 3-5 edits)
- [Current Progress] What's done
- [Active Task] What's in progress  
- [Verified Working Features] What's tested

---

## Change Log

### V1.0 (2026-02-15)
- Initial working baseline
- 5 account aggregation
- File-driven data architecture
- API usage tracking
- Technical specification viewer

---

**Dashboard URL:** http://localhost:8080  
**This Spec:** `/api/system/spec`  
**Control Script:** `mc.sh`
