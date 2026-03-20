---
name: openclaw-governance
description: "Injects governance and learning reminder during agent bootstrap"
metadata:
  openclaw:
    emoji: "📚"
    events: ["agent:bootstrap"]
---
# OpenClaw Governance Hook

## What It Does
- Fires on agent:bootstrap before workspace files are injected
- Injects GOVERNANCE_REMINDER.md as a virtual bootstrap file into every session
- Reminds Jarvis to load governance, log learnings, and commit before session closes
- Skips subagent sessions automatically

## Requirements
- No configuration needed

## Enable
```
openclaw hooks enable openclaw-governance
```
