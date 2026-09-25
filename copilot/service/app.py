"""Discharge Copilot service (Part 3): integrated with MediTrack without changing MediTrack's code.

  read   : MIS reporting replica (read-only)       -> adapter builds Encounter JSON
  entry  : MediTrack "External Links" config        -> opens /#/review/{IP_NO}
  write  : MediTrack batch-import hot-folder (PDF)  -> appears in patient's Documents tab
"""
import difflib
import os
import statistics
import threading
import time
from datetime import datetime
from pathlib import Path

import logfire
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from copilot_core import observability
from copilot_core.agent import generate_draft
from copilot_core.encounter import load_encounter
from copilot_core.models import Encounter, SummaryDraft
from copilot_core.rules import readiness_score, tpa_checklist
from copilot_core.trace import draft_to_text, summarize, trace
from legacy_meditrack.backend.db import HOTFOLDER

from . import pdf
from .store import DATA, REPLICA, db, event, now, replica

UI_DIST = Path(__file__).resolve().parent.parent / "ui" / "dist"
POLL_S = 2
LOGFIRE_URL = os.getenv("LOGFIRE_PROJECT_URL", "https://logfire.pydantic.dev")

app = FastAPI(title="CityCare Discharge Copilot")


# ------------------------------------------------------------------ adapter (background)
def _encounter(ip_no: str) -> Encounter:
    with replica() as r:
        enc = load_encounter(r, ip_no)
    if not enc:
        raise HTTPException(404, f"{ip_no} not in replica")
    return enc


def process_discharge(ip_no: str, advised_at: str) -> None:
    with logfire.span("adapter.process_discharge", ip_no=ip_no):
        enc = _encounter(ip_no)
        res = generate_draft(enc)
        flags = summarize(trace(draft_to_text(res.draft), enc))
        with db() as c:
            c.execute("""UPDATE draft SET status='READY', ready_at=?, source=?, model=?, latency_ms=?, input_tokens=?,
                         output_tokens=?, cost_usd=?, draft_json=?, trace_flags=?, error=? WHERE ip_no=?""",
                      (now(), res.source, res.model, res.latency_ms, res.input_tokens, res.output_tokens, res.cost_usd,
                       res.draft.model_dump_json(), flags["hallucinated"] + flags["unverified"], res.error, ip_no))
        event(ip_no, "copilot", "DRAFT_READY", f"{res.source} draft in {res.latency_ms} ms")


def adapter_loop() -> None:
    """Watch the replica for 'Discharge Advised' patients and draft their summaries."""
    while True:
        try:
            if REPLICA.exists():
                with replica() as r:
                    advised = r.execute("SELECT IP_NO, DSCH_ADV_DT FROM IP_ADM_DTL WHERE STS='DA'").fetchall()
                with db() as c:
                    known = {row[0] for row in c.execute("SELECT ip_no FROM draft")}
                for ip_no, adv in advised:
                    if ip_no in known:
                        continue
                    with db() as c:
                        c.execute("INSERT INTO draft (ip_no, status, advised_at) VALUES (?, 'GENERATING', ?)", (ip_no, adv))
                    event(ip_no, "adapter", "DISCHARGE_ADVISED_DETECTED", f"advised at {adv}")
                    try:
                        process_discharge(ip_no, adv)
                    except Exception as e:
                        with db() as c:
                            c.execute("UPDATE draft SET status='ERROR', error=? WHERE ip_no=?", (str(e)[:300], ip_no))
        except Exception as e:
            print(f"[adapter] {e}")
        time.sleep(POLL_S)


@app.on_event("startup")
def startup():
    observability.setup("discharge-copilot-service")
    DATA.mkdir(parents=True, exist_ok=True)
    db().close()
    threading.Thread(target=adapter_loop, daemon=True).start()


# ------------------------------------------------------------------ API
def _row(ip_no: str) -> dict:
    with db() as c:
        r = c.execute("SELECT * FROM draft WHERE ip_no=?", (ip_no,)).fetchone()
    if not r:
        raise HTTPException(404, "No draft yet - is the patient marked 'Discharge Advised' in MediTrack?")
    return dict(r)


