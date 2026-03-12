# Gateway Integration Guide

## Files Created

### 1. enforcement.json
Location: `workspace/governance/enforcement.json`

Contains the allow-list permissions for each role:
- **jarvis**: read, memory_*, sessions_*, message, tts (no write/edit/exec)
- **alex**: read, write, edit, exec, memory_* (no sessions_spawn)
- **scout**: read, exec, session_status, sessions_list

Currently in **shadow mode** (`enabled: false`) — violations are logged but not blocked.

### 2. enforcement.js
Location: `workspace/governance/enforcement.js`

The enforcement module that intercepts tool calls.

## Integration Steps

### Option A: Direct Integration (Recommended)

Add to Gateway source at the tool execution intercept point:

```javascript
const governance = require('./workspace/governance/enforcement.js')

// Before tool execution
function executeTool(agentId, toolName, args) {
  const result = governance.enforceToolCall(agentId, toolName)
  
  if (!result.allowed) {
    return { ok: false, error: result.reason }
  }
  
  // Continue with tool execution...
}
```

### Option B: Runtime Injection

The Gateway can load the module dynamically via WORKSPACE environment variable:

```bash
export WORKSPACE=/Users/raitsai/.openclaw/workspace
openclaw gateway start
```

The enforcement.js will automatically load from `$WORKSPACE/governance/enforcement.json`.

## Enabling Enforcement

To switch from shadow mode to enforcement:

```json
{
  "enabled": true
}
```

Or reload at runtime (if Gateway supports config hot-reload).

## Testing

Test in current session:

```bash
# Try a denied tool - should show SHADOW log
# Check Gateway logs for [governance] SHADOW entries
```

## Verification

Current state:
- ✅ enforcement.json created with correct allow-lists
- ✅ shadow mode enabled (violations logged, not blocked)
- ✅ enforcement.js module ready for integration
- ⚠️ Gateway integration pending
