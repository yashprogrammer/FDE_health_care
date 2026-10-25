#!/bin/sh
# azd postdeploy hook: point the reset job at the image just deployed, seed the database if it is empty,
# and print the URLs.
set -e
val() { azd env get-values 2>/dev/null | sed -n -E "s/^$1=//p" | head -n1 | sed -E 's/^"(.*)"$/\1/'; }
# the model deployment now exists: later `azd up` runs must not re-PUT it (Foundry throttles repeats: 715-123420)
azd env set FOUNDRY_MODEL_EXISTS true >/dev/null
IMAGE=$(val SERVICE_MEDITRACK_IMAGE_NAME)
if [ -n "$IMAGE" ]; then
  IMAGE="$IMAGE" sh "$(dirname "$0")/reset.sh" if-empty
fi
echo ""
echo "MediTrack HMS   $(val MEDITRACK_URL)    (user: citycare, password: $(val DEMO_PASSWORD))"
echo "Cloud POC       $(val POC_URL)    (password: $(val DEMO_PASSWORD))"
echo "AI tab External Link URL:  /copilot/#/embed/review/{IP_NO}   Display: Patient file tab"
