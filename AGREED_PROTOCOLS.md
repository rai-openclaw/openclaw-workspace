# Agreed Protocols

**Last Updated:** 2026-02-15  
**Effective:** Immediately  
**Applies To:** All Mission Control Development

---

## Universal Rules (All Tasks)

### 1. Be Proactive, Not Reactive
When you present ideas, I will:
- Offer suggestions for improvements when possible
- Explain trade-offs of different approaches
- If no improvements are possible, explicitly acknowledge that your approach is optimal
- Never just "yes sir" and execute without discussion

---

## Non-Programming Rules (Basic Tasks)

### 1. Efficiency Over Verbosity
- Brief acknowledgements only
- No repetitive summaries
- State Sync format only (no unnecessary narration)

---

## Programming/Implementation Rules (Fundamental Ideals)

These apply to ALL programming work without exception.

### 1. Data-Driven Architecture
- ALL values must be driven by source files
- NO hardcoding unless explicitly justified
- If hardcoding is necessary, I must explain why and get approval
- Source of truth: tracker files, not code

### 2. No Band-Aid Solutions
- Fix issues at the source, never work around them
- Proper architecture over quick fixes
- Root cause analysis required before implementation
- No port hopping, zombie process accumulation, or temporary patches

### 3. Surgical Precision Over Rebuilds
- Edit 5-10 lines maximum for targeted changes
- Use `sed` or `edit` for small modifications, never rewrite entire functions
- No creating duplicate files (server_5050.py, server_6060.py, etc.)
- Fix one thing at a time, verify, then proceed
- Propose approach with trade-offs before executing

### 4. Validation Before Integration
- Test each component in isolation before connecting to the system
- Mock external dependencies (APIs, file reads) during development
- Never test "live" on the production server
- Verify data parsing works with actual files before building UI

### 5. Stop and Ask Triggers
If I encounter any of the following, I must STOP and ask you before continuing:
- Same error 3+ times (error loop detected)
- Port conflicts or zombie processes
- Test failures after "simple" changes
- Unexpected data format
- Any situation where I'm randomly trying fixes without understanding the root cause

**Action:** Document the error, explain what I tried, ask for direction. Do not keep hacking.

---

## Implementation Framework

After we agree on a solution direction, follow this sequence exactly:

### 1. TDS Protocol (Technical Design Spec)
Create `docs/specs/[feature-name].md` containing:
- **Goals:** What the feature does
- **Affected Files:** Full paths to every file that needs modification
- **Estimated Scope:** X lines across Y files (target: 5-10 lines per change)
- **API/Contract Changes:** Any changes to APIs or shared states
- **Step-by-Step Plan:** 5-10 verifiable implementation steps

### 2. Contract-First Coding
- Never modify existing function signatures without explicit approval
- If signature change is required: perform global search for all references and update simultaneously
- Run test command after every single file edit to verify no regressions

### 3. Thinking Mode Refactoring (Conditional)
**Trigger:** Files >300 lines OR high cyclomatic complexity

If triggered:
- Pause implementation
- Focus on decoupling logic
- Extract utilities into modular files
- Avoid adding if/else blocks to existing complex functions
- Propose refactoring plan before continuing

### 4. Checkpointer Strategy
Every 3-5 successful file modifications, provide State Sync:

```
[Current Progress]
- What's been completed

[Active Task]
- What's currently in progress

[Verified Working Features]
- What's been tested and confirmed working
```

### 5. Wait for "Proceed"
**DO NOT IMPLEMENT until explicitly told "Proceed"**

After steps 1-4 are complete and documented, wait for your explicit "Proceed" command before writing any implementation code.

---

## No Emergency Exceptions

This is not a production system. There are NO emergency exceptions.

- Server down? Follow protocol.
- Data issue? Follow protocol.
- "Quick fix needed"? Follow protocol.

The foundation must remain clean. If something is broken, proper TDS and implementation framework still apply.

---

## Verification

Before starting any task, I will verify against this document:
- [ ] Universal rules understood
- [ ] Task type identified (programming vs non-programming)
- [ ] Fundamental ideals acknowledged
- [ ] Implementation framework ready to execute

**If unclear on any point, I will ask before proceeding.**

---

**Reference Files:**
- V1.1 Baseline: `v1.1_backup/`
- Current Spec: `docs/specs/mission_control_spec.md`
- Dashboard: http://localhost:8080
