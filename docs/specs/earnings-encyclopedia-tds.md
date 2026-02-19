# Technical Design Spec: Earnings Research Encyclopedia

**Version:** 1.0  
**Date:** 2026-02-18  
**Status:** Draft  
**Risk Level:** MEDIUM  
**Author:** Subagent (DeepSeek V3)

---

## Goal
Create an "Earnings Encyclopedia" tab in Mission Control that consolidates Bob's daily earnings research into a searchable, historical database. The encyclopedia will track research evolution across quarters, provide smart consolidation of new vs old research, and offer diff views to show what changed.

---

## Problem Statement

**Current State:**
- Bob produces daily earnings research in JSON format (`daily_earnings_research_YYYY-MM-DD.json`)
- Research is scattered across daily files with no consolidation
- No historical tracking of research evolution for specific tickers
- No search capability across research history
- Manual research requests don't automatically update consolidated view
- Current Earnings tab shows only basic data without historical context

**Desired State:**
- New "Earnings Encyclopedia" tab with search bar
- Consolidated view of all research for any ticker across time
- Smart merging: new research overrides relevant fields, preserves historical data
- Diff view showing what changed since last research
- Automatic pickup when research files update
- Manual research requests update the encyclopedia
- Track research evolution across quarters

---

## Data Architecture

### 1. Source Data Format (Bob's Daily Research)

**File Pattern:** `daily_earnings_research_YYYY-MM-DD.json`

**Expected JSON Structure:**
```json
{
  "research_date": "2026-02-18",
  "total_tickers": 11,
  "summary": "Daily Earnings Research - Wednesday, February 18, 2026",
  "tickers": [
    {
      "ticker": "CVNA",
      "company_name": "Carvana Co.",
      "earnings_date": "2026-02-18",
      "earnings_time": "AMC",
      "expected_move": "15.5%",
      "grade": "B-",
      "analysis": {
        "business_overview": "Online used car marketplace with vehicle vending machines and home delivery.",
        "recent_news": "Expected to report Q4 2025 earnings with consensus EPS of $1.10-$1.13 and revenue of $5.20-$5.24B.",
        "risks": "High valuation, cyclical auto market sensitivity, competition from traditional dealers and CarMax.",
        "catalysts": "Continued growth in online car buying adoption, margin expansion potential."
      },
      "recommendation": "Watch",
      "reasoning": "High implied volatility suggests big move expected, but stock already up significantly YTD."
    },
    {
      "ticker": "DASH",
      "company_name": "DoorDash, Inc.",
      "earnings_date": "2026-02-18",
      "earnings_time": "AMC",
      "expected_move": "12.4%",
      "grade": "C+",
      "analysis": {
        "business_overview": "Leading food delivery service in US, expanding into grocery and retail delivery.",
        "recent_news": "Options traders see expected move of +/- 19.93 points. Stock down 22% over past month.",
        "risks": "Intense competition, regulatory challenges, high customer acquisition costs, profitability concerns.",
        "catalysts": "International expansion, grocery delivery growth, potential profitability improvements."
      },
      "recommendation": "Avoid",
      "reasoning": "Stock under pressure, competitive landscape challenging, recent earnings miss concerning."
    }
  ]
}
```

**Key Fields per Ticker:**
- `ticker` - Symbol (CVNA, DASH, etc.)
- `company_name` - Full company name
- `earnings_date` - Date of earnings report
- `earnings_time` - AMC (After Market Close) or BMO (Before Market Open)
- `expected_move` - Expected volatility percentage
- `grade` - Letter grade (A-F scale with +/-)
- `analysis` - Object with structured analysis sections
- `recommendation` - Action (Trade/Watch/Avoid)
- `reasoning` - Summary reasoning for recommendation
- `research_date` - Inherited from parent object

### 2. Encyclopedia Data Schema

**File:** `portfolio/data/earnings_encyclopedia.json`

