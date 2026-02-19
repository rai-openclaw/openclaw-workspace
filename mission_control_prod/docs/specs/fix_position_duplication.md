# Technical Design Spec: Fix Position Duplication in Portfolio API

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Problem Statement

**Current Issue:**
Positions are appearing multiple times in `/api/portfolio` response - once per account that holds them.

**Example:**
- RKT appears 3 times (Robinhood, SEP-IRA, Roth IRA)
- CRM appears 3 times (SEP-IRA, Schwab #2, Roth IRA)
- AMD appears 3 times (Robinhood, SEP-IRA, Roth IRA)

**Expected Behavior:**
Each ticker should appear once with aggregated data across all accounts.

---

## Root Cause

The `api_portfolio()` function in `server.py` creates separate position entries for each account's holdings instead of aggregating them.

---

## Affected Files

| File | Path | Changes |
|------|------|---------|
| Server API | `server.py` | Fix position aggregation logic in `api_portfolio()` |
| Dashboard | `templates/dashboard.html` | Add cost basis column to options table |

**Estimated Scope:** ~35 lines across 2 files

---

## Solution

### Fix 1: Position Aggregation Logic

Replace duplicate-creating logic with proper aggregation that sums cost basis and returns across all accounts holding the same ticker.

### Fix 2: Options Cost Basis Column

Add cost basis column to options table in dashboard.

---

## Step-by-Step Implementation

### Step 1: Fix position aggregation
**File:** `server.py`  
**Lines:** ~30 modified  
**Verification:** API returns 9 unique positions (not 18)

### Step 2: Add options cost basis column
**File:** `dashboard.html`  
**Lines:** ~5 modified

### Step 3: Restart and verify
**Action:** `./mc.sh restart`  
**Verification:** No duplicates, options show cost basis

### Step 4: Update V1.3 backup

---

## Verification Checklist

- [ ] API returns 9 unique positions (not 18 duplicates)
- [ ] RKT shows 4,700 shares total (aggregated)
- [ ] Options table has cost basis column
- [ ] Dashboard displays correctly

---

**Awaiting Proceed command before implementation.**
