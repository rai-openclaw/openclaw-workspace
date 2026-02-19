# Alex's Memory

**Agent:** Alex (Lead Developer)
**Model:** DeepSeek V3
**Role:** Implementation, coding tasks, 90% cost savings vs Kimi
**Last Updated:** 2026-02-18

---

## 📋 How to Use This File

**At Session Start:** Read this file to load:
- Coding patterns and protocols
- Past mistakes to avoid
- Project-specific knowledge
- What worked / what didn't

**At Session End:** Append new section with:
- What I built or fixed
- What went wrong and why
- What I learned
- Files modified, tested, backed up

---

## Session Log (Newest First)

### 2026-02-18: JavaScript Syntax Fix - Dashboard Broken

**Problem:** Corporate tab edits broke entire dashboard. Site stuck on "Loading...", tabs unclickable.

**Root Cause:** 
- Brace mismatch in `loadCorporate()` function (331 open, 334 close)
- Stray duplicate code block from previous edit
- Unclosed template literals

**Solution:**
- Located and removed stray duplicate code in `loadCorporate()`
- Rebalanced braces to 302 open / 302 close
- Validated with `node -c` syntax check
- Rebuilt Docker container and deployed

**Mistakes / Learned:**
- ❌ I created duplicate code when editing Corporate tab
- ❌ Didn't validate brace balance before claiming done
- ❌ Template literals can break if not carefully balanced
- ✅ Surgical edits (edit tool) better than rewrites for existing code
- ✅ Always validate JS syntax: `grep -o '{' file.js | wc -l` vs `grep -o '}' file.js | wc -l`

**Files Modified:**
- `~/mission-control/templates/dashboard.html` - Fixed loadCorporate() function

**Backup:**
- GitHub repo created: https://github.com/rai-openclaw/mission-control-dashboard
- Local git commit: "Mission Control Dashboard - Post JavaScript fix backup"

**Tested:**
- ✓ HTTP 200 response
- ✓ All 6 APIs responding (Portfolio, Corporate, Ideas, Schedule, Analysis, APIs)
- ✓ JavaScript syntax validated (302 balanced braces)
- ✓ Holdings tab loads data (34 stocks, 10 options)
- ✓ Tabs clickable and functional

**Regression Test Results:** All systems operational

---

## Coding Protocol (AGENTS.md) - STRICT COMPLIANCE REQUIRED

### Step 1: Detect Coding Task
If user asks for code changes → Use this protocol. Skip for questions only.

### Step 2: Architecture Check (30 seconds)
Answer mentally:
- What file(s) will I modify?
- What's the data flow? (source → transform → output)
- Are there existing patterns I should follow?
- Could this break existing functionality?

**If unclear → ASK before proceeding**

### Step 3: TDS Required?
Check if Technical Design Spec exists:
- `docs/specs/[feature-name].md` exists?
- TDS covers data architecture?
- TDS has testing requirements?

**If NO TDS:**
```
"This needs a Technical Design Spec. Options:
A) I draft TDS now, you review
B) You describe architecture, I draft TDS
C) We proceed without TDS (higher risk)"
```
**Wait for explicit choice.**

### Step 4: Risk Assessment
**HIGH RISK** (requires backup + extra testing):
- Modifies server.py
- Changes database/JSON schemas
- Affects multiple tabs/features
- Breaking changes to APIs

**LOW RISK** (standard testing):
- CSS only changes
- HTML layout tweaks
- Adding new data (no schema changes)

### Step 5: Implementation
**For HIGH RISK:**
1. Create backup: `cp file.py file.py.backup`
2. Make changes
3. Restart server (if Python modified)
4. Test the specific change
5. Test adjacent features

**For LOW RISK:**
1. Make changes
2. Test in browser

### Step 6: Verification Checklist
Before saying "done":
- [ ] Change works as intended?
- [ ] No console errors?
- [ ] Mobile responsive (if UI)?
- [ ] Data flow verified?
- [ ] Server restarted (if needed)?

**Report format:**
```
Files: [list modified]
Backup: [location or N/A]
Server restart: [Yes/No]
Tested: [Yes/No - what was tested]
```

---

## User's Code Style Preferences

### File Organization
- **Flask server:** `server.py` in project root
- **Templates:** `templates/` directory
- **Static assets:** `static/css/` and `static/js/`
- **Data:** `data/` directory with JSON files
- **Specs:** `docs/specs/` for Technical Design Specs

### Python Patterns
- Use **type hints** where helpful but not required
- Prefer **explicit imports** over wildcard
- Use **f-strings** for string formatting
- Error handling: Try/except with specific exceptions
- Logging: Use print() for simple debugging, proper logging for production

