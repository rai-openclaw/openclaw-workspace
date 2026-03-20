# Errors Log
Structured log of command failures, tool errors, and unexpected behavior.

Format: ERR-YYYYMMDD-XXX

---

## ERR-20260320-001

**Priority:** high  
**Status:** known limitation

**Description:** MiniMax API rate limiting caused Alex and Scout subagents to fail during L2 task execution. Multiple concurrent sessions (35 active) triggered "API rate limit reached. Please try again later." error.

**Impact:** Subagent sessions appeared stuck (high input tokens, minimal output) then failed with rate limit error. Validation could not complete.

**Workaround:** Reduce concurrent session count or wait for rate limit reset. Consider implementing rate limit handling in subagent spawn logic.

---
