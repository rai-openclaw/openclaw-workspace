# Summary TDS: Fix All Issues v2.1

**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## What I'll Fix

### 1. Missing API Endpoints (Root Cause of Broken Tabs)
**Files:** `server.py`  
**Lines to add:** ~100 lines  
**Endpoints to restore:**
- `/api/analysis-archive` - Returns stock analysis from portfolio_tracker.md
- `/api/earnings-research` - Returns earnings research markdown
- `/api/ideas` - Returns ideas from NOTES.md
- `/api/schedule` - Returns schedule data
- `/api/corporate` - Returns team structure
- `/api/usage` - Returns API usage stats

**Why broken:** I removed these when rewriting server.py for v2

---

### 2. Portfolio Display Fixes
**File:** `templates/dashboard.html` (JavaScript only)  
**Lines to modify:** ~80 lines in `loadPortfolio()` function

**Changes:**

| Issue | Current | Fix |
|-------|---------|-----|
| **Cost Basis** | Shows total ($65,759) | Show per-share ($13.99) |
| **P/L%** | Missing | Add back with color coding |
| **Colors** | Plain text | Green=positive, Red=negative |
| **Account column** | Shows "1,400 shares" | Show "$26,152" (dollar value) |

**Column Structure (Final):**

**Stocks:**
| Ticker | Shares | Price | Cost Basis/Share | Value | P/L % | Accounts |

**Options:**
| Ticker | Type | Strike | Exp | Contracts | Entry Premium | Value | Accounts |

**Cash:**
| Asset | Total | Details | Accounts |

**Misc:**
| Asset | Amount | Price | Cost Basis/Share | Value | P/L % | Accounts |

---

## Files to Modify

| File | Changes | Lines |
|------|---------|-------|
| `server.py` | Add 6 API endpoints | ~100 lines added |
| `templates/dashboard.html` | Fix loadPortfolio() JS | ~80 lines modified |

**Total:** ~180 lines across 2 files

---

## Calculation Logic

### Cost Basis Per Share
```javascript
// Stocks
costBasisPerShare = stock.total_cost_basis / stock.total_shares

// Misc (like ETH)
costBasisPerShare = item.total_cost_basis / item.total_amount
```

### Account Breakdown (Dollar Values)
```javascript
// For each account in stock.accounts
accountValue = account.shares * stock.price
show: "${account.account}: ${formatCurrency(accountValue)}"

// Not: "${account.account}: ${account.shares} shares"
```

### P/L % Color Coding
```javascript
if (return_pct > 0) class = 'positive' // Green
if (return_pct < 0) class = 'negative' // Red
```

---

## Verification Checklist

After implementation:
- [ ] Stock Analysis Archive tab loads
- [ ] Daily Earnings Research tab loads
- [ ] Ideas & Notes tab loads
- [ ] Portfolio shows Cost Basis per share
- [ ] Portfolio shows P/L % with green/red colors
- [ ] Account column shows dollar values
- [ ] All 5 portfolio sections display correctly
- [ ] Other tabs (Earnings, Corporate, API Usage, etc.) work

---

**Proceed with implementation?**
