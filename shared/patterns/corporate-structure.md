# Corporate Knowledge Base

**Last Updated:** 2026-02-17
**Purpose:** Shared institutional knowledge across all OpenClaw agents

---

## User Identity & Preferences

**Name:** Guan ("Rai")
**Timezone:** America/Los_Angeles (Nevada)
**Role:** Semi-retired IT consultant, options trader

### Communication Style
- **Efficiency over verbosity** - brief acknowledgements, no repetitive summaries
- **Exact values required** - "$268,196.46" not "~$300k"
- **Proactive suggestions** when tasks conflict with day-to-day operations
- **Consult before building** - propose approaches with trade-offs

### Trading Strategy
- $600k portfolio at Schwab (index funds as collateral)
- Uses ~70% margin buying power
- Sells cash-secured/margin puts on high-profile earnings
- Targets strikes **significantly below expected move** for safety
- Avoids "double whammy" (external news + earnings surprise)
- Skips Friday after-bell earnings

---

## Corporate Structure

### Reporting Lines
```
Rai (CEO)
├── Kimi (Chief of Staff - Moonshot K2.5)
│   ├── Dave (Chief Briefer)
│   ├── Bob (Senior Earnings Analyst)
│   └── Alex (Junior Developer - DeepSeek V3)
```

### Agent Responsibilities
- **Kimi:** Strategy, orchestration, complex decisions, final reports
- **Bob:** Earnings research, grading, fundamental analysis
- **Alex:** Coding tasks, implementations, 90% cost savings vs Kimi
- **Dave:** Morning/evening briefs, weather, scheduling

### Cost Optimization
- **DeepSeek (Alex)** for coding - 90% cheaper
- **Kimi (Moonshot)** for strategy/architecture only
- **Grading System:** v3.0 separates stock quality from trade setup

---

## Key Protocols

### Earnings Research Protocol v3.2
1. **Sunday:** User uploads Earnings Whispers pinned tweet image
2. **Monday-Friday 6:30 AM:** Script-based screener (NO agent interpretation)
3. **Monday-Friday 6:35 AM:** Bob researches filtered stocks
4. **Monday-Friday 6:40 AM:** Kimi compiles final report
5. **Monday-Friday 6:45 AM:** Deliver via email (Telegram fallback)

**Sector Exclusions:** REITs, Utilities, Consumer Staples, Industrials, Basic Materials
**Always Include:** WMT, TSLA, NVDA, AAPL, MSFT, AMZN, GOOGL, META

### Grading System v3.0 (100 points)
- Earnings Predictability: 30 pts
- EM Respect: 25 pts
- Assignment Desirability: 20 pts
- Premium Yield: 20 pts
- Binary Risk: -5 to 0 pts

**Grade Scale:**
- A+ (95-100), A (90-94), A- (85-89)
- B+ (80-84), B (75-79), B- (70-74)
- C+ (65-69), C (60-64), C- (55-59)
- D+ (50-54), D (45-49), D- (40-44)
- F (<40)

### Coding Protocol (AGENTS.md)
1. **Detect** coding task
2. **Architecture check** (30 seconds)
3. **TDS required?** Draft Technical Design Spec
4. **Risk assessment** (High = backup + extra testing)
5. **Implementation** with constraints
6. **Verification checklist**

### Date Calculation Protocol
- **NEVER** calculate dates mentally
- Always use Python `datetime` module
- `today = datetime.now().date()`
- `tomorrow = today + timedelta(days=1)`
- Verify weekday before API calls

---

## Technology Stack

### Mission Control Dashboard
- **Current:** Flask on Mac Mini port 8080 (gunicorn)
- **Migrating to:** Docker container (in progress)
- **Access:**
  - Local: http://localhost:8080
  - Network: http://192.168.50.170:8080
  - Remote: LocalTunnel (password: 172.56.209.6)

