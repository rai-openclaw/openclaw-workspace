# Development-to-Production Merge Tracking

**Purpose:** Track changes when building on dev (port 8081) for merging back to production (port 8080)
**Challenge:** Alex times out, work may be split across sessions
**Solution:** Change log + checkpoint commits

---

## The Problem

Alex builds feature on port 8081 → Session times out → Changes scattered → How to merge to production?

**Without tracking:**
- Don't know what files changed
- Don't know what's working vs broken
- Risk of missing pieces
- Risk of overwriting production

**With tracking:**
- Clear list of modified files
- Checkpoint commits preserve progress
- Can resume after timeout
- Safe merge back to production

---

## Solution: Change Log + Git Checkpoints

### 1. Change Log File

**Location:** `~/mission-control-dev/CHANGELOG.md`

**Format:**
```markdown
# Development Change Log - Earnings Encyclopedia

## Session 1 - 2026-02-18 10:00 AM
**Status:** In Progress
**Working:** Data layer, parser
**Files Modified:**
- `data_layer.py` - Added load_earnings_encyclopedia()
- `data/earnings_encyclopedia.json` - Created schema
**Notes:** Parser working, moving to API endpoints
**Next:** Build /api/earnings-encyclopedia endpoint

## Session 2 - 2026-02-18 2:00 PM  
**Status:** In Progress
**Working:** API endpoints
**Files Modified:**
- `server.py` - Added 4 new endpoints
- `data_layer.py` - Added merge function
**Notes:** Endpoints responding, need testing
**Next:** Build frontend UI

## Session 3 - 2026-02-18 5:00 PM
**Status:** Complete
**Working:** Frontend, integration
**Files Modified:**
- `templates/dashboard.html` - Added encyclopedia tab
- `static/css/encyclopedia.css` - New styles
**Notes:** Feature complete on port 8081
**Next:** Testing before merge to production

## Merge to Production - 2026-02-19 9:00 AM
**Status:** Merged
**Files Copied:**
- `data_layer.py`
- `server.py`
- `templates/dashboard.html`
- `static/css/encyclopedia.css`
- `data/earnings_encyclopedia.json`
**Testing:** All tests passed on port 8080
**Backup:** Created before merge
```

### 2. Git Checkpoint Commits

**Process:**
1. Alex starts work
2. Every 30 minutes OR at natural break points:
   - `git add -A`
   - `git commit -m "Checkpoint: [what's working]"`
3. If timeout occurs → Work preserved in git
4. New session → `git log` to see where we left off

**Benefits:**
- Work never lost
- Can see progression
- Can rollback if needed
- Clear audit trail

---

## Alex's Updated Workflow

### Before Starting (Each Session)
```bash
# 1. Read change log
cat ~/mission-control-dev/CHANGELOG.md

# 2. Check git status
cd ~/mission-control-dev
git status
git log --oneline -3

# 3. Read TDS
# Review what we're building

# 4. Append to change log
echo "## Session X - $(date)" >> CHANGELOG.md
echo "**Status:** Starting" >> CHANGELOG.md
```

### During Work (Every 30 min or milestone)
```bash
# Checkpoint commit
git add -A
git commit -m "Checkpoint: [brief description of what's working]"

# Update change log
echo "**Files Modified:** [list]" >> CHANGELOG.md
echo "**Notes:** [what's working]" >> CHANGELOG.md
```

### At Timeout or Session End
```bash
# Emergency commit (even if incomplete)
git add -A
git commit -m "WIP: [what was being worked on] - timeout"

# Update change log
echo "**Status:** Timeout / Paused" >> CHANGELOG.md
echo "**Next:** [what to do next session]" >> CHANGELOG.md
```

---

## Merge to Production Process

### Step 1: Verify Dev is Complete
```bash
cd ~/mission-control-dev
# Check change log - all phases complete?
cat CHANGELOG.md

# Check git log - all commits there?
git log --oneline

# Test on port 8081
curl http://localhost:8081/api/earnings-encyclopedia?ticker=CVNA
```

### Step 2: Backup Production
```bash
cd ~/mission-control
# Create backup branch
git checkout -b backup-before-encyclopedia

# Or timestamp backup
cp -r ~/mission-control ~/mission-control-backup-$(date +%Y%m%d)
```

### Step 3: Copy Changes (Using Change Log)
```bash
# Read change log to get file list
FILES=$(grep -E "^- " ~/mission-control-dev/CHANGELOG.md | sed 's/^- //' | sort -u)

# Copy each file
for file in $FILES; do
    cp ~/mission-control-dev/$file ~/mission-control/$file
    echo "Copied: $file"
done
```

### Step 4: Test on Production Port
```bash
cd ~/mission-control
docker-compose restart

# Test
curl http://localhost:8080/api/earnings-encyclopedia?ticker=CVNA
```

### Step 5: Commit Production
```bash
cd ~/mission-control
git add -A
git commit -m "Merge: Earnings Encyclopedia feature from dev

Source: port 8081 development
Files: [list from change log]
Testing: Passed
Backup: [location]"
```

---

## Handling Alex Timeouts

### If Alex Times Out Mid-Task:

1. **Check Git:** `git log` shows last checkpoint
2. **Check Change Log:** Shows what was being worked on
3. **Check Files:** `git diff HEAD~1` shows recent changes
4. **Resume:** New Alex session starts from last checkpoint

### If Multiple Timeouts:

Each timeout = checkpoint commit  
Each session = reads change log + git log  
Work continues incrementally  
Final merge uses complete change log

---

## File Location Best Practices

### Recommended: `~/mission-control/data/`

**Why:**
- Same location as other data (holdings.json, ideas.json)
- Mounted in Docker container
- Backed up with other data
- Consistent with existing architecture

**Structure:**
```
~/mission-control/data/
├── holdings.json
├── ideas.json
├── corporate.json
├── earnings_encyclopedia.json      ← NEW
└── research/                       ← NEW
    ├── daily/
    │   ├── 2026-02-18.json
    │   └── 2026-02-19.json
    └── archive/
```

### Alternative: Separate Research Directory

**Structure:**
```
~/.openclaw/workspace/research/
├── daily/
│   └── 2026-02-18.json
├── archive/
└── encyclopedia.json
```

**Downside:** 
- Different location from other data
- Separate backup strategy needed
- More complex data layer

### Recommendation: Use `~/mission-control/data/`

Keep all Mission Control data in one place.

---

## Summary Checklist for Alex

**Before Building:**
- [ ] Create `~/mission-control-dev/CHANGELOG.md`
- [ ] Set up port 8081 container
- [ ] Read TDS
- [ ] First checkpoint commit

**During Building:**
- [ ] Update CHANGELOG.md at each milestone
- [ ] Git checkpoint commit every 30 min
- [ ] Note what works vs what's broken

**If Timeout:**
- [ ] Emergency commit: `git commit -m "WIP: ..."`
- [ ] Update CHANGELOG with status

**Before Merge:**
- [ ] Verify CHANGELOG shows all phases complete
- [ ] Verify all files listed in CHANGELOG
- [ ] Backup production
- [ ] Copy files from change log
- [ ] Test on port 8080
- [ ] Commit production

---

**Next Step:** Update Bob to output JSON, then Alex can start building with this tracking system.
