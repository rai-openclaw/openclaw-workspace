# Mission Control V1 Baseline

**Created:** 2026-02-15
**Status:** Working baseline

## What's Included

### APIs Working
- ✅ `/api/portfolio` - 30 positions across 5 accounts, aggregated
- ✅ `/api/usage` - 5 APIs tracked (Moonshot, Finnhub, Gemini, Brave, CoinGecko)
- ✅ `/api/ideas` - 10 ideas from NOTES.md
- ✅ `/api/analysis-archive` - 5 stock analyses
- ✅ `/api/earnings-research` - Bob's research placeholder
- ✅ `/api/stock/<ticker>` - Stock detail endpoint
- ✅ `/api/refresh-prices` - ETH price refresh

### Features
- Portfolio Holdings: Aggregated positions (e.g., RKT = 3,900 shares across RH+SEP+Roth)
- Account Breakdown: 5 accounts with totals
- Cash & SGOV: Tracked per account
- Options Positions: CSP puts displayed
- API Usage Dashboard: With billing links
- Ideas & Notes: Structured list view
- Analysis Archive: Stock research cards
- Team Structure: Corporate hierarchy (Rai, Dave, Bob)

### File Structure
```
mission_control/
├── server.py              # Main Flask app
├── templates/
│   └── dashboard.html     # Frontend
├── mc.sh                  # Control script
├── v1_backup/             # This directory
│   ├── server_v1.py
│   ├── dashboard_v1.html
│   ├── mc_v1.sh
│   └── README_V1.md
└── server.log             # Runtime logs
```

### Control Commands
```bash
cd ~/.openclaw/workspace/mission_control
./mc.sh start   # Start server
./mc.sh stop    # Stop server
./mc.sh status  # Check status
```

### Data Sources
- Portfolio: `../portfolio/*_tracker.md` (5 files)
- Ideas: `../ideas/NOTES.md`
- Analysis: `../portfolio/portfolio_tracker.md`
- Earnings: `../daily_earnings_research.md`

### Known Limitations
- Prices are from tracker files (not real-time)
- Returns calculated as 0 (need cost basis parsing)
- Earnings calendar hardcoded (needs data file)
- ETH price is cached (manual refresh only)

### Total Portfolio Value
- Robinhood: $300,124
- SEP-IRA: $393,729
- Schwab CSP: $687,464
- Schwab #2: $211,632
- Roth IRA: $69,307
- **Grand Total: $1,662,256**

### Next Steps for V2
1. Real-time price fetching via Finnhub
2. Return calculations with cost basis
3. Earnings calendar from data file
4. Options P&L tracking
5. Trade journal integration

## Restoration
To restore V1:
```bash
cd ~/.openclaw/workspace/mission_control
cp v1_backup/server_v1.py server.py
cp v1_backup/dashboard_v1.html templates/dashboard.html
./mc.sh restart
```

---
**Dashboard URL:** http://localhost:8080
