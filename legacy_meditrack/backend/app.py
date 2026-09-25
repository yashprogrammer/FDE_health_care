"""MediTrack HMS v3.2 - application server.

The /int/* endpoints are INTERNAL: they exist only for MediTrack's own UI,
are undocumented, and hospital IT policy forbids external systems calling them.
"""
import re
import shutil
import threading
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import DOCS_DIR, HOTFOLDER, audit, connect, now, row, rows

UI_DIST = Path(__file__).resolve().parent.parent / "ui" / "dist"
HOTFOLDER_PATTERN = re.compile(r"^(IP\d{4}-\d{4})_([A-Z_]+?)_(\d{14})\.pdf$")
USER = "rmo.karan"  # MediTrack has no SSO; demo session is logged in as the RMO

app = FastAPI(title="MediTrack HMS v3.2 (internal)")


# ---------------------------------------------------------------- census / patient
@app.get("/int/census")
def census():
    with connect() as c:
        return rows(c, """
            SELECT a.IP_NO, p.UHID, p.PT_NM, p.PT_AGE, p.PT_SEX, a.WRD_CD, a.BED_NO, d.DR_NM, a.PAY_MODE,
                   a.TPA_NM, a.STS, a.ADM_DT, a.DSCH_ADV_DT
            FROM IP_ADM_DTL a JOIN PT_MST p ON p.PT_ID = a.PT_ID JOIN DR_MST d ON d.DR_ID = a.DR_ID
            WHERE a.STS IN ('ADM', 'DA') ORDER BY a.WRD_CD, a.BED_NO""")


@app.get("/int/discharged")
def discharged():
    with connect() as c:
        return rows(c, """
            SELECT a.IP_NO, p.UHID, p.PT_NM, a.WRD_CD, d.DR_NM, a.PAY_MODE, a.ADM_DT, a.DSCH_ADV_DT, a.DSCH_DT,
                   (SELECT COUNT(*) FROM IP_DSCH_SUMM s WHERE s.IP_NO = a.IP_NO) AS HAS_SUMM
            FROM IP_ADM_DTL a JOIN PT_MST p ON p.PT_ID = a.PT_ID JOIN DR_MST d ON d.DR_ID = a.DR_ID
            WHERE a.STS = 'DSCH' ORDER BY HAS_SUMM DESC, a.DSCH_DT DESC LIMIT 60""")


@app.get("/int/ip/{ip_no}")
def ip_detail(ip_no: str):
    with connect() as c:
        adm = row(c, """
            SELECT a.*, p.UHID, p.PT_NM, p.PT_AGE, p.PT_SEX, p.PT_MOB, p.PT_ADDR, d.DR_NM, d.DR_SPCL, d.DR_REG_NO
            FROM IP_ADM_DTL a JOIN PT_MST p ON p.PT_ID = a.PT_ID JOIN DR_MST d ON d.DR_ID = a.DR_ID
            WHERE a.IP_NO = ?""", ip_no)
        if not adm:
            raise HTTPException(404, "IP NO NOT FOUND")
        q = lambda sql: rows(c, sql, ip_no)  # noqa: E731
        return {
            "adm": adm,
            "diags": q("SELECT * FROM IP_DIAG_DTL WHERE IP_NO=? ORDER BY DIAG_TYP DESC, ID"),
            "procs": q("SELECT * FROM IP_PROC_DTL WHERE IP_NO=? ORDER BY PROC_DT"),
            "labs": q("SELECT * FROM LAB_RSLT WHERE IP_NO=? ORDER BY RSLT_DT"),
            "meds": q("SELECT * FROM PHR_ISS_DTL WHERE IP_NO=? ORDER BY ISS_TYP DESC, ID"),
            "notes": q("SELECT * FROM CLN_NOTE WHERE IP_NO=? ORDER BY NOTE_DT"),
            "docs": q("SELECT * FROM PT_DOC WHERE IP_NO=? ORDER BY DOC_ID"),
            "summary": row(c, "SELECT * FROM IP_DSCH_SUMM WHERE IP_NO=?", ip_no),
            "claims": q("SELECT * FROM TPA_CLM_DTL WHERE IP_NO=? ORDER BY SUBM_DT"),
            "links": [
                {**lnk, "HREF": lnk["LNK_URL"].replace("{IP_NO}", ip_no).replace("{UHID}", adm["UHID"])}
                for lnk in rows(c, "SELECT * FROM SYS_EXT_LNK WHERE IS_ACTV=1 ORDER BY LNK_ID")
            ],
        }


