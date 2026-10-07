#!/bin/sh
# azd preprovision hook: fill in passwords, and look up how gpt-oss-20b is offered in the Foundry region
# (model format / version / SKU), so the Bicep model deployment matches what Azure actually offers.
set -e
val() { azd env get-value "$1" 2>/dev/null || true; }

if [ -z "$(val PG_ADMIN_PASSWORD)" ]; then
  azd env set PG_ADMIN_PASSWORD "Pg$(openssl rand -hex 16)" >/dev/null
  echo "Generated PG_ADMIN_PASSWORD (stored in .azure/<env>/.env)"
fi
if [ -z "$(val DEMO_PASSWORD)" ]; then
  pw="citycare-$(openssl rand -hex 3)"
  azd env set DEMO_PASSWORD "$pw" >/dev/null
  echo "Generated DEMO_PASSWORD: $pw   (MediTrack login user: citycare; also the cloud POC password)"
fi

LOC=$(val FOUNDRY_LOCATION); [ -n "$LOC" ] || LOC=$(val AZURE_LOCATION); [ -n "$LOC" ] || LOC=centralindia
MODEL=$(val FOUNDRY_MODEL_NAME); [ -n "$MODEL" ] || MODEL=gpt-oss-20b

if ! command -v az >/dev/null 2>&1 || ! az account show >/dev/null 2>&1; then
  echo "WARNING: Azure CLI missing or not logged in (az login) - skipping the Foundry model check, using defaults."
  exit 0
fi

latest="sort_by([?model.name=='$MODEL'], &model.version) | [-1].model"
FORMAT=$(az cognitiveservices model list -l "$LOC" --query "$latest.format" -o tsv 2>/dev/null || true)
if [ -z "$FORMAT" ]; then
  echo "ERROR: $MODEL is not offered to this subscription in region '$LOC' (Azure AI Foundry)."
  echo "       Find a region that has it (Foundry portal > Model catalog > $MODEL > Deploy), then:"
  echo "         azd env set FOUNDRY_LOCATION <region>     # e.g. eastus2 or swedencentral; the apps stay in $(val AZURE_LOCATION)"
  exit 1
fi
VERSION=$(az cognitiveservices model list -l "$LOC" --query "$latest.version" -o tsv)
SKUS=$(az cognitiveservices model list -l "$LOC" --query "$latest.skus[].name" -o tsv)
SKU=$(echo "$SKUS" | grep -x GlobalStandard || echo "$SKUS" | grep -x DataZoneStandard || echo "$SKUS" | head -n1)

azd env set FOUNDRY_MODEL_FORMAT "$FORMAT" >/dev/null
azd env set FOUNDRY_MODEL_VERSION "$VERSION" >/dev/null
azd env set FOUNDRY_SKU "$SKU" >/dev/null
echo "Foundry: $MODEL (format $FORMAT, version $VERSION, sku $SKU) in $LOC"
