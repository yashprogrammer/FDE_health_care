"""Adapter: MediTrack's cryptic legacy tables -> clean Encounter contract.

This is the only module that knows MediTrack's schema (reverse-engineered with Suresh from IT).
It reads IT's read-only "mis" reporting views (same names as MediTrack's tables) through a mis_ro login.
"""
import hashlib
import os

import psycopg

from .models import ClinicalNote, Diagnosis, Encounter, LabResult, Medication, Procedure

# read-only reporting login (member of mis_ro, search_path = mis)
MIS_DB_URL = os.getenv("MIS_DB_URL", "postgresql://mis_report:mis_report@localhost:5432/citycare")


def upper_row(cursor):
    """Dict rows keyed by MediTrack's UPPERCASE column names (Postgres folds names to lowercase)."""
    names = [d.name.upper() for d in cursor.description] if cursor.description else []
    return lambda values: dict(zip(names, values))


def connect_mis(url: str = MIS_DB_URL) -> psycopg.Connection:
    return psycopg.connect(url, row_factory=upper_row, autocommit=True)


def _rows(conn: psycopg.Connection, sql: str, *args) -> list[dict]:
    return conn.cursor(row_factory=upper_row).execute(sql, args).fetchall()


def load_encounter(conn: psycopg.Connection, ip_no: str) -> Encounter | None:
    adm = _rows(conn, """
        SELECT a.*, p.UHID, p.PT_NM, p.PT_AGE, p.PT_SEX, d.DR_NM, d.DR_SPCL, d.DR_REG_NO
        FROM IP_ADM_DTL a JOIN PT_MST p ON p.PT_ID = a.PT_ID JOIN DR_MST d ON d.DR_ID = a.DR_ID
        WHERE a.IP_NO = %s""", ip_no)
    if not adm:
        return None
    a = adm[0]
    meds = _rows(conn, "SELECT * FROM PHR_ISS_DTL WHERE IP_NO=%s ORDER BY ID", ip_no)
    to_med = lambda m: Medication(drug=m["DRUG_NM"], dose=m["DOSE"], frequency=m["FREQ"],  # noqa: E731
                                  route=m["ROUTE"], duration=m["DUR"] or "")
    summ = _rows(conn, "SELECT SUMM_TXT FROM IP_DSCH_SUMM WHERE IP_NO=%s", ip_no)
    return Encounter(
        ip_no=a["IP_NO"], uhid=a["UHID"], patient_name=a["PT_NM"], age=a["PT_AGE"], sex=a["PT_SEX"],
        admission_date=a["ADM_DT"], discharge_advised_date=a["DSCH_ADV_DT"], ward=a["WRD_CD"], bed=a["BED_NO"],
        consultant=a["DR_NM"], consultant_speciality=a["DR_SPCL"], consultant_reg_no=a["DR_REG_NO"],
        pay_mode=a["PAY_MODE"], tpa_name=a["TPA_NM"], policy_no=a["POL_NO"], reason_for_admission=a["ADM_RSN"],
        diagnoses=[Diagnosis(icd10=r["ICD_CD"], description=r["DIAG_DESC"], type=r["DIAG_TYP"])
                   for r in _rows(conn, "SELECT * FROM IP_DIAG_DTL WHERE IP_NO=%s ORDER BY ID", ip_no)],
        procedures=[Procedure(code=r["PROC_CD"], description=r["PROC_DESC"], date=r["PROC_DT"], surgeon=r["SURGEON"])
                    for r in _rows(conn, "SELECT * FROM IP_PROC_DTL WHERE IP_NO=%s ORDER BY PROC_DT", ip_no)],
        labs=[LabResult(test=r["TST_NM"], value=r["RSLT_VAL"] or "", unit=r["UOM"] or "", ref_range=r["REF_RNG"] or "",
                        flag=r["FLG"] or "", date=r["RSLT_DT"], status=r["STS"])
              for r in _rows(conn, "SELECT * FROM LAB_RSLT WHERE IP_NO=%s ORDER BY RSLT_DT, ID", ip_no)],
        inpatient_meds=[to_med(m) for m in meds if m["ISS_TYP"] == "INPATIENT"],
        discharge_meds=[to_med(m) for m in meds if m["ISS_TYP"] == "DISCHARGE"],
        notes=[ClinicalNote(datetime=r["NOTE_DT"], type=r["NOTE_TYP"], author=r["AUTH"], text=r["NOTE_TXT"])
               for r in _rows(conn, "SELECT * FROM CLN_NOTE WHERE IP_NO=%s ORDER BY NOTE_DT", ip_no)],
        documents=sorted({r["DOC_TYP"] for r in _rows(conn, "SELECT DOC_TYP FROM PT_DOC WHERE IP_NO=%s", ip_no)}),
        reference_summary=summ[0]["SUMM_TXT"] if summ else None,
    )


def deidentify(enc: Encounter, pseudo_id: str) -> Encounter:
    """Mask direct identifiers for the POC export (names, UHID, policy). Clinical content is kept."""
    return enc.model_copy(update={
        "ip_no": pseudo_id,
        "uhid": "UHID-" + hashlib.sha256(enc.uhid.encode()).hexdigest()[:8].upper(),
        "patient_name": f"Patient {pseudo_id}",
        "policy_no": "XXXX" if enc.policy_no else None,
    })