@app.post("/int/ip/{ip_no}/discharge-advise")
def discharge_advise(ip_no: str):
    with connect() as c:
        cur = c.execute("UPDATE IP_ADM_DTL SET STS='DA', DSCH_ADV_DT=? WHERE IP_NO=? AND STS='ADM'", (now(), ip_no))
        if cur.rowcount == 0:
            raise HTTPException(409, "PATIENT NOT IN ADMITTED STATE")
        audit(c, USER, "DISCHARGE_ADVISED", ip_no)
    return {"ok": True}


@app.post("/int/ip/{ip_no}/discharge")
def final_discharge(ip_no: str):
    with connect() as c:
        cur = c.execute("UPDATE IP_ADM_DTL SET STS='DSCH', DSCH_DT=? WHERE IP_NO=? AND STS='DA'", (now(), ip_no))
        if cur.rowcount == 0:
            raise HTTPException(409, "DISCHARGE NOT ADVISED")
        audit(c, USER, "FINAL_DISCHARGE", ip_no)
    return {"ok": True}


class ManualSummary(BaseModel):
    text: str


@app.post("/int/ip/{ip_no}/manual-summary")
def save_manual_summary(ip_no: str, body: ManualSummary):
    with connect() as c:
        c.execute("INSERT OR REPLACE INTO IP_DSCH_SUMM VALUES (?,?,?,?)", (ip_no, body.text, USER, now()))
        audit(c, USER, "MANUAL_SUMMARY_SAVED", ip_no)
    return {"ok": True}


SUMMARY_TEMPLATE = """CITYCARE HOSPITALS, PUNE - DISCHARGE SUMMARY  (Form MRD/DS/07 rev.3)

Patient Name: ____________   UHID: ________   IP No: ________
Date of Admission: ________   Date of Discharge: ________
Consultant: ______________   Reg No: ________

Diagnosis:
Presenting complaints:
Hospital course:
Procedures:
Investigations:
Condition at discharge:
Discharge medications:
Follow-up:

Signature of treating doctor: ____________
"""


@app.get("/int/ip/{ip_no}/summary-template", response_class=PlainTextResponse)
def summary_template(ip_no: str):
    return PlainTextResponse(SUMMARY_TEMPLATE, headers={"Content-Disposition": f'attachment; filename="DSCH_{ip_no}.doc"'})


# ---------------------------------------------------------------- documents
@app.post("/int/ip/{ip_no}/docs")
async def upload_doc(ip_no: str, doc_typ: str = Form(...), file: UploadFile = File(...)):
    file_nm = f"{ip_no}_{doc_typ}_{int(time.time())}.pdf"
    (DOCS_DIR / file_nm).write_bytes(await file.read())
    with connect() as c:
        c.execute("INSERT INTO PT_DOC (IP_NO, DOC_TYP, FILE_NM, UPL_DT, UPL_BY) VALUES (?,?,?,?,?)",
                  (ip_no, doc_typ, file_nm, now(), USER))
        audit(c, USER, f"DOC_UPLOAD:{doc_typ}", ip_no)
    return {"ok": True}


@app.get("/int/docs/{doc_id}")
def get_doc(doc_id: int):
    with connect() as c:
        d = row(c, "SELECT * FROM PT_DOC WHERE DOC_ID=?", doc_id)
    if not d:
        raise HTTPException(404)
    return FileResponse(DOCS_DIR / d["FILE_NM"], media_type="application/pdf", filename=d["FILE_NM"],
                        content_disposition_type="inline")


