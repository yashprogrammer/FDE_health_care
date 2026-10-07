"""Demo reset: hospital IT's DB setup (roles, schemas, grants), reseed MediTrack, clear the Copilot's drafts.

Locally it runs in docker compose's "init" service; in Azure it is the reset Container Apps Job.
  python -m scripts.reset            full reset
  python -m scripts.reset --if-empty only seed when MediTrack has no data yet (first start)
  (any other argument, e.g. --full, is ignored: full reset; RESET_IF_EMPTY=1 = --if-empty, used by the Azure job)
"""
import os
import sys

import psycopg

from copilot import bootstrap as copilot_bootstrap
from copilot.service import store as copilot_store
from legacy_meditrack.backend import bootstrap as meditrack_bootstrap
from legacy_meditrack.backend.db import connect_once
from legacy_meditrack.backend.seed import seed


def has_data() -> bool:
    try:
        with connect_once() as c:
            return c.execute("SELECT COUNT(*) AS N FROM IP_ADM_DTL").fetchone()["N"] > 0
    except psycopg.Error:
        return False


def main() -> None:
    meditrack_bootstrap.main()
    copilot_bootstrap.main()
    if_empty = "--if-empty" in sys.argv or os.getenv("RESET_IF_EMPTY") == "1"
    if if_empty and has_data():
        print("MediTrack already has data - keeping it (use ./run.sh reset to start over)")
        copilot_store.init()
        return
    seed()
    copilot_store.reset()
    print("Demo state reset: MediTrack reseeded, Copilot drafts cleared, AI tab link removed")


if __name__ == "__main__":
    main()
