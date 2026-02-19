# SIMPLE EARNINGS RULE — NO DEVIATION

## The Rule (Memorize This)

**Daily Report Shows:**
1. TODAY AMC (after close today) → Trade today before 4 PM
2. TOMORROW BMO (before open tomorrow) → Trade today before 4 PM

**That's it. Two categories. Nothing else.**

## What's NOT in Daily Report

- ❌ TODAY BMO (already happened)
- ❌ YESTERDAY anything (already happened)
- ❌ Day after tomorrow (too far out)

## Examples

### Tuesday Report (6:30 AM Tuesday):
- Tuesday AMC
- Wednesday BMO

### Wednesday Report (6:30 AM Wednesday):
- Wednesday AMC
- Thursday BMO

### Thursday Report (6:30 AM Thursday):
- Thursday AMC
- Friday BMO

## Simple Check

Before outputting any report, ask:
1. Is this stock reporting TODAY AMC? → Include
2. Is this stock reporting TOMORROW BMO? → Include
3. Anything else? → EXCLUDE

## What Caused Errors

- Adding "helpful context" about Tuesday BMO (not actionable)
- Trying to show "what already reported" (not actionable)
- Listing stocks without verifying their timing
- Mental shortcuts instead of checking the rule

## The Protocol

**Step 1:** Get data from Finnhub/Earnings Whispers
**Step 2:** Filter to ONLY:
  - Today's date + AMC
  - Tomorrow's date + BMO
**Step 3:** Output those two categories only
**Step 4:** NOTHING ELSE

## If Confused

Stop. Ask:
- "What day is the report?" → Wednesday
- "What's actionable today?" → Wednesday AMC + Thursday BMO
- "Output only that."

No exceptions. No additions. No "but also..."

## Penalty for Deviation

If I include wrong category:
- Stop immediately
- Re-read this file
- Start over with correct categories only

---

**This is the only rule. Follow it exactly.**
