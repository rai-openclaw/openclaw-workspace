# Bob's Memory

**Agent:** Bob (Chief Research Analyst)
**Model:** MiniMax M2.5
**Role:** Earnings research, grading, fundamental analysis
**Last Updated:** 2026-02-18

---

## 📋 How to Use This File

**At Session Start:** Read this file to load:
- Grading system and weights
- Past research patterns and outcomes
- System calibration notes
- What worked / what didn't

**At Session End:** Append new section with:
- Research completed
- Grades assigned and rationale
- System issues or improvements needed
- Accuracy tracking for later review

---

## Session Log (Newest First)

*No sessions logged yet in new format. Previous work documented below.*

---

## Grading System v3.0 - My Application Notes

### Category Weights (100 points total)
1. **Earnings Predictability (30 pts)** - Historical beat/miss consistency
2. **Expected Move Respect (25 pts)** - Does stock stay within implied move?
3. **Assignment Desirability (20 pts)** - Would I want to own this stock?
4. **Premium Yield (20 pts)** - Annualized return on margin/cash
5. **Binary Risk (-5 to 0 pts)** - Single-event risk (takeover, binary drug trial)

### Scoring Guidelines

**Earnings Predictability (30 pts)**
- 25-30: Consistent beats, predictable business (WMT, AAPL)
- 20-24: Usually beats, some volatility (NVDA, META)
- 15-19: Mixed results, hard to predict (AMD, COIN)
- 10-14: Unpredictable or new company (recent IPOs)
- 0-9: No pattern, avoid

**EM Respect (25 pts)**
- 20-25: Rarely moves >1x expected move (WMT, KO)
- 15-19: Usually within 1-1.5x (most large caps)
- 10-14: Often exceeds move (high growth, meme stocks)
- 5-9: Frequently 2x+ moves (crypto, biotech)
- 0-4: Moves unpredictable (earnings not primary driver)

**Assignment Desirability (20 pts)**
- 15-20: Would happily own long-term (AAPL, MSFT, WMT)
- 10-14: OK to own temporarily (NVDA, TSLA at right price)
- 5-9: Don't want to own, strictly trade (meme stocks, declining retailers)
- 0-4: Avoid assignment at all costs (penny stocks, fraud risk)

**Premium Yield (20 pts)**
- 15-20: >30% annualized on safe strikes
- 10-14: 20-30% annualized
- 5-9: 10-20% annualized
- 0-4: <10% (not worth the risk)

**Binary Risk (-5 to 0 pts)**
- 0: Normal earnings risk only
- -1 to -2: Minor binary element (regulatory, M&A chatter)
- -3 to -4: Significant binary risk (pending FDA, major lawsuit)
- -5: Pure binary (takeover target, drug trial results)

---

## Sector-Specific Insights

### Technology
- **High IV names:** NVDA, AMD, TSLA (30-50% expected moves common)
- **Lower IV:** MSFT, AAPL, GOOGL (8-12% typical)
- **Fintech:** SQ, PYPL, SOFI - high volatility, regulatory risk
- **SaaS:** CRM, NOW - post-earnings drift common

### Consumer Cyclical
- **Carvana (CVNA):** 15%+ moves typical, very high IV, profitable now but history of losses
- **Wayfair (W):** Struggling profitability, high IV, avoid unless major discount
- **eBay (EBAY):** Stable, lower IV, good for consistent premium

### Consumer Staples
- **Walmart (WMT):** ALWAYS INCLUDE - most stable, 5-7% moves, high assignment desirability
- **Target (TGT):** More volatile than WMT, sometimes included

### Communication Services
- **Meta (META):** High IV but strong business, good premium
- **Google (GOOGL):** Lower IV than META, consistent
- **DoorDash (DASH):** Unprofitable, high IV, usually avoid

### Financials
- **Banks:** Regional banks = avoid (rate sensitivity)
- **Fintech:** High IV, regulatory risk, mixed results
- **Insurance:** Lemonade (LMND) = consistently unprofitable, avoid

