# Semantic Clarification Protocol (SCP)

## 1. Purpose

SCP prevents semantic ambiguity before L2+ implementation. Financial and reporting logic must be unambiguous.

## 2. Rule

For all L2+ changes, Jarvis must perform a mandatory **Ambiguity Scan** before design or delegation.

## 3. SCP Requirements

### Ambiguity Scan

Jarvis must explicitly list potential ambiguities in:
- Time window definitions
- Aggregation rules
- Filtering scope
- Summary vs lifetime distinctions
- Financial metric definitions
- Edge cases

### Clarification Checklist

Jarvis must present clarification questions to the user. **No assumptions allowed** for financial/reporting logic.

## 4. Spec Lock

After user confirmation, Jarvis must declare:

> **"SEMANTIC SPEC LOCKED"**

Only after this declaration may AEF Step 2 (Design) begin.

## 5. Enforcement

If ambiguity is detected and not clarified, implementation is prohibited.
