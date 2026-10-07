"""Container entrypoint: one image, the role is chosen by APP_ROLE (meditrack | copilot | reset)."""
import os
import sys

ROLES = {
    "meditrack": ["uvicorn", "legacy_meditrack.backend.app:app", "--host", "0.0.0.0", "--port", "8001"],
    "copilot": ["uvicorn", "copilot.service.app:app", "--host", "0.0.0.0", "--port", "8002"],
    "reset": [sys.executable, "-m", "scripts.reset"],
}

role = os.getenv("APP_ROLE", "")
if role not in ROLES:
    sys.exit(f"APP_ROLE must be one of {', '.join(ROLES)} (got {role!r})")
cmd = ROLES[role] + sys.argv[1:]
os.execvp(cmd[0], cmd)