```json
{
  "version": "1.0",
  "last_updated": "2026-02-18T22:10:00Z",
  "tickers": {
    "CVNA": {
      "company_name": "Carvana Co.",
      "latest_research_date": "2026-02-18",
      "research_history": [
        {
          "research_date": "2026-02-18",
          "source_file": "daily_earnings_research_2026-02-18.md",
          "earnings_date": "2026-02-18",
          "earnings_time": "AMC",
          "expected_move": "15.5%",
          "grade": "B-",
          "analysis": {
            "business_overview": "Online used car marketplace with vehicle vending machines...",
            "recent_news": "Expected to report Q4 2025 earnings with consensus EPS...",
            "risks": "High valuation, cyclical auto market sensitivity...",
            "catalysts": "Continued growth in online car buying adoption..."
          },
          "recommendation": "Watch",
          "reasoning": "High implied volatility suggests big move expected..."
        },
        {
          "research_date": "2025-11-15",
          "source_file": "daily_earnings_research_2025-11-15.md",
          "earnings_date": "2025-11-15",
          "earnings_time": "AMC",
          "expected_move": "12.8%",
          "grade": "C+",
          "analysis": { ... },
          "recommendation": "Avoid",
          "reasoning": "Previous quarter missed estimates..."
        }
      ],
      "consolidated_view": {
        "current_grade": "B-",
        "current_recommendation": "Watch",
        "grade_history": [
          {"date": "2025-11-15", "grade": "C+"},
          {"date": "2026-02-18", "grade": "B-"}
        ],
        "recommendation_history": [
          {"date": "2025-11-15", "recommendation": "Avoid"},
          {"date": "2026-02-18", "recommendation": "Watch"}
        ],
        "key_risks": ["High valuation", "Cyclical auto market", "Competition"],
        "key_catalysts": ["Online car buying adoption", "Margin expansion"],
        "quarters_researched": ["Q4 2025", "Q1 2026"],
        "first_researched": "2025-11-15",
        "last_updated": "2026-02-18"
      }
    },
    "DASH": { ... }
  }
}
```

### 3. Historical Tracking Strategy

**Versioning Approach:**
- Each research entry stored with full context
- Consolidated view shows current state with pointers to history
- Timeline view available for evolution tracking
- Quarter-based grouping for seasonal patterns

**Storage Location:**
- Primary: `portfolio/data/earnings_encyclopedia.json`
- Backup: `portfolio/data/earnings_encyclopedia_backup.json` (auto-created before updates)
- Archive: `portfolio/analyses/earnings/` (optional raw research storage)

---

## Consolidation Logic

### Fields That Get Overridden (New Research Wins)
1. **Grade** - Latest grade replaces previous
2. **Recommendation** - Latest action recommendation
3. **Expected Move** - Latest volatility expectation
4. **Recent News** - Always use most recent news
5. **Earnings Date/Time** - For upcoming earnings only
6. **Reasoning** - Latest analysis reasoning

### Fields That Get Preserved/Appended
1. **Business Overview** - Keep original unless major business model change
2. **Historical Risks** - Append new risks, don't delete old ones
3. **Historical Catalysts** - Append new catalysts
4. **Earnings Track Record** - Preserve all historical earnings dates
5. **Grade History** - Preserve all historical grades
6. **Recommendation History** - Preserve all historical recommendations

### Conflict Resolution Rules
1. **Same Ticker, Same Earnings Date**: New research overrides old (latest timestamp wins)
2. **Same Ticker, Different Earnings Date**: Treat as separate research entries (different quarter)
3. **Multiple Entries Same Day**: Use the most complete/confident analysis (tie-breaker: file modification time)
4. **Conflicting Grades**: Use latest grade, but flag in consolidated view
5. **Timestamp Priority**: Latest research date wins regardless of source (manual or automated)

### Smart Merging Algorithm
```python
def merge_research(existing_ticker_data, new_research):
    """
    Merge new research into existing ticker data
    """
    # Add new research to history
    existing_ticker_data["research_history"].append(new_research)
    
    # Update latest research date
    existing_ticker_data["latest_research_date"] = new_research["research_date"]
    
    # Update consolidated view
    consolidated = existing_ticker_data["consolidated_view"]
    
    # Override fields
    consolidated["current_grade"] = new_research["grade"]
    consolidated["current_recommendation"] = new_research["recommendation"]
    
    # Append to history arrays
    consolidated["grade_history"].append({
        "date": new_research["research_date"],
        "grade": new_research["grade"]
    })
    consolidated["recommendation_history"].append({
        "date": new_research["research_date"],
        "recommendation": new_research["recommendation"]
    })
    
    # Merge risks and catalysts (unique items)
    new_risks = extract_risks(new_research["analysis"]["risks"])
    consolidated["key_risks"] = list(set(consolidated["key_risks"] + new_risks))
    
    # Track quarters
    quarter = get_quarter_from_date(new_research["earnings_date"])
    if quarter not in consolidated["quarters_researched"]:
        consolidated["quarters_researched"].append(quarter)
    
    return existing_ticker_data
```

