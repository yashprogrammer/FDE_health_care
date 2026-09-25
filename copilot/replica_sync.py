"""Simulates CityCare IT's MIS reporting replica: copies MediTrack's DB every few seconds.

In the hospital this is Oracle Data Guard owned by IT. The Copilot only ever READS the replica,
never MediTrack's primary database.
"""
import os
import sqlite3
import time
from pathlib import Path

from legacy_meditrack.backend.db import DB_PATH

REPLICA = Path(__file__).resolve().parent / "data" / "replica.db"
INTERVAL_S = 3


def sync_once() -> None:
    REPLICA.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPLICA.with_suffix(".tmp")
    src = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    dst = sqlite3.connect(tmp)
    src.backup(dst)
    dst.close()
    src.close()
    os.replace(tmp, REPLICA)   # atomic swap: readers never see a half-written replica


if __name__ == "__main__":
    print(f"[replica-sync] {DB_PATH.name} -> {REPLICA} every {INTERVAL_S}s")
    while True:
        try:
            sync_once()
        except Exception as e:
            print(f"[replica-sync] {e}")
        time.sleep(INTERVAL_S)
