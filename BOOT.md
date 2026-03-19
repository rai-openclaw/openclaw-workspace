# Boot Sequence

This file runs automatically on every gateway startup via the boot-md hook.

## Step 1 — Load Governance

Read ~/.openclaw/workspace/governance/RUNTIME.md fully before doing anything else. Confirm understanding of: AEF levels, Alex/Scout loop, agentId spawn requirement, atomic commit rule.

## Step 2 — Check Learnings

Read ~/.openclaw/workspace/.learnings/ERRORS.md Report any items with Status: pending and Priority: high or critical.

## Step 3 — Load Memory

Read today's memory file from ~/.openclaw/workspace/memory/ Summarize what was worked on most recently.

## Step 4 — Git Status

Run git status on both repos:
- ~/.openclaw/workspace
- ~/.openclaw/workspace/mission-control-next

Report any uncommitted changes before accepting any new tasks.

## Step 5 — Ready

Report: "Boot sequence complete. Governance loaded. Ready for tasks."