---

## API Design

### 1. Primary Endpoint: `/api/earnings-encyclopedia`

**GET Parameters:**
- `?ticker=CVNA` - Get specific ticker data
- `?search=all` - Get all tickers (paginated)
- `?search=term` - Search across tickers and company names
- `?quarter=Q1-2026` - Filter by quarter
- `?limit=50&offset=0` - Pagination

**Response Format (Single Ticker):**
```json
{
  "ticker": "CVNA",
  "company_name": "Carvana Co.",
  "latest_research_date": "2026-02-18",
  "research_count": 5,
  "quarters_researched": ["Q4 2025", "Q1 2026", "Q2 2026"],
  "current_grade": "B-",
  "current_recommendation": "Watch",
  "research_history": [
    {
      "research_date": "2026-02-18",
      "earnings_date": "2026-02-18",
      "grade": "B-",
      "recommendation": "Watch",
      "summary": "High implied volatility suggests big move..."
    }
  ],
  "consolidated": {
    "grade_history": [...],
    "recommendation_history": [...],
    "key_risks": [...],
    "key_catalysts": [...]
  }
}
```

**Response Format (Search All):**
```json
{
  "total_tickers": 147,
  "limit": 50,
  "offset": 0,
  "tickers": [
    {
      "ticker": "CVNA",
      "company_name": "Carvana Co.",
      "latest_research_date": "2026-02-18",
      "current_grade": "B-",
      "current_recommendation": "Watch",
      "research_count": 5
    },
    ...
  ]
}
```

### 2. Diff Endpoint: `/api/earnings-encyclopedia/diff`

**GET Parameters:**
- `?ticker=CVNA` - Required
- `?compare_date=2025-11-15` - Compare against specific date (default: previous research)

**Response Format:**
```json
{
  "ticker": "CVNA",
  "current_date": "2026-02-18",
  "compare_date": "2025-11-15",
  "changes": {
    "grade": {"from": "C+", "to": "B-", "direction": "improved"},
    "recommendation": {"from": "Avoid", "to": "Watch", "direction": "improved"},
    "expected_move": {"from": "12.8%", "to": "15.5%", "direction": "increased"},
    "new_risks": ["Increased competition from CarMax"],
    "new_catalysts": ["Margin expansion potential"],
    "summary": "Upgraded from Avoid to Watch due to improved outlook..."
  }
}
```

### 3. Update Endpoint: `/api/earnings-encyclopedia/update`

**POST Parameters:**
- `ticker` (required)
- `research_date` (required)
- `research_data` (required, JSON)

**Purpose:** Manual research updates (from user requests)

### 4. Scan Endpoint: `/api/earnings-encyclopedia/scan`

**POST (no parameters)**

**Purpose:** Force rescan of all research files to rebuild encyclopedia

---

## Frontend Design

### 1. New Tab Integration

**Location:** Add to sidebar navigation after "Earnings" tab
```html
<div class="nav-item" onclick="showView('earnings-encyclopedia', event)">
    Earnings Encyclopedia
</div>
```

**View Container:**
```html
<div id="earnings-encyclopedia-view" class="view">
    <div class="encyclopedia-header">
        <h2>Earnings Research Encyclopedia</h2>
        <div class="encyclopedia-controls">
            <div class="search-box">
                <input type="text" id="encyclopedia-search" 
                       placeholder="Search tickers or companies..." 
                       onkeyup="searchEncyclopedia(event)">
                <button onclick="clearSearch()">Clear</button>
            </div>
            <div class="filter-controls">
                <select id="grade-filter">
                    <option value="">All Grades</option>
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                </select>
                <select id="recommendation-filter">
                    <option value="">All Recommendations</option>
                    <option value="Trade">Trade</option>
                    <option value="Watch">Watch</option>
                    <option value="Avoid">Avoid</option>
                </select>
                <button onclick="refreshEncyclopedia()">Refresh</button>
            </div>
        </div>
    </div>
    
    <div id="encyclopedia-content">
        <!-- Dynamic content -->
    </div>
</div>
```

### 2. Search Results Display

