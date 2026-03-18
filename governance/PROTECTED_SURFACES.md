# Protected Surfaces

## 1. Purpose
Protected surfaces are structural system contracts that may not be modified without L2 or L3 classification under AIP. Silent modification is prohibited.

## 2. Canonical Data Schemas
The following canonical data structures are protected:
- trades ledger schema
- open positions structure
- closed positions structure
- portfolio holdings schema
- earnings analysis structure
- earnings grade output structure
- ideas board schema

Any shape modification requires L2 or higher.

## 3. Reconciliation Engine
The deterministic reconciliation logic that:
- Matches opens and closes
- Calculates cost basis
- Determines realized P/L
- Resolves expirations and assignments
- Produces open positions

This logic is protected. Algorithmic modification requires L2 or higher. Full redesign requires L3.

## 4. API Contracts
All API response shapes exposed to Mission Control are protected. This includes:
- performance endpoints
- open positions endpoints
- earnings endpoints
- portfolio endpoints

Response shape changes require L2 or higher.

## 5. Canonical vs Interface Boundary
Mission Control must never:
- Become source of truth
- Store canonical trading state
- Modify canonical schema directly

Workspace remains authoritative. Boundary violations require L3.

## 6. Governance Layer
Files within `/governance/` are protected. Modifying governance requires L3.

## 7. Ideas Directory
The directory `workspace/ideas/` is a protected surface. Agents may not create or modify files in this directory.

Ideas must be written only through the API (`POST /api/ideas`). Filesystem writes to store ideas are forbidden.

## 8. System Services
All infrastructure services are managed by launchd and may not be started or stopped manually by agents. Infrastructure services include:
- OpenClaw Gateway
- Mission Control (Next.js dashboard) — managed via `com.openclaw.mission-control.plist`
- Automation runners
- Background agents

Agents must NOT start services manually using commands such as:
- `npm run dev`
- `next dev`
- `node server.py`
- `python server.py`

Before starting any service, agents must verify whether it is already managed by launchd. If a service is not responding, the correct recovery procedure is:
```
launchctl kickstart -k gui/$UID/<service-label>
```

Agents must never spawn duplicate service instances.

## 9. OpenClaw Configuration
`~/.openclaw/openclaw.json` is a protected system configuration file.

Agents must NEVER:
- Read this file
- Write to this file
- Modify this file in any way
- Pass it to any command or script

This file contains sensitive credentials and system configuration.
It is not tracked in git. Corruption requires manual recovery.
Only the user may modify this file directly.