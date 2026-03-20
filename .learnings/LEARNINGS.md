# Learnings Log
Structured log of corrections, knowledge gaps, and best practices.

Format: LRN-YYYYMMDD-XXX

---

## LRN-20260319-001

**Area:** infra  
**Priority:** high  
**Status:** promoted (added to TOOLS.md)

**Description:** The sessions_spawn tool requires the `agentId` parameter explicitly — using `label` alone defaults to Jarvis subagent instead of the intended agent. This caused all Alex and Scout tasks to actually run as Jarvis subagents unknowingly.

**Correction:** Always include `agentId: "alex"` for implementation tasks and `agentId: "scout"` for validation tasks when calling sessions_spawn.

**Prevention:** Governance updated to enforce explicit agentId in all spawn calls.

---

## LRN-20260320-001

**Area:** governance  
**Priority:** high  
**Status:** promoted (added to ROLES.md)

**Description:** Session-end only learning capture is risky — if the session crashes or ends unexpectedly, all learnings are lost. Today the gateway crashed twice (18:44 and 18:50) with no graceful shutdown, resulting in no memory entry for March 20.

**Correction:** Learnings must be captured immediately when discovered (bug found, fix applied, protocol gap identified), not just at session end. Write to .learnings/LEARNINGS.md mid-session. Memory entry at session end should summarize, not re-document.

**Prevention:** ROLES.md updated with Learning Capture Rule (Section 11).
