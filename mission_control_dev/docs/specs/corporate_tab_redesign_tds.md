# TDS: Corporate Tab Redesign - Visual Org Chart

## Overview
**CRITICAL: Update the EXISTING "Corporate" tab INSIDE Mission Control dashboard.**  
**DO NOT create a separate webpage. DO NOT create corporate_structure.html.**

Redesign the existing Corporate tab (already in dashboard.html) to show a visual organization chart instead of simple text cards.

**Status:** Draft  
**Author:** Kimi (EA)  
**Date:** Feb 16, 2026  
**Scope:** Modify existing Corporate tab view in dashboard.html ONLY

---

## ⚠️ CRITICAL CONSTRAINTS

### What NOT to do:
- ❌ Create a new file like corporate_structure.html
- ❌ Create a separate /corporate-structure route
- ❌ Redirect to a different page

### What TO do:
- ✅ Update the EXISTING Corporate tab content in dashboard.html
- ✅ The tab already exists at: `<div id="corporate-view" class="view">`
- ✅ Keep it inside the single-page dashboard application
- ✅ URL stays as: http://localhost:8080/ (user clicks "Corporate" tab)

---

## Current State

The Corporate tab currently shows simple stacked cards with employee info.

Location in dashboard.html:
```html
<div id="corporate-view" class="view">
    <h2 style="margin-bottom: 1rem;">Corporate Structure</h2>
    <div id="corporate-content">
        <!-- CONTENT GOES HERE -->
    </div>
</div>
```

---

## Target State

Visual tree hierarchy showing reporting structure:

```
                    👔 Rai (CEO)
                         |
                    🤵 Kimi (Chief of Staff)
                         |
        ┌───────────────┼───────────────┐
        |               |               |
     📋 Dave         📊 Bob        👨‍💻 Alex
   (Operations)   (Operations)   (Technical)
```

---

## Data Architecture

### Source of Truth: portfolio/data/corporate.json
```json
{
  "departments": [
    {"id": "executive", "name": "Executive", "color": "gold", "hex": "#f59e0b"},
    {"id": "operations", "name": "Operations", "color": "blue", "hex": "#3b82f6"},
    {"id": "technical", "name": "Technical", "color": "green", "hex": "#10b981"}
  ],
  "team": [
    {"id": "rai", "name": "Rai", "emoji": "👔", "role": "CEO", "department": "executive", "level": 1, ...},
    {"id": "kimi", "name": "Kimi", "emoji": "🤵", "role": "Chief of Staff", "department": "executive", "level": 2, ...},
    {"id": "dave", "name": "Dave", "emoji": "📋", "role": "Chief Briefer", "department": "operations", "level": 3, ...},
    {"id": "bob", "name": "Bob", "emoji": "📊", "role": "Senior Analyst", "department": "operations", "level": 3, ...},
    {"id": "alex", "name": "Alex", "emoji": "👨‍💻", "role": "Junior Developer", "department": "technical", "level": 3, ...}
  ]
}
```

### API Endpoint (Already Exists):
- GET `/api/corporate` returns the JSON above

---

## Implementation

### Files to Modify:

**1. mission_control/templates/dashboard.html**

Update the `loadCorporate()` JavaScript function:
```javascript
async function loadCorporate() {
    // 1. Fetch /api/corporate
    // 2. Organize team by level (1, 2, 3)
    // 3. Generate HTML with tree layout
    // 4. Render to #corporate-content
}
```

Add CSS (in <style> section):
```css
/* Tree layout styles */
.org-chart { display: flex; flex-direction: column; align-items: center; }
.org-level { display: flex; justify-content: center; gap: 1.5rem; }
.org-connector { /* Visual lines between levels */ }

/* Cards by department */
.org-card.executive { border-color: #f59e0b; }
.org-card.operations { border-color: #3b82f6; }
.org-card.technical { border-color: #10b981; }
```

### Visual Design:
- Level 1 (Rai): Centered, larger card, gold border
- Level 2 (Kimi): Centered, purple border  
- Level 3 (Team): 3-column row, blue/green borders
- Connecting lines between levels
- Click to expand details (responsibilities, model info)
- Responsive: Stack vertically on mobile

---

## Testing Checklist

- [ ] /api/corporate returns 5 team members
- [ ] Corporate tab shows tree layout (not stacked cards)
- [ ] Rai at top, Kimi middle, Team at bottom
- [ ] Color coding matches departments
- [ ] Clicking cards expands details
- [ ] Responsive on mobile
- [ ] NO separate page created
- [ ] Still inside dashboard.html

---

## Approval

**Reviewed TDS?** Changes needed?  
**Say "proceed" when ready to implement.**

Coder: Alex (DeepSeek V3)
