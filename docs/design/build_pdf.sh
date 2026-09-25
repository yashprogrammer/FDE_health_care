#!/usr/bin/env bash
# Render the HLD/LLD (HTML + Mermaid) to PDF with headless Chrome.
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules/mermaid ] || npm install --silent
OUT="../CityCare_Discharge_Copilot_HLD_LLD.pdf"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --allow-file-access-from-files --virtual-time-budget=30000 \
  --print-to-pdf="$OUT" "file://$PWD/hld_lld.html" 2>/dev/null
echo "PDF -> $(cd .. && pwd)/CityCare_Discharge_Copilot_HLD_LLD.pdf"
