#!/bin/bash
PORT=8080
PIDFILE=/tmp/mission_control.pid

case "$1" in
    start)
        if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
            echo "Server already running on port $PORT (PID: $(cat $PIDFILE))"
            exit 0
        fi
        cd "$(dirname "$0")"
        
        # Use gunicorn for proper process management
        GUNICORN="/Users/raitsai/Library/Python/3.9/bin/gunicorn"
        $GUNICORN -w 2 -b 0.0.0.0:$PORT \
            --pid "$PIDFILE" \
            --daemon \
            --access-logfile /dev/null \
            --error-logfile /tmp/gunicorn_error.log \
            server:app
        
        sleep 2
        if [ -f "$PIDFILE" ]; then
            echo "✅ Server ready: http://localhost:$PORT (PID: $(cat $PIDFILE))"
        else
            echo "❌ Failed to start server"
            exit 1
        fi
        ;;
    stop)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            # Gunicorn handles SIGTERM gracefully - kills all workers
            kill $PID 2>/dev/null
            sleep 1
            # Force kill if still running
            kill -9 $PID 2>/dev/null
            rm -f "$PIDFILE"
            echo "✅ Stopped"
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
            echo "✅ Running on port $PORT (PID: $(cat $PIDFILE))"
        else
            echo "❌ Not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
