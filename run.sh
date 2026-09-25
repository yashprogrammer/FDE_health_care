#!/usr/bin/env bash
# CityCare demo launcher.  Usage: ./run.sh {setup|reset|legacy|poc|warm}
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

build_ui() {
  [ -d "$1/node_modules" ] || (cd "$1" && npm install --silent)
  (cd "$1" && npm run build --silent >/dev/null)
}

case "${1:-}" in
  setup)
    [ -d .venv ] || uv venv -q .venv --python 3.13
    uv pip install -q -r requirements.txt --python $PY
    for ui in legacy_meditrack/ui; do (cd "$ui" && npm install --silent); done
    $PY -m legacy_meditrack.backend.seed
    ;;
  reset)
    $PY -m legacy_meditrack.backend.seed
    rm -f poc/data/feedback.jsonl
    ;;
  legacy)
    [ -f legacy_meditrack/data/meditrack.db ] || $PY -m legacy_meditrack.backend.seed
    build_ui legacy_meditrack/ui
    echo "MediTrack HMS -> http://localhost:8001"
    exec $PY -m uvicorn legacy_meditrack.backend.app:app --port 8001
    ;;
  poc)
    [ -f legacy_meditrack/data/meditrack.db ] || $PY -m legacy_meditrack.backend.seed
    [ -f poc/data/deidentified_encounters.json ] || $PY -m poc.export_deidentified
    echo "Discharge Copilot POC -> http://localhost:8501"
    exec $PY -m streamlit run poc/app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
    ;;
  warm)
    # pre-generate live LLM drafts for every patient so the demo has an offline fallback
    $PY -m scripts.warm_cache
    ;;
  *)
    echo "Usage: ./run.sh {setup|reset|legacy|poc|warm}"; exit 1 ;;
esac
