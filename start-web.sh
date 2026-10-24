#!/bin/sh
set -eu
# Free web-host deployment: run public-data shadow scanner alongside the read-only dashboard.
# Trading remains disabled. Ephemeral files may be lost when the host restarts or sleeps.
python -m shadow.worker &
WORKER_PID=$!
shutdown() {
  kill -TERM "$WORKER_PID" 2>/dev/null || true
  wait "$WORKER_PID" 2>/dev/null || true
}
trap shutdown TERM INT
uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8080}" &
API_PID=$!
wait "$API_PID"
