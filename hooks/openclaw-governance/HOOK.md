---
name: openclaw-governance
description: "Auto-log tool errors to .learnings/ERRORS.md and trigger learning review on session end"
homepage: https://docs.openclaw.ai/hooks
metadata:
  openclaw:
    emoji: "📚"
    events: ["agent:bootstrap"]
    requires:
      bins: ["node"]
---
# OpenClaw Governance Hook

## What It Does
- `tool_result_persist`: Detects tool failures and auto-writes to `.learnings/ERRORS.md`
- `command:new`: Injects a learning review reminder before session ends

## Requirements
- Node.js must be installed
- `~/.openclaw/workspace/.learnings/` must exist
