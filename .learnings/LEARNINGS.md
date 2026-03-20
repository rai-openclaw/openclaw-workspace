# Learnings Log
Structured log of corrections, knowledge gaps, and best practices.

Format: LRN-YYYYMMDD-XXX

---

## LRN-20260320-003

**Area:** governance  
**Priority:** high  
**Status:** pending

**Description:** Silent retry behavior — spawning Alex v2 and v3 without reporting back or getting user authorization after v1 failed is a governance violation. The agent is not authorized to retry failed subagent spawns autonomously.

**Correction:** When a subagent spawn fails, report the failure immediately to the user and WAIT for instruction before retrying. Do not silently spawn follow-up attempts.

**Prevention:** Add explicit rule to ROLES.md: "Never retry a failed subagent spawn without user authorization. Report failure and wait."

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

**Description:** Session-end only learning capture is risky — crashes lose everything. Today the gateway crashed twice (18:44 and 18:50) with no graceful shutdown, resulting in no memory entry for March 20.

**Correction:** Learnings must be captured IMMEDIATELY when specific triggers occur: tool errors, bug discovery, user corrections, governance gaps, better approaches discovered, or unexpected API behavior. Write to .learnings/LEARNINGS.md immediately. Session end memory should summarize, not re-document.

**Prevention:** ROLES.md updated with Learning Capture Rule (Section 11) listing 6 specific triggers.

---

## LRN-20260320-002

**Area:** backend  
**Priority:** medium  
**Status:** resolved

**Description:** EXPIRE_WORTHLESS trades were filtered by event.timestamp instead of event.expiration, causing them to appear in monthly view but not weekly view.

**Correction:** Fixed by using event.expiration for closed_at in plEngine.ts when event_type is EXPIRE_WORTHLESS.

**Prevention:** When filtering trades by date range, ensure the correct date field is used (expiration date for expired options, timestamp for closes).
