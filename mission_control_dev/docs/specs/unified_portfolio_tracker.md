# Technical Design Spec: Unified Portfolio Tracker

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Goal
Migrate from 5 separate portfolio tracker files to a single unified tracker that dynamically supports any number of accounts without code changes.

---

## Problem Statement

**Current State:**
- 5 hardcoded tracker files: `robinhood_tracker.md`, `sep_ira_tracker.md`, `schwab_csp_tracker.md`, `schwab_secondary_tracker.md`, `roth_ira_tracker.md`
- Server.py has hardcoded dictionary of 5 accounts
- Adding 6th account requires:
  - New file creation
  - Code changes in server.py (3+ places)
  - Dashboard updates
  - mc.sh updates
- Violates data-driven architecture principle

**Desired State:**
- Single file: `portfolio/unified_portfolio_tracker.md`
- Dynamic account parsing (no hardcoded account names)
- Add new account = add new section to unified file (zero code changes)
- Server automatically discovers all accounts from file

---

## Affected Files

| File | Path | Changes | Lines |
|------|------|---------|-------|
| New unified tracker | `~/.openclaw/workspace/portfolio/unified_portfolio_tracker.md` | Create new | ~300 |
| Server.py | `~/.openclaw/workspace/mission_control/server.py` | Replace 5-file logic with unified parser | ~50 |
| Dashboard (Webapp) | `~/.openclaw/workspace/mission_control/templates/dashboard.html` | Dynamic account cards, remove hardcoded names | ~15 |
| TDS Spec | `~/.openclaw/workspace/mission_control/docs/specs/mission_control_spec.md` | Update data sources section | ~5 |
| Archive old files | `~/.openclaw/workspace/portfolio/` | Move to `portfolio/archive/` | 5 files |

**Estimated Scope:** 65-70 lines across 4 files + 1 new file creation

---

## Unified File Format

**File:** `portfolio/unified_portfolio_tracker.md`