### JavaScript Patterns
- Use **vanilla JS** (no frameworks unless specified)
- **Event delegation** for dynamic elements
- **Arrow functions** for callbacks
- **Template literals** (backticks) for HTML strings
- **Strict equality** (===) not loose (==)

### HTML/CSS Patterns
- **Tailwind classes** preferred for styling
- **Semantic HTML** (nav, main, section, article)
- **Mobile-first** responsive design
- **CSS Grid** for layouts, **Flexbox** for components

---

## Project-Specific Patterns

### Mission Control Dashboard
**Architecture:**
- Flask backend serves HTML + API endpoints
- Jinja2 templates with embedded JavaScript
- Data stored in JSON files (not database)
- Real-time updates via fetch() API calls

**Key Files:**
- `server.py` - Main Flask app, routes, API endpoints
- `templates/dashboard.html` - Main UI template
- `data/*.json` - Portfolio, ideas, corporate data

**API Endpoints Pattern:**
```python
@app.route('/api/endpoint', methods=['GET'])
def api_endpoint():
    data = load_data()
    return jsonify(data)
```

### Data Layer Pattern
```python
def load_json(filename):
    """Load JSON from data directory"""
    with open(f'data/{filename}', 'r') as f:
        return json.load(f)

def save_json(filename, data):
    """Save JSON to data directory"""
    with open(f'data/{filename}', 'w') as f:
        json.dump(data, f, indent=2)
```

### JavaScript Fetch Pattern
```javascript
fetch('/api/endpoint')
  .then(r => r.json())
  .then(data => {
    // Update DOM
  })
  .catch(err => console.error(err));
```

---

## Common Mistakes & Corrections

### JavaScript Brace Balance
**CRITICAL:** Always verify brace balance equals 0
```bash
# Check before claiming done
cat file.js | tr -cd '{}' | awk '{print length}'
# If result != 0, there's a mismatch
```

**Past Errors:**
- Caching fix implementation: brace mismatch caused -17 balance
- Edit functionality: multiple nested functions caused scope issues
- **Fix:** Use surgical `edit` tool, verify balance after each change

### Surgical Edits vs Rewrites
**Preferred:** Use `edit` tool for small changes
```
edit: oldText="exact match" newText="replacement"
```

**Avoid:** Using `write` for full file rewrites
- Loses context
- Easy to miss small details
- Harder to review

### Parser Functions
**Issue:** Empty columns caused `len(values) < len(headers)` to fail
**Fix:** Accept `len(headers) - 1` values to handle trailing empty cells

**Issue:** Stray tables matched wrong sections
**Fix:** Filter tables with exactly 7 columns ending in status words (Track, Hold, Monitor)

---

## Testing Requirements

### Before Marking Complete
1. **Server running?** Check `docker ps` or `lsof -i :8080`
2. **Browser test:** Open http://localhost:8080
3. **Console errors?** Check DevTools → Console
4. **Mobile check:** Resize browser to mobile width
5. **Adjacent features:** Test related tabs/functionality

### Specific Tests by Change Type
**CSS Changes:**
- Visual inspection at multiple widths
- Check contrast ratios
- Verify no layout shifts

**JavaScript Changes:**
- Check console for errors
- Test all affected buttons/interactions
- Verify data updates correctly

**Python Changes:**
- Restart server
- Test specific endpoint
- Test error handling (bad input)

**API Changes:**
- Test with curl or browser
- Verify response format
- Check error responses

---

## Docker Patterns

### Dockerfile Structure
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    restart: always
```

### Commands to Know
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Check status
docker ps
```

---

## File Backup Strategy

### High Risk Changes
```bash
# Always backup before modifying
cp server.py server.py.backup.$(date +%Y%m%d_%H%M%S)

# Or use git
git add -A
git commit -m "Before: [description of change]"
```

### When to Create Backup
- [ ] Modifying server.py
- [ ] Changing template structure
- [ ] Database/JSON schema changes
- [ ] API endpoint modifications

### Restore Process
```bash
# If change breaks
cp server.py.backup.[timestamp] server.py
docker-compose restart  # if using Docker
```

---

## Cost Optimization

### My Role (DeepSeek V3)
- **Use for:** Coding tasks, implementations, debugging
- **Cost:** ~90% cheaper than Kimi
- **Limitations:** Less reasoning depth, follow protocols strictly

### When to Escalate to Kimi
- Architecture decisions
- Protocol violations
- Unclear requirements
- Complex debugging

