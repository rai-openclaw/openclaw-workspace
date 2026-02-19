# Technical Design Spec: Replace Flask Dev Server with Gunicorn

**Version:** 1.0  
**Date:** 2026-02-15  
**Status:** Complete

---

## Goal
Replace Flask's development server with gunicorn WSGI server to eliminate zombie processes and enable proper process management.

---

## Problem Statement
- Flask dev server (`app.run()`) creates orphaned child processes
- `kill -9` kills parent but leaves children holding port 8080
- Launchd cannot properly manage Flask dev server lifecycle
- Port conflicts require manual intervention (violated Stop and Ask trigger 5+ times today)

---

## Affected Files

| File | Path | Changes |
|------|------|---------|
| requirements.txt | `~/.openclaw/workspace/mission_control/requirements.txt` | Add gunicorn |
| mc.sh | `~/.openclaw/workspace/mission_control/mc.sh` | Replace python3 server.py with gunicorn command |
| server.py | `~/.openclaw/workspace/mission_control/server.py` | No changes (gunicorn imports app) |
| launchd plist | `~/Library/LaunchAgents/com.openclaw.missioncontrol.plist` | Update ProgramArguments to use gunicorn |

**Estimated Scope:** 5-10 lines across 3 files

---

## API/Contract Changes

**No API changes.** This is infrastructure only.

- All `/api/*` endpoints remain identical
- No request/response schema changes
- No frontend changes required

---

## Solution: Gunicorn WSGI Server

Gunicorn (Green Unicorn) is a production-grade WSGI server with:
- Proper worker process management
- Clean shutdown kills all workers
- Master process monitors workers
- Automatic worker respawning
- Signal handling for graceful shutdown

### Command Structure
```bash
gunicorn -w 2 -b 0.0.0.0:8080 server:app
```

- `-w 2`: 2 worker processes (can adjust based on load)
- `-b 0.0.0.0:8080`: Bind to all interfaces on port 8080
- `server:app`: Import app from server.py

---

## Step-by-Step Implementation

### Step 1: Add gunicorn to requirements.txt
**File:** `requirements.txt`  
**Lines to add:** 1  
**Verification:** `cat requirements.txt | grep gunicorn`

### Step 2: Update mc.sh start command
**File:** `mc.sh`  
**Lines to modify:** 1 (in start case)  
**Change:** Replace `python3 -B server.py` with `gunicorn -w 2 -b 0.0.0.0:8080 server:app`  
**Verification:** `./mc.sh start` starts gunicorn, port 8080 responds

### Step 3: Update launchd plist
**File:** `~/Library/LaunchAgents/com.openclaw.missioncontrol.plist`  
**Lines to modify:** 3 (ProgramArguments array)  
**Change:** Replace python3 path with gunicorn path and arguments  
**Verification:** `launchctl load` succeeds, service starts on boot

### Step 4: Test clean shutdown
**Verification:** 
```bash
./mc.sh stop
# Verify no processes on 8080
python3 -c "import socket; print('Port free' if socket.socket().connect_ex(('localhost', 8080)) != 0 else 'Port in use')"
```

### Step 5: Test restart cycle
**Verification:**
```bash
./mc.sh restart
# Verify new process started
curl -s http://localhost:8080/api/portfolio | head -c 50
```

---

## Rollback Strategy

If gunicorn fails:
1. Stop service: `./mc.sh stop`
2. Restore V1.1 baseline: `cp v1.1_backup/* .`
3. Restart: `./mc.sh start`

**Last Known Good:** V1.1 in `v1.1_backup/`

---

## Error Handling

- Gunicorn not installed: pip3 install -r requirements.txt
- Port in use (during transition): Kill remaining zombies manually once
- Permission denied: Check gunicorn binary path

---

## Benefits

1. **No more zombies** - Master process tracks all workers
2. **Clean shutdown** - SIGTERM propagates to all workers
3. **Production ready** - Industry standard WSGI server
4. **Better performance** - Multiple workers handle concurrent requests
5. **Proper logging** - Structured access logs

---

## Verification Checklist

- [ ] gunicorn installed successfully
- [ ] mc.sh uses gunicorn command
- [ ] launchd plist updated
- [ ] Server starts on port 8080
- [ ] All API endpoints respond correctly
- [ ] Stop command kills all processes
- [ ] Restart works without port conflicts
- [ ] No zombie processes after 3 stop/start cycles

---

**Complete command before implementation.**
