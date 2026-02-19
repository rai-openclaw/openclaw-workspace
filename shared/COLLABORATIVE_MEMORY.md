# Collaborative Memory Guide

**Purpose:** How agents share knowledge, learn from each other, and build collective intelligence.

---

## Memory Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    COLLABORATIVE MEMORY                      │
├─────────────────────────────────────────────────────────────┤
│  Personal Memory (Per-Agent)                                │
│  ├── agents/alex/MEMORY.md     - Alex's coding experiences  │
│  ├── agents/bob/MEMORY.md      - Bob's research outcomes    │
│  ├── agents/scout/MEMORY.md    - Scout's testing patterns   │
│  └── ...                                                    │
│                                                             │
│  Shared Memory (Cross-Agent)                                │
│  ├── shared/protocols/         - Standards all follow       │
│  ├── shared/patterns/          - Reusable solutions         │
│  └── shared/history/           - Daily chronological logs   │
│                                                             │
│  State Memory (Jarvis/Main)                                 │
│  └── MEMORY.md                 - Current system state       │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use Each Type

### Personal Memory (agents/{name}/MEMORY.md)

**Use for:**
- Individual learning and mistakes
- Personal workflow improvements
- Specific tasks I completed
- My own screw-ups and fixes

**Example - Alex writes:**
```markdown
## 2026-02-18: JavaScript Brace Mismatch
**Problem:** Dashboard broken after my edit
**Mistake:** Created duplicate code block
**Lesson:** Always validate brace balance before claiming done
```

**Other agents READ this when:**
- Alex needs to remember his own patterns
- Kimi wants to understand what Alex broke before
- Scout wants to know what to test for

### Shared Protocols (shared/protocols/)

**Use for:**
- Rules all agents must follow
- Standards that don't change often
- Cross-agent agreements

**Example:**
- `coding-protocol.md` - AGENTS.md standards (Alex follows this)
- `testing-protocol.md` - Scout's testing standards
- `grading-protocol.md` - Bob's research standards

**When to update:**
- When process changes
- When lessons become rules
- When new standards established

### Shared Patterns (shared/patterns/)

**Use for:**
- Solutions multiple agents use
- Architecture patterns
- Organizational knowledge

**Example:**
- `corporate-structure.md` - Team hierarchy
- `auth-patterns.md` - How we handle logins (GitHub, APIs)
- `data-migration-pattern.md` - How to migrate JSON schemas

**When to update:**
- When a reusable solution emerges
- When architecture decisions are made
- When org structure changes

### Shared History (shared/history/)

**Use for:**
- Chronological daily log
- Cross-agent events
- System-wide changes

**Format:** `shared/history/YYYY-MM-DD.md`

**Example:**
```markdown
# 2026-02-18

## Events
- Alex broke dashboard with JS syntax error
- Alex fixed it, Scout tested, all verified
- New agent memory architecture implemented
- GitHub backup established

## Agent Activities
- **Alex:** Fixed JavaScript, deployed to Docker
- **Scout:** Regression testing
- **Jarvis:** Coordination, architecture setup

## System Changes
- Docker container rebuilt
- GitHub repo: mission-control-dashboard created
- All agents now have MEMORY.md
```

**Who writes this:**
- Jarvis maintains it daily
- Any agent can append significant cross-agent events

---

## Collaboration Patterns

### Pattern 1: Learning from Mistakes

**When Alex breaks something:**
1. Alex logs in his MEMORY.md (what broke, why, how he fixed)
2. Scout logs in his MEMORY.md (what he tested, what he found)
3. Pattern moves to shared/patterns/ if it's reusable (e.g., "JS Brace Balance Check")

**Example progression:**
- Alex breaks dashboard → Alex logs mistake
- Scout finds regression issues → Scout logs testing pattern
- Kimi reviews → Kimi documents architecture principle
- **Result:** `shared/patterns/javascript-debugging.md` created

### Pattern 2: Handoff Documentation

**When work transfers between agents:**

```
Alex builds → Scout tests → Kimi reviews architecture
     ↓              ↓                  ↓
Alex's MEMORY    Scout's MEMORY     Kimi's MEMORY
"Built X,        "Tested X,         "Validated X,
 issues Y"        found Z"           pattern W"
     ↓              ↓                  ↓
         shared/history/YYYY-MM-DD.md
         "X built, tested, deployed"
```