```markdown
# Unified Portfolio Tracker
**Last Updated:** 2026-02-15

---

## Account: Robinhood
**Type:** Taxable Brokerage  
**Broker:** Robinhood  
**Total Value:** $300,124

### Stock Positions
| Ticker | Company | Shares | Current Price | Current Value | Total Return |
|--------|---------|--------|---------------|---------------|--------------|
| RKT | Rocket Companies | 1,400 | $18.68 | $26,152.00 | +$7,716.60 |
| SHOP | Shopify | 440 | $112.70 | $49,588.00 | +$8,287.33 |
| ... | ... | ... | ... | ... | ... |

### Options Positions
| Ticker | Type | Strike | Expiration | Quantity | Price | Value |
|--------|------|--------|------------|----------|-------|-------|
| PYPL | PUT (Short) | $45.00 | Feb 20, 2026 | -10 | $4.50 | -$45,000 |

### Cash & Equivalents
| Position | Shares | Price | Value |
|----------|--------|-------|-------|
| SGOV | 201.20 | $100.52 | $20,224.62 |
| Cash | - | - | $11,432.00 |

### Crypto
| Asset | Amount | Current Price | Value |
|-------|--------|---------------|-------|
| ETH | 11.43 | $2,800.00 | $32,004.00 |

---

## Account: SEP-IRA
**Type:** Retirement (SEP-IRA)  
**Broker:** Schwab  
**Total Value:** $393,728.73

### Stock Positions
| Ticker | Company | Shares | Current Price | Current Value |
|--------|---------|--------|---------------|---------------|
| HOOD | Robinhood | 700 | $76.07 | $53,249.00 |
| RKT | Rocket Companies | 2,500 | $18.88 | $47,200.00 |
| ... | ... | ... | ... | ... |

### Options Positions
| Ticker | Type | Strike | Expiration | Quantity | Price | Value |
|--------|------|--------|------------|----------|-------|-------|
| FIGR | CALL (Short) | $42.50 | Feb 26, 2026 | -1 | $0.20 | -$20.00 |

### Cash & Equivalents
| Position | Shares | Price | Value |
|----------|--------|-------|-------|
| SGOV | 350 | $100.52 | $35,182.00 |
| Cash | - | - | $2,572.00 |

---

## Account: Schwab CSP
**Type:** Taxable (Margin)  
**Broker:** Schwab  
**Total Value:** $687,464.15

### Stock Positions
| Ticker | Company | Shares | Current Price | Current Value |
|--------|---------|--------|---------------|---------------|
| ELF | e.l.f. Beauty | 200 | $81.47 | $16,294.00 |
| TTD | The Trade Desk | 600 | $25.82 | $15,492.00 |

### Index Funds (Collateral)
| Ticker | Fund Name | Shares | Current Price | Current Value |
|--------|-----------|--------|---------------|---------------|
| VSEQX | Vanguard Extended Market | 5,860.559 | $39.46 | $231,573.34 |
| VTCLX | Vanguard Tax-Managed Capital | 446.53 | $352.09 | $157,218.75 |
| VTMSX | Vanguard Tax-Managed Small Cap | 2,514.233 | $107.22 | $269,576.06 |

### CSP Positions (Short Puts)
| Ticker | Type | Strike | Expiration | Quantity | Price | Value |
|--------|------|--------|------------|----------|-------|-------|
| ELF | PUT (Short) | $110.00 | Feb 26, 2026 | -6 | $29.225 | -$17,535.00 |
| AMD | PUT (Short) | $220.00 | Feb 26, 2026 | -4 | $14.275 | -$5,710.00 |

---

## Account: Schwab #2
**Type:** Taxable (Margin)  
**Broker:** Schwab  
**Total Value:** $211,632.15

### Stock Positions
| Ticker | Company | Shares | Current Price | Current Value |
|--------|---------|--------|---------------|---------------|
| CRM | Salesforce | 320 | $189.72 | $60,710.40 |
| AMZN | Amazon | 265 | $198.95 | $52,721.75 |
| GOOG | Alphabet | 170 | $306.00 | $52,020.00 |
| MSFT | Microsoft | 115.3923 | $400.20 | $46,180.00 |

### CSP Positions (Short Puts)
| Ticker | Type | Strike | Expiration | Quantity | Price | Value |
|--------|------|--------|------------|----------|-------|-------|
| AMD | PUT (Short) | $200.00 | Mar 26, 2026 | -1 | $7.330 | -$7,330.00 |
| ELF | PUT (Short) | $105.00 | Mar 26, 2026 | -2 | $25.000 | -$5,000.00 |

---

## Account: Roth IRA
**Type:** Retirement (Roth IRA)  
**Broker:** Schwab  
**Total Value:** $69,307.26

### Stock Positions
| Ticker | Company | Shares | Current Price | Current Value |
|--------|---------|--------|---------------|---------------|
| AMD | AMD | 100 | $206.77 | $20,677.00 |
| RKT | Rocket Companies | 800 | $18.68 | $14,944.00 |
| CRM | Salesforce | 60 | $189.72 | $11,383.20 |
| NKE | Nike | 100 | $63.00 | $6,300.00 |
| FUBO | FuboTV | 4,000 | $1.34 | $5,360.00 |
| PYPL | PayPal | 100 | $40.36 | $4,036.00 |

### Cash & Equivalents
| Position | Shares | Price | Value |
|----------|--------|-------|-------|
| SGOV | 65.7288 | $100.52 | $6,607.06 |

---

## Cross-Account Summary

### Total Portfolio Value
| Account | Value |
|---------|-------|
| Robinhood | $300,124.00 |
| SEP-IRA | $393,728.73 |
| Schwab CSP | $687,464.15 |
| Schwab #2 | $211,632.15 |
| Roth IRA | $69,307.26 |
| **Grand Total** | **$1,662,256.29** |

### Position Overlaps
| Ticker | Total Shares | Accounts |
|--------|--------------|----------|
| RKT | 4,700 | Robinhood (1,400), SEP-IRA (2,500), Roth IRA (800) |
| CRM | 420 | SEP-IRA (40), Schwab #2 (320), Roth IRA (60) |
| AMD | 300 | Robinhood (100), SEP-IRA (100), Roth IRA (100) |
| NKE | 603.42 | Robinhood (203.42), SEP-IRA (300), Roth IRA (100) |

### Options Exposure
| Ticker | Total Contracts | Strategy |
|--------|-----------------|----------|
| ELF | -8 contracts | CSP (6 Schwab CSP + 2 Schwab #2) |
| AMD | -5 contracts | CSP (4 Schwab CSP + 1 Schwab #2) |
| FIGR | -3 contracts | Covered calls (SEP-IRA) |
| PYPL | -10 contracts | CSP (Robinhood) |

---

*Data Source: Brokerage statements via Finnhub API*  
*Last Price Update: 2026-02-15 15:30 PST*
```

---

## API/Contract Changes