**Grid View (Default):**
```html
<div class="encyclopedia-grid">
    <div class="ticker-card" data-ticker="CVNA">
        <div class="ticker-header">
            <div class="ticker-symbol">CVNA</div>
            <div class="ticker-grade grade-b">B-</div>
        </div>
        <div class="ticker-company">Carvana Co.</div>
        <div class="ticker-meta">
            <span>Last: 2026-02-18</span>
            <span>5 quarters</span>
        </div>
        <div class="ticker-recommendation recommendation-watch">Watch</div>
        <button onclick="viewTickerDetails('CVNA')">View History</button>
    </div>
</div>
```

### 3. Ticker Detail View

**Three-Panel Layout:**
1. **Left Panel:** Current consolidated view
2. **Middle Panel:** Research timeline (quarterly)
3. **Right Panel:** Diff view (changes since last research)

**Features:**
- Timeline slider to navigate through quarters
- Side-by-side comparison of any two research dates
- Export to PDF/CSV
- Add manual notes/updates

### 4. Diff View Component

**Visual Diff Display:**
```html
<div class="diff-view">
    <div class="diff-header">
        <div class="diff-old">Nov 15, 2025</div>
        <div class="diff-arrow">→</div>
        <div class="diff-new">Feb 18, 2026</div>
    </div>
    <div class="diff-content">
        <div class="diff-item grade-diff">
            <div class="diff-label">Grade</div>
            <div class="diff-old-value grade-c">C+</div>
            <div class="diff-new-value grade-b">B-</div>
            <div class="diff-direction improved">↑ Improved</div>
        </div>
        <div class="diff-item recommendation-diff">
            <div class="diff-label">Recommendation</div>
            <div class="diff-old-value recommendation-avoid">Avoid</div>
            <div class="diff-new-value recommendation-watch">Watch</div>
            <div class="diff-direction improved">↑ Improved</div>
        </div>
        <!-- Additional diffs -->
    </div>
</div>
```

---

## File Locations & Data Flow

### Source Files
```
~/.openclaw/workspace/
├── daily_earnings_research_2026-02-18.md
├── daily_earnings_research_2026-02-17.md
├── research_archive/
│   ├── daily_earnings_research_2025-*.md
│   └── ...
```

### Encyclopedia Files
```
~/.openclaw/workspace/mission_control_dev/
├── portfolio/
│   ├── data/
│   │   ├── earnings_encyclopedia.json          # Primary consolidated data
│   │   └── earnings_encyclopedia_backup.json   # Auto-backup
│   └── analyses/
│       └── earnings/
│           ├── CVNA_history.json               # Optional per-ticker archive
│           └── ...
```

### Code Files
```
~/.openclaw/workspace/mission_control_dev/
├── data_layer.py                              # Add encyclopedia parsing functions
├── server.py                                  # Add new API endpoints
├── templates/
│   └── dashboard.html                         # Add encyclopedia tab and JavaScript
└── docs/specs/
    └── earnings-encyclopedia-tds.md          # This document
```

### Data Flow Diagram
```
1. Daily Research (JSON) 
   → JSON parser extracts ticker data
   → Merged into encyclopedia.json (latest timestamp wins)
   → API serves consolidated data
   → Frontend displays with search/diff

2. Manual Research Request
   → User provides research data
   → POST to /api/earnings-encyclopedia/update
   → Updates encyclopedia.json
   → Frontend refreshes

3. Daily Scheduled Sync (Recommended for MVP)
   → Runs daily at 7:30 AM PT
   → After Dave's evening brief (includes Bob's research)
   → Before next day's 6 AM morning brief
   → Scans all research JSON files
   → Updates encyclopedia automatically

4. Trigger Options (Future Enhancements)
   → Option A: After Dave completes morning brief (real-time)
   → Option B: After manual research completion (immediate)
   → Option C: File watcher on research directory (event-driven)
```

---

## Development Environment

**Goal:** Build and test WITHOUT touching production (port 8080)

### Option 1: Separate Development Container (Recommended)

**Setup:**
```bash
# Copy mission-control to dev location
cp -r ~/mission-control ~/mission-control-dev

# Modify docker-compose.yml for port 8081
cd ~/mission-control-dev
# Edit: ports: - "8081:8080"

# Start dev server
docker-compose up -d

# Access at: http://localhost:8081
```