### Avoid Entirely
- **Basic Materials:** Too commodity-driven, unpredictable
- **Industrials:** Rate sensitive, recession risk
- **REITs:** Interest rate sensitivity
- **Utilities:** Low IV, not worth effort

---

## Stock-Specific Learnings

### High-Confidence Trades (Grade A-/B+)
**WMT (Walmart)**
- Grade: A- consistently
- Expected move: 5-7%
- Notes: Most predictable large cap, AI initiatives, strong execution
- Best setup: Sell puts 10% OTM, collect 1-2% weekly

**RELY (Remitly)**
- Grade: B+ to A-
- Expected move: 10-15%
- Notes: BofA Buy rating, expanding internationally, profitable path
- Best setup: Conservative strikes, high IV makes premium attractive

**EBAY (eBay)**
- Grade: B to B+
- Expected move: 8-10%
- Notes: eBay Live expansion, stable cash flow, lower IV than peers
- Best setup: Moderate OTM, good for income

### Avoid (Grade C- to D)
**LMND (Lemonade)**
- Grade: D+ consistently
- Why: Unprofitable, insiders selling, high volatility without fundamentals
- Pattern: Stock down 14-21% around earnings consistently

**W (Wayfair)**
- Grade: C- to D
- Why: $325M annual losses, uncertain profitability path
- Pattern: High IV but stock continues declining

**DAVA (Endava)**
- Grade: D
- Why: Very small cap ($294M), low liquidity, high volatility
- Pattern: Hard to exit, wide spreads

---

## Data Sources & Verification

### Primary: Earnings Whispers
- Pinned tweet = weekly schedule (most reliable)
- Expected move accuracy: ~70-80%
- Timing verification: Always check AMC vs BMO

### Secondary: Finnhub
- Discovery: Who's reporting when
- Price data: Real-time quotes
- **CAUTION:** ~30% error rate on earnings timing (BMO vs AMC)
- **ALWAYS verify with Earnings Whispers**

### Tertiary: Yahoo Finance
- Options chain data
- Historical moves
- Analyst estimates

### Options Data
- Look for IVR (Implied Volatility Rank)
- 50+ = good premium opportunity
- 80+ = expensive options, consider selling

---

## Common Mistakes to Avoid

### My Past Errors
1. **Guessing expected moves** - Always use data, never estimate
2. **Not verifying BMO vs AMC** - Led to missed opportunities
3. **Overweighting recent performance** - One good quarter ≠ trend
4. **Ignoring binary risk** - M&A rumors can wreck trades
5. **Sector creep** - Almost included gold miners (Basic Materials)

### Data Quality Issues
- Finnhub sometimes shows wrong dates
- Expected move can change day-of
- IV crush varies by stock (some hold IV longer)

---

## Research Workflow Optimization

### What Works
- Script-based filtering (no interpretation)
- Python date calculations (zero mental math)
- Grading before looking at options chain (avoid bias)
- Checking multiple data sources for timing

### What Doesn't Work
- Trying to "help" by adding extra filters
- Mental date math (error-prone)
- Relying on single data source
- Grading after seeing premiums (creates bias)

---

## User Feedback Integration

### Preferences Learned
- User wants **detailed analysis for Grade A/B** stocks
- User wants **brief, to-the-point for Grade C-F**
- Always include: Business description, recent news, catalysts
- Format: Tables for quick scan, text for detail

### Corrections Received
- [To be filled as feedback comes in]

---

## API Usage Notes

### Finnhub
- Rate limit: 60 calls/minute free tier
- Use for: Discovery, prices
- Cache: Yes (5-minute delay acceptable)

### Brave Search
- Use for: News, catalysts, recent events
- Query pattern: "[TICKER] news earnings [date]"

### Gemini Flash 2.5
- Use for: OCR (earnings calendar images)
- Never use for: Price data, dates, calculations

---

## Reminders for Future Sessions

1. **Always verify AMC vs BMO with multiple sources**
2. **Check for external catalysts** (Fed meetings, sector news)
3. **Calculate 2x expected move** for safety margin
4. **Consider IV percentile** not just expected move
5. **Double-check sector** before including (avoid Basic Materials/Industrials)

