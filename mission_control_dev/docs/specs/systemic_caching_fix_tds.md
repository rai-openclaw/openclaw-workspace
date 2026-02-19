# TDS: Systemic Caching Fix - All API Endpoints

## CRITICAL: This affects ALL endpoints. Test everything.

## Overview
Add cache-control headers to ALL API endpoints and implement cache-busting in frontend to ensure data updates immediately when JSON changes.

**Risk Level: HIGH** - Affects entire site
**Testing Required: ALL endpoints must be verified**

---

## BACKUP FIRST (CRITICAL)

Before any changes:
```bash
# Create full backup
cp -r ~/.openclaw/workspace/portfolio/data ~/.openclaw/workspace/portfolio/data.backup.$(date +%Y%m%d_%H%M%S)
cp ~/.openclaw/workspace/mission_control/server.py ~/.openclaw/workspace/mission_control/server.py.backup
```

---

## Implementation

### Phase 1: Backend - Add Cache Headers (ALL Endpoints)

Modify EVERY API endpoint in `server.py` to return cache-control headers:

```python
response = jsonify(data)
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
response.headers['Pragma'] = 'no-cache'
response.headers['Expires'] = '0'
return response
```

**Endpoints to update:**
1. `/api/portfolio`
2. `/api/analysis-archive`
3. `/api/earnings-research`
4. `/api/ideas`
5. `/api/schedule`
6. `/api/corporate`
7. `/api/usage`
8. `/api/queue-status`
9. `/api/idea-update` (POST)
10. `/api/idea-delete` (POST)

**Helper function approach (RECOMMENDED):**
Create a helper function to avoid code duplication:
```python
def json_response(data):
    """Return JSON response with cache-control headers"""
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

Then replace all `return jsonify(data)` with `return json_response(data)`.

### Phase 2: Frontend - Cache Busting (ALL Fetch Calls)

Update EVERY fetch call in `dashboard.html` to add timestamp:

**Change from:**
```javascript
fetch('/api/ideas')
```

**To:**
```javascript
fetch('/api/ideas?t=' + Date.now())
```

**Functions to update:**
1. `loadHoldings()`
2. `loadAnalysis()`
3. `loadEarnings()`
4. `loadIdeas()`
5. `loadSchedule()`
6. `loadCorporate()`
7. `loadUsage()`
8. `updateIdeaStatus()`
9. `deleteIdea()`

---

## Testing Protocol (MANDATORY)

### After Backend Changes:
1. **RESTART SERVER** (critical)
2. **Test EVERY endpoint:**
   ```bash
   curl -I http://localhost:8080/api/portfolio | grep -i cache
   curl -I http://localhost:8080/api/ideas | grep -i cache
   # ... test ALL endpoints
   ```
3. **Verify headers present:** Must see `Cache-Control: no-cache`

### After Frontend Changes:
1. **Hard refresh browser** (Cmd+Shift+R)
2. **Test each tab:**
   - Holdings: Verify data loads
   - Analysis: Verify data loads
   - Earnings: Verify data loads
   - Ideas: Verify data loads, test update/delete
   - Schedule: Verify data loads
   - Corporate: Verify data loads
   - API Usage: Verify data loads
3. **Test cache busting:**
   - Modify a JSON file directly
   - Refresh browser
   - Verify changes appear immediately

### Edge Cases:
- POST endpoints (update/delete) must also have cache headers
- Error responses must have cache headers
- Empty responses must have cache headers

---

## Rollback Plan

If anything breaks:
```bash
# Restore from backup
cp ~/.openclaw/workspace/mission_control/server.py.backup ~/.openclaw/workspace/mission_control/server.py
# Restore data if needed
cp -r ~/.openclaw/workspace/portfolio/data.backup.* ~/.openclaw/workspace/portfolio/data
# Restart
./mc.sh restart
```

---

## Success Criteria

- [ ] ALL API endpoints return Cache-Control headers
- [ ] ALL frontend fetch calls include timestamp
- [ ] Server restarted and running
- [ ] ALL tabs load data correctly
- [ ] Data changes appear immediately after JSON modification
- [ ] No console errors
- [ ] Mobile works correctly

---

## Files to Modify

1. `mission_control/server.py` - Add cache headers to ALL endpoints
2. `mission_control/templates/dashboard.html` - Add cache-busting to ALL fetch calls

---

## Report Requirements

MUST include:
```
Backup created: YES/NO
Endpoints updated: X/Y
Server restarted: YES/NO
All endpoints tested: YES/NO
All tabs tested: YES/NO
Cache headers verified: YES/NO
Issues: [any issues]
```

---

## Approval

**HIGH RISK - Review carefully. Say "proceed" only when ready to implement with full testing.**
