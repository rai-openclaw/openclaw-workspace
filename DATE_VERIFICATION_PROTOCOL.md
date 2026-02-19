# Date Verification Protocol (CRITICAL)

## The Problem
Repeated date errors in earnings research make reports useless. One day error = missed trades.

## Root Causes
1. Multiple conflicting data sources (TipRanks, company IR, Finnhub, news sites)
2. Verbal reasoning ("Wed BMO = Tue actionable") prone to mental errors
3. No systematic "today vs earnings date" calculation
4. Assumptions about BMO/AMC without verification

## Solutions

### 1. Single Source of Truth (SSOT)
**Primary:** Company Investor Relations page ONLY
**Backup:** Earnings call press release from company
**Never use:** Aggregator sites (TipRanks, Yahoo, MarketBeat) as primary

### 2. Date Math Template (MANDATORY)

Before claiming any date, fill this out:

```
TODAY'S DATE: [YYYY-MM-DD, Day of week]

EARNINGS DATE: [YYYY-MM-DD]
EARNINGS TIME: [BMO / AMC / TBA]

VERIFICATION STEPS:
1. Is earnings date AFTER today? [Y/N]
2. If BMO: Actionable date = earnings date - 1 trading day
3. If AMC: Actionable date = earnings date (same day)
4. Confirm day of week for actionable date

ACTIONABLE DATE: [YYYY-MM-DD, Day of week]
RESEARCH DATE: [YYYY-MM-DD, Day of week] (day before actionable)

VERIFIED: [Y/N]
```

### 3. Visual Calendar Rule

When researching week of Feb 17-21:

```
Mon 17: [Actionable for Mon AMC, Tue BMO]
Tue 18: [Actionable for Tue AMC, Wed BMO]
Wed 19: [Actionable for Wed AMC, Thu BMO]
Thu 20: [Actionable for Thu AMC, Fri BMO]
Fri 21: [SKIP - weekend risk]
```

**Print this. Check every stock against it.**

### 4. Bob's Updated Instructions

Add to research task:

```
MANDATORY DATE VERIFICATION:

For each stock found:
1. Visit company IR page for official earnings date/time
2. Fill out Date Math Template
3. Tag with: [Actionable TODAY] or [Actionable FUTURE DATE]
4. If time unclear, mark [TBA - VERIFY]

NEVER report a date without:
- Official company source
- Completed Date Math Template
- Confirmed actionable date
```

### 5. Date Verification Checklist (Kimi)

Before sending any report:

```
- [ ] Every date verified against company IR
- [ ] Every stock has actionable date explicitly stated
- [ ] BMO stocks flagged as "trade previous day"
- [ ] AMC stocks flagged as "trade same day"
- [ ] Weekend earnings excluded
- [ ] No date assumed from memory
```

### 6. Punishment for Errors

**If a date error makes it to user:**
- Log in optimization journal
- Update protocol with specific fix
- Re-verify ALL dates in that report
- If systematic, add calendar integration

## Example (Correct)

```
Stock: LMND
IR Page: lemonade.com/investor
Earnings: Feb 19, 2026, 8:00 AM ET (BMO)

Date Math:
- Today: Feb 17, 2026 (Tue)
- Earnings: Feb 19, 2026 (Thu)
- BMO = trade day before = Feb 18 (Wed)
- Research: Feb 18 AM (Wed)

Tag: [Actionable Wed 18] - Trade before close
Research: Wed 6:30 AM

VERIFIED: YES
```

## Tools to Use

1. **Company IR Pages** - Official source
2. **Finnhub Calendar** - Cross-reference only
3. **Calendar App** - Visual day counting
4. **Date Calculator** - Trading day math

## Never Do

- Guess dates
- Trust single aggregator site
- Use verbal reasoning ("Wed BMO = Tue")
- Skip verification step
- Assume AMC vs BMO without checking

---

**Protocol Version: 1.0**
**Enforced: Immediately**
**Violations logged in: research_optimization_journal.md**