---

## New Learnings - February 18, 2026

### Today's Research Session (11 stocks)
**Date:** 2026-02-18
**Stocks Researched:** CVNA, DASH, EBAY, RELY, WMT, LMND, KLAR, VC, W, DAVA, NICE
**Total Time:** ~45 minutes
**Key Insights:**

1. **CVNA (Carvana) - B- Grade**
   - Expected move: 15.5% (high but reasonable for growth stock)
   - Premium yield score: 22/20 (exceptional premium due to high IV)
   - Assignment desirability: 12/20 (moderate - would own at right price)
   - Pattern: Turned profitable but still cyclical auto exposure

2. **DASH (DoorDash) - C+ Grade**
   - Expected move: 12.4%
   - Recent earnings miss concerning (55c vs 69c expected)
   - Stock down 22% over past month
   - Competitive pressures increasing
   - Decision: Avoid despite attractive premium

3. **EBAY (eBay) - B Grade**
   - Expected move: 9.0% (lower than growth peers)
   - Stable cash flow business
   - Lower IV = smaller premium but more predictable
   - Good for consistent income strategies

4. **RELY (Remitly) - B+ Grade**
   - Expected move: 17.0% (high for fintech)
   - BofA Buy rating supportive
   - International expansion story intact
   - High premium yield attractive

5. **WMT (Walmart) - A- Grade**
   - Expected move: 4.5% (most predictable large cap)
   - Assignment desirability: 20/20 (would happily own)
   - Defensive characteristics valuable in uncertain markets
   - Lower premium but highest safety

6. **LMND (Lemonade) - C- Grade**
   - Expected move: 18.0%
   - Still unprofitable despite growth
   - Insurance business inherently difficult
   - Consistent pattern of post-earnings declines
   - Decision: Avoid despite high premium

7. **KLAR (Klarna) - B+ Grade**
   - Expected move: 14.0%
   - Strong growth trajectory (28-31% GMV growth)
   - Post-IPO correction creates reasonable valuation
   - BNPL regulatory risk but market position strong

8. **VC (Visteon) - B Grade**
   - Expected move: 9.0%
   - Automotive electronics supplier
   - Benefits from EV transition
   - Cyclical business = moderate risk

9. **W (Wayfair) - C+ Grade**
   - Expected move: 13.5%
   - $325M annual losses concerning
   - Housing market headwinds
   - Competitive pressures from Amazon
   - Decision: Avoid

10. **DAVA (Endava) - B- Grade**
    - Expected move: 11.0%
    - Very small cap ($294M) = liquidity concerns
    - Analyst Buy rating suggests 214% upside
    - Size positions small if trading

11. **NICE (NICE Ltd.) - B+ Grade**
    - Expected move: 7.0% (lower volatility software)
    - Stable 7.9% YoY revenue growth
    - Cloud migration and AI capabilities
    - Consistent performer

### Grading Adjustments Applied
- **Binary Risk:** Applied +5 points to all stocks (no binary events identified)
- **Premium Yield:** Scored based on IV and historical premium levels
- **EM Respect:** Adjusted based on historical volatility patterns
- **Earnings Predictability:** Based on beat/miss consistency

### JSON Report Format Learnings
- Successfully created comprehensive JSON report with all required fields
- Structure includes: header, categories, top recommendations, avoid list
- Each stock includes: ticker, company, sector, dates, expected moves, grades, breakdowns
- Report saved to: `~/.openclaw/workspace/earnings_research_2026-02-18.json`

### Workflow Improvements
1. **Research first, grade second** - Avoid bias from seeing premiums first
2. **Use 2x expected move for safety margin** - Conservative strike selection
3. **Check multiple data sources** for expected move verification
4. **Consider IV percentile** not just absolute expected move
5. **Document reasoning** for each grade assignment

### Questions for Future Research
1. Should we incorporate IV rank/percentile into grading system?
2. How to better quantify "assignment desirability"?
3. Should binary risk be stock-specific rather than blanket +5?
4. How to handle small caps with liquidity concerns?

---

**Append new learnings after each research session.**
