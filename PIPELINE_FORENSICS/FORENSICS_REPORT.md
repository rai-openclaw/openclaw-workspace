# Pipeline Forensics Report

**Run Date:** March 16, 2026  
**Execution Time:** 06:34 - 06:35 PST  
**Pipeline Version:** run_pipeline.py

---

## Stage 1: pull_earnings_today.py

| Attribute | Value |
|-----------|-------|
| Script | `pull_earnings_today.py` |
| Input | Nasdaq Earnings Calendar API |
| Output | `data/cache/todays_candidates.json` |
| Total Raw | 423 earnings |
| After Timing Filter | 89 candidates |
| Final Output | 89 tickers |

### Sample Entry (First Ticker)

```json
{
  "ticker": "KT",
  "report_time": "AMC",
  "report_date": "2026-03-16",
  "source": "nasdaq_filtered"
}
```

### Field Schema

| Field | Type | Description |
|-------|------|-------------|
| ticker | string | Stock symbol |
| report_time | string | "AMC" or "BMO" |
| report_date | string | YYYY-MM-DD |
| source | string | "nasdaq_filtered", "include_list" |

---

## Stage 2: research_engine.py

| Attribute | Value |
|-----------|-------|
| Script | `research_engine.py` |
| Input | `data/cache/todays_candidates.json` |
| Output | `data/analysis/analysis_raw.json` |
| Input Count | 89 candidates |
| After Filters | 3 tradeable |

### Sample Entry (First Ticker - SMTC)

```json
{
  "ticker": "SMTC",
  "analysis_date": "2026-03-16T06:35:43.389238",
  "price_timeline": [...],
  "key_movement": {
    "type": "earnings spike",
    "magnitude": 34.17,
    "reference_frames": {...}
  },
  "earnings_event": {
    "date": "2025-11-25",
    "price_before": 63.85,
    "price_after": 71.78,
    "reaction_percent": 12.42
  },
  "options_context": {
    "implied_move": 13.96,
    "atm_iv": 162.2,
    "underlying_price": 86.65,
    "dte": 4,
    "expiration": "2026-03-20"
  },
  "historical_volatility": {
    "down_1x": 0.95,
    "down_1_5x": 1.0,
    "down_2x": 1.0,
    "median_move": 0.0478
  },
  "technical_analysis": {
    "support_levels": [82.02],
    "resistance_levels": [96.3],
    "trend": "bullish",
    "sma_20": 87.75,
    "sma_50": 83.62
  },
  "sector_context": {...},
  "trade_desk_analysis": {...},
  "market": {...},
  "options": {...},
  "report": {...},
  "probabilities": {...},
  "grading": {...},
  "meta": {...}
}
```

### Field Schema (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| ticker | string | Stock symbol |
| analysis_date | datetime | ISO timestamp |
| price_timeline | array | 30-day price history |
| key_movement | object | Price spike detection |
| earnings_event | object | Past earnings reaction |
| options_context | object | IV, EM, DTE, expiration |
| historical_volatility | object | Downside probabilities |
| technical_analysis | object | Trend, SMA, support/resistance |
| sector_context | object | Relative performance |
| trade_desk_analysis | object | Summary, viability assessment |
| market | object | Price, ATM strike |
| options | object | Straddle, EM % |
| report | object | Date, time (AMC/BMO) |
| probabilities | object | Down 1x, 1.5x, 2x |
| grading | object | Grade, score |
| meta | object | Status, tags |

---

## Stage 3: probability_engine_v1.py

| Attribute | Value |
|-----------|-------|
| Script | `probability_engine_v1.py` |
| Input | `data/analysis/analysis_raw.json` |
| Output | `data/analysis/analysis_with_probs.json` |
| Input Count | 3 candidates |
| Output Count | 3 with probabilities |

### Sample Entry (First Ticker - SMTC)

```json
{
  "ticker": "SMTC",
  "report": {"date": "2026-03-16", "time": "AMC"},
  "market": {"price": 86.55, "atm_strike": 85.0, "expiration": "2026-03-20"},
  "options": {"straddle": 12.55, "em_percent": 14.50},
  "probabilities": {
    "down_1x": 0.95,
    "down_1_5x": 1.0,
    "down_2x": 1.0,
    "median_move": 0.0478,
    "max_move": 0.1887
  },
  "grading": {"grade": null, "score_total": null, "data_ready": true},
  "meta": {"status": "ok", "tags": ["TRADE"]}
}
```

### Field Schema

| Field | Type | Description |
|-------|------|-------------|
| ticker | string | Stock symbol |
| report | object | Date, time |
| market | object | Price, ATM strike, expiration |
| options | object | Straddle cost, EM % |
| probabilities | object | Down 1x, 1.5x, 2x, median, max |
| grading | object | Grade, score, data_ready |
| meta | object | Status, tags |

---

## Stage 4: analysis_batch.py

| Attribute | Value |
|-----------|-------|
| Script | `analysis_batch.py` |
| Input | `data/analysis/analysis_raw.json` |
| Output | `data/analysis/analysis_raw.json` (overwrites) |
| Action | Calls `analyze_batch()` from analysis_engine.py |

**Note:** Stage 4 runs the unified analysis engine which enriches the data with:
- Full news timeline
- Material events
- Analyst activity
- Enhanced trade desk analysis
- Sector context
- Peer context

The output is written back to `analysis_raw.json`, which now contains the full enriched data (same as Stage 2 sample shown above).

---

## Stage 5: send_email.py

| Attribute | Value |
|-----------|-------|
| Script | `send_email.py` |
| Input | `data/analysis/analysis_raw.json` |
| Output | Email to guanwu87@gmail.com |
| Recipients | guanwu87@gmail.com |

### Email Render Summary

The email renders the following data for each ticker:

| Section | Fields |
|---------|--------|
| Header | Ticker, Price, EM%, Report Date/Time |
| Key Metrics | Implied Move, Historical Median, ATM IV |
| Technical | Trend, Sector ETF, Sector Relative Return |
| Catalysts | Material events, news headlines |
| Trade Desk | Summary, CSP viability, downside probabilities |
| Probability Table | ↓1x, ↓1.5x, ↓2x columns |

---

## Pipeline Statistics

| Metric | Value |
|--------|-------|
| Total Raw Earnings | 423 |
| After Timing Filter | 89 |
| After Price Filter (> $15) | ~19 |
| After Healthcare Filter | ~19 |
| After Weekly Options Filter (DTE 0-10) | 3 |
| Final Tradeable Candidates | 3 |

### Filter Breakdown

- **Filtered (No Weekly Options):** 16
- **Filtered (Options Unavailable):** 0
- **Tradeable:** 3 (SMTC, GDS, ASO)

---

## Artifacts Location

```
PIPELINE_FORENSICS/
├── stage1_calendar/
│   ├── pull_earnings_today.py
│   └── todays_candidates.json
├── stage2_research/
│   ├── research_engine.py
│   └── analysis_raw.json
├── stage3_probabilities/
│   ├── probability_engine_v1.py
│   └── analysis_with_probs.json
├── stage4_analysis/
│   ├── analysis_batch.py
│   └── analysis_raw.json (enriched)
└── stage5_email_render/
    └── send_email.py
```