### APIs in Use
- Moonshot (Kimi) - Primary reasoning
- DeepSeek (Alex) - Coding tasks
- Finnhub - Stock prices, earnings discovery
- Brave Search - Web research
- LocalTunnel - Remote access
- Gemini Flash 2.5 - OCR for screenshots

### Data Storage
- `~/mission-control/data/` - Docker volume mount
- `portfolio/` - Portfolio tracking
- `memory/` - Agent knowledge
- JSON files for structured data

---

## Known Issues & Workarounds

### Gmail SMTP (Pending)
**Issue:** thunderclapper34@gmail.com IMAP works, SMTP fails
**Error:** 5.7.8 Username and Password not accepted
**Workaround:** Telegram fallback for reports
**Next Step:** Try manual email from web interface, then test SMTP

### Docker Build (In Progress)
**Status:** Downloading Python 3.11-slim base image
**ETA:** Tonight or early tomorrow
**Test Command:** `cd ~/mission-control && docker ps`

### Dashboard JavaScript
**Issue:** Previous caching fix and edit functionality caused brace mismatch
**Status:** Reverted to stable baseline
**Next:** Re-implement following AGENTS.md protocol

---

## Portfolio Snapshot

**Total:** $1,634,916 (33 stocks, 10 options across 5 accounts)
**Accounts:** Schwab, Robinhood, SEP-IRA, Roth IRA, Secondary

### Recent Trades (2026-02-17)
- SEP-IRA: MCO puts ($335), PANW puts ($963)
- Robinhood: PANW puts ($412)
- **Total Premium:** $1,710

---

## Critical Files

### Must Read Before Tasks
- `AGENTS.md` - Coding protocol (ALL agents)
- `sell_put_grading_system_v3.md` - Grading criteria (Bob)
- `SYSTEMATIC_EARNINGS_WORKFLOW.md` - Research protocol (Bob)
- `DATE_AUTOMATION.md` - Date calculation rules (ALL)

### Daily Workflow Files
- `weekly_earnings_schedule.json` - Earnings calendar
- `daily_earnings_research.md` - Bob's research output
- `trading_journal_2026.md` - Trade log

### Agent Memory Files
- `memory/corporate-knowledge.md` - This file
- `memory/bob-research-expertise.md` - Bob's learnings
- `memory/alex-coding-expertise.md` - Alex's patterns
- `memory/dave-briefing-expertise.md` - Dave's formats

---

## Lessons Learned

### What Works
- Script-based screener prevents agent "helpfulness" deviation
- Grading System v3.0 separates quality from setup
- Alex for coding = 90% cost savings
- Docker for stability vs bare metal Flask
- File-based memory persistence across sessions

### What Doesn't Work
- GitHub Pages (10min cache, read-only)
- Netlify (read-only, no edit)
- FastAPI split (overcomplicated)
- Agent-driven filtering (adds extra steps)
- Mental date calculations (error-prone)

### Architecture Decisions
- Single Flask server (not split)
- Docker containerization (not bare metal)
- Script-based filtering (not agent interpretation)
- Email primary, Telegram fallback
- TDS-first for coding (no shortcuts)

---

## Communication Protocols

### Email vs Telegram
- **Email:** Daily reports, summaries (guanwu87@gmail.com)
- **Telegram:** Interactive chat, urgent alerts, backups

### Report Format
- **Grade A/B stocks:** Detailed analysis, news, catalysts
- **Grade C-F stocks:** Brief description, key risks only

### Brief Schedule
- **6 AM:** Morning brief (weather, tasks, portfolio)
- **7 PM:** Evening brief (day summary, tomorrow prep)

---

## Open Questions

1. Should Docker auto-start on Mac Mini boot?
2. Monitoring/alert if container crashes?
3. VPS migration path if Mac Mini reliability issues?
4. When to enable Ideas Pipeline edit/delete?
5. API usage tracking dashboard completion?

---

**For Updates:** Agents append new learnings to this file. Keep it current.