def _current(row: dict) -> SummaryDraft | None:
    raw = row["edited_json"] or row["draft_json"]
    return SummaryDraft.model_validate_json(raw) if raw else None


@app.get("/api/drafts")
def list_drafts():
    with db() as c:
        drafts = [dict(r) for r in c.execute("SELECT ip_no, status, advised_at, ready_at, signed_at, signed_by, source, "
                                             "latency_ms, edit_pct FROM draft ORDER BY advised_at DESC")]
    if REPLICA.exists():
        with replica() as r:
            for d in drafts:
                p = r.execute("""SELECT p.PT_NM, p.PT_AGE, p.PT_SEX, a.WRD_CD, a.BED_NO, a.PAY_MODE, a.TPA_NM, dr.DR_NM
                                 FROM IP_ADM_DTL a JOIN PT_MST p ON p.PT_ID=a.PT_ID JOIN DR_MST dr ON dr.DR_ID=a.DR_ID
                                 WHERE a.IP_NO=?""", (d["ip_no"],)).fetchone()
                d.update(dict(p) if p else {})
    return drafts


@app.get("/api/drafts/{ip_no}")
def get_draft(ip_no: str):
    row = _row(ip_no)
    enc = _encounter(ip_no)
    cur = _current(row)
    checks = tpa_checklist(enc)
    findings = trace(draft_to_text(cur), enc) if cur else []
    return {
        "meta": {k: v for k, v in row.items() if k not in ("draft_json", "edited_json")},
        "encounter": enc.model_dump(exclude={"reference_summary"}),
        "draft": cur.model_dump() if cur else None,
        "checks": [c.model_dump() for c in checks],
        "readiness": readiness_score(checks),
        "trace": {"summary": summarize(findings), "flags": [f.model_dump() for f in findings if f.status != "verified"]},
    }


@app.get("/api/drafts/{ip_no}/checks")
def get_checks(ip_no: str):
    """Re-evaluated from the replica on every call, so a document uploaded in MediTrack shows up within seconds."""
    checks = tpa_checklist(_encounter(ip_no))
    return {"checks": [c.model_dump() for c in checks], "readiness": readiness_score(checks)}


class DraftIn(BaseModel):
    draft: SummaryDraft


@app.put("/api/drafts/{ip_no}")
def save_draft(ip_no: str, body: DraftIn):
    row = _row(ip_no)
    if row["status"] == "SIGNED":
        raise HTTPException(409, "Already signed")
    original = draft_to_text(SummaryDraft.model_validate_json(row["draft_json"]))
    edited = draft_to_text(body.draft)
    edit_pct = round(100 * (1 - difflib.SequenceMatcher(None, original, edited).ratio()), 1)
    enc = _encounter(ip_no)
    findings = trace(edited, enc)
    with db() as c:
        c.execute("UPDATE draft SET edited_json=?, edit_pct=? WHERE ip_no=?", (body.draft.model_dump_json(), edit_pct, ip_no))
    event(ip_no, "doctor", "DRAFT_EDITED", f"{edit_pct}% changed")
    return {"edit_pct": edit_pct,
            "trace": {"summary": summarize(findings), "flags": [f.model_dump() for f in findings if f.status != "verified"]}}


@app.post("/api/drafts/{ip_no}/regenerate")
def regenerate(ip_no: str):
    row = _row(ip_no)
    if row["status"] == "SIGNED":
        raise HTTPException(409, "Already signed")
    with db() as c:
        c.execute("UPDATE draft SET status='GENERATING', edited_json=NULL, edit_pct=NULL WHERE ip_no=?", (ip_no,))
    process_discharge(ip_no, row["advised_at"])
    return get_draft(ip_no)


class SignIn(BaseModel):
    signed_by: str


