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

End of Protected Surfaces.
