#!/bin/bash
# Production server on port 8080

cd "$(dirname "$0")"
./mc.sh restart
echo "Production server: http://localhost:8080"