@app.post("/api/drafts/{ip_no}/sign")
def sign(ip_no: str, body: SignIn):
    row = _row(ip_no)
    if row["status"] == "SIGNED":
        raise HTTPException(409, "Already signed")
    enc = _encounter(ip_no)
    draft = _current(row)
    checks = tpa_checklist(enc)
    signed_at = now()
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    fname = f"{ip_no}_DSCHSUMM_{stamp}.pdf"
    with logfire.span("writeback.hotfolder", ip_no=ip_no, file=fname):
        tmp = HOTFOLDER / f".{fname}.part"          # importer ignores dot-files until the rename
        pdf.render(enc, draft, body.signed_by, signed_at, tmp)
        tmp.rename(HOTFOLDER / fname)
    with db() as c:
        c.execute("UPDATE draft SET status='SIGNED', signed_at=?, signed_by=?, tpa_score_at_sign=?, pdf_file=? WHERE ip_no=?",
                  (signed_at, body.signed_by, readiness_score(checks), fname, ip_no))
    event(ip_no, body.signed_by, "SIGNED", f"PDF -> MediTrack hot-folder: {fname}")
    return {"ok": True, "file": fname}


@app.get("/api/drafts/{ip_no}/pdf")
def preview_pdf(ip_no: str):
    enc = _encounter(ip_no)
    draft = _current(_row(ip_no))
    out = DATA / f"preview_{ip_no}.pdf"
    pdf.render(enc, draft, "(unsigned preview)", now(), out)
    return FileResponse(out, media_type="application/pdf", content_disposition_type="inline")


@app.get("/api/metrics")
def metrics():
    with replica() as r:
        base = {row["PAY_MODE"]: {"n": row["N"], "tat_hrs": row["TAT"]} for row in r.execute(
            """SELECT PAY_MODE, COUNT(*) N, ROUND(AVG((JULIANDAY(DSCH_DT)-JULIANDAY(DSCH_ADV_DT))*24),1) TAT
               FROM IP_ADM_DTL WHERE STS='DSCH' AND DSCH_ADV_DT IS NOT NULL GROUP BY PAY_MODE""")}
        q = r.execute("SELECT COUNT(*), SUM(CLM_STS='QUERY') FROM TPA_CLM_DTL").fetchone()
        reasons = [dict(x) for x in r.execute(
            "SELECT QRY_RSN reason, COUNT(*) n FROM TPA_CLM_DTL WHERE CLM_STS='QUERY' GROUP BY QRY_RSN ORDER BY n DESC")]
    with db() as c:
        rows = [dict(x) for x in c.execute("SELECT * FROM draft")]
        events = [dict(x) for x in c.execute("SELECT * FROM event ORDER BY id DESC LIMIT 25")]

    def mins(a, b):
        fmt = "%Y-%m-%d %H:%M:%S"
        pa = datetime.strptime(a if len(a) > 16 else a + ":00", fmt)
        return (datetime.strptime(b, fmt) - pa).total_seconds() / 60

    ready = [r["latency_ms"] / 1000 for r in rows if r["ready_at"] and r["latency_ms"]]
    signed = [r for r in rows if r["signed_at"]]
    return {
        "baseline": {"cash_tat_hrs": base.get("CASH", {}).get("tat_hrs"), "cashless_tat_hrs": base.get("CASHLESS", {}).get("tat_hrs"),
                     "tpa_query_pct": round(100 * (q[1] or 0) / q[0], 1) if q[0] else None, "query_reasons": reasons,
                     "discharges": sum(v["n"] for v in base.values())},
        "pilot": {
            "drafted": sum(1 for r in rows if r["ready_at"]),
            "signed": len(signed),
            "median_draft_s": round(statistics.median(ready), 1) if ready else None,
            "median_advised_to_signed_min": round(statistics.median([mins(r["advised_at"], r["signed_at"]) for r in signed]), 1) if signed else None,
            "avg_tpa_readiness_at_sign": round(statistics.mean([r["tpa_score_at_sign"] for r in signed])) if signed else None,
            "avg_edit_pct": round(statistics.mean([r["edit_pct"] or 0 for r in signed]), 1) if signed else None,
            "trace_flags": sum(r["trace_flags"] or 0 for r in rows),
            "ai_cost_usd": round(sum(r["cost_usd"] or 0 for r in rows), 5),
            "sources": {s: sum(1 for r in rows if r["source"] == s) for s in ("live", "cached", "template")},
        },
        "events": events,
        "logfire_url": LOGFIRE_URL,
    }


# ------------------------------------------------------------------ UI
if UI_DIST.exists():
    app.mount("/assets", StaticFiles(directory=UI_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        return FileResponse(UI_DIST / "index.html")
