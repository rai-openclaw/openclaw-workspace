# Chrome Extension Browser Testing Workflow

**Purpose:** Reliable visual/UI testing using Chrome extension relay  
**Status:** Primary method for Mission Control testing  
**Last Updated:** 2026-02-18

---

## Why Chrome Extension vs Gateway Browser

| Method | Reliability | Setup | Best For |
|--------|-------------|-------|----------|
| Gateway browser | 🔴 Flaky | Complex, breaks often | Automated CI |
| **Chrome extension** | 🟢 Reliable | One-time setup, stable | Manual testing |

**Key insight:** For trading dashboards, visual bugs are more common than API bugs. Chrome extension provides reliable visual testing.

---

## One-Time Setup (User Does This)

### Step 1: Install OpenClaw Browser Relay Extension

1. Install the Chrome extension (from Chrome Web Store or provided by OpenClaw)
2. Pin it to toolbar for easy access

### Step 2: Attach Tab (Per Session)

**When an agent needs browser testing:**

1. **Agent says:** "I need to test the UI. Please attach a Chrome tab:"
   - Open Chrome
   - Navigate to the site (e.g., http://localhost:8080)
   - Click the **OpenClaw Browser Relay** toolbar icon
   - When badge shows "ON", tell me "attached"

2. **User replies:** "Attached"

3. **Agent proceeds:** Uses `profile="chrome"` for all browser commands

---

## Agent Testing Workflow

### For Scout (QA Testing)

```javascript
// 1. Check if browser available
browser.status

// If not attached, ask user to attach
// Once attached, proceed:

// 2. Open target page
browser.open:
  targetUrl: "http://localhost:8080"
  profile: "chrome"

// 3. Take snapshot to see page structure
browser.snapshot:
  profile: "chrome"
  
// 4. Navigate to specific tab
browser.act:
  request:
    kind: click
    ref: "Corporate"  // or "Holdings", "Analysis", etc.

// 5. Check for console errors
browser.console:
  profile: "chrome"
  
// 6. Test responsive (resize)
browser.act:
  request:
    kind: resize
    width: 768
    height: 1024
```

### For Alex (Visual Verification)

```javascript
// After making UI changes:
browser.open:
  targetUrl: "http://localhost:8080"
  profile: "chrome"

browser.snapshot:
  profile: "chrome"
  // Verify changes appear correctly
  
// Test interaction
browser.act:
  request:
    kind: click
    ref: "Refresh Prices"

// Verify result
browser.snapshot:
  profile: "chrome"
```

---

## Common Issues & Solutions

### Issue: "No attached tab found"

**Cause:** Chrome extension not activated on any tab  
**Solution:** User must click toolbar icon on the target tab  
**Badge shows:** "ON" when attached

### Issue: Browser commands timeout

**Cause:** Tab disconnected, Chrome closed, or extension error  
**Solution:** 
1. Check Chrome is open
2. Re-attach tab (click toolbar icon again)
3. Retry browser command

### Issue: Page not loading

**Cause:** Server not running, wrong URL  
**Solution:**
1. Verify http://localhost:8080 loads in Chrome
2. Check Docker container: `docker ps`
3. Restart if needed: `docker-compose restart`

---

## Testing Checklist (For Scout)

### Visual Smoke Test (Quick)

```
□ Page loads without console errors
□ Main navigation visible and clickable
□ Data displays (not "Loading...")
□ No obvious layout breaks
```

### Full Regression (When Major Changes)

```
□ All tabs render (Holdings, Analysis, Earnings, Ideas, Corporate, Schedule, APIs)
□ Holdings shows portfolio data
□ Corporate tree shows hierarchy
□ Ideas kanban displays cards
□ Responsive: Desktop (1920px)
□ Responsive: Tablet (768px)
□ Responsive: Mobile (375px)
□ No console JavaScript errors
□ Interactive elements work (buttons, forms)
```

---

## When to Use What

| Scenario | Method | Why |
|----------|--------|-----|
| Quick API check | curl | Fast, no setup needed |
| Visual verification | Chrome ext | See what user sees |
| Responsive testing | Chrome ext | Resize and screenshot |
| Regression suite | Chrome ext | Comprehensive UI validation |
| Broken Chrome ext | curl + manual | Fallback when tools fail |

---

## Best Practices

### For Users

1. **Keep Chrome open** during agent testing sessions
2. **Attach tab before testing** - one click on toolbar icon
3. **Re-attach if browser commands fail** - extension can disconnect
4. **Navigate to correct URL first** - agent will use current page

### For Agents

1. **Always check browser.status first** - fail fast if not available
2. **Ask clearly for attachment** - specific instructions reduce friction
3. **Test visual before claiming done** - API passing ≠ UI working
4. **Document what you tested visually** - include in MEMORY.md

### For Scout Specifically

1. **Browser testing is PRIMARY** - Not optional for UI work
2. **Ask for Chrome attachment** - Don't fall back to curl silently
3. **Test responsive breakpoints** - Mobile issues are common
4. **Screenshot on failure** - `browser.screenshot` captures evidence

---

## Integration with Memory System

**Scout's testing reports must include:**

```markdown
## 2026-02-18: UI Testing - [Feature]

**Method:** Chrome extension (profile="chrome")
**User Action Required:** Tab attached at [time]

**Visual Tests:**
- ✅ Desktop render (1920px)
- ✅ Tablet render (768px)
- ✅ Mobile render (375px)
- ✅ Console: No errors
- ✅ Interactions: Buttons work

**API Backup Tests:**
- ✅ /api/portfolio responds
- ✅ /api/corporate responds

**Evidence:**
- Screenshots: [if taken]
- Console log: [if errors]

**Result:** ✅ PASS / ❌ FAIL
```

---

## Troubleshooting Guide

### If Chrome extension stops working mid-test:

1. Check Chrome still open
2. Check tab still exists
3. Re-attach via toolbar icon
4. Continue from where you left off

### If user can't find toolbar icon:

1. Chrome menu → Extensions → OpenClaw Browser Relay
2. Click "Remove" then reinstall if needed
3. Pin to toolbar for easy access

### If site doesn't load in Chrome:

1. Check http://localhost:8080 directly
2. If fails, check Docker: `docker ps`
3. If Docker down: `cd ~/mission-control && docker-compose up -d`
4. Retry in Chrome

---

**Last Updated:** 2026-02-18  
**Next Review:** When workflow changes or issues emerge
