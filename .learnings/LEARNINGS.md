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
