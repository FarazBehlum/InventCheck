#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
if [[ ! -x backend/.venv/bin/python || ! -d frontend/node_modules ]]; then
  echo 'Install dependencies first; see README.md.' >&2
  exit 1
fi
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &
backend_pid=$!
frontend_pid=''
cleanup() {
  kill "$backend_pid" 2>/dev/null || true
  if [[ -n "$frontend_pid" ]]; then kill "$frontend_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
for attempt in {1..30}; do
  if ! kill -0 "$backend_pid" 2>/dev/null; then
    echo 'Backend could not start. Check the error above and whether port 8000 is occupied.' >&2
    exit 1
  fi
  if curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1; then break; fi
  sleep 1
done
if ! curl -fsS http://127.0.0.1:8000/api/health >/dev/null; then
  echo 'Backend did not become ready within 30 seconds.' >&2
  exit 1
fi
cd frontend
node node_modules/vite/bin/vite.js --host 127.0.0.1 &
frontend_pid=$!
echo 'InventCheck: http://127.0.0.1:5173 — press Ctrl+C to stop.'
wait "$frontend_pid"
