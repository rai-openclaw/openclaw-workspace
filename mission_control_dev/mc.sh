#!/bin/bash
PORT=8081
PIDFILE=/tmp/mission_control.pid

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    start)
        if [ -f "$PIDFILE" ]; then
            OLD_PID=$(cat "$PIDFILE")
            if kill -0 $OLD_PID 2>/dev/null; then
                echo "Server already running on port $PORT (PID: $OLD_PID)"
                exit 0
            fi
        fi
        
        # Kill any existing processes on port 8081
        for pid in $(lsof -ti:$PORT 2>/dev/null); do
            kill -9 $pid 2>/dev/null
        done
        
        cd "$SCRIPT_DIR"
        
        # Start Flask server
        python3 server.py $PORT > /tmp/mission_control.log 2>&1 &
        NEW_PID=$!
        echo $NEW_PID > "$PIDFILE"
        
        sleep 3
        
        if kill -0 $NEW_PID 2>/dev/null && curl -s http://localhost:$PORT > /dev/null; then
            echo "✅ Server ready: http://localhost:$PORT (PID: $NEW_PID)"
        else
            echo "❌ Failed to start server"
            rm -f "$PIDFILE"
            exit 1
        fi
        ;;
    stop)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            kill $PID 2>/dev/null
            sleep 1
            kill -9 $PID 2>/dev/null
            rm -f "$PIDFILE"
        fi
        
        # Also kill any python processes on the port
        for pid in $(lsof -ti:$PORT 2>/dev/null); do
            kill -9 $pid 2>/dev/null
        done
        
        echo "✅ Stopped"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 $PID 2>/dev/null && curl -s http://localhost:$PORT > /dev/null; then
                echo "✅ Running on port $PORT (PID: $PID)"
                exit 0
            fi
        fi
        echo "❌ Not running"
        rm -f "$PIDFILE" 2>/dev/null
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