**Each agent logs:**
- What they received
- What they did
- What they handed off
- Issues found

### Pattern 3: Collective Learning

**When multiple agents encounter same issue:**

1. Individual agents log in their MEMORY.md
2. Pattern emerges
3. Jarvis/Kimi documents in shared/patterns/
4. All agents reference the shared pattern

**Example:**
- Bob: "API X rate limits at Y requests"
- Alex: "Hit rate limit on API X again"
- Dave: "API X failed during briefing"
- **Result:** `shared/patterns/api-rate-limiting.md` created with strategies

---

## How to Reference Other Agents' Memories

### In Personal Memory

**When logging work that involved others:**
```markdown
## 2026-02-18: Tested Alex's Dashboard Fix
**Context:** Alex fixed JavaScript syntax error (see agents/alex/MEMORY.md)
**What I tested:** ...
**Found:** ...
**Handoff:** Reported to Jarvis, verified with Kimi
```

### In Shared Patterns

**When documenting reusable solutions:**
```markdown
# JavaScript Debugging Patterns

**Contributors:** Alex (mistakes), Scout (testing), Kimi (architecture)

## Brace Balance Check
**Origin:** Alex's 2026-02-18 dashboard break
**Pattern:** Always validate before deploy
**Code:** ...
```

### In Shared History

**When logging daily events:**
```markdown
## 2026-02-18: Dashboard Recovery
**Timeline:**
- Alex broke JS syntax (agents/alex/MEMORY.md#2026-02-18)
- Scout tested fix (agents/scout/MEMORY.md#2026-02-18)
- Kimi validated architecture approach
```

---

## Memory Maintenance Responsibilities

| Agent | Personal Memory | Shared Contribution |
|-------|----------------|---------------------|
| **Alex** | Log every coding task | Share patterns when code solutions reusable |
| **Bob** | Log every research | Share patterns when grading insights emerge |
| **Dave** | Log every briefing | Share patterns when communication standards evolve |
| **Scout** | Log every test | Share testing protocols, bug patterns |
| **Kimi** | Log every architecture | Document patterns, principles, root causes |
| **Jarvis** | Log coordination | Maintain shared/history/, consolidate patterns |

---

## Red Flags (When Memory System Failing)

⚠️ **Agent repeating same mistake** → Not reading personal memory
⚠️ **Multiple agents hit same issue** → Not sharing to shared/patterns/
⚠️ **No context on why decision made** → Not logging to shared/history/
⚠️ **"I didn't know that"** → Not reading shared protocols
⚠️ **Daily check shows old entries** → Agent not logging at session close
⚠️ **Silent workarounds** → Agent not flagging broken tools/systems

## Core Principle: Flag Broken Tools Immediately

When I discover a tool isn't working (browser timeouts, API failures, auth issues), I must:

1. **Stop and report** - Don't just work around it silently
2. **Explain the impact** - What's blocked, what's the workaround
3. **Propose solutions** - How do we fix the root cause
4. **Log it** - Document in shared/patterns/ if it's a recurring issue

**Examples:**

❌ **Wrong:**
> "Scout timed out, I'll just test with curl instead"

✅ **Right:**
> "The browser tool is timing out (both Scout and Alex hit this). This blocks UI testing. Workaround: Use curl for API validation. Fix needed: Check gateway browser service status. I'll log this in shared/patterns/tool-issues.md"

**Why this matters:** The user can't fix what they don't know about. Silent workarounds hide systemic problems that keep breaking agent workflows.

---

## Quick Reference

**Starting new task:**
1. Read my personal MEMORY.md (load context)
2. Read relevant shared/protocols/ (follow standards)
3. Read relevant shared/patterns/ (use existing solutions)

**During task:**
- Note what works, what doesn't
- Document mistakes immediately
- Reference other agents' work when relevant

**Ending task (MANDATORY):**
1. Append to my personal MEMORY.md
2. If pattern emerged, suggest to Jarvis/Kimi for shared/patterns/
3. If cross-agent event, Jarvis logs to shared/history/

**Daily (7 AM):**
- Memory check runs automatically
- Reports gaps to Jarvis
- Included in morning brief

---

**Last Updated:** 2026-02-18
**Next Review:** When pattern emerges or system breaks
