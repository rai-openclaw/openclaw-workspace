# Earnings Research Process - TDS

**Version:** 2.0  
**Date:** 2026-02-19  
**Status:** Active  

---

## Overview

Weekly earnings research workflow that processes user-provided Earnings Whisper data once, then daily filtering for research and reporting.

---

## Input

1. **User Screenshot** — Sent via Telegram/Signal (WEEKLY, usually Sunday)
   - Contains: Earnings Whisper calendar showing stocks reporting Mon-Fri
   - Format: Image/png

2. **Always Include List** — `always_include_list.json`
   - Stocks user always wants researched regardless of calendar

3. **Always Exclude List** — `always_exclude_list.json`
   - Stocks/industries to always exclude (e.g., industrials)

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ WEEKLY: EXTRACT & STORE (Once when screenshot received)         │
├─────────────────────────────────────────────────────────────────┤
│ STEP 1: EXTRACT TICKERS FROM SCREENSHOT                         │
│ Input: User screenshot                                          │
│ Action: OCR or manual extraction                                │
│ Output: raw_tickers_YYYY-MM-DD.json                            │
│ Format: [{ticker, date, time (BMO/AMC)}, ...]                 │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: FILTER & STORE                                          │
│ Input: raw_tickers                                              │
│ Action: Remove always_exclude                                   │
│ Output: weekly_earnings_calendar_YYYY-MM-DD.json              │
│ Format: [{ticker, date, time, filtered: false}, ...]          │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│ DAILY: RESEARCH CYCLE (Mon-Fri 6:30 AM)                        │
├─────────────────────────────────────────────────────────────────┤
│ STEP 3: FILTER DAILY LIST                                        │
│ Input: weekly_earnings_calendar + always_include                │
│ Action: Filter by today(AMC) + tomorrow(BMO) + always_include  │
│ Output: screened_tickers_YYYY-MM-DD.json                       │
│ Who: Jarvis (or Bob)                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: BOB RESEARCH                                            │
│ Input: screened_tickers_YYYY-MM-DD.json                        │
│ Action: v4.0 grading system research                           │
│ Output: analysis_YYYY-MM-DD.json                               │
│ Who: Bob (MiniMax)                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE & SEND REPORT                                   │
│ Input: analysis_YYYY-MM-DD.json                                 │
│ Action: HTML + email                                            │
│ Output: Email to guanwu87@gmail.com                            │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Locations

| File | Path | Description |
|------|------|-------------|
| User screenshot | `screenshots/earnings_*` | User-provided |
| Raw tickers | `data/raw_tickers_YYYY-MM-DD.json` | Extracted from screenshot |
| Weekly calendar | `data/weekly_earnings_calendar.json` | Filtered, persistent |
| Always include | `data/always_include_list.json` | User config |
| Always exclude | `data/always_exclude_list.json` | User config |
| Daily screened | `data/screened_tickers_YYYY-MM-DD.json` | Today's list |
| Analysis | `analysis/analysis_YYYY-MM-DD.json` | Bob's output |

---

## Weekly Calendar JSON Schema

```json
{
  "week_of": "2026-02-16",
  "created": "2026-02-15T14:00:00Z",
  "source": "earnings_whisper_screenshot",
  "earnings": [
    {"ticker": "WMT", "date": "2026-02-19", "time": "BMO"},
    {"ticker": "NVDA", "date": "2026-02-19", "time": "AMC"},
    {"ticker": "BABA", "date": "2026-02-20", "time": "BMO"}
  ]
}
```

---

## Daily Filter Logic

```python
today = date.today()
tomorrow = today + timedelta(days=1)

# Get today's AMC + tomorrow's BMO
daily_tickers = [
    e for e in weekly_calendar["earnings"]
    if (e["date"] == today and e["time"] == "AMC") or
       (e["date"] == tomorrow and e["time"] == "BMO")
]

# Add always_include
for ticker in always_include_list:
    if ticker not in daily_tickers:
        daily_tickers.append(ticker)

# Remove always_exclude
daily_tickers = [t for t in daily_tickers if t not in always_exclude]
```

---

## Cron Schedule (Updated)

| Time | Job | Trigger |
|------|-----|---------|
| Weekly (Sun 4pm) | Jarvis - Process Screenshot | Manual or when screenshot detected |
| Mon-Fri 6:00 AM | Jarvis - Filter Daily List | Automatic |
| Mon-Fri 6:30 AM | Bob - Research | Automatic |
| Mon-Fri 6:45 AM | Jarvis - Send Report | Automatic |

---

## Key Rules

1. **Screenshot processed ONCE** — Extract and store, never repeat
2. **Daily = filter only** — No re-extraction needed
3. **Always include merged daily** — Portfolio positions always researched
4. **Always exclude applied once** — At weekly storage time

---

**Owner:** Jarvis  
**Last Updated:** 2026-02-19  
**Version:** 2.0
