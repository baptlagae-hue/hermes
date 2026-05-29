#!/bin/bash
# Start both API backend and static frontend server
# uvicorn stays in foreground (systemd tracks it), http-server runs in background
set -a
source /root/.hermes/.env
set +a

cd /root/expertise-transfer-engine

# Start frontend server in background
python3 -m http.server 8011 --bind 127.0.0.1 --directory frontend/dist &
FRONTEND_PID=$!

# Start API server in foreground (systemd will track this PID)
uvicorn backend.main:app --host 127.0.0.1 --port 8010
EXIT_CODE=$?

# When uvicorn stops, kill the frontend server
kill $FRONTEND_PID 2>/dev/null
exit $EXIT_CODE
