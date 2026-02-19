## Idea: Mission Control P&L Tracking Dashboard

**Submitted:** 2026-02-18
**Status:** Backlog
**Priority:** Medium

### Description
Build a comprehensive P&L tracking system for CSP trades with weekly, monthly, and YTD views.

### Requirements

**Data Structure:**
- Trade JSON with lifecycle tracking (open → close)
- Fields: date, account, ticker, action, strike, expiration, contracts, premium, close_premium, realized_pnl, days_held, status

**Views:**
1. **Weekly View** - Daily P&L bars (green/red), week total
2. **Monthly View** - Week-by-week breakdown, monthly target progress
3. **YTD View** - Cumulative line chart, % to $100k goal
4. **Trade Detail** - Individual trade cards with lifecycle

**Metrics:**
- Win rate by grade (A vs B vs C validation)
- Avg days held
- Risk-adjusted returns (P&L per dollar at risk)
- Grade alignment score (% trades following analysis)
- Best/worst performing tickers

**API Endpoints:**
- GET /api/pl/weekly?week=2026-W07
- GET /api/pl/monthly?month=2026-02
- GET /api/pl/daily?date=2026-02-18
- GET /api/pl/ytd
- GET /api/trades/open
- GET /api/trades/closed

### Notes
- Wait for system health check before building
- Trades currently in trading_journal.md
- Need to migrate to structured JSON
- Consider real-time updates vs batch processing

### Next Steps
1. ✅ Logged as idea
2. ⏳ System health check
3. ⏳ TDS (Technical Design Spec) if approved
4. ⏳ Alex build