**Benefits:**
- ✅ Complete isolation from production
- ✅ Can break things without impact
- ✅ Separate data volumes
- ✅ Easy to wipe and restart

### Option 2: Same Container, Feature Flag

**Setup:**
- Add feature flag: `ENCYCLOPEDIA_ENABLED = False` (default)
- Develop with flag off
- Enable only when fully tested

**Benefits:**
- ✅ Same environment as production
- ✅ Easier migration when ready
- ⚠️ Risk: Could break production if misconfigured

### Recommended Approach: Option 1 (Separate Container)

1. Build full feature on port 8081
2. Test thoroughly with production-like data
3. When ready, copy changes to production
4. Deploy to port 8080

---

## Implementation Steps

### Phase 1: Data Layer & Parser (Week 1)
1. **Create parser for JSON research files**
   - Function: `parse_daily_research_json(filepath)`
   - Reads structured JSON data from Bob's research (`daily_earnings_research_YYYY-MM-DD.json`)
   - No markdown parsing needed (JSON is native format)
   - Validates JSON schema before processing

2. **Create encyclopedia data structure**
   - Function: `load_earnings_encyclopedia()`
   - Function: `save_earnings_encyclopedia(data)`
   - Function: `merge_research_into_encyclopedia(new_research)`

3. **Build initial encyclopedia**
   - Scan all historical research files
   - Create consolidated encyclopedia.json
   - Generate backup

### Phase 2: API Endpoints (Week 1)
1. **Add new endpoints to server.py**
   - `/api/earnings-encyclopedia` (GET)
   - `/api/earnings-encyclopedia/diff` (GET)
   - `/api/earnings-encyclopedia/update` (POST)
   - `/api/earnings-encyclopedia/scan` (POST)

2. **Update existing earnings endpoint**
   - Modify `/api/earnings-research` to use encyclopedia data
   - Maintain backward compatibility

### Phase 3: Frontend Integration (Week 2)
1. **Add new tab to dashboard.html**
   - Sidebar navigation item
   - View container with search UI
   - JavaScript functions for encyclopedia

2. **Create encyclopedia UI components**
   - Search bar with autocomplete
   - Grid view of tickers
   - Detail view with timeline
   - Diff view component

3. **Integrate with existing dashboard**
   - Consistent styling
   - Responsive design
   - Error handling

### Phase 4: Auto-Update & Monitoring (Week 2)
1. **Daily Scheduled Sync (Primary Method)**
   - Cron job: Daily at 7:30 AM PT
   - Scans all research JSON files
   - Updates encyclopedia automatically
   - Logs changes for audit
   - Trigger: After Dave's brief, before next day

2. **Manual Update Endpoint (On-Demand)**
   - POST to `/api/earnings-encyclopedia/scan`
   - Force immediate rescan
   - Use after manual research or urgent updates

3. **Manual Research Integration**
   - Form for manual research entry
   - Validation and confirmation
   - Option to trigger immediate sync or wait for daily

---

## Edge Cases & Error Handling

### 1. Ticker Not Found
- **UI:** Show "No research found" with option to request research
- **API:** Return 404 with suggestion to scan for updates
- **Logging:** Record missing ticker for future monitoring

### 2. Multiple Research Entries Same Day
- **Resolution:** Use most recent file (by timestamp)
- **UI:** Show all entries with timestamps
- **Warning:** Flag potential duplicates for review

### 3. Research Spanning Multiple Quarters
- **Handling:** Treat as separate research entries
- **Grouping:** Organize by quarter in timeline view
- **Consolidation:** Show quarter-over-quarter trends

### 4. Manual vs Automated Research Merging
- **Priority:** Latest timestamp wins (regardless of source)
- **Examples:** 
  - Manual research Feb 1, Automated Feb 15 → Automated wins
  - Automated Feb 15, Manual Feb 20 → Manual wins
- **Flagging:** Track source (manual/auto) for audit purposes
- **Audit:** Log all merges with timestamps and sources

### 5. Data Corruption or Schema Changes
- **Backup:** Always keep backup before updates
- **Validation:** Schema validation on load
- **Recovery:** Auto-rollback to last good version

### 6. Large Research History (1000+ entries)
- **Pagination:** API supports limit/offset
- **Lazy Loading:** Load history on demand
- **Performance:** Index tickers for fast search

