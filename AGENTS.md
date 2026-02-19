# AGENTS.md - Coding & Development Protocol

## When This Applies

**USE THIS PROTOCOL when:**
- Modifying code files (Python, JavaScript, HTML, CSS)
- Creating new features or functionality
- Changing data structures or schemas
- Adding/updating API endpoints
- Database or configuration changes

**SKIP THIS PROTOCOL when:**
- Answering questions (weather, passwords, definitions)
- Reading or analyzing existing code
- Simple lookups or research
- Non-technical tasks

---

## The Protocol

### STEP 1: Detect Coding Task
Before writing ANY code, ask:
> "This involves code changes. Should I follow the coding protocol?"

If yes → Continue to Step 2

### STEP 2: Architecture Check (30 seconds)
Answer these mentally:
- [ ] What file(s) will I modify?
- [ ] What's the data flow? (source → transform → output)
- [ ] Are there existing patterns I should follow?
- [ ] Could this break existing functionality?

If any answer is unclear → **ASK BEFORE PROCEEDING**

### STEP 3: TDS Required?
Check if TDS exists:
- [ ] docs/specs/[feature-name].md exists?
- [ ] TDS covers data architecture?
- [ ] TDS has testing requirements?

**If NO TDS:**
```
"This needs a Technical Design Spec. Options:
A) I draft TDS now, you review
B) You describe architecture, I draft TDS  
C) We proceed without TDS (higher risk)"

Wait for explicit choice.
```

### STEP 4: Risk Assessment
**HIGH RISK** (requires backup + extra testing):
- Modifies server.py
- Changes database/JSON schemas
- Affects multiple tabs/features
- Breaking changes to APIs

**LOW RISK** (standard testing):
- CSS only changes
- HTML layout tweaks
- Adding new data (no schema changes)

### STEP 5: Implementation
**For HIGH RISK:**
1. Create backup: cp file.py file.py.backup
2. Make changes
3. Restart server (if Python modified)
4. Test the specific change
5. Test adjacent features

**For LOW RISK:**
1. Make changes
2. Test in browser

### STEP 6: Verification Checklist
Before saying "done":
- [ ] Change works as intended?
- [ ] No console errors?
- [ ] Mobile responsive (if UI)?
- [ ] Data flow verified?
- [ ] Server restarted (if needed)?

**Report format:**
Files: [list modified]
Backup: [location or N/A]
Server restart: [Yes/No]
Tested: [Yes/No - what was tested]

---

## Sub-Agent Protocol (Alex)

When spawning Alex for coding tasks:

**MUST INCLUDE:**
"Follow AGENTS.md coding protocol.
TDS: [path to TDS file]
Risk level: [High/Low]
Backup required: [Yes/No]

MANDATORY REPORT:
- Files modified: ___
- Backup location: ___
- Server restarted: ___
- Tested endpoints: ___
- Issues: ___"

**Alex CANNOT mark complete without:**
1. Backup created (if High Risk)
2. Server restarted (if Python changed)
3. Testing verification
4. Explicit report

---

## Quick Reference

| Trigger | Action |
|---------|--------|
| "Build X" / "Create Y" | Draft TDS first |
| "Fix bug in Z" | Architecture check, then fix |
| "Update CSS" | Low risk, test visually |
| "Add endpoint" | HIGH RISK - TDS + backup + test all |
| "Simple question" | Skip protocol |

---

## Why This Matters

**Rushing costs more time:**
- 10 min planning → saves 2 hours debugging
- TDS prevents rewrites
- Architecture first prevents breaking things

**Remember:**
"Measure twice, cut once" applies to code.
