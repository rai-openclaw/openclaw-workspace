#!/bin/bash

# Mission Control Server Manager
# Usage: ./mc.sh {start|stop|restart|status}

PORT=8080
PIDFILE=".server.pid"

case "$1" in
  start)
    # Check if already running
    if [ -f "$PIDFILE" ]; then
      OLD_PID=$(cat "$PIDFILE")
      if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Server already running (PID: $OLD_PID)"
        exit 1
      fi
    fi
    
    # Check port is free
    python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', $PORT))
sock.close()
exit(0 if result != 0 else 1)
" || {
      echo "Port $PORT is in use. Run: ./mc.sh stop"
      exit 1
    }
    
    # Start server with gunicorn
    echo "Starting Mission Control on port $PORT..."
    /Users/raitsai/Library/Python/3.9/bin/gunicorn -w 2 -b 0.0.0.0:$PORT server:app > server.log 2>&1 &
    echo $! > "$PIDFILE"
    
    sleep 3
    if curl -s http://localhost:$PORT/api/portfolio > /dev/null; then
      echo "✅ Server ready: http://localhost:$PORT"
    else
      echo "❌ Server failed to start"
      rm -f "$PIDFILE"
      exit 1
    fi
    ;;
    
  stop)
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 2
        kill -9 "$PID" 2>/dev/null
      fi
      rm -f "$PIDFILE"
      echo "✅ Stopped"
    else
      # Try to find and kill any gunicorn process on our port
      pkill -f "gunicorn.*server:app" 2>/dev/null
      echo "✅ Stopped (via process name)"
    fi
    ;;
    
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    if [ -f "$PIDFILE" ]; then
      PID=$(cat "$PIDFILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "✅ Running (PID: $PID)"
        echo "   http://localhost:$PORT"
      else
        echo "❌ Not running (stale PID file)"
        rm -f "$PIDFILE"
      fi
    else
      echo "❌ Not running"
    fi
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
