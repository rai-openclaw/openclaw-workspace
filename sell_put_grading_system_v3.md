# Sell Put Strategy Grading System (v3.0) — Volatility-Optimized

**Last Updated:** February 17, 2026  
**Purpose:** Grade earnings plays for volatility traders (not long-term investors)

---

## Philosophy

**We trade volatility, not companies.**

A "good" earnings play:
1. Stays within expected move (you keep premium)
2. Pays well for the risk (high yield)
3. Won't blow up your account if assigned

An inflated expected move (like PANW's 9%) can be BETTER than normal if risk is priced in — you get more premium for similar win probability.

---

## Grade Scale

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A+** | 95-100 | Exceptional volatility trade | Full size, best setup |
| **A** | 90-94 | Excellent risk/reward | Full size |
| **B+** | 85-89 | Solid volatility play | Normal size |
| **B** | 80-84 | Decent trade | Normal size, watch closely |
| **C+** | 75-79 | Borderline | Small size or skip |
| **C** | 70-74 | Weak | Skip unless desperate |
| **D** | 65-69 | Poor | Avoid |
| **F** | 0-64 | Dangerous | Stay away |

---

## Scoring Formula (100 Points)

### 1. Earnings Predictability (30 points)
**Question:** Will they beat/miss, or stay predictable?

| Beat Rate Last 8Q | Points |
|-------------------|--------|
| 7-8 beats | 30 pts |
| 5-6 beats | 25 pts |
| 3-4 beats | 20 pts |
| 1-2 beats | 10 pts |
| 0 beats | 0 pts |

**Why it matters:** Predictable companies respect expected moves. Surprises cause blowouts.

---

### 2. EM Respect at Current Level (25 points)
**Question:** Will stock stay within TODAY's expected move (not historical)?

| Confidence Level | Points | Example |
|------------------|--------|---------|
| Very high (85%+) | 25 pts | Known catalyst priced in, likely contained |
| High (75-84%) | 20 pts | Normal pattern, expect containment |
| Medium (60-74%) | 15 pts | Uncertain, 50/50 |
| Low (40-59%) | 8 pts | Volatile name, often exceeds EM |
| Very low (<40%) | 0 pts | Meme stock, avoid |

**Key insight:** Inflated EM (like PANW 9% vs normal 4.5%) can score HIGH here if you believe the risk is priced in. You're grading "will it stay within 9%?" not "is 9% unusual?"

---

### 3. Assignment Desirability (20 points)
**Question:** If assigned, do I want to own this?

| Factor | Assessment | Points |
|--------|------------|--------|
| Valuation | Reasonable PE (<50x) | 8 pts |
| Growth | Growing revenue/earnings | 6 pts |
| Balance Sheet | Strong cash, low debt | 6 pts |
| Red flags | High PE, declining growth | -5 to 0 pts |

**Why it matters:** 10-20% of puts get assigned. Don't sell puts on garbage you'd hate to own.

---

### 4. Premium Yield (20 points)
**Question:** Is the income worth the capital tie-up?

| Weekly Yield at 1x EM Strike | Points |
|------------------------------|--------|
| >2.5% | 20 pts |
| 2.0-2.5% | 17 pts |
| 1.5-2.0% | 14 pts |
| 1.0-1.5% | 10 pts |
| 0.5-1.0% | 5 pts |
| <0.5% | 0 pts |

**Why it matters:** You're tying up capital. 0.6% weekly (CDNS) doesn't justify $28k margin.

---

### 5. Binary Risk Penalty (-5 to 0 points)
**Question:** Any surprise events, not already priced in?

| Risk Type | Penalty |
|-----------|---------|
| Known/announced M&A | 0 pts (priced in) |
| Fed week (known event) | -1 pt |
| Rumored/new M&A | -3 pts |
| Surprise CEO departure | -4 pts |
| Regulatory investigation (new) | -5 pts |
| "Double whammy" risk | -5 pts |

**Key insight:** Only penalize SURPRISES. Known risks are already in the EM.

---

## How to Explain Grades in Reports

**Required format for each stock:**

```
### [TICKER] — Grade: [X] ([Score]/100)

| Component | Score | Explanation |
|-----------|-------|-------------|
| Earnings Predictability (30) | XX/30 | [Why: beat rate, consistency] |
| EM Respect at Current (25) | XX/25 | [Why: will it stay in today's EM?] |
| Assignment Desirability (20) | XX/20 | [Why: want to own if assigned?] |
| Premium Yield (20) | XX/20 | [Why: yield worth capital?] |
| Binary Risk Penalty (0) | -X/0 | [Any surprises?] |
| **TOTAL** | **XX/100** | **[Grade]** |

**Key Insight:** [1-2 sentence summary of why this grade]
```

---

## Example: PANW (Feb 17, 2026)

### PANW — Grade: B+ (84/100)

| Component | Score | Explanation |
|-----------|-------|-------------|
| Earnings Predictability (30) | 29/30 | 9 straight beats. They execute consistently. |
| EM Respect at Current (25) | 22/25 | 9% EM is inflated but risk is priced in. Likely stays within 9% if they execute. |
| Assignment Desirability (20) | 13/20 | Great company but 83x PE. Don't want assignment at these levels. |
| Premium Yield (20) | 20/20 | 2.5% weekly exceptional. Fully compensates for risk. |
| Binary Risk Penalty (0) | -0/0 | CyberArk M&A known and priced in. Fed tomorrow is known. |
| **TOTAL** | **84/100** | **B+** |

**Key Insight:** Inflated 9% EM is priced-in M&A risk. High premium compensates. Trade with normal sizing.

---

## Example: CDNS (Feb 17, 2026)

### CDNS — Grade: C+ (71/100)

| Component | Score | Explanation |
|-----------|-------|-------------|
| Earnings Predictability (30) | 28/30 | 4 straight beats, consistent. |
| EM Respect at Current (25) | 23/25 | 3-4% normal, stays within range historically. |
| Assignment Desirability (20) | 16/20 | Boring but stable duopoly. Fine to own. |
| Premium Yield (20) | 5/20 | 0.6% weekly terrible. Doesn't justify capital tie-up. |
| Binary Risk Penalty (0) | -1/0 | Fed week minor risk. |
| **TOTAL** | **71/100** | **C+** |

**Key Insight:** Safe but premium too low. 0.6% yield on $28k margin is poor use of capital. Skip.

---

## Grade Benchmarks

| Grade | What It Means |
|-------|---------------|
| **A+/A** | High win probability + great premium. Best risk/reward. |
| **B+/B** | Solid trade. Good premium, manageable risk. |
| **C+** | Borderline. Either low premium or elevated risk. Small size only. |
| **C** | Skip. Premium too low or risk too high. |
| **D/F** | Dangerous. Avoid entirely. |

---

*Version 3.0 — Volatility-Optimized for Earnings Traders*