### Current API Response (Before)
```json
{
  "account_totals": {
    "Robinhood": 300124,
    "SEP-IRA": 393728.73,
    "Schwab CSP": 687464.15,
    "Schwab #2": 211632.15,
    "Roth IRA": 69307.26
  }
}
```

### New API Response (After)
Same structure, but dynamically generated from parsed accounts.
If you add "## Account: Fidelity" section, it automatically appears in API.

**No breaking changes** - response schema identical, just source is unified file.

---

## New Parser Functions

### `parse_unified_tracker(filepath)`
**Purpose:** Parse single unified file into structured data  
**Returns:**
```python
{
  "accounts": {
    "Robinhood": {
      "type": "Taxable Brokerage",
      "broker": "Robinhood",
      "total_value": 300124.00,
      "positions": [...],
      "options": [...],
      "cash_sg": {...},
      "crypto": {...}
    },
    "SEP-IRA": {...},
    ...
  },
  "grand_total": 1662256.29,
  "overlaps": {...}
}
```

### `extract_accounts_from_unified(content)`
**Purpose:** Find all "## Account: Name" sections dynamically  
**Returns:** List of account names (no hardcoding)

---

## Step-by-Step Implementation

### Step 1: Create unified tracker file
**File:** `portfolio/unified_portfolio_tracker.md`  
**Lines:** ~300 (migrating from 5 files)  
**Verification:** File exists, all 5 accounts present

### Step 2: Create unified parser function
**File:** `server.py`  
**Lines:** ~40 new lines  
**Function:** `parse_unified_tracker()`  
**Verification:** Parse test returns all 5 accounts

### Step 3: Update api_portfolio endpoint
**File:** `server.py`  
**Lines:** ~15 modified  
**Change:** Replace hardcoded 5-file logic with unified parser  
**Verification:** `/api/portfolio` returns identical data

### Step 4: Update api_usage endpoint (account totals source)
**File:** `server.py`  
**Lines:** ~5 modified  
**Change:** Source from unified file instead of separate trackers  
**Verification:** Account totals correct

### Step 5: Update Dashboard (Webapp)
**File:** `templates/dashboard.html`  
**Lines:** ~15-15 modified  

**Changes Required:**
1. **Sidebar navigation** - Remove hardcoded account names in portfolio view
2. **Account breakdown cards** - Make account cards dynamically generated from API
3. **Portfolio table** - Ensure accounts column reads from unified data
4. **JavaScript `loadPortfolio()` function** - Update to handle dynamic account list

**Current Hardcoded (to remove):**
```javascript
// Example of what to remove/replace:
{ name: 'Robinhood', value: data.account_totals['Robinhood'] }
// Replace with dynamic loop over data.account_totals keys
```

**Verification:** 
- Dashboard renders all 5 accounts
- Adding test account to unified file shows new account in UI
- No account names hardcoded in HTML/JS

### Step 6: Update mission_control_spec.md
**File:** `docs/specs/mission_control_spec.md`  
**Lines:** ~5 modified  
**Change:** Update data sources table  
**Verification:** Spec reflects unified architecture

### Step 7: Archive old tracker files
**Action:** Move 5 old files to `portfolio/archive/`  
**Verification:** Old files not in main portfolio directory

### Step 8: Test new account addition
**Action:** Add "## Account: Test" section to unified file  
**Verification:** New account appears in API without code changes

### Step 9: Full integration test
**Verification:**
- All API endpoints work
- Dashboard displays correctly
- No errors in server.log
- 3 restart cycles pass

### Step 10: Create V1.3 backup
**Action:** Backup to `v1.3_backup/`  
**Verification:** All files backed up

---

## Rollback Strategy

If unified tracker fails:
1. Stop server: `./mc.sh stop`
2. Restore old files from `portfolio/archive/`
3. Restore server.py from `v1.2_backup/`
4. Start server: `./mc.sh start`

**Last Known Good:** V1.2 in `v1.2_backup/`

---

## Benefits

1. **Scalable:** Add accounts without code changes
2. **Maintainable:** Single file to update
3. **Visible:** Cross-account overlaps clear
4. **Data-Driven:** No hardcoded account names
5. **DRY:** No duplicate parsing logic

---

## Verification Checklist

- [ ] Unified file created with all 5 accounts
- [ ] Parser extracts all accounts dynamically
- [ ] API returns identical data structure
- [ ] Dashboard renders without hardcoded names
- [ ] Adding test account works without code changes
- [ ] Old files archived
- [ ] V1.3 backup created

---

**Awaiting Proceed command before implementation.**
