#!/bin/sh
# azd postdeploy hook: point the reset job at the image just deployed, seed the database if it is empty,
# and print the URLs.
set -e
val() { azd env get-value "$1" 2>/dev/null || true; }
IMAGE=$(val SERVICE_MEDITRACK_IMAGE_NAME)
if [ -n "$IMAGE" ]; then
  IMAGE="$IMAGE" sh "$(dirname "$0")/reset.sh" if-empty
fi
echo ""
echo "MediTrack HMS   $(val MEDITRACK_URL)    (user: citycare, password: $(val DEMO_PASSWORD))"
echo "Cloud POC       $(val POC_URL)    (password: $(val DEMO_PASSWORD))"
echo "AI tab External Link URL:  /copilot/#/embed/review/{IP_NO}   Display: Patient file tab"
