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