### Token Efficiency
- **Read files once,** cache in context
- **Batch similar edits** when possible
- **Avoid re-reading** same files repeatedly
- **Use grep/search** to find specific lines, don't read full files

---

## Communication Style

### Task Acceptance
```
"I'll [do the task]. [Time estimate]."
```

### Progress Updates
```
"Step [X] complete. Moving to [next step]."
```

### Completion Report (REQUIRED)
```
**Complete:**
- Files modified: [list]
- Backup created: [yes/no - location]
- Server restarted: [yes/no]
- Tested: [yes/no - what was tested]
- Issues: [none or list]
```

### When Stuck
```
"I'm stuck on [specific issue]. Options:
A) [approach 1 with trade-offs]
B) [approach 2 with trade-offs]
Which would you prefer?"
```

---

## Project History

### Mission Control Evolution
- **v1.0:** Basic Flask server, bare metal
- **v2.0:** Gunicorn WSGI, stable baseline
- **v2.1 (current):** Docker containerization (in progress)

### Known Working Versions
- `backups/v2.0_complete/` - Last stable baseline
- `dashboard.html.pre-minimal` - Stable version with features

### Failed Approaches (Learn From These)
- GitHub Pages: 10min cache, read-only
- Netlify: Read-only, no edit
- FastAPI split: Overcomplicated, CORS issues

---

## Reminders for Future Sessions

1. **Always check brace balance** for JavaScript changes
2. **Never skip verification checklist** before claiming done
3. **Create backup for high-risk changes**
4. **Use surgical edits** (edit tool) not rewrites
5. **Restart server** after Python changes
6. **Test in browser** even for "simple" changes
7. **Read AGENTS.md** if unsure about protocol

---

## Trading Data Migration & Integration (2026-02-18)

### Data Migration Learnings

**Schema Design Decisions:**
1. **Trades JSON Structure:**
   - Used `trade_id` UUID for unique identification
   - Included both `timestamp` (ISO format) and `date` (YYYY-MM-DD) for flexibility
   - Added `status` field (OPEN/CLOSED) with `close_date` for closed trades
   - Included `realized_pnl` for closed trades, calculated from entry/exit premiums

2. **Portfolio Positions Structure:**
   - Nested structure: accounts → positions → options arrays
   - Each option includes strike, expiration, contracts, entry_premium
   - Separate from holdings.json which tracks stocks/ETFs

3. **Research Calibration Structure:**
   - Array of research results with grading outcomes
   - Includes expected vs actual moves for calibration tracking
   - `calibration_note` field for qualitative assessment

**Integration Challenges:**
1. **Path Management:** Trading data stored in workspace (`~/.openclaw/workspace/data/`) while Mission Control uses portfolio data directory
2. **Schema Validation:** Added schema validation with warnings instead of failures
3. **Data Layer Extension:** Extended existing `data_layer.py` with new functions instead of creating separate module
4. **API Endpoint Design:** Followed existing patterns in `server.py` for consistency

### Implementation Patterns

**Data Layer Extension:**
```python
def load_trades() -> dict:
    """Load trading history data from workspace directory"""
    workspace_data_dir = Path("/Users/raitsai/.openclaw/workspace/data")
    json_path = workspace_data_dir / "trades.json"
    # ... load and validate
```

**Summary Calculation:**
```python
def calculate_pnl_summary() -> dict:
    """Calculate YTD P&L metrics from trades"""
    # Filter by current year, count wins/losses
    # Calculate win rate, premium collected, etc.
```

**API Endpoint Pattern:**
```python
@app.route('/api/trades')
def get_trades():
    """Return all historical trades"""
    if USE_DATA_LAYER:
        trades_data = load_trades()
        return jsonify(trades_data)
```

**Frontend Integration:**
- Added new "Trading" tab to navigation
- Created `loadTrading()` function that fetches multiple endpoints in parallel
- Rendered summary cards, open positions table, and recent trades list
- Used existing CSS classes for consistency

### Testing Results
- All 4 new API endpoints working correctly
- Data flows from JSON files → data layer → API → frontend
- Summary calculations accurate based on YTD trades
- Frontend renders without console errors

### Files Modified
1. `data_layer.py` - Added 6 new trading functions
2. `server.py` - Added 5 new API endpoints, updated imports
3. `dashboard.html` - Added Trading tab, navigation, JavaScript functions

**Backup:** `server.py.backup` created before modifications
**Server Restart:** Tested with temporary server on port 8082
**Tested:** All endpoints verified with curl, data flows validated

---

**Append new patterns and corrections after each coding session.**
