# Validation Requirements

## 1. Purpose

Validation ensures that system integrity is preserved after changes. Scout is responsible for enforcing these checks. No L2 or L3 change may be considered complete without validation.

## 2. Validation Levels

**L0 — Cosmetic**
Validation optional.

**L1 — Local**
Recommended validation:
- Build succeeds
- No console errors introduced
- No unintended API contract changes

**L2 — Structural**
Mandatory validation:
- Build succeeds without error
- All API response shapes remain valid unless declared
- No protected surface modified without classification
- Reconciliation engine sanity preserved
- No new console errors
- No scope drift beyond declaration

**L3 — Foundational**
Mandatory validation:
- All L2 checks
- Migration plan executed correctly
- Rollback plan tested or verified
- Canonical data integrity confirmed
- No cross-repo contract breakage

## 3. Reconciliation Sanity Check

When reconciliation logic is touched:
- Confirm: Open + closed positions reconcile deterministically
- No orphaned trades exist
- No duplicate cost basis calculations
- Idempotency preserved

## 4. API Contract Integrity

If API responses are modified:
- Confirm: Response shape matches declared design
- Mission Control compatibility preserved
- No silent field removal

## 5. Scope Drift Check

Scout must confirm:
- Only declared files were modified
- No unrelated modules were altered

Undeclared modification triggers revert per AIP.

## 6. Validation Failure Protocol

If validation fails:
- Change is rejected
- Revert required
- Reclassification required if scope expanded

No partial acceptance.
