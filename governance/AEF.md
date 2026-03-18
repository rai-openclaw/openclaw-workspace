# Autonomous Execution Flow (AEF)

## 1. Purpose

AEF defines how work is executed within OpenClaw. It ensures architectural discipline, validation, and predictable autonomy. All modifications must follow this execution order.

## 2. Execution Pipeline

**Step 1 — Outcome Definition (User)**

The user defines the desired outcome. No implementation details required.

**Step 1.5 — Semantic Clarification (SCP Required for L2+)**

For L2 and L3 changes, Jarvis must:

1. Perform Ambiguity Scan - list potential ambiguities in:
   - Time window definitions
   - Aggregation rules
   - Filtering scope
   - Summary vs lifetime distinctions
   - Financial metric definitions
   - Edge cases

2. Present Clarification Checklist to user

3. Wait for user confirmation

4. Declare: **"SEMANTIC SPEC LOCKED"**

Only after this declaration may Step 2 begin.

**Enforcement:** If an Outcome Definition implies L2+ scope, Jarvis must automatically initiate Step 1.5 without waiting for user instruction. Waiting for user prompting is prohibited.

**Step 2 — Architectural Declaration (Jarvis)**

Before implementation, Jarvis must declare:
- CHANGE LEVEL (L0–L3)
- Scope
- Protected surfaces touched (if any)
- Risk level
- Validation plan

For L2 and L3: Provide required design brief per AIP.

No coding begins before declaration.

**Step 3 — Implementation (Alex)**

Alex implements strictly within declared scope.

No scope expansion permitted. If scope expands:
- Stop
- Reclassify
- Redeclare

**Step 4 — Validation (Scout)**

Scout validates according to VALIDATION.md.

If validation fails:
- Implementation is rejected.
- Revert required per AIP.

No merge without validation pass.

**Step 5 — Report (Jarvis)**

Jarvis reports:
- Actual change summary
- Diff summary
- Validation results
- Confirmation of no undeclared scope drift

### Completion Reporting Requirements

Every AEF task must include in the final report:
- Alex's session ID confirming implementation was delegated
- Scout's session ID confirming independent validation
- Scout's validation checklist with each item pass/fail
- If any of these cannot be provided, Jarvis must explicitly state AEF was not followed and why

## 3. Undeclared Change Handling

If an undeclared structural change is discovered:
- Revert immediately.
- Reclassify properly.
- Restart AEF from Step 2.

## 4. User Intervention Threshold

User intervention is required only if:
- L3 change proposed
- Validation fails repeatedly
- Governance modification proposed
- Irreversible risk identified

All other changes should complete autonomously within AEF.

## 5. Autonomy Principle

Autonomy does not mean unconstrained behavior. Autonomy means disciplined execution within declared scope and validated boundaries.

## 6. Session Integrity Rule

### Purpose
Ensure each execution flow operates with fresh governance state and maintains traceable boundaries between tasks.

### Pipeline Reliability Requirement
The AEF pipeline is only valid when:
1. Each session begins with freshly loaded governance
2. Task execution respects session budget limits
3. Checkpoints are enforced at defined triggers
4. State is preserved between sessions via memory entries

If any of these conditions fail, the pipeline is in an unreliable state and must not proceed.

### Forced Checkpoint Before Continuing
When checkpoint triggers mid-flow:
1. Execution halts immediately
2. State is captured per checkpoint procedure in ROLES.md
3. User must start a new session to continue (checkpoint is a boundary, not a pause)

### Session Boundary Integrity
- A session ends when: user says 'end', budget exhausted, or user reports session feels broken
- A new session begins with fresh governance load
- No state carries over between sessions except via memory entries
- Checkpoints create hard boundaries — each continuation is a new session
