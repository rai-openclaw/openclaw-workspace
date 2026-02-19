# TDS: Fix Ideas Update Error - "Idea Not Found"

## Problem
User gets "failed to update idea: idea not found" when trying to update ideas.

## Root Causes Identified
1. **Stale browser cache** - Browser showing deleted ideas that no longer exist
2. **Missing idea-009** - Options backtester was accidentally deleted
3. **Poor error handling** - No clear message about stale data

## Solutions

### 1. Backend: Better Error Messages
Update `/api/idea-update` to return clearer error:
```json
{
  "success": false,
  "error": "Idea not found",
  "message": "This idea may have been deleted. Please refresh the page.",
  "requested_id": "idea-xxx"
}
```

### 2. Frontend: Auto-refresh on Error
When update fails with "not found":
- Show alert: "Idea not found. Refreshing data..."
- Automatically call `loadIdeas()` to refresh from server
- Clear the stale cache issue

### 3. Frontend: Add Timestamp Check
Add `last_updated` timestamp comparison:
- Store timestamp when Ideas tab loads
- If server data is newer, auto-refresh
- Show "New data available - click to refresh" banner

### 4. Backend: Add Cache-Busting Headers
Add to `/api/ideas` endpoint response:
```python
response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
response.headers['Pragma'] = 'no-cache'
```

### 5. Quick Fix Already Applied
✅ Restored idea-009 (Options backtester) to ideas.json

## Implementation

### Phase 1: Backend (Alex)
1. Update `/api/idea-update` error response with helpful message
2. Add cache-control headers to `/api/ideas`
3. Return requested_id in error for debugging

### Phase 2: Frontend (Alex)
1. Update `updateIdeaStatus()` error handler:
   - If error is "not found", show alert and auto-refresh
2. Add `loadIdeas()` call on error
3. Add timestamp check in `loadIdeas()`

### Files to Modify
- `mission_control/server.py` - Better error messages + headers
- `mission_control/templates/dashboard.html` - Auto-refresh on error

## Testing
- [ ] Update non-existent idea shows helpful error
- [ ] Page auto-refreshes when stale data detected
- [ ] Cache headers prevent browser caching
- [ ] idea-009 can be updated successfully

## Note
User should hard-refresh browser (or close/reopen tab) to clear stale data immediately.
