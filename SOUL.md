# SOUL.md — Governance Loader

Governance rules live in `/workspace/governance`. On startup, agents must read and load the following files into context:

- governance/CONSTITUTION.md
- governance/ROLES.md
- governance/VALIDATION.md
- governance/AIP.md
- governance/AEF.md
- governance/PROTECTED_SURFACES.md
- governance/SCP.md
- governance/RPP.md

These define system rules and must be read before performing structural changes.
