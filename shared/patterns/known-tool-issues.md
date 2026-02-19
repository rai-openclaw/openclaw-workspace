# Known Tool Issues

**Last Updated:** 2026-02-18
**Status:** Active - Workaround in place

---

## Issue #1: Browser Automation Tool Timeouts

**Problem:** Browser automation (browser.open, browser.snapshot, etc.) consistently times out or hangs indefinitely.

**Symptoms:**
- Agent calls `browser.open()` → no response
- Agent calls `browser.start()` → no response
- Agent calls `browser.snapshot()` → timeout after 2-5 minutes
- Session eventually kills agent due to timeout

**Root Cause:** Browser tool requires:
- Chrome extension attached to active tab, OR
- OpenClaw-managed browser profile properly started, OR
- Gateway browser service running

Currently none of these are properly configured/available.

**Impact:**
- ❌ Cannot perform visual UI testing
- ❌ Cannot take screenshots for verification
- ❌ Cannot test browser interactions (clicking, form submission)
- ✅ API testing still works (curl, direct HTTP requests)
- ✅ Data validation still works (JSON verification)

**Workaround:**
Use direct HTTP/API testing instead of browser automation:

```bash
# Instead of browser.open() + browser.snapshot()
# Use:
curl -s http://localhost:8080/api/portfolio | jq
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

**When to use workaround:**
- Testing API endpoints (✅ preferred method)
- Validating data integrity (✅ works well)
- Checking server health (✅ reliable)

**When workaround is insufficient:**
- Visual layout testing (❌ need browser)
- CSS/styling verification (❌ need browser)
- JavaScript interaction testing (❌ need browser)
- Mobile responsive testing (❌ need browser)

**Affected Agents:**
- **Scout** - Cannot perform UI regression testing
- **Alex** - Cannot visually verify UI changes
- **Any agent** needing visual confirmation

**Solution Implemented:**

**Chrome Extension Workflow** (PRIMARY METHOD)
- **Setup:** See `shared/patterns/chrome-extension-testing.md`
- **Usage:** User attaches Chrome tab via toolbar icon, agent uses `profile="chrome"`
- **Reliability:** High - stable connection, real browser testing
- **Effort:** One-time extension install, per-session tab attachment

**Why this beats gateway browser:**
- Gateway service is flaky and breaks often
- Chrome extension is reliable and gives real browser control
- UI testing is critical for Mission Control (most bugs are visual)

**Fallback (if Chrome unavailable):**
- API testing with curl (backup only)
- Manual user spot-check for visual elements
- Document in report: "Visual testing limited, APIs verified"

**Current Status:**
- ✅ Chrome extension workflow documented
- ✅ Scout's SOUL.md updated (UI testing primary)
- ✅ Testing protocol established
- ⏸️ Awaiting first full test run with Chrome ext

**Next Steps:**
- [x] Document Chrome extension workflow
- [x] Update Scout's testing protocol
- [ ] Test full workflow on next UI change
- [ ] Train user on one-time setup

---

## Issue #2: [Placeholder for future issues]

**Problem:** 

**Symptoms:**

**Root Cause:**

**Impact:**

**Workaround:**

**Solutions Considered:**

**Current Status:**

**Next Steps:**

---

**How to Add New Issues:**

1. Document the problem clearly
2. Explain symptoms so others can recognize it
3. Document root cause if known
4. List workarounds
5. Update status as situation changes
6. Assign ownership for resolution

**When to escalate:**
- Issue blocks critical path for >24 hours
- Multiple agents hitting same problem
- Workaround insufficient for task requirements
