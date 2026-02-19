# Jarvis's Memory

**Agent:** Jarvis (Chief of Staff)
**Model:** MiniMax M2.5
**Role:** Coordination, task management, team interface
**Last Updated:** 2026-02-18

---

## 📋 How to Use This File

**At Session Start:** Read this file to load:
- Team status and ongoing work
- Recent decisions and context
- Coordination patterns that work
- What to watch for

**At Session End:** Append new section with:
- Agents spawned and tasks assigned
- What got done vs what didn't
- Handoffs between agents
- Issues or blockers encountered

---

## Session Log (Newest First)

### 2026-02-18: JavaScript Fix Coordination & Architecture Cleanup

**Agents Spawned:**
1. **Alex** (DeepSeek) - Fix JavaScript syntax errors in dashboard
2. **Scout** (MiniMax M2.5) - Regression testing (standby, then active)

**Tasks Completed:**
- ✅ Alex diagnosed and fixed brace mismatch (331→302 balanced braces)
- ✅ Docker container rebuilt and deployed
- ✅ All 6 APIs verified working
- ✅ GitHub backup created: https://github.com/rai-openclaw/mission-control-dashboard
- ✅ Agent memory architecture redesigned and implemented
- ✅ Moved `memory/*-expertise.md` → `agents/*/MEMORY.md`
- ✅ Created `shared/{protocols,patterns,history}` structure
- ✅ Updated all agent SOUL.md files with memory references
- ✅ Added GitHub API to api_usage.json

**Handoffs:**
- Alex → Scout: "Fix deployed, ready for testing"
- Scout completed regression test via direct curl (browser tool issues)

**Issues:**
- Scout's browser automation had issues (timeouts)
- Workaround: Used direct curl commands for API validation
- All tests passed despite browser tool limitations

**Decisions:**
1. Established mandatory session-close protocol for all agents
2. New architecture: `agents/{name}/MEMORY.md` + `shared/{protocols,patterns,history}/`
3. Every agent MUST append to their MEMORY.md before saying "done"

**Team Status:**
- Alex: On-call, needs reminder to test before claiming done
- Scout: On-demand, use for UI/trading-critical testing
- Bob: Active for earnings research (daily 6:30 AM)
- Dave: Active for briefings (6 AM, 7 PM)
- Kimi: On-demand for complex/architecture work

---

## Team Roster & Status

| Agent | Role | Model | Status | Best For |
|-------|------|-------|--------|----------|
| Alex | Lead Developer | DeepSeek V3 | On-call | Coding, debugging, architecture |
| Bob | Research Analyst | MiniMax M2.5 | Active (daily) | Earnings research, grading |
| Dave | Executive Assistant | MiniMax M2.5 | Active (daily) | Briefings, summaries |
| Kimi | Special Projects | Kimi K2.5 | On-demand | Complex setups, stuck problems |
| Scout | QA & Testing | MiniMax M2.5 | On-demand | Testing Alex's work |
| Jarvis | Chief of Staff | MiniMax M2.5 | Active | Coordination, task management |

---

## Coordination Patterns That Work

### When to Spawn Whom

**Coding Tasks:**
- Standard work → Alex
- Complex architecture → Kimi (with Alex for implementation)
- UI/trading-critical → Alex + Scout for testing

**Research Tasks:**
- Earnings plays → Bob (daily, systematic)
- Quick lookup → Bob or Jarvis
- Deep analysis → Bob with follow-up calibration

**Briefings:**
- Standard morning/evening → Dave
- Complex days → Kimi
- Emergency/trading alerts → Jarvis direct

### Testing Protocol

**Alex's Responsibility:**
- Test his own work before declaring done
- Validate on desktop AND mobile
- Check console errors

**When to Add Scout:**
- UI work (visual rendering)
- Trading-critical features
- Before major releases
- When Alex is learning new tech

### Escalation Path

1. Agent stuck → Kimi assists
2. Agent times out → Auto-restart, continue working
3. Multiple failures → Jarvis intervenes, may switch models
4. Architecture questions → Kimi always

---

## Known Issues & Watchlist

### Current System Health
- ✅ Docker container stable (port 8080)
- ✅ All APIs responding
- ✅ GitHub backup in place
- ✅ JavaScript syntax validated

### Things to Monitor
- Alex's tendency to skip testing before claiming done
- Scout's browser automation reliability
- Token usage - prefer DeepSeek for coding (90% cheaper)

### Recent Pain Points
1. JavaScript brace mismatch (FIXED - add to Alex's patterns)
2. GitHub auth expired (FIXED - reauthorized)
3. Agent memory not being updated (FIXED - new architecture)

---

## User Preferences

### Task Management
- All tasks auto-included in 6 AM and 7 PM briefs
- Don't ask - just populate briefs
- User checks briefs, doesn't ask "what's on my schedule"

### Data Quality
- Critical for trading - never estimate
- If API fails, propose solutions immediately
- Prefer automation over manual workarounds

### Problem Solving
- Propose 2-3 solutions when tools fail
- Prefer spending time to automate vs manual
- Examples: Gemini Flash 2.5 for OCR, APIs for flight data

### Communication
- Direct, no corporate speak
- Actions > explanations
- Own mistakes immediately

---

## Daily Rhythm

### 6:00 AM - Morning Brief
- Spawn Dave for briefing generation
- Include: weather, schedule, trading snapshot
- Deliver via Telegram

### Throughout Day
- Handle ad-hoc requests
- Spawn agents as needed
- Monitor system health

### 5:00 PM - Trade Summary
- Check for new trades
- Send summary via Telegram
- Remind about open positions

### 7:00 PM - Daily Summary
- Compile day's work
- Email to guanwu87@gmail.com
- Log to MEMORY.md

---

**Append coordination notes after each significant session.**
