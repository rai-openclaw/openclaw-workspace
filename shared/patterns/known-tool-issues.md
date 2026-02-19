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

**Solutions Considered:**

1. **Fix gateway browser service** (preferred long-term)
   - Requires: Investigate why browser tool not responding
   - Effort: Unknown, may need OpenClaw support
   - Benefit: Full browser testing restored

2. **Use Chrome extension** (alternative)
   - Requires: User attaches Chrome tab via OpenClaw Browser Relay
   - Effort: Manual per-session
   - Benefit: Real browser testing

3. **Accept workaround** (current state)
   - Use API testing for data integrity
   - Ask user to spot-check UI visually
   - Document limitations in test reports

**Current Status:**
- Using Workaround #3 (API testing only)
- Scout's regression tests use curl instead of browser automation
- Visual verification delegated to manual user check

**Next Steps:**
- [ ] Jarvis to investigate gateway browser service status
- [ ] If fixable, restore browser testing for Scout
- [ ] If not fixable, update Scout's SOUL.md to remove browser dependency

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
