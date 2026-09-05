#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

MODE="${1:-live}"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

case "$MODE" in
  live)
    APP="ficopilot.api.live:create_live_app"
    ;;
  live-search)
    APP="ficopilot.api.live_search:create_live_search_app"
    ;;
  demo)
    APP="ficopilot.api.demo:create_demo_app"
    ;;
  *)
    echo "Usage: ./start.sh [live|live-search|demo]" >&2
    exit 1
    ;;
esac

if [[ ! -d frontend/node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm --prefix frontend install
fi

API_PID=""
FE_PID=""

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$API_PID" ]]; then
    kill "$API_PID" 2>/dev/null || true
  fi
  if [[ -n "$FE_PID" ]]; then
    kill "$FE_PID" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Mode:     $MODE"
echo "API:      http://${API_HOST}:${API_PORT}"
echo "Frontend: http://${FRONTEND_HOST}:${FRONTEND_PORT}"
echo "Press Ctrl+C to stop."

uv run uvicorn "$APP" --factory --reload --host "$API_HOST" --port "$API_PORT" &
API_PID=$!

health_url="http://${API_HOST}:${API_PORT}/health"
echo "Waiting for API at ${health_url}..."
api_ready=0
for _ in $(seq 1 60); do
  if curl -sf "$health_url" >/dev/null; then
    api_ready=1
    break
  fi
  if ! kill -0 "$API_PID" 2>/dev/null; then
    echo "API process exited before becoming ready." >&2
    exit 1
  fi
  sleep 0.5
done

if [[ "$api_ready" -ne 1 ]]; then
  echo "API did not become ready within 30s. Is port ${API_PORT} free, and is .env configured for mode '${MODE}'?" >&2
  exit 1
fi

echo "API is ready. Starting frontend..."

npm --prefix frontend run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" &
FE_PID=$!

wait
