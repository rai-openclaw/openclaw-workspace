# Earnings Screener Workflow v1.0
## Final Locked Process (As of Feb 17, 2026)

**Status:** ACTIVE  
**Last Updated:** February 17, 2026  
**Owner:** Rai  
**EA:** Kimi

---

## Overview

Daily earnings screener that filters high-profile stocks reporting earnings, applies grading system, and delivers actionable report to Rai's Gmail every market morning.

---

## Weekly Setup (Sunday Evening)

**Trigger:** Automated reminder

**Process:**
1. Reminder prompts Rai to upload Earnings Whispers pinned tweet image
2. Rai uploads image via Telegram
3. Kimi extracts ticker symbols with dates/times using Gemini Flash 2.5
4. Save to `weekly_earnings_schedule.json`

**Output:** Weekly schedule with ~50-70 tickers and their reporting dates/times

---

## Daily Execution (Monday-Friday, 6:30 AM PST)

### Step 1: Screener Script (Automated)
**Tool:** `earnings_screener.py`

**Input:** `weekly_earnings_schedule.json`

**Filters Applied:**
- Date filter: Today AMC + Tomorrow BMO only
- Sector exclusions:
  - REITs
  - Utilities
  - Consumer Staples
  - Industrials
  - Basic Materials
- Always-include check: WMT, TSLA, NVDA, AAPL, MSFT, AMZN, GOOGL, META bypass sector filters

**Output:** 1-15 filtered stocks with symbol, market cap, sector

---

### Step 2: Bob Research (Sub-agent)
**Agent:** Bob (Senior Earnings Analyst)
**Model:** DeepSeek V3

**Input:** Filtered stock list from Step 1

**Tasks:**
1. Research each stock's expected move
2. Check historical earnings move accuracy
3. Look for external catalysts/news
4. Apply Grading System v3.0:
   - Earnings Predictability (30 pts)
   - Expected Move Respect (25 pts)
   - Assignment Desirability (20 pts)
   - Premium Yield (20 pts)
   - Binary Risk (-5 to 0 pts)
5. Generate raw research notes

**Output:** Research data sent to Kimi (not directly to Rai)

---

### Step 3: Report Compilation (Kimi)
**Agent:** Kimi (EA)
**Model:** Moonshot K2.5

**Input:**
- Screener output (stocks + market caps + sectors)
- Bob's research (grades, expected moves, notes)

**Tasks:**
1. Compile final formatted report
2. Format as table with columns:
   - Ticker
   - Market Cap
   - Expected Move
   - 2x Expected Move (safety margin)
   - Grade (A-F)
   - Score (0-100)
   - Recommendation (Trade/Avoid/Watch)
   - Notes/Catalysts
3. Quality check for completeness
4. Add any necessary context/flags

**Output:** Final report ready for delivery

---

### Step 4: Delivery
**Time:** By 6:45 AM PST
**Channel:** Gmail (guanwu87@gmail.com)
**Subject:** "Daily Earnings Screener - [Day] [Date]"

---

## Report Format

```
DAILY EARNINGS SCREENER - Wednesday February 18, 2026
Generated: 6:35 AM PST

CATEGORY 1: Today AMC (After Close) - Trade before 4 PM
| Ticker | Market Cap | Exp Move | 2x Move | Grade | Score | Rec | Notes |
|--------|-----------|----------|---------|-------|-------|-----|-------|
| CVNA   | $74.6B    | ±12%     | ±24%    | B+    | 78    | Trade | Q4 deliveries |
| DASH   | $69.1B    | ±10%     | ±20%    | A-    | 85    | Trade | Strong growth |
| EBAY   | $37.2B    | ±8%      | ±16%    | B     | 72    | Watch | Guidance key |
| RELY   | $4.5B     | ±15%     | ±30%    | C+    | 68    | Avoid | High volatility |

CATEGORY 2: Tomorrow BMO (Before Open) - Trade before 4 PM
| Ticker | Market Cap | Exp Move | 2x Move | Grade | Score | Rec | Notes |
|--------|-----------|----------|---------|-------|-------|-----|-------|
| WMT    | $1,028B   | ±5%      | ±10%    | B     | 75    | Trade | Always include |
| LMND   | $4.8B     | ±14%     | ±28%    | B+    | 79    | Trade | Beat streak |
| W      | $10.8B    | ±18%     | ±36%    | A-    | 82    | Trade | Turnaround play |

AUDIT LOG:
  Weekly schedule: 63 tickers
  Screener filtered: 19 tickers
  Bob graded: 11 tickers
  Final report: 11 tickers

METHODOLOGY:
  ✓ Earnings Whispers weekly focus list
  ✓ Sector exclusions applied
  ✓ Grading System v3.0
  ✓ Quality checked
```

---

## Files & Locations

| File | Purpose | Location |
|------|---------|----------|
| `weekly_earnings_schedule.json` | Weekly earnings data | `~/.openclaw/workspace/` |
| `earnings_screener.py` | Screener script | `~/.openclaw/workspace/` |
| `earnings_screener_lists.json` | Exclude/always-include lists | `~/.openclaw/workspace/` |
| `sell_put_grading_system_v3.md` | Grading methodology | `~/.openclaw/workspace/` |
| `EARNINGS_SCREENER_WORKFLOW.md` | This document | `~/.openclaw/workspace/` |

---

## Agent Responsibilities

### Kimi (EA)
- Sunday: Extract weekly data from EW image
- Daily: Run screener script
- Daily: Compile final report
- Daily: Deliver to Gmail
- Quality control

### Bob (Senior Earnings Analyst)
- Daily: Research filtered stocks
- Daily: Apply grading system
- Daily: Send raw research to Kimi

---

## Success Criteria

- Report delivered by 6:45 AM daily
- 1-15 stocks per report
- All stocks have grades and expected moves
- No manual intervention required (except Sunday upload)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-17 | Initial locked workflow |

---

**END OF DOCUMENT**

**This workflow is locked. Changes require explicit approval from Rai.**
