# Earnings Screener Protocol v3.2
## Agent Enforcement Version

**Created:** February 17, 2026  
**Updated:** February 17, 2026 (Enforcement v3.2)  
**Purpose:** Daily earnings screening with STRICT protocol compliance  
**Status:** ACTIVE

---

## CRITICAL: Agent Task Prefix

**MUST INCLUDE THIS AT THE START OF EVERY AGENT TASK:**

> **STRICT PROTOCOL ENFORCEMENT:** You may ONLY perform the steps listed below. Adding ANY additional analysis, filtering, scoring, ranking, or steps beyond what is explicitly listed is a **PROTOCOL VIOLATION**. If you catch yourself adding extra steps, STOP and remove them. Output ONLY what is requested. No recommendations. No analysis. No "helpful extras."

---

## Architecture Overview

```
WEEKLY SETUP (Sunday Evening):
├── User uploads Earnings Whispers pinned tweet image
├── Extract using Gemini Flash 2.5 OCR
├── Store ticker + date + time (BMO/AMC) in weekly_earnings_schedule.json
└── Data source: Single tweet, extracted as-is

DAILY EXECUTION (Tue-Sat 6:30 AM):
┌─────────────────────────────────────────────────────────────────────┐
│                    EARNINGS SCREENER PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE 1: INGESTION                                                  │
│  ├── Load weekly_earnings_schedule.json                             │
│  ├── Identify Category A: Today AMC tickers                         │
│  ├── Identify Category B: Tomorrow BMO tickers                      │
│  ├── Log counts                                                     │
│  └── CHECKPOINT: Stop. Wait for user confirmation.                  │
│                                                                      │
│  PHASE 2: ENRICHMENT                                                 │
│  ├── Fetch market_cap for each ticker                               │
│  ├── Fetch sector for each ticker                                   │
│  ├── DO NOT fetch: momentum, fundamentals, sentiment,               │
│  │                 analyst ratings, debt/equity, growth metrics     │
│  ├── Log completion                                                 │
│  └── CHECKPOINT: Stop. Wait for user confirmation.                  │
│                                                                      │
│  PHASE 3: FILTERING (SECTOR ONLY)                                    │
│  ├── Exclude tickers with sector in:                                │
│  │   [REITs, Utilities, Consumer Staples, Real Estate,             │
│  │    Electric Utilities, Food Products]                            │
│  ├── Check always-include list (bypass sector filter if match)      │
│  ├── DO NOT apply: momentum filters, fundamental screening,         │
│  │                  volatility checks, scoring, ranking             │
│  ├── Log exclusions                                                 │
│  └── CHECKPOINT: Stop. Wait for user confirmation.                  │
│                                                                      │
│  PHASE 4: OUTPUT                                                     │
│  ├── List Category A tickers (Today AMC) with market cap            │
│  ├── List Category B tickers (Tomorrow BMO) with market cap         │
│  ├── Provide audit log: "Processed X, Passed Y, Excluded Z"         │
│  ├── DO NOT provide: analysis, recommendations, momentum scores,    │
│  │                    rankings, "high priority" labels               │
│  └── FINAL CHECKPOINT: Answer "Did you add any steps not explicitly │
│                       listed above?" If YES → discard and restart.  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Weekly Setup (Sunday Evening)

**Trigger:** Reminder prompts user to upload image

**Process:**
1. **User uploads** Earnings Whispers pinned tweet image via Telegram
2. **Extract using Gemini Flash 2.5:**
   ```
   Prompt: "Extract all stock ticker symbols with their dates and times 
   (BMO/AMC) for the week. List by day: Monday BMO, Monday AMC, 
   Tuesday BMO, Tuesday AMC, etc."
   ```
3. **Store in** `weekly_earnings_schedule.json`:
   ```json
   {
     "week_of": "2026-02-16",
     "extracted_by": "gemini-flash-2.5",
     "source": "earnings_whispers_pinned_tweet",
     "tickers": [
       {"symbol": "CVNA", "date": "2026-02-18", "time": "AMC"},
       {"symbol": "WMT", "date": "2026-02-19", "time": "BMO"}
     ]
   }
   ```

**Important:** Gemini Flash 2.5 is the designated OCR tool. Do NOT use local tesseract or visual reading.

---

## Daily Execution Protocol

### Phase 1: Ingestion

**MANDATORY TASK PREFIX:**
> STRICT PROTOCOL ENFORCEMENT: Phase 1 only. Load data. Identify categories. Log counts. STOP. Do not proceed to Phase 2.

**Steps:**
- [ ] Load `weekly_earnings_schedule.json`
- [ ] Filter for Category A: `date == TODAY && time == "AMC"`
- [ ] Filter for Category B: `date == TOMORROW && time == "BMO"`
- [ ] Log: "Category A: [N] tickers, Category B: [N] tickers"

**EXPLICITLY DO NOT:**
- ❌ Add any tickers not in the weekly schedule
- ❌ Remove tickers based on any criteria
- ❌ Proceed to Phase 2 without user confirmation

---

### Phase 2: Enrichment

**MANDATORY TASK PREFIX:**
> STRICT PROTOCOL ENFORCEMENT: Phase 2 only. Fetch market cap and sector. NOTHING ELSE. STOP after completion.

**Steps:**
- [ ] For each ticker in Category A + B:
  - [ ] Fetch `marketCapitalization` from Finnhub `/stock/profile2`
  - [ ] Fetch `industry`/`sector` from Finnhub `/stock/profile2`
- [ ] Store enriched data
- [ ] Log: "Enriched [N] tickers"

**EXPLICITLY DO NOT:**
- ❌ Fetch momentum data
- ❌ Fetch fundamentals (P/E, debt/equity, growth)
- ❌ Fetch analyst ratings
- ❌ Fetch sentiment scores
- ❌ Calculate any metrics
- ❌ Proceed to Phase 3 without user confirmation

---

### Phase 3: Filtering (SECTOR ONLY)

**MANDATORY TASK PREFIX:**
> STRICT PROTOCOL ENFORCEMENT: Phase 3 only. Apply SECTOR filter ONLY. No other filters. No scoring. No ranking. STOP after completion.

**Steps:**
- [ ] Load `earnings_screener_lists.json` (exclude and always-include lists)
- [ ] For each ticker:
  - [ ] IF ticker in `exclude_list` → EXCLUDE (log reason)
  - [ ] ELSE IF ticker in `always_include_list` → INCLUDE (log "bypass sector filter")
  - [ ] ELSE IF sector in `[REITs, Utilities, Consumer Staples, Real Estate, Electric Utilities, Food Products]` → EXCLUDE (log sector)
  - [ ] ELSE → INCLUDE
- [ ] Log: "Passed: [N], Excluded: [N]"

**EXPLICITLY DO NOT:**
- ❌ Filter by market cap
- ❌ Filter by momentum
- ❌ Filter by fundamentals
- ❌ Filter by volatility
- ❌ Score or rank tickers
- ❌ Apply "quality" metrics
- ❌ Proceed to Phase 4 without user confirmation

---

### Phase 4: Output

**MANDATORY TASK PREFIX:**
> STRICT PROTOCOL ENFORCEMENT: Phase 4 only. Output lists. Provide audit log. NO ANALYSIS. NO RECOMMENDATIONS. FINAL CHECKPOINT before completion.

**Steps:**
- [ ] List Category A tickers with: symbol, market_cap, sector
- [ ] List Category B tickers with: symbol, market_cap, sector
- [ ] Provide audit log:
  ```
  AUDIT LOG:
    Phase 1: Processed [N] tickers from weekly schedule
      - Category A: [N] tickers
      - Category B: [N] tickers
    Phase 2: Enriched [N] tickers
    Phase 3: [N] tickers passed sector filter
      - Excluded by sector: [N]
      - Excluded by exclude list: [N]
      - Always-include bypass: [N]
    Phase 4: [N] tickers in final list
  ```
- [ ] **FINAL CHECKPOINT:** Answer: "Did you add any steps not explicitly listed in Protocol v3.2?"
    - If YES → "Protocol violation detected. Discarding output. Restarting from Phase 1."
    - If NO → "Protocol compliance verified. Task complete."

**EXPLICITLY DO NOT:**
- ❌ Provide analysis or commentary
- ❌ Label tickers as "high priority" or "top pick"
- ❌ Add momentum scores
- ❌ Add rankings
- ❌ Provide trading recommendations
- ❌ Add "helpful context" or "insights"

---

## Supporting Files

### weekly_earnings_schedule.json
Updated weekly via Gemini OCR. Contains ticker + date + time.

### earnings_screener_lists.json
```json
{
  "exclude_list": {
    "description": "Never include these tickers",
    "stocks": []
  },
  "always_include_list": {
    "description": "Bypass sector filter if in this list",
    "stocks": [
      {"symbol": "WMT", "reason": "Core holding", "added_date": "2026-02-17"}
    ]
  }
}
```

---

## Protocol Violation Examples

| Violation | Why It's Wrong | Correct Action |
|-----------|---------------|----------------|
| "CVNA has strong momentum so I ranked it #1" | Added momentum analysis | Just list CVNA with market cap and sector |
| "Filtered out small caps under $5B" | Added market cap filter | Only apply sector filter |
| "Applied fundamental screening" | Added extra phase | Only sector filter in Phase 3 |
| "Top 3 picks based on catalysts" | Added ranking/analysis | List all tickers that passed filter |
| "EQX scored 8.5/10" | Added scoring | No scores, just list the ticker |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-02-17 | Initial 3-rule protocol |
| v2.0-2.2 | 2026-02-17 | Phase-based with Tier 1 filters |
| v3.0 | 2026-02-17 | Simplified weekly focus architecture |
| **v3.2** | 2026-02-17 | **Agent enforcement version with explicit negative constraints** |

---

**END OF PROTOCOL**

**Remember:** If it doesn't say you CAN do it, you CAN'T do it. Strict compliance only.
