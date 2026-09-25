"""Logfire tracing for Pydantic AI. Sends to Logfire only if LOGFIRE_TOKEN is set; otherwise stays silent."""
import os

import logfire

from . import config  # noqa: F401  (loads .env)

_done = False


def setup(service_name: str) -> bool:
    global _done
    if not _done:
        logfire.configure(service_name=service_name, send_to_logfire="if-token-present", console=False,
                          scrubbing=False)  # synthetic data only; real deployments keep scrubbing on
        logfire.instrument_pydantic_ai()
        _done = True
    return bool(os.getenv("LOGFIRE_TOKEN"))
