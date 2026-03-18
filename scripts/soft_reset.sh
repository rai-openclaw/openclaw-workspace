#!/bin/bash
# Soft Reset Script - Graceful session cleanup and gateway restart

echo "=== Soft Reset Starting ==="

# 1. Commit and push workspace
cd /Users/raitsai/.openclaw/workspace
git add -A
git diff --cached --quiet || git commit -m "[System] Soft reset checkpoint"
git push origin dev 2>/dev/null || echo "Nothing to push (workspace)"

# 2. Commit and push mission-control-next
cd /Users/raitsai/.openclaw/workspace/mission-control-next
git add -A
git diff --cached --quiet || git commit -m "[System] Soft reset checkpoint"
git push origin dev 2>/dev/null || echo "Nothing to push (mission-control-next)"

# 3. Run new session
echo "🔄 Starting fresh session..."
bash ~/.openclaw/workspace/scripts/new_session.sh

echo "=== Soft Reset Complete ==="
echo "Start a fresh conversation to continue."