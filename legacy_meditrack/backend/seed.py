"""(Re)create MediTrack's database with synthetic CityCare data.

Usage: python -m legacy_meditrack.backend.seed
"""
import random
import shutil
from datetime import datetime, timedelta

from fpdf import FPDF

from . import seed_data as S
from .db import DATA_DIR, DB_PATH, DOCS_DIR, HOTFOLDER, SCHEMA, connect

DOC_TITLES = {
    "ID_PROOF": "Patient ID Proof (Aadhaar - masked)",
    "CONSENT": "Informed Consent Form",
    "CATH_RPT": "Cardiac Catheterisation Lab Report",
    "IMPLANT_STKR": "Implant Sticker / Invoice",
    "OT_NOTE": "Operation Theatre Notes",
}


def scanned_pdf(path, title: str, ip_no: str, name: str, lines: list[str] | None = None) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, "CITYCARE HOSPITALS, PUNE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 11)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"IP No: {ip_no}    Patient: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for line in lines or ["[scanned document]"]:
        pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def insert_encounter(conn, enc: dict) -> None:
    cur = conn.execute(
        "INSERT INTO PT_MST (UHID, PT_NM, PT_AGE, PT_SEX, PT_MOB, PT_ADDR) VALUES (?,?,?,?,?,?)",
        (enc["uhid"], enc["name"], enc["age"], enc["sex"], enc["mob"], enc["addr"]),
    )
    ip = enc["ip"]
    conn.execute(
        "INSERT INTO IP_ADM_DTL VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (ip, cur.lastrowid, enc["adm"], enc["ward"], enc["bed"], enc["dr"], enc["pay"], enc.get("tpa"),
         enc.get("pol"), enc["rsn"], enc["sts"], enc.get("adv"), enc.get("dsch")),
    )
    for icd, desc, typ in enc.get("diags", []):
        conn.execute("INSERT INTO IP_DIAG_DTL (IP_NO, ICD_CD, DIAG_DESC, DIAG_TYP) VALUES (?,?,?,?)", (ip, icd, desc, typ))
    for code, desc, dt, surgeon in enc.get("procs", []):
        conn.execute("INSERT INTO IP_PROC_DTL (IP_NO, PROC_CD, PROC_DESC, PROC_DT, SURGEON) VALUES (?,?,?,?,?)",
                     (ip, code, desc, dt, surgeon))
    for lab in enc.get("labs", []):
        conn.execute("INSERT INTO LAB_RSLT (IP_NO, TST_NM, RSLT_VAL, UOM, REF_RNG, FLG, RSLT_DT, STS) VALUES (?,?,?,?,?,?,?,?)",
                     (ip, *lab))
    for med in enc.get("meds", []):
        conn.execute("INSERT INTO PHR_ISS_DTL (IP_NO, DRUG_NM, DOSE, FREQ, ROUTE, DUR, ISS_TYP) VALUES (?,?,?,?,?,?,?)",
                     (ip, *med))
    for dt, typ, auth, txt in enc.get("notes", []):
        conn.execute("INSERT INTO CLN_NOTE (IP_NO, NOTE_DT, NOTE_TYP, AUTH, NOTE_TXT) VALUES (?,?,?,?,?)", (ip, dt, typ, auth, txt))
    for doc_typ in enc.get("docs", []):
        file_nm = f"{ip}_{doc_typ}.pdf"
        lines = None
        if doc_typ == "CATH_RPT":
            lines = [n[3] for n in enc["notes"] if n[1] == "DR" and ("CAG" in n[3] or "PCI" in n[3])]
        scanned_pdf(DOCS_DIR / file_nm, DOC_TITLES.get(doc_typ, doc_typ), ip, enc["name"], lines)
        conn.execute("INSERT INTO PT_DOC (IP_NO, DOC_TYP, FILE_NM, UPL_DT, UPL_BY) VALUES (?,?,?,?,?)",
                     (ip, doc_typ, file_nm, enc["adm"], "MRD"))
    if enc.get("summary"):
        conn.execute("INSERT INTO IP_DSCH_SUMM VALUES (?,?,?,?)", (ip, enc["summary"], enc["dr"], enc["adv"]))
    if enc.get("tpa_claim"):
        conn.execute("INSERT INTO TPA_CLM_DTL (IP_NO, SUBM_DT, CLM_STS, QRY_RSN, APPR_DT) VALUES (?,?,?,?,?)",
                     (ip, *enc["tpa_claim"]))


