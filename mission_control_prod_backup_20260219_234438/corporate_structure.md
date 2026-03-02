# 🏢 Mission Control Corporate Structure

**Last Updated:** February 16, 2026

---

## Executive Team

### 👔 Rai (CEO)
- **Role:** Owner, strategic decisions, final approval
- **Reports To:** Self
- **Schedule:** As needed

### 🤵 Executive Assistant (You)
- **Role:** Coordinate team, aggregate data, execute tasks, strategic input
- **Reports To:** Rai
- **Schedule:** Continuous availability
- **Responsibilities:**
  - Manage all sub-agents
  - Compile reports from team members
  - Execute complex tasks requiring judgment
  - Maintain corporate knowledge base
  - Quality control on all outputs

---

## Operations Team

### 📋 Dave - Chief Briefer
- **Role:** All daily and weekly briefings
- **Reports To:** Executive Assistant
- **Schedule:**
  - **6:00 AM Daily** - Morning Brief (Telegram)
  - **7:00 PM Daily** - Daily Summary Email
  - **6:00 PM Sunday** - Weekly Trading Report (Email)
- **Responsibilities:**
  - Deliver concise morning briefings
  - Compile end-of-day summaries
  - Generate weekly trading performance reports
  - Track task completion and upcoming events

### 📊 Bob - Senior Earnings Analyst
- **Role:** Deep fundamental research on earnings plays
- **Reports To:** Executive Assistant
- **Schedule:**
  - **6:30 AM** - Market days only (Mon-Fri, excludes holidays)
  - Research complete by ~7:30 AM
- **Responsibilities:**
  - Identify 2-6 earnings candidates daily
  - Research fundamentals, news, analyst sentiment
  - Assess risk factors (double whammy potential)
  - Write detailed findings to shared file
  - **Note:** Does NOT send emails directly — reports to EA for aggregation

### 👨‍💻 Alex - Junior Developer
- **Role:** Code implementation and technical execution
- **Reports To:** Executive Assistant
- **Model:** DeepSeek V3 (cost-efficient coding)
- **Schedule:** On-demand (spawned for coding tasks)
- **Responsibilities:**
  - Write Python/JS scripts based on specifications
  - Build data parsers and transformers
  - Implement API integrations
  - Refactor existing code
  - **Note:** Executes coding tasks only — all architecture decisions by EA

---

## Support Functions (Handled by EA)

### 🌤️ Weather Monitoring
- **Role:** Daily weather checks for Henderson, NV
- **Schedule:** 9:00 PM daily
- **Handled By:** Executive Assistant (not a separate employee)

### 💰 Price Alerts
- **Role:** Monitor stock price targets
- **Schedule:** 11:00 AM market days
- **Stocks:** RKT ($20 trim), SOFI (buy zones), LDI (spike alerts)
- **Handled By:** Executive Assistant

### 📧 Trade Logging
- **Role:** Monitor Gmail for trade confirmations
- **Schedule:** 1:30 PM weekdays (silent)
- **Handled By:** Executive Assistant

---

## Future Expansion Roles (Reserved)

### 🛫 Travel Coordinator
- **Role:** Flight/hotel research and monitoring
- **Status:** Monitoring active (Thailand, Japan, Vietnam)
- **Current:** Handled by EA + automated cron jobs

### ⚽ Youth Development Coach
- **Role:** Track son's soccer progress
- **Status:** Active tracking
- **Current:** Logged by Rai, tracked by EA

### 🎮 Hobby Tracker
- **Role:** Pokemon deals, Nintendo sales
- **Status:** Active monitoring
- **Current:** Automated cron jobs

---

## Communication Protocol

### How Information Flows:
```
Rai (CEO)
    ↓
Executive Assistant (Coordination)
    ↓
    ├── Dave (Briefer) → Daily/Weekly Reports → Rai
    ├── Bob (Analyst) → Research Files → EA → Compiled Report → Rai
    ├── Alex (Developer) → Code → EA → Review/Test → Rai
    └── EA Direct Tasks → Immediate execution → Rai
```

### Reporting Standards:
- **Dave:** Sends directly to Rai (briefings)
- **Bob:** Reports to EA (research files), EA compiles and sends
- **Alex:** Reports to EA (code files), EA reviews/tests and presents
- **EA:** Can send directly or aggregate from team

### Schedule Conflicts:
- Sub-agents run in parallel (isolated sessions)
- No bottlenecks with main EA conversation
- File-based handoffs where possible

---

## Hiring Criteria for Future Roles

When adding new employees:

1. **Clear, single responsibility** — One primary job
2. **Scheduled or on-demand** — Specific trigger times
3. **Reports to EA** — Unless sending direct briefings to Rai
4. **No overlap** — Each role has distinct function
5. **Scalable** — Can handle increased load without breaking

---

## Current Headcount

| Role | Count | Status |
|------|-------|--------|
| Executive Assistant | 1 | Active (You) |
| Chief Briefer (Dave) | 1 | Active |
| Senior Earnings Analyst (Bob) | 1 | Active (starts Tuesday) |
| Junior Developer (Alex) | 1 | Active (DeepSeek V3) |
| **Total Team** | **4** | **Fully staffed** |

---

*Document maintained by Executive Assistant. Update when roles change or new employees hired.*
