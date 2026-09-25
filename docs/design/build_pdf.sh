#!/usr/bin/env bash
# Render the design docs (HTML + Mermaid) to PDF with headless Chrome.
#   hld_lld_simple.html   -> ../CityCare_Discharge_Copilot_HLD_LLD.pdf           (main, easy to read)
#   hld_lld_detailed.html -> ../CityCare_Discharge_Copilot_HLD_LLD_detailed.pdf  (technical reference)
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules/mermaid ] || npm install --silent
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
render() {
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
    --virtual-time-budget=30000 --print-to-pdf="$2" "file://$PWD/$1" 2>/dev/null
  echo "PDF -> $(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
}
render hld_lld_simple.html ../CityCare_Discharge_Copilot_HLD_LLD.pdf
render hld_lld_detailed.html ../CityCare_Discharge_Copilot_HLD_LLD_detailed.pdf
