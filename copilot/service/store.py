"""The Copilot's OWN database (drafts + audit). Separate from MediTrack by design."""
import sqlite3
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DB = DATA / "copilot.db"
REPLICA = DATA / "replica.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS draft (
    ip_no TEXT PRIMARY KEY, status TEXT, advised_at TEXT, ready_at TEXT, signed_at TEXT, signed_by TEXT,
    source TEXT, model TEXT, latency_ms INT, input_tokens INT, output_tokens INT, cost_usd REAL,
    draft_json TEXT, edited_json TEXT, edit_pct REAL, tpa_score_at_sign INT, trace_flags INT, pdf_file TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS event (
    id INTEGER PRIMARY KEY, ts TEXT, ip_no TEXT, actor TEXT, action TEXT, detail TEXT
);
"""


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def db() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def replica() -> sqlite3.Connection:
    c = sqlite3.connect(f"file:{REPLICA}?mode=ro", uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def event(ip_no: str, actor: str, action: str, detail: str = "") -> None:
    with db() as c:
        c.execute("INSERT INTO event (ts, ip_no, actor, action, detail) VALUES (?,?,?,?,?)",
                  (now(), ip_no, actor, action, detail))
