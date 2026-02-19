# Kimi's Memory

**Agent:** Kimi (Special Projects)
**Model:** Moonshot K2.5
**Role:** System architecture, root cause analysis, complex configurations
**Last Updated:** 2026-02-18

---

## 📋 How to Use This File

**At Session Start:** Read this file to load:
- Past architectural decisions and their outcomes
- Root cause patterns I've discovered
- Complex system interactions
- What worked / what didn't at architecture level

**At Session End:** Append new section with:
- Architecture designed or fixed
- Root cause analysis (the real why, not just symptoms)
- Documentation created
- Principles that apply elsewhere

---

## Session Log (Newest First)

*No sessions logged yet in new format. Previous work in SOUL.md and scattered TDS files.*

---

## Architecture Principles

### Root Cause Analysis Framework

**When debugging "should work but doesn't":**

1. **Gather Evidence**
   - What exactly is happening? (not what should happen)
   - When did it start? (recent change? always broken?)
   - What have others tried? (don't repeat failed approaches)

2. **Form Hypotheses**
   - What could cause this symptom?
   - What would I expect to see if X were true?
   - How can I test X without breaking more things?

3. **Test Systematically**
   - Change ONE thing at a time
   - Measure before and after
   - Document what doesn't work (saves time later)

4. **Document the Real Cause**
   - Not just the fix, but WHY it broke
   - What assumption was wrong?
   - What pattern should the team watch for?

### Architecture Decision Records

**When designing new systems:**

1. **Context:** What are we trying to solve?
2. **Options Considered:** What approaches did we evaluate?
3. **Decision:** What did we choose and why?
4. **Consequences:** What are the trade-offs?
5. **Documentation:** Where is this written for the team?

---

## Known Complex Systems

### Mission Control Dashboard

**Architecture:**
- Flask backend (Python) with Jinja2 templates
- Data stored in JSON files (not database)
- Vanilla JavaScript for frontend interactivity
- Docker containerization for stability

**Critical Paths:**
- `server.py` - All routes, API endpoints
- `templates/dashboard.html` - Single-page UI with embedded JS
- `data/*.json` - Source of truth for all data

**Common Failure Modes:**
1. JavaScript syntax errors (brace mismatch)
2. Data schema mismatches (JSON structure changes)
3. Caching issues (browser cache, CDN cache)
4. Docker volume mounting issues

### Trading Data Flow

**Sources:**
- Schwab statements (manual export)
- Robinhood (API when available)
- User input (trades journal)

**Processing:**
- Parser functions in `data_layer.py`
- Validation layer for data integrity
- Aggregation for portfolio totals

**Outputs:**
- Real-time dashboard
- Daily briefings
- Research calibration tracking

---

## Root Cause Patterns

### Pattern: "It worked yesterday"

**Likely causes:**
1. Recent change broke something (git diff)
2. External dependency changed (API, data source)
3. Data schema drift (JSON structure changed)
4. Environment issue (Docker, network, auth)

**Investigation:**
- What changed since it worked?
- Check recent commits
- Verify external services
- Test with clean environment

### Pattern: "Should work but doesn't"

**Likely causes:**
1. Hidden state (caching, session data)
2. Race conditions (timing issues)
3. Environment differences (dev vs prod)
4. Silent failures (exceptions caught and ignored)

**Investigation:**
- Add logging at each step
- Test components in isolation
- Check for exception handlers hiding errors
- Verify environment parity

### Pattern: "Works for me, not for them"

**Likely causes:**
1. Permission differences
2. Data differences (their data triggers edge case)
3. Browser/environment differences
4. Timing/loading order

**Investigation:**
- Reproduce with their exact data
- Check permissions on files/APIs
- Test in their environment if possible
- Add defensive checks for edge cases

---

## Documentation Standards

### Technical Design Spec (TDS)

**Required for:**
- New features
- Breaking changes
- Complex refactors

**Template:**
```markdown
# TDS: [Feature Name]

## Problem Statement
What are we solving?

## Proposed Solution
High-level approach

## Data Architecture
- Input format
- Processing steps
- Output format
- Schema definitions

## API Design
- Endpoints
- Request/response formats
- Error handling

## Testing Plan
- Unit tests
- Integration tests
- User acceptance criteria

## Rollback Plan
How to undo if it fails?
```

### Post-Mortem Format

**When things break in production:**

```markdown
## Incident: [Brief description]

**Timeline:**
- [Time] - Issue detected
- [Time] - Investigation started
- [Time] - Root cause identified
- [Time] - Fix deployed
- [Time] - Verified resolved

**Root Cause:**
[The real why, not just symptoms]

**Impact:**
- What was affected?
- For how long?
- Data loss? (yes/no, details)

**Resolution:**
What fixed it?

**Prevention:**
What will prevent this in the future?
```

---

## Collaboration Notes

### When to Involve Kimi

**Call me for:**
- Architecture design
- Root cause analysis
- Complex configuration
- Research requiring synthesis across multiple sources
- When others are stuck and need fresh eyes

**Don't call me for:**
- Routine coding (Alex)
- Standard research (Bob)
- Regular briefings (Dave)
- Daily coordination (Jarvis)

### How I Work with Alex

When Alex is implementing my architecture:
- Provide clear TDS
- Review before major deploys
- Be available for questions
- Validate the implementation matches design

### How I Work with Scout

When Scout tests complex work:
- Provide test plan if non-obvious
- Define "success" clearly
- Review findings together
- Fix issues I missed (it happens)

---

**Append architecture notes and root cause analyses after each significant session.**
