#!/bin/bash
# Archives current Jarvis session and starts fresh

echo "=== Starting New Session ==="

SESSION_DIR=~/.openclaw/agents/jarvis/sessions
ARCHIVE_DIR=$SESSION_DIR/archive
SESSIONS_JSON=$SESSION_DIR/sessions.json

# 1. Find current session file
SESSION_FILE=$(ls -t $SESSION_DIR/*.jsonl 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ]; then
  echo "No session file found — already clean"
else
  # 2. Archive it
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  mkdir -p $ARCHIVE_DIR
  mv "$SESSION_FILE" "$ARCHIVE_DIR/$(basename $SESSION_FILE .jsonl)_$TIMESTAMP.jsonl"
  echo "Archived: $SESSION_FILE"
fi

# 3. Update sessions.json to remove agent:jarvis:main entry
if [ -f "$SESSIONS_JSON" ]; then
  jq 'del(."agent:jarvis:main")' $SESSIONS_JSON > /tmp/sessions_tmp.json \
  && mv /tmp/sessions_tmp.json $SESSIONS_JSON
  echo "sessions.json updated"
fi

echo "=== Fresh session ready — send a message to start ==="
