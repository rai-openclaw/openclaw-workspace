# Systematic Earnings Research Workflow

## Step 1: Get Reliable Calendar (One Source)
**Primary Source:** Finnhub API earnings calendar
**Why:** Structured data, includes date/time/symbol, no interpretation needed
**Call:** `GET /calendar/earnings?from=YYYY-MM-DD&to=YYYY-MM-DD`

**Output Format:**
```json
{
  "earningsCalendar": [
    {
      "date": "2026-02-19",
      "epsActual": null,
      "epsEstimate": 0.94,
      "hour": "amc",  // "bmo" or "amc"
      "quarter": 2,
      "revenueActual": null,
      "revenueEstimate": 2580000000,
      "symbol": "PANW",
      "year": 2026
    }
  ]
}
```

## Step 2: Filter Systematically

**No guessing. Use data fields only.**

**For each stock in calendar:**
1. Get company profile from Finnhub (market cap, sector)
2. Check expected move from options data if available
3. Apply filters:

| Include If | Data Check |
|------------|-----------|
| Market Cap >$50B | `profile.marketCapitalization > 50000` |
| Expected Move >8% | From options API or estimate |
| In Rai's Portfolio | Check holdings.json |
| High-Profile Tech | Manual list: FVRR, UPWK, ROKU, SNOW, PLTR, etc. |

**Result:** Filtered list with symbols, dates, times

## Step 3: Build Daily Actionable Lists

**From the filtered data, create two lists per day:**

```
WEDNESDAY FEB 19:
- AMC (Trade Wed before 4 PM): [CVNA, DASH, ...]
- BMO (Already reported, skip): [WMT, BABA, ...]

THURSDAY FEB 20:
- AMC (Trade Thu): [...]
- BMO (Trade Wed): [LMND, W, ...]
```

## Step 4: Research Each Actionable Stock

**For each stock in today's actionable list:**
1. Pull historical earnings from Finnhub
2. Web search for recent news
3. Get options expected move
4. Apply grading system
5. Write to report

## Step 5: Daily Report Format

**Morning Report (6:30 AM) covers:**
```
TODAY'S ACTIONABLE PLAYS:

[Trade Today Before Close - AMC Tonight]
- CVNA: Expected move X%, grade Y
- DASH: Expected move X%, grade Y

[Trade Today Before Close - BMO Tomorrow]
- LMND: Expected move X%, grade Y  
- W: Expected move X%, grade Y

[Skip - Already Reported BMO]
- None
```

## Key Principle

**Use data fields, not mental math:**
- API says `hour: "amc"` → Trade same day
- API says `hour: "bmo"` → Trade previous day
- No interpretation needed

## Bob's Updated Task

```
1. Call Finnhub earnings calendar for Mon-Fri (full week view)
2. For each result, call Finnhub profile for market cap
3. Filter: Market cap >$50B OR expected move >8% OR high-profile tech list
4. Sort by hour: amc (today) vs bmo (tomorrow)
5. Research each actionable stock
6. Report: "Trade today" vs "Trade tomorrow" clearly labeled
```

## Example Output

**Tuesday Feb 17 Report:**
```
TODAY (Trade before 4 PM):
- PANW (AMC tonight): 9% EM, Grade B+
- CDNS (AMC tonight): 4% EM, Grade C+

TOMORROW (Trade Wed before 4 PM):
- CVNA (Wed AMC): 13% EM, high volatility
- DASH (Wed AMC): 10% EM, gig economy
- LMND (Thu BMO): 12% EM, insurtech
- W (Thu BMO): 8% EM, e-commerce
```

## Calendar Data Sources (Ranked)

1. **Finnhub API** - Primary, structured, reliable
2. **Earnings Whispers** - Backup for expected moves
3. **Company IR** - Verify if conflict

**Never use:** Aggregator news sites as primary source

## Check Before Researching

- [ ] Calendar data from API (not memory)
- [ ] All stocks have date + hour field
- [ ] Filter applied systematically
- [ ] Sorted by actionable date
- [ ] No stocks missed due to bad filter

---

**This removes all date interpretation. Just use API data.**
