# Architectural Integrity Protocol (AIP)

## 1. Purpose

AIP enforces structural discipline across all OpenClaw repositories. No architectural change may occur without explicit classification and scope declaration.

## 2. Mandatory Change Classification

Every modification must be classified before implementation:

**L0 — Cosmetic**
- UI text
- Styling
- Formatting
- Logging

No logic or structural impact.

**L1 — Local**
- Single-module logic update
- Bug fix without contract change
- Internal refactor within file scope

Must not modify:
- Shared schemas
- API contracts
- Canonical data structures

**L2 — Structural**
- Cross-module changes
- API shape modification
- Schema expansion
- Ledger logic changes
- Data flow redesign

Requires:
- Explicit scope definition
- Impact declaration
- Risk assessment

**L3 — Foundational**
- Canonical schema redesign
- Cross-repository structural changes
- Reconciliation engine redesign
- Governance modifications

Requires:
- Written design brief
- Migration plan
- Rollback plan

No change may be implemented without declared level. Undeclared changes are invalid.

## 2.1 Undeclared Change Enforcement

If a change is implemented without prior classification:
- The change must be reverted.
- A proper change classification must be declared.
- Implementation may only resume after declaration.
- Retroactive classification is not permitted without revert.

This rule applies to all L1–L3 changes.
- API shape modification
- Schema expansion
- Ledger logic changes
- Data flow redesign

Requires:
- Explicit scope definition
- Impact declaration
- Risk assessment

**L3 — Foundational**
- Canonical schema redesign
- Cross-repository structural changes
- Reconciliation engine redesign
- Governance modifications

Requires:
- Written design brief
- Migration plan
- Rollback plan

No change may be implemented without declared level. Undeclared changes are invalid.

## 3. Spec Before Structural Work

For all L2 and L3 changes:

Implementation must not begin until:
- Problem statement is defined
- Affected files are listed
- Contract impact is declared
- Risk level is stated
- Rollback plan is described

## 4. Protected Surface Rule

Certain system surfaces are protected and may not be modified without L2 or L3 declaration. Protected surfaces are defined in: `PROTECTED_SURFACES.md`

Silent modification of protected surfaces is prohibited.

## 5. No Full-File Rewrite Rule

Full-file rewrites are prohibited unless:
- Classified as L3
- Justified in design brief
- Demonstrably reduces complexity

Incremental modification is required by default.

## 6. Scope Containment

No change may expand beyond declared scope. If scope expands:
- Change must be reclassified.

## 7. Regression Awareness

For L2 or L3 changes:

Explicitly state:

> "This change does not affect: [list unaffected subsystems]."

This enforces systemic awareness.
