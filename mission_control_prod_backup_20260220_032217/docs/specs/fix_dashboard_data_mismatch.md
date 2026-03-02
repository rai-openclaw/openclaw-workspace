# Technical Design Spec: Fix Dashboard Data Mismatch

**Version:** 1.1  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Issue 1: Portfolio Table Error

### Problem
Dashboard shows "Error loading portfolio data"

### Root Cause
Dashboard expects `pos.current_price`, API returns `pos.price`

### Solution
Change API field from `'price'` to `'current_price'`

---

## Issue 2: Earnings Research Error

### Problem
Dashboard shows "Error loading research data"

### Root Cause
Dashboard expects array, API returns object `{"content": "..."}`

### Solution
Update dashboard to handle object format

---

## Issue 3: Stock Analysis Missing Extended Data

### Problem
Analysis archive no longer shows price targets, thesis, or extended data when clicked

### Root Cause
When I updated the API to add `full_text`, I may have broken the parsing logic that extracts specific fields (price targets, thesis, etc.)

### Investigation Needed
Check current `api_analysis_archive()` implementation:
- Does it still parse grade correctly?
- Does it extract price targets from markdown?
- Does it preserve all section content?

### Solution Options
- **Option A**: Enhance parsing to extract structured fields (thesis, price targets, etc.)
- **Option B**: Use full_text and parse on frontend (simpler, more flexible)

**Recommended: Option A** (maintain structured data)

---

## Affected Files

| File | Path | Changes |
|------|------|---------|
| Server API | `server.py` | Fix `price`→`current_price`, fix analysis parsing |
| Dashboard | `templates/dashboard.html` | Fix earnings research handling |

**Estimated Scope:** ~30 lines across 2 files

---

## Implementation Steps

### Step 1: Fix position field name
Change `'price'` to `'current_price'` in position aggregation

### Step 2: Fix analysis archive parsing
Ensure it extracts: grade, price targets, thesis, all sections properly

### Step 3: Fix earnings research handling
Handle object format instead of array

### Step 4: Restart and verify all sections

### Step 5: Update backup

---

**Awaiting Proceed command.**
