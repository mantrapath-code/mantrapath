#!/usr/bin/env bash
set -euo pipefail

: "${TRANSLATION_PORT:=8010}"
: "${TRANSLATION_GRPC_PORT:=9010}"

echo "Starting Translation Service HTTP on :${TRANSLATION_PORT} and gRPC on :${TRANSLATION_GRPC_PORT}"

# Start HTTP (FastAPI) in background
python -m uvicorn main:app --host 0.0.0.0 --port "${TRANSLATION_PORT}" &
HTTP_PID=$!

# Start gRPC server (foreground)
python grpc_server.py &
GRPC_PID=$!

trap 'echo "Stopping..."; kill ${HTTP_PID} ${GRPC_PID} 2>/dev/null || true; wait' SIGINT SIGTERM

wait ${HTTP_PID} ${GRPC_PID}
