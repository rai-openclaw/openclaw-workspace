# OpenClaw Constitution

## 1. Purpose

OpenClaw is a deterministic AI operating system designed to assist in capital allocation, research, trade management, and future business operations. It consists of:

- Canonical Memory Layer (workspace data)
- Intelligence Layer (agents)
- Interface Layer (Mission Control)

Mission Control is visualization only. The workspace is canonical authority.

## 2. Authority Structure

All governance authority resides exclusively in the `/governance` directory. No file outside `/governance` may define:

- Agent authority
- Architectural rules
- Autonomy scope
- Validation standards
- Coding protocols
- Escalation rules

Root-level bootstrap files are non-authoritative stubs.

## 3. Agent Governance

Agents do not define their own identity, autonomy, or authority. All agent behavior is derived from:

- `AIP.md` (Architectural Integrity Protocol)
- `AEF.md` (Autonomous Execution Flow)
- `ROLES.md` (Role definitions)
- `VALIDATION.md` (Validation requirements)

Agent-level sovereignty is prohibited.

## 4. Architectural Integrity Principle

The system must be safer and more predictable after every change. No modification may introduce:

- Undeclared contract drift
- Silent structural changes
- Hidden side effects
- Regression risk without validation

All structural changes must follow AIP.

## 5. Governance Hierarchy

Authority order:

1. CONSTITUTION.md
2. AIP.md
3. AEF.md
4. ROLES.md
5. VALIDATION.md
6. RPP.md

No other governance sources are valid.

## 6. Scope

This constitution applies globally to:

- openclaw-workspace
- mission-control-next
- All future OpenClaw repositories