### 7. Conflicting Information
- **Visualization:** Highlight conflicts in UI
- **Resolution:** User can manually resolve
- **Notes:** Allow adding clarification notes

---

## Testing Strategy

### Unit Tests
1. **Parser Tests**
   - Test markdown extraction for various formats
   - Test edge cases (missing fields, malformed files)
   - Test archive file parsing

2. **Merge Logic Tests**
   - Test field overriding rules
   - Test conflict resolution
   - Test historical preservation

3. **API Tests**
   - Test all endpoints with valid/invalid data
   - Test error responses
   - Test pagination and filtering

### Integration Tests
1. **End-to-End Data Flow**
   - Parse sample research → merge → API → frontend
   - Test manual update flow
   - Test file change detection

2. **UI Tests**
   - Test search functionality
   - Test diff view calculations
   - Test responsive design

3. **Performance Tests**
   - Load time with 1000+ tickers
   - Search performance
   - Memory usage

### User Acceptance Tests
1. **Bob's Workflow**
   - Daily research appears in encyclopedia
   - Search finds historical research
   - Diff shows meaningful changes

2. **Manual Research**
   - Can add research via UI/API
   - Updates appear immediately
   - Conflicts handled gracefully

---

## Rollback Strategy

### If Implementation Fails:
1. **Stop server:** `./mc.sh stop`
2. **Restore files from backup:**
   - Restore `server.py` from backup
   - Remove encyclopedia tab from dashboard.html
   - Remove new API endpoints
3. **Start server:** `./mc.sh start`

### Backup Locations:
- `mission_control_dev/server.py.backup.encyclopedia`
- `portfolio/data/earnings_encyclopedia_backup.json`
- `v1.3_backup/` (full system backup)

### Gradual Rollout:
1. Deploy data layer only (read-only)
2. Deploy API endpoints (test with curl)
3. Deploy frontend (hidden behind feature flag)
4. Enable for all users

---

## Success Metrics

### Quantitative
1. **Coverage:** % of researched tickers in encyclopedia (target: 100%)
2. **Accuracy:** Data consistency between source and consolidated (target: 99%)
3. **Performance:** Search response time < 500ms for 1000 tickers
4. **Uptime:** API availability > 99.9%

### Qualitative
1. **Usability:** Bob can find any historical research in < 30 seconds
2. **Insightfulness:** Diff view provides meaningful quarter-over-quarter insights
3. **Reliability:** No data loss during updates
4. **Maintainability:** Adding new research requires no code changes

---

## Future Enhancements

### Phase 2 (Q2 2026)
1. **Sentiment Analysis:** Auto-detect positive/negative tone shifts
2. **Pattern Recognition:** Identify recurring themes across quarters
3. **Peer Comparison:** Compare research against sector peers
4. **Performance Tracking:** Track post-earnings stock performance vs recommendation

### Phase 3 (Q3 2026)
1. **Natural Language Search:** "Find stocks with improving margins"
2. **Alert System:** Notify when research changes significantly
3. **Export Tools:** Export to research reports, presentations
4. **API for External Tools:** Allow other systems to query encyclopedia

---

## Verification Checklist

### Pre-Implementation
- [ ] TDS reviewed and approved
- [ ] Backup of current system created
- [ ] Test data prepared (sample research files)
- [ ] Development environment ready

### Phase 1: Data Layer
- [ ] Parser extracts data from markdown files
- [ ] Encyclopedia data structure created
- [ ] Merge logic implemented and tested
- [ ] Initial encyclopedia built from historical data

### Phase 2: API
- [ ] All API endpoints implemented
- [ ] Endpoints return correct data formats
- [ ] Error handling working
- [ ] Backward compatibility maintained

### Phase 3: Frontend
- [ ] New tab added to dashboard
- [ ] Search functionality working
- [ ] Detail view with timeline
- [ ] Diff view showing changes
- [ ] Responsive design tested

### Phase 4: Integration
- [ ] Auto-update on file changes
- [ ] Manual research entry form
- [ ] All edge cases handled
- [ ] Performance acceptable

### Post-Implementation
- [ ] Full system backup created
- [ ] Documentation updated
- [ ] Bob trained on new features
- [ ] Success metrics being tracked

---

## Approval

**This TDS follows AGENTS.md protocol for MEDIUM risk coding task.**

**Changes needed? Questions?**
**Say "proceed" when ready to implement.**

**Coder:** Alex (DeepSeek V3)