# Technical Design Spec: Rebuild Unified Tracker with Cost Basis

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Goal
Rebuild unified portfolio tracker with standardized cost basis columns for all accounts, and update parser to calculate returns from any available data source.

---

## Problem Statement

**Current Issue:**
- Robinhood has "Total Return" column
- SEP-IRA, Schwab CSP, Schwab #2 missing cost basis data in unified tracker
- Parser only looks for "Total Return" column
- Returns showing $0 for 3 of 5 accounts

**Solution:**
1. Add consistent columns to all accounts in unified tracker
2. Update parser to calculate returns from available data:
   - If "Total Return" exists → use it
   - If "Cost Basis" exists → calculate: Return = Current Value - Cost Basis
   - Calculate return % = (Return / Cost Basis) × 100

---

## Affected Files

| File | Path | Changes | Lines |
|------|------|---------|-------|
| Unified tracker | `~/.openclaw/workspace/portfolio/unified_portfolio_tracker.md` | Rebuild with cost basis columns | ~300 |
| Server parser | `~/.openclaw/workspace/mission_control/server.py` | Update parse_unified_tracker() | ~20 |

**Estimated Scope:** ~320 lines across 2 files

---

## Unified Tracker Column Standard

All accounts will have:
```markdown
| Ticker | Company | Shares | Current Price | Current Value | Cost Basis | Total Return | Return % |
```

- **Cost Basis:** Total cost of position (shares × cost/share)
- **Total Return:** Dollar gain/loss (can be blank, calculated from Cost Basis)
- **Return %:** Percentage return (can be blank, calculated)

---

## Parser Logic Update

```python
# For each position row:
current_value = float(row.get('Current Value', '$0').replace('$', '').replace(',', ''))
cost_basis_str = row.get('Cost Basis', '$0').replace('$', '').replace(',', '')
total_return_str = row.get('Total Return', '+$0').replace('+', '').replace('-', '').replace('$', '').replace(',', '')

# Priority 1: Use Total Return if provided
try:
    total_return = float(total_return_str)
    if row.get('Total Return', '').startswith('-'):
        total_return = -total_return
except:
    total_return = None

# Priority 2: Calculate from Cost Basis if available
try:
    cost_basis = float(cost_basis_str)
    if total_return is None:
        total_return = current_value - cost_basis
    return_pct = (total_return / cost_basis * 100) if cost_basis > 0 else 0
except:
    return_pct = 0
    if total_return is None:
        total_return = 0
```

---

## Step-by-Step Implementation

### Step 1: Backup current unified tracker
**File:** `unified_portfolio_tracker.md`  
**Action:** Copy to `unified_portfolio_tracker_backup.md`  
**Verification:** Backup file exists

### Step 2: Rebuild unified tracker with standard columns
**File:** `unified_portfolio_tracker.md`  
**Lines:** ~300 (rewrite)  

**For each account:**
1. Add "Cost Basis" column header
2. Add "Total Return" column header  
3. Add "Return %" column header
4. Populate data from archived tracker files

**Data sources:**
- Robinhood: Use existing Total Return data
- SEP-IRA: Calculate from archived tracker cost basis
- Schwab CSP: Calculate from archived tracker
- Schwab #2: Calculate from archived tracker
- Roth IRA: Use existing data

### Step 3: Update parse_unified_tracker()
**File:** `server.py`  
**Lines:** ~20 modified  
**Function:** Update position parsing to extract cost basis and calculate returns  
**Verification:** Parser returns return data for all positions

### Step 4: Test calculations
**Verification:**
```bash
curl -s http://localhost:8080/api/portfolio | python3 -c "
import json,sys
d=json.load(sys.stdin)
for p in d['positions'][:5]:
    print(f\"{p['ticker']}: Return=\${p['return']:.2f} ({p['return_pct']:.1f}%)\")
"
```

### Step 5: Restart and verify
**Action:** `./mc.sh restart`  
**Verification:** All positions show calculated returns

### Step 6: Update V1.3 backup
**Action:** Copy fixed files to `v1.3_backup/`  
**Verification:** Backup updated

---

## Rollback Strategy

If rebuild fails:
1. Stop server
2. Restore from `unified_portfolio_tracker_backup.md`
3. Restart server

---

## Verification Checklist

- [ ] Unified tracker has consistent columns for all 5 accounts
- [ ] Cost Basis populated for all positions
- [ ] Parser calculates returns correctly
- [ ] API returns non-zero returns for all positions
- [ ] Dashboard displays correct return percentages
- [ ] Backup created

---

**Awaiting Proceed command.**
