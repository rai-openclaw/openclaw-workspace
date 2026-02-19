# Sell Put Strategy Grading System (v2.0)

**Last Updated:** February 17, 2026  
**Purpose:** Systematic evaluation of cash-secured put earnings plays

---

## Grade Scale

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A+** | 95-100 | Exceptional | Auto-trade, full size |
| **A** | 90-94 | Excellent | Strong conviction, full size |
| **B+** | 85-89 | Solid play | Good risk/reward, trade with confidence |
| **B** | 80-84 | Decent | Tradeable, watch closely |
| **C+** | 75-79 | Borderline | Small size only |
| **C** | 70-74 | Weak | Skip unless desperate |
| **D** | 65-69 | Poor | Avoid, multiple red flags |
| **F** | 0-64 | Stay away | Dangerous setup |

---

## Scoring Formula (100 Point Scale)

### 1. Earnings Consistency (25 points) — *Most Important*
Beat rate last 8 quarters:
- 7-8 beats: 25 pts
- 5-6 beats: 20 pts
- 3-4 beats: 15 pts
- 1-2 beats: 10 pts
- 0 beats: 0 pts

### 2. Premium Yield (25 points) — *Income Focus*
Expected move strike premium (weekly):
- >2.5% of strike price: 25 pts
- 2.0-2.5%: 20 pts
- 1.5-2.0%: 15 pts
- 1.0-1.5%: 10 pts
- 0.5-1.0%: 5 pts
- <0.5%: 0 pts

### 3. Safety Margin (20 points) — *Protection*
Strike distance vs expected move:
- >2x expected move away: 20 pts
- 1.5-2x expected move: 15 pts
- 1.0-1.5x expected move: 10 pts
- 0.5-1.0x expected move: 5 pts
- <0.5x expected move: 0 pts

### 4. Expected Move Respect (15 points) — *Historical Behavior*
Does stock stay within expected move historically?
- 80%+ within range: 15 pts
- 60-79%: 10 pts
- 40-59%: 5 pts
- <40%: 0 pts

### 5. Financial Health Trend (10 points) — *Business Quality*
- Consistent growth/profitability: 10 pts
- Stable: 5 pts
- Declining: 0 pts

### 6. External Catalyst Risk (5 points) — *Adjustment Only*
- Clean/no major news: 5 pts
- Known/announced events (M&A, Fed): 3 pts
- Rumored/new events: 0 pts

---

## Red Flags (Point Deductions, Not Auto-Downgrades)

| Risk Factor | Deduction |
|-------------|-----------|
| Recent major M&A (announced) | -2 pts |
| Recent major M&A (rumored/surprise) | -5 pts |
| Fed week / FOMC meeting | -3 pts |
| Friday after-bell earnings | Exclude entirely |
| Recent analyst downgrade cluster | -2 pts |
| Insider selling (significant) | -2 pts |
| Double whammy potential (external + earnings) | -5 pts |

---

## Grade Benchmarks

### A (90-100): "Exceptional"
**Example:** CRM with 6% expected move, $5+ premium, 15 quarters of beats, calm external environment
- Rare: Maybe 1-2 per month
- Auto-trade with full size

### B+ (85-89): "Solid play"
**Example:** PANW today — 9 quarters beats, 2.5% premium, known M&A noise
- Good risk/reward
- Trade with confidence, normal size

### B (80-84): "Decent"
- Tradeable but watch closely
- Either good premium with some risk OR low premium but super safe

### C+ (75-79): "Borderline"
- Small size only if trading
- Mediocre premium + some risk flags

### C (70-74): "Weak"
- Skip unless desperate
- Low premium OR high risk, not worth it

### D/F (<70): "Avoid"
- Dangerous setup
- UNH disaster scenario (external news + earnings bomb)

---

## Example Calculations

### PANW (Feb 17, 2026)
| Category | Score | Notes |
|----------|-------|-------|
| Earnings Consistency | 25/25 | 9/9 quarters beats |
| Premium Yield | 25/25 | $150 PUT @ $3.75 = 2.5% weekly |
| Safety Margin | 18/20 | $150 = 10.2% below (1.1x expected move) |
| Expected Move Respect | 8/15 | 2x historical avg = risky |
| Financial Health | 8/10 | Good but slowing growth |
| External Catalyst | 3/5 | Known CyberArk M&A (-2) |
| **TOTAL** | **87/100 = B+** | Solid play, trade with confidence |

### CDNS (Feb 17, 2026)
| Category | Score | Notes |
|----------|-------|-------|
| Earnings Consistency | 25/25 | 4/4 quarters beats |
| Premium Yield | 5/25 | $280 PUT @ $1.75 = 0.6% weekly |
| Safety Margin | 20/20 | Very safe distance |
| Expected Move Respect | 15/15 | Historically stable |
| Financial Health | 8/10 | Stable, slow growth |
| External Catalyst | 2/5 | Fed week (-3) |
| **TOTAL** | **75/100 = C+** | Borderline, low premium |

---

## Quick Reference Card

| Grade | Score | Verdict | Sizing |
|-------|-------|---------|--------|
| A+/A | 90-100 | Exceptional | Full size |
| B+ | 85-89 | Solid play | Full size |
| B | 80-84 | Decent | Normal size |
| C+ | 75-79 | Borderline | Small size |
| C | 70-74 | Weak | Skip |
| D/F | <70 | Avoid | Skip |

**Key Principle:** Premium yield and earnings consistency matter most. External catalysts are adjustments, not deal-breakers.
