# Technical Design Spec: Fix Three API Issues

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Awaiting Proceed

---

## Issue 1: Portfolio Table Error

### Confirmed Problem
Dashboard JavaScript error when accessing `pos.current_price.toFixed(2)` - field is undefined

### Confirmed Root Cause
- **Dashboard location:** templates/dashboard.html line 1037
- **Dashboard expects:** `pos.current_price`
- **API location:** server.py function `api_portfolio()` 
- **API returns:** `pos.price` (wrong field name)

### Implementation

**File:** `server.py`  
**Function:** `api_portfolio()` (around line 407-420)  
**Change type:** 1 field rename  
**Lines affected:** 3 lines

**Before:**
```python
all_positions[ticker] = {
    'ticker': ticker,
    'company': pos.get('company', ''),
    'shares': 0,
    'cost_basis': 0,
    'return': 0,
    'value': 0,
    'price': pos.get('price', 0),  # <-- WRONG
    'accounts': []
}
```

**After:**
```python
all_positions[ticker] = {
    'ticker': ticker,
    'company': pos.get('company', ''),
    'shares': 0,
    'cost_basis': 0,
    'return': 0,
    'value': 0,
    'current_price': pos.get('price', 0),  # <-- FIXED
    'accounts': []
}
```

---

## Issue 2: Earnings Research Error

### Confirmed Problem
Dashboard shows "Error loading research data" because it tries to access `.length` on object

### Confirmed Root Cause
- **Dashboard location:** templates/dashboard.html function `loadEarningsResearch()` lines 1367-1400
- **Dashboard expects:** Array with `research.length` and `research.forEach()`
- **API location:** server.py function `api_earnings_research()` 
- **API returns:** `{"content": "markdown text"}` (object, not array)

### Implementation

**File:** `templates/dashboard.html`  
**Function:** `loadEarningsResearch()`  
**Change type:** Handle object format instead of array  
**Lines affected:** ~15 lines (rewrite function body)

**Before:**
```javascript
async function loadEarningsResearch() {
    try {
        const response = await fetch('/api/earnings-research');
        const research = await response.json();
        
        let html = `
            <div class="card">
                <input type="text" placeholder="Search by ticker..." onkeyup="filterEarningsResearch(this.value)" style="width: 100%; padding: 0.75rem; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); margin-bottom: 1rem;">
                <div style="font-size: 0.8125rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    ${research.length} reports • Sorted by date (latest first)
                </div>
        `;
        
        window.earningsResearchData = research;
        
        if (research.length === 0) {
            html += 'No research reports...';
        } else {
            research.forEach(item => { ... });
        }
    }
}
```

**After:**
```javascript
async function loadEarningsResearch() {
    try {
        const response = await fetch('/api/earnings-research');
        const data = await response.json();
        
        // Handle object format {content: "..."}
        const content = data.content || '';
        const hasContent = content.trim().length > 0;
        
        let html = '<div class="card">';
        
        if (!hasContent) {
            html += `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                    <div>No research reports yet.</div>
                    <div style="font-size: 0.8125rem; margin-top: 0.5rem;">Bob's first report: Tuesday Feb 18, 6:30 AM</div>
                </div>
            `;
        } else {
            html += `
                <div style="font-size: 0.8125rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    ${content.split('###').length - 1} sections • Research content
                </div>
                <div class="markdown-content" style="white-space: pre-wrap; font-size: 0.875rem; line-height: 1.6;">${content}</div>
            `;
        }
        
        html += '</div>';
        document.getElementById('earnings-research-content').innerHTML = html;
    }
}
```

---

## Issue 3: Analysis Archive Missing Extended Data

### Confirmed Problem
`full_text` field is empty string ("") for all analyses - no price targets or thesis available

### Confirmed Root Cause
- **Location:** server.py function `api_analysis_archive()` line ~567
- **Problem:** `content.split('##')` splits on ANY '##' substring
- **Impact:** Table headers like `| ## |` trigger incorrect splits
- **Result:** Sections become single-line, content is lost

### Implementation

**File:** `server.py`  
**Function:** `api_analysis_archive()`  
**Change type:** Fix split delimiter  
**Lines affected:** 1 line

**Before:**
```python
sections = content.split('##')
```

**After:**
```python
sections = content.split('\n## ')
```

---

## Summary of Changes

| Issue | File | Function | Lines | Change Type |
|-------|------|----------|-------|-------------|
| 1. Portfolio field | server.py | api_portfolio() | 3 lines | Field rename: price → current_price |
| 2. Earnings format | dashboard.html | loadEarningsResearch() | ~15 lines | Handle object {content} instead of array |
| 3. Analysis split | server.py | api_analysis_archive() | 1 line | Change split('##') to split('\n## ') |

**Total:** 2 files, ~20 lines of code changes

---

## Step-by-Step Implementation

### Step 1: Fix portfolio field (server.py)
- Open server.py
- Find `api_portfolio()` function
- Change `'price': pos.get('price', 0)` to `'current_price': pos.get('price', 0)`
- Lines: ~407, ~417 (two occurrences if in dict literal)

### Step 2: Fix earnings research (dashboard.html)
- Open templates/dashboard.html
- Find `loadEarningsResearch()` function (around line 1367)
- Rewrite to handle `data.content` object format
- Remove array-specific logic (.length, .forEach)

### Step 3: Fix analysis split (server.py)
- Find `api_analysis_archive()` function
- Change `content.split('##')` to `content.split('\n## ')`
- Line: ~567

### Step 4: Restart server
```bash
./mc.sh restart
```

### Step 5: Verify all three fixes
```bash
# Test portfolio
curl -s http://localhost:8080/api/portfolio | python3 -c "
import json,sys
d=json.load(sys.stdin)
p=d['positions'][0] if d['positions'] else {}
print('Portfolio:', 'current_price' in p)
"

# Test analysis
curl -s http://localhost:8080/api/analysis-archive | python3 -c "
import json,sys
d=json.load(sys.stdin)
if d: print('Analysis:', len(d[0].get('full_text','')) > 100)
"

# Test earnings
curl -s http://localhost:8080/api/earnings-research | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('Earnings:', 'content' in d)
"
```

### Step 6: Update V1.3 backup
```bash
cp server.py v1.3_backup/
cp templates/dashboard.html v1.3_backup/
```

---

## Rollback Strategy
If fixes fail:
```bash
cd ~/.openclaw/workspace/mission_control
cp v1.3_backup/server.py .
cp v1.3_backup/dashboard.html .
./mc.sh restart
```

---

**Awaiting Proceed command.**
