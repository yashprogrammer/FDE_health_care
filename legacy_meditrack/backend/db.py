import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "meditrack.db"
DOCS_DIR = DATA_DIR / "documents"
HOTFOLDER = DATA_DIR / "import_hotfolder"
SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def rows(conn: sqlite3.Connection, sql: str, *args) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def row(conn: sqlite3.Connection, sql: str, *args) -> dict | None:
    r = conn.execute(sql, args).fetchone()
    return dict(r) if r else None


def audit(conn: sqlite3.Connection, usr: str, actn: str, ref: str) -> None:
    conn.execute("INSERT INTO SYS_AUDIT (TS, USR, ACTN, REF) VALUES (?,?,?,?)", (now(), usr, actn, ref))
