# TDS: Editable Ideas Pipeline

## Overview
Add edit capabilities to Ideas Pipeline - change status from UI, delete ideas, inline editing.

**Status:** Draft
**Scope:** Ideas tab in Mission Control dashboard
**Approach:** API endpoints + UI controls

---

## Requirements

### Functional Requirements
1. **Change Status from UI** - Dropdown on each idea card to move between columns
2. **Delete Idea** - Delete button with confirmation dialog
3. **Inline Edit** - Click to edit title/description (optional v2)
4. **Auto-save** - Changes persist to JSON file immediately

### UI Design (Kanban Board)
Each idea card gets an "Actions" dropdown:
```
┌─────────────────────────┐
│ AI-Powered Trade Journal│
│ 💼 Trading | 💬 Discussing│
│                         │
│ [Actions ▼]            │
└─────────────────────────┘
```

Dropdown menu:
- Move to: Backlog
- Move to: Discussing  
- Move to: Approved
- Move to: In Progress
- Move to: Done
- ────────────────
- ✏️ Edit (v2)
- 🗑️ Delete...

Delete confirmation:
"Delete 'AI-Powered Trade Journal'? This cannot be undone."
[Cancel] [Delete]

---

## Data Architecture

### API Endpoints

**POST /api/idea-update**
```json
{
  "idea_id": "idea-001",
  "updates": {
    "status": "approved",
    "priority": "high"
  }
}
```
Response: `{"success": true, "idea": {...}}`

**POST /api/idea-delete**
```json
{
  "idea_id": "idea-001"
}
```
Response: `{"success": true, "deleted_id": "idea-001"}`

### Backend Logic

**Update Endpoint:**
1. Read ideas.json
2. Find idea by ID
3. Apply updates
4. Update last_updated timestamp
5. Save to file
6. Return updated idea

**Delete Endpoint:**
1. Read ideas.json
2. Find idea by ID
3. Remove from array
4. Save to file
5. Return success

**Safety:**
- Backup ideas.json before any write operation
- Validate idea_id exists before update/delete
- Prevent deleting if idea is "in_progress" (warn user)

---

## Implementation

### Phase 1: Backend (Alex)
1. Add `/api/idea-update` endpoint to server.py
2. Add `/api/idea-delete` endpoint to server.py
3. Both endpoints modify portfolio/data/ideas.json
4. Add validation and error handling

### Phase 2: Frontend (Alex)
1. Add "Actions" dropdown to each idea card in Kanban
2. Add JavaScript functions:
   - `updateIdeaStatus(ideaId, newStatus)`
   - `deleteIdea(ideaId)`
3. Add confirmation dialog for delete
4. Refresh Kanban after successful operation
5. Show success/error toast messages

### UI Components

**Actions Dropdown:**
```html
<select onchange="handleAction(this, 'idea-001')">
  <option>Actions...</option>
  <option value="backlog">→ Move to Backlog</option>
  <option value="discussing">→ Move to Discussing</option>
  <option value="approved">→ Move to Approved</option>
  <option value="in_progress">→ Move to In Progress</option>
  <option value="done">→ Move to Done</option>
  <option disabled>──────────</option>
  <option value="delete">🗑️ Delete...</option>
</select>
```

**Confirmation Modal:**
```html
<div class="modal" id="delete-modal">
  <div class="modal-content">
    <h3>Delete Idea?</h3>
    <p>Are you sure you want to delete "<span id="delete-idea-title"></span>"?</p>
    <button onclick="closeModal()">Cancel</button>
    <button onclick="confirmDelete()" style="background:red;">Delete</button>
  </div>
</div>
```

---

## Files to Modify

**Backend:**
- `mission_control/server.py` - Add 2 new endpoints

**Frontend:**
- `mission_control/templates/dashboard.html` - Add Actions dropdown to idea cards
- Add JavaScript functions for update/delete
- Add modal for confirmation

---

## Testing Checklist

- [ ] Can change idea status from dropdown
- [ ] Kanban updates immediately after status change
- [ ] Can delete idea with confirmation
- [ ] Deleted idea disappears from board
- [ ] Changes persist after refresh
- [ ] JSON file updated correctly
- [ ] Error handling works (invalid ID, etc.)

---

## Notes

**Why not inline editing yet?**
- Status change and delete are 80% of use cases
- Inline editing adds complexity (focus management, validation)
- Can add in v2 if needed

**Security:**
- No auth needed (local usage only)
- But validate all inputs
- Backup before destructive operations

---

## Approval

**Review TDS. Say "proceed" for Alex to implement.**
