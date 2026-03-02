# Repository Promotion Protocol (RPP)

## 1. Purpose

RPP governs how changes are promoted across branches in OpenClaw repositories. It ensures that AIP and VALIDATION cannot be bypassed through improper merging.

## 2. Branch Model

All OpenClaw repositories follow:
- `main` → Production (stable, deployable)
- `dev` → Development integration branch

No direct commits to main. All changes must land in dev first.

## 3. Development Rules

All work must:
- Follow AEF execution flow
- Be classified under AIP before implementation
- Pass required validation before promotion

Feature branches are optional but not required.

## 4. Promotion to Main

`dev` → `main` merge allowed only when:
- Validation requirements satisfied
- No unresolved scope drift
- No known regression
- Change classification documented

If validation fails: Merge is prohibited.

## 5. Emergency Revert Protocol

If main becomes unstable:
- Immediate revert to last stable commit
- Fix implemented in dev
- Validation re-run
- Re-promote only after validation passes

No hot-fixes directly on main.

## 6. Commit Discipline

Commits must:
- Represent a single logical change
- Include change level (L0–L3)
- Not bundle unrelated modifications

Example:

```
[L2] Expand earnings grade schema
Scope: earnings pipeline
Validation: PASS
```

## 7. Governance Supremacy

RPP enforces governance. If branch behavior conflicts with AIP or VALIDATION:
- AIP and VALIDATION take precedence.
