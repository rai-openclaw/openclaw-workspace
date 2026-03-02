#!/bin/bash

PIDFILE="server.pid"
LOGFILE="server.log"
PORT=8080

case "$1" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "Server already running (PID: $(cat $PIDFILE))"
      exit 1
    fi
    
    echo "Starting server on port $PORT..."
    python3 -B server.py > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    
    sleep 3
    if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "✅ Server running (PID: $(cat $PIDFILE))"
      echo "Dashboard: http://localhost:$PORT"
    else
      echo "❌ Failed to start"
      rm -f "$PIDFILE"
      exit 1
    fi
    ;;
    
  stop)
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill -TERM "$PID" 2>/dev/null
        sleep 2
        if kill -0 "$PID" 2>/dev/null; then
          echo "Force killing..."
          kill -9 "$PID" 2>/dev/null
        fi
        echo "✅ Stopped"
      else
        echo "Server not running (stale PID file)"
      fi
      rm -f "$PIDFILE"
    else
      echo "No PID file found"
    fi
    ;;
    
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "✅ Server running (PID: $(cat $PIDFILE))"
      echo "Dashboard: http://localhost:$PORT"
    else
      echo "❌ Server not running"
      rm -f "$PIDFILE" 2>/dev/null
    fi
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
