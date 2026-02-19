# Earnings Research Process - TDS

**Version:** 1.0  
**Date:** 2026-02-19  
**Status:** Active  

---

## Overview

Weekly earnings research workflow that processes user-provided Earnings Whisper data through filtering, research, and reporting.

---

## Input

1. **User Screenshot** — Sent via Telegram/Signal
   - Contains: Earnings Whisper calendar showing stocks reporting Mon-Fri
   - Format: Image/png or text

2. **Always Include List** — `always_include_list.json`
   - Stocks user always wants researched regardless of calendar
   - Example: Portfolio holdings with earnings

3. **Exclude List** — `industrial_exclusions.json`
   - Industries to filter out (e.g., industrials, utilities)
   - Stocks to exclude regardless

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: EXTRACT TICKERS FROM SCREENSHOT                         │
│ Input: User screenshot                                          │
│ Action: OCR or manual extraction                                │
│ Output: raw_earnings_tickers_YYYY-MM-DD.json                    │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: FILTER INDUSTRIALS                                       │
│ Input: raw_earnings_tickers_YYYY-MM-DD.json                     │
│ Action: Remove by industry sector                                │
│ Output: filtered_earnings_tickers_YYYY-MM-DD.json                │
│ Script: filter_by_industry.py                                   │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: COMBINE LISTS                                           │
│ Input: filtered_tickers + always_include_list                    │
│ Action: Merge dedupe                                             │
│ Output: screened_tickers_YYYY-MM-DD.json                        │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: BOB RESEARCH                                             │
│ Input: screened_tickers_YYYY-MM-DD.json                         │
│ Action: v4.0 grading system research                            │
│ Output: analysis_YYYY-MM-DD.json                                │
│ Who: Bob (MiniMax)                                              │
│ Schema: See Appendix A                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE REPORT                                          │
│ Input: analysis_YYYY-MM-DD.json                                  │
│ Action: Convert to HTML                                          │
│ Output: report_YYYY-MM-DD.html                                  │
│ Script: generate_report.py                                       │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: SEND EMAIL                                               │
│ Input: report_YYYY-MM-DD.html                                    │
│ Action: SMTP to guanwu87@gmail.com                               │
│ Subject: Daily Earnings Research - YYYY-MM-DD                    │
│ Who: Jarvis                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Locations

| File | Path | Description |
|------|------|-------------|
| Raw screenshot | `~/.openclaw/workspace/screenshots/` | User-provided |
| Raw tickers | `data/raw_earnings_tickers_YYYY-MM-DD.json` | Extracted from screenshot |
| Filtered tickers | `data/filtered_earnings_tickers_YYYY-MM-DD.json` | After industrial filter |
| Always include | `data/always_include_list.json` | User config |
| Exclude list | `data/industrial_exclusions.json` | User config |
| Screened list | `data/screened_tickers_YYYY-MM-DD.json` | Combined list for Bob |
| Analysis | `analysis/analysis_YYYY-MM-DD.json` | Bob's research output |
| Report | `/tmp/report_YYYY-MM-DD.html` | HTML email |

---

## Key Rules

1. **NEVER auto-scrape** — Use user's screenshot as source of truth
2. **Manual extraction** — If screenshot unclear, ask user for tickers
3. **Filter FIRST** — Remove industrials before Bob runs
4. **Verify dates** — Confirm earnings dates match screenshot
5. **No API fallback** — Don't guess if data missing, ask user

---

## Cron Schedule

| Time | Job | Action |
|------|-----|--------|
| Mon-Fri 6:00 AM | Jarvis | Check for new screenshot, run Steps 1-3 |
| Mon-Fri 6:30 AM | Bob | Run Step 4 (research) |
| Mon-Fri 6:45 AM | Jarvis | Run Steps 5-6 (report + email) |

---

## Error Handling

| Error | Response |
|-------|----------|
| No screenshot | Alert user: "Waiting for earnings screenshot" |
| Unclear screenshot | Ask user: "What tickers from this week?" |
| Filter script fails | Alert user: "Filter failed, manual review needed" |
| Bob fails | Alert user: "Research failed, will retry" |
| Report fails | Alert user: "Report generation failed" |

---

## Appendix A: Analysis JSON Schema

```json
{
  "date": "2026-02-19",
  "grading_system": "v4.0",
  "stocks": {
    "WMT": {
      "ticker": "WMT",
      "grade": "B",
      "total_score": 61,
      "earnings_date": "2026-02-19",
      "expected_move_percent": 6.5,
      "iv_percentile": 95,
      "beat_rate": "75%",
      "red_flags": ["new CEO", "guidance miss risk"],
      "summary": "Good setup but expensive options"
    }
  }
}
```

---

## Appendix B: Report HTML Schema

```html
<h1>Daily Earnings Research - {date}</h1>
<h2>Grade A (High Conviction)</h2>
<!-- Stocks with grade A -->
<h2>Grade B (Monitor)</h2>
<!-- Stocks with grade B -->
<h2>Grade C/D (Avoid)</h2>
<!-- Low graded stocks -->
```

---

**Owner:** Jarvis (process owner)  
**Last Updated:** 2026-02-19
