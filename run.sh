#!/usr/bin/env bash
# CityCare demo launcher.
#
# Local (docker compose - same images as Azure):
#   ./run.sh legacy        MediTrack only (Postgres + MediTrack + gateway)      -> http://localhost:8001
#   ./run.sh integrated    + Discharge Copilot (AI tab at /copilot/)             -> http://localhost:8001
#   ./run.sh reset         reseed MediTrack, clear Copilot drafts, remove the AI tab link
#   ./run.sh down          stop the local stack (data is kept; `down -v` style wipe: ./run.sh wipe)
# Local POC (Python venv, Groq):
#   ./run.sh setup         one-time: Python venv + npm packages
#   ./run.sh poc           Streamlit POC                                        -> http://localhost:8501
#   ./run.sh poc-export    re-export the de-identified encounters (needs the local stack running)
#   ./run.sh warm          refresh the cached fallback drafts with live Groq calls (needs the local stack)
#   ./run.sh eval          run the eval from the command line (Groq)
# Azure (azd + Bicep; see DEMO_RUNBOOK.md):
#   ./run.sh cloud-up      provision + deploy everything (hospital RG + POC RG), then reset the demo data
#   ./run.sh cloud-reset   run the reset job (reseed MediTrack, clear drafts)
#   ./run.sh cloud-urls    print the MediTrack and cloud POC URLs
#   ./run.sh eval-foundry  run the eval against the Azure AI Foundry deployment
#   ./run.sh cloud-down    delete all Azure resources (azd down --purge)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

azd_env() { azd env get-value "$1" 2>/dev/null; }

case "${1:-}" in
  setup)
    [ -d .venv ] || uv venv -q .venv --python 3.13
    uv pip install -q -r requirements.txt --python $PY
    for ui in legacy_meditrack/ui copilot/ui; do (cd "$ui" && npm install --silent); done
    ;;
  legacy)
    echo "MediTrack HMS -> http://localhost:${MEDITRACK_PORT:-8001}"
    exec docker compose up --build db init meditrack gateway
    ;;
  integrated)
    echo "MediTrack HMS (+ AI Discharge Draft tab) -> http://localhost:${MEDITRACK_PORT:-8001}"
    exec docker compose up --build
    ;;
  reset)
    docker compose run --rm --build init --full
    rm -f poc/data/feedback.jsonl
    ;;
  down)
    docker compose down
    ;;
  wipe)
    docker compose down -v
    rm -rf legacy_meditrack/data copilot/data
    ;;
  poc)
    echo "Discharge Copilot POC (local sandbox) -> http://localhost:8501"
    exec $PY -m streamlit run poc/app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
    ;;
  poc-export)
    $PY -m poc.export_deidentified
    ;;
  warm)
    # pre-generate live LLM drafts for every patient so the demo has an offline fallback
    $PY -m scripts.warm_cache
    ;;
  eval)
    $PY -m scripts.run_eval
    ;;
  eval-foundry)
    COPILOT_PROVIDER=foundry FOUNDRY_ENDPOINT="$(azd_env FOUNDRY_ENDPOINT)" FOUNDRY_DEPLOYMENT="$(azd_env FOUNDRY_DEPLOYMENT)" \
      FOUNDRY_API_KEY="$(az cognitiveservices account keys list -g "$(azd_env AZURE_RESOURCE_GROUP)" -n "$(azd_env FOUNDRY_ACCOUNT_NAME)" --query key1 -o tsv)" \
      $PY -m scripts.run_eval
    ;;
  cloud-up)
    azd up
    ;;
  cloud-reset)
    ./infra/hooks/reset.sh
    ;;
  cloud-urls)
    echo "MediTrack HMS (hospital RG) -> $(azd_env MEDITRACK_URL)   user: citycare"
    echo "Copilot POC   (POC RG)      -> $(azd_env POC_URL)"
    ;;
  cloud-down)
    azd down --purge --force
    ;;
  *)
    sed -n '2,25p' "$0"; exit 1 ;;
esac