def insert_historic(conn, rng: random.Random) -> None:
    """~3 months of MIS-level admissions: enough to reproduce the discharge-delay pattern."""
    start = datetime(2026, 6, 25, 8, 0)
    counters: dict[str, int] = {}
    for i in range(S.HISTORIC_COUNT):
        adm = start + timedelta(hours=rng.uniform(0, 24 * 85))
        yymm = adm.strftime("%y%m")
        counters[yymm] = counters.get(yymm, 500) + 1
        ip = f"IP{yymm}-{counters[yymm]:04d}"
        los_days = rng.choice([2, 3, 3, 4, 4, 5, 6])
        adv = (adm + timedelta(days=los_days)).replace(hour=rng.choice([9, 10, 10, 11]), minute=rng.randint(0, 59))
        cashless = rng.random() < 0.6
        name = f"{rng.choice(S.HISTORIC_FIRST_NAMES)} {rng.choice(S.HISTORIC_LAST_NAMES)}"
        cur = conn.execute("INSERT INTO PT_MST (UHID, PT_NM, PT_AGE, PT_SEX, PT_MOB, PT_ADDR) VALUES (?,?,?,?,?,?)",
                           (f"CC-2026-9{i:05d}", name, rng.randint(18, 85), rng.choice("MF"), "", "Pune"))
        claim = None
        if cashless:
            subm = adv + timedelta(hours=rng.uniform(1.8, 2.8))          # summary writing + final bill
            if rng.random() < 0.43:                                      # insurer raises a query
                appr = subm + timedelta(hours=rng.uniform(4.0, 6.0))
                claim = (_fmt(subm), "QUERY", rng.choice(S.TPA_QUERY_REASONS), _fmt(appr))
            else:
                appr = subm + timedelta(hours=rng.uniform(2.0, 3.4))
                claim = (_fmt(subm), "APPROVED", None, _fmt(appr))
            dsch = appr + timedelta(minutes=rng.randint(15, 40))
        else:
            dsch = adv + timedelta(hours=rng.uniform(1.8, 3.2))
        conn.execute(
            "INSERT INTO IP_ADM_DTL VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (ip, cur.lastrowid, _fmt(adm), rng.choice(["3C-MED", "4B-CARD", "3A-ORTH", "2B-SURG"]), str(rng.randint(1, 14)),
             rng.choice(["D01", "D02", "D03", "D04"]), "CASHLESS" if cashless else "CASH",
             rng.choice(S.TPA_NAMES) if cashless else None, None, "", "DSCH", _fmt(adv), _fmt(dsch)),
        )
        if claim:
            conn.execute("INSERT INTO TPA_CLM_DTL (IP_NO, SUBM_DT, CLM_STS, QRY_RSN, APPR_DT) VALUES (?,?,?,?,?)", (ip, *claim))


def seed() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DOCS_DIR.mkdir(parents=True)
    HOTFOLDER.mkdir(parents=True)
    conn = connect()
    conn.executescript(SCHEMA.read_text())
    conn.executemany("INSERT INTO DR_MST VALUES (?,?,?,?)", S.DOCTORS)
    for enc in S.PAST + S.CURRENT:
        insert_encounter(conn, enc)
    insert_historic(conn, random.Random(42))
    conn.execute("INSERT INTO SYS_EXT_LNK (LNK_LBL, LNK_URL, DISP_MD, IS_ACTV, CRT_BY, CRT_DT) VALUES (?,?,?,?,?,?)",
                 ("PACS Image Viewer", "http://pacs.citycare.local/viewer?uhid={UHID}", "LINK", 1, "admin", "2016-03-14 11:20"))
    conn.commit()
    conn.close()
    print(f"MediTrack DB seeded -> {DB_PATH}")


if __name__ == "__main__":
    seed()
