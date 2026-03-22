# Errors Log
Structured log of command failures, tool errors, and unexpected behavior.

Format: ERR-YYYYMMDD-XXX

---

## ERR-20260320-002

**Priority:** high  
**Status:** known limitation

**Description:** Repeated launchctl ETIMEDOUT causing double restart on every config change. Gateway attempts full process restart via spawnSync launchctl, but launchctl times out (ThrottleInterval=1 may cause this). Falls back to in-process restart which works fine every time.

**Impact:** Every config change triggers two restarts: first fails with ETIMEDOUT, then succeeds with in-process fallback. This has happened 15+ times since March 3.

**Root cause:** launchd plist has ThrottleInterval=1, which may prevent rapid restarts. Gateway spawnSync call to launchctl fails with timeout.

**Workaround:** The in-process fallback works reliably. Could configure gateway to skip launchctl entirely and use in-process restart only. Config location: openclaw.json has no restart method option — requires code/config change in gateway.

---

**Priority:** high  
**Status:** known limitation

**Description:** MiniMax API rate limiting caused Alex and Scout subagents to fail during L2 task execution. Multiple concurrent sessions (35 active) triggered "API rate limit reached. Please try again later." error.

**Impact:** Subagent sessions appeared stuck (high input tokens, minimal output) then failed with rate limit error. Validation could not complete.

**Workaround:** Reduce concurrent session count or wait for rate limit reset. Consider implementing rate limit handling in subagent spawn logic.

---
