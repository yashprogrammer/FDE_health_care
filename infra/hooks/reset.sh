#!/bin/sh
# Run the Azure reset job and wait for it.
#   reset.sh            full reset: reseed MediTrack, clear Copilot drafts, remove the AI tab link
#   reset.sh if-empty   only seed when MediTrack has no data yet (used after every deploy)
#   IMAGE=<image> ...   also point the job at this image first
set -e
val() { azd env get-value "$1" 2>/dev/null || true; }
RG=$(val AZURE_RESOURCE_GROUP)
JOB=$(val RESET_JOB_NAME)
[ -n "$RG" ] && [ -n "$JOB" ] || { echo "No azd environment with a reset job - run ./run.sh cloud-up first"; exit 1; }
MODE=0; [ "${1:-}" = "if-empty" ] && MODE=1

az extension add --name containerapp --upgrade --yes >/dev/null 2>&1 || true
if [ -n "${IMAGE:-}" ]; then
  az containerapp job update -n "$JOB" -g "$RG" --image "$IMAGE" --set-env-vars RESET_IF_EMPTY=$MODE -o none
else
  az containerapp job update -n "$JOB" -g "$RG" --set-env-vars RESET_IF_EMPTY=$MODE -o none
fi
EXEC=$(az containerapp job start -n "$JOB" -g "$RG" --query name -o tsv)
printf "Reset job %s started" "$EXEC"
while :; do
  STATUS=$(az containerapp job execution show -n "$JOB" -g "$RG" --job-execution-name "$EXEC" --query properties.status -o tsv)
  case "$STATUS" in
    Succeeded) echo " - done"; break ;;
    Failed|Stopped|Degraded)
      echo " - $STATUS. Logs: az containerapp job logs show -n $JOB -g $RG --execution $EXEC --container reset"; exit 1 ;;
    *) printf "."; sleep 5 ;;
  esac
done
