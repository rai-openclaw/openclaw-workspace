# Technical Design Spec: Fix All Issues v2.1

**Version:** 2.1  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Issues Identified & Root Causes

### Issue 1: Missing API Endpoints (CRITICAL)
**What broke:** Stock Analysis Archive, Daily Earnings Research, Ideas & Notes tabs show "Error loading"

**Root cause:** When rewriting server.py for v2, I only kept `/api/portfolio` and `/api/refresh-prices`. Removed all other endpoints:
- `/api/analysis-archive`
- `/api/earnings-research`
- `/api/ideas`
- `/api/schedule`
- `/api/corporate`
- etc.

**Fix:** Restore ALL original API endpoints in server.py

---

### Issue 2: Cost Basis Display (DATA)
**Current:** Showing `total_cost_basis` (aggregated across accounts)
**Should show:** Cost basis per share OR cost basis for that specific holding

**Example:**
- RKT total: 4,700 shares
- Total cost basis: $65,759
- **Display:** $65,759 (not per share - that's the actual cost basis for the position)

Actually, re-reading: "single stock value only" means show the total cost basis for that ticker (not per-account breakdown in the main column). This is already correct in v2.

**Clarification needed:** Show total cost basis for the position (current behavior) or per-share cost?

---

### Issue 3: P/L% Missing
**What was removed:** Return dollar amount column
**What should stay:** Return % (P/L percentage)

**Fix:** Add back `return_pct` column with color coding (green/red)

---

### Issue 4: Color Formatting Lost
**Missing:** Green for positive returns, red for negative
**Fix:** Restore CSS classes `positive`/`negative` with color coding

---

### Issue 5: Account Column Shows Shares
**Current:** "Robinhood: 1,400 shares"
**Should be:** "Robinhood: $26,152" (value, not shares)

**Fix:** Change account breakdown to show dollar value per account

---

## Implementation Plan

### Step 1: Restore All API Endpoints
Add back to server.py:
- `/api/analysis-archive` - Parse portfolio_tracker.md
- `/api/earnings-research` - Read daily_earnings_research.md
- `/api/ideas` - Parse ideas/NOTES.md
- `/api/schedule` - Parse son_schedule.md
- `/api/corporate` - Return hardcoded structure
- `/api/usage` - Return API usage stats
- `/api/system/spec` - Read TDS file

### Step 2: Fix Portfolio Display
Update dashboard JavaScript:
1. **Keep Cost Basis:** Show `total_cost_basis` (already correct)
2. **Add P/L%:** Add column with `return_pct` and color coding
3. **Color coding:** Green for positive, red for negative
4. **Account values:** Show `$value` not `shares` count

### Step 3: Column Structure

**Stocks & ETFs:**
| Ticker | Shares | Price | Cost Basis | Value | P/L % | Accounts |

**Options:**
| Ticker | Type | Strike | Expiration | Contracts | Entry Premium | Value | Accounts |

**Cash:**
| Asset | Total | Details | Accounts |

**Misc:**
| Asset | Amount | Price | Cost Basis | Value | P/L % | Accounts |

### Step 4: Account Breakdown Format
Show value in each account:
```
▼ 3 accounts
  Robinhood: $26,152
  SEP-IRA: $46,700  
  Roth IRA: $14,944
```

Not:
```
▼ 3 accounts
  Robinhood: 1,400 shares  ← WRONG
```

---

## Verification

After fix:
- [ ] All tabs load without errors
- [ ] Portfolio shows all 5 sections
- [ ] Cost basis column visible
- [ ] P/L % column with color coding
- [ ] Account breakdown shows dollar values
- [ ] Green/red colors for returns
- [ ] All other tabs (Earnings, Analysis, Ideas, etc.) working

---

**Awaiting Proceed.**
