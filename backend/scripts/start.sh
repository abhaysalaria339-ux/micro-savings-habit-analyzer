#!/usr/bin/env sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"
UVICORN_LOG_LEVEL="${UVICORN_LOG_LEVEL:-info}"

exec python -m uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WEB_CONCURRENCY" \
    --log-level "$UVICORN_LOG_LEVEL"