def hotfolder_importer() -> None:
    """Batch Document Import (v2.4, 2013). Picks up scanned PDFs dropped by the MRD scanner.
    Filename convention: <IP_NO>_<DOC_TYP>_<YYYYMMDDHHMMSS>.pdf"""
    rejected = HOTFOLDER / "rejected"
    while True:
        for f in sorted(HOTFOLDER.glob("*.pdf")):
            m = HOTFOLDER_PATTERN.match(f.name)
            try:
                with connect() as c:
                    if not m or not row(c, "SELECT 1 FROM IP_ADM_DTL WHERE IP_NO=?", m.group(1)):
                        rejected.mkdir(exist_ok=True)
                        shutil.move(f, rejected / f.name)
                        continue
                    shutil.move(f, DOCS_DIR / f.name)
                    c.execute("INSERT INTO PT_DOC (IP_NO, DOC_TYP, FILE_NM, UPL_DT, UPL_BY) VALUES (?,?,?,?,?)",
                              (m.group(1), m.group(2), f.name, now(), "BATCH_IMPORT"))
                    audit(c, "BATCH_IMPORT", f"DOC_IMPORTED:{m.group(2)}", m.group(1))
            except Exception as e:  # legacy importer: log and keep going
                print(f"[importer] {f.name}: {e}")
        time.sleep(3)


@app.on_event("startup")
def start_importer():
    HOTFOLDER.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=hotfolder_importer, daemon=True).start()


# ---------------------------------------------------------------- admin: external links
class ExtLink(BaseModel):
    label: str
    url: str
    mode: Literal["LINK", "TAB"] = "LINK"


@app.get("/int/admin/extlinks")
def list_links():
    with connect() as c:
        return rows(c, "SELECT * FROM SYS_EXT_LNK ORDER BY LNK_ID")


@app.post("/int/admin/extlinks")
def add_link(body: ExtLink):
    with connect() as c:
        c.execute("INSERT INTO SYS_EXT_LNK (LNK_LBL, LNK_URL, DISP_MD, IS_ACTV, CRT_BY, CRT_DT) VALUES (?,?,?,1,?,?)",
                  (body.label, body.url, body.mode, "it.suresh", now()))
        audit(c, "it.suresh", "EXT_LINK_ADDED", body.label)
    return {"ok": True}


@app.post("/int/admin/extlinks/{lnk_id}/toggle")
def toggle_link(lnk_id: int):
    with connect() as c:
        c.execute("UPDATE SYS_EXT_LNK SET IS_ACTV = 1 - IS_ACTV WHERE LNK_ID=?", (lnk_id,))
    return {"ok": True}


# ---------------------------------------------------------------- MIS
@app.get("/int/mis/discharge-tat")
def mis_discharge_tat():
    with connect() as c:
        by_mode = rows(c, """
            SELECT PAY_MODE, COUNT(*) AS N,
                   ROUND(AVG((JULIANDAY(DSCH_DT) - JULIANDAY(DSCH_ADV_DT)) * 24), 1) AS AVG_TAT_HRS
            FROM IP_ADM_DTL WHERE STS='DSCH' AND DSCH_ADV_DT IS NOT NULL GROUP BY PAY_MODE""")
        claims = row(c, """SELECT COUNT(*) AS N, SUM(CLM_STS='QUERY') AS QUERIES,
                                  ROUND(100.0 * SUM(CLM_STS='QUERY') / COUNT(*), 1) AS QUERY_PCT FROM TPA_CLM_DTL""")
        reasons = rows(c, """SELECT QRY_RSN, COUNT(*) AS N FROM TPA_CLM_DTL WHERE CLM_STS='QUERY'
                             GROUP BY QRY_RSN ORDER BY N DESC""")
    return {"by_mode": by_mode, "claims": claims, "reasons": reasons}


@app.get("/int/audit")
def audit_log():
    with connect() as c:
        return rows(c, "SELECT * FROM SYS_AUDIT ORDER BY ID DESC LIMIT 50")


# ---------------------------------------------------------------- UI
if UI_DIST.exists():
    app.mount("/assets", StaticFiles(directory=UI_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        return FileResponse(UI_DIST / "index.html")
