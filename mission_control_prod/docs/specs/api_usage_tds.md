# TDS: API Usage Tab - Table Layout

## Overview
Redesign the API Usage tab with a clean HTML table structure showing all APIs, their purpose, pricing tier, and dashboard links.

**Status:** Draft
**Scope:** Update API Usage tab in Mission Control dashboard
**Approach:** JSON data-driven with HTML table layout

---

## Requirements

### Functional Requirements
1. **Table Layout**: Clean HTML `<table>` with columns
2. **Data-Driven**: All content from `portfolio/data/api_usage.json`
3. **Key Columns**:
   - API Name (with provider)
   - Purpose/Description (what it's used for)
   - Tier (Free / Paid badge)
   - Pricing (cost per 1M tokens)
   - Dashboard Link (click to manage/reload credits)
   - Status (Active / Inactive / Error)

### Visual Design
- Clean table with alternating row colors
- Color-coded status (green=active, red=error)
- Free tier highlighted (green badge)
- Paid tier with cost info
- Dashboard links open in new tab

---

## Data Architecture

### Schema Fields:
- `id`, `name`, `provider`, `purpose`, `tier` (Free/Paid)
- `status` (Active/Inactive/Error)
- `pricing`: input_per_1m, output_per_1m
- `dashboard_url`: link to manage API
- `limits`: requests_per_min, monthly_limit

### 5 APIs:
1. **Moonshot** (Kimi) - Primary LLM - Paid - $0.60/$2.50 per 1M
2. **DeepSeek** (NEW) - Coding for Alex - Paid - $0.14/$0.28 per 1M
3. **Finnhub** - Stock prices - Free - 60 req/min
4. **Brave Search** - Web search - Free
5. **LocalTunnel** - Remote access - Free

---

## Implementation

### Phase 1: Data Layer (Alex)
1. Create `portfolio/schemas/api_usage.schema.json`
2. Create `portfolio/data/api_usage.json` with 5 APIs
3. Add `load_api_usage()` to `data_layer.py`
4. Update `/api/usage` endpoint in `server.py`

### Phase 2: Frontend (Alex)
1. Update `loadUsage()` in `dashboard.html`
2. Create HTML table with columns:
   - Name | Purpose | Tier | Pricing | Status | Dashboard
3. Style with minimal CSS
4. Dashboard links open in new tab

### Table Structure:
| API Name | Purpose | Tier | Pricing | Status | Dashboard |
|----------|---------|------|---------|--------|-----------|
| Moonshot AI | Primary LLM | Paid | $0.60/M in<br>$2.50/M out | ● Active | [Open →] |
| DeepSeek V3 | Coding for Alex | Paid | $0.14/M in<br>$0.28/M out | ● Active | [Open →] |
| Finnhub | Stock prices | Free | Free | ● Active | [Open →] |
| Brave Search | Web search | Free | Free | ● Active | [Open →] |
| LocalTunnel | Remote access | Free | Free | ● Active | [Open →] |

---

## Files to Modify

**New:**
- `portfolio/schemas/api_usage.schema.json`
- `portfolio/data/api_usage.json`

**Modified:**
- `mission_control/data_layer.py`
- `mission_control/server.py`
- `mission_control/templates/dashboard.html`

---

## Approval

**Review TDS. Say "proceed" when ready for Alex.**
