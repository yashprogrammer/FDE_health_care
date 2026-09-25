"""TPA-readiness checklist. Deterministic rules, NOT an LLM: the insurer's rules are known, so we use code.

Each rule maps to a real query reason seen in CityCare's TPA_CLM_DTL history.
"""
from typing import Literal

from pydantic import BaseModel

from .models import Encounter

CARDIAC = ["I20", "I21", "I22", "I24", "I25"]

# CPT code -> diagnosis families that justify it + documents the TPA expects
PROC_RULES: dict[str, dict] = {
    "92928": {"dx": CARDIAC, "docs": ["CATH_RPT", "IMPLANT_STKR"]},        # PTCA + stent
    "93458": {"dx": CARDIAC, "docs": ["CATH_RPT"]},                        # coronary angiography
    "27447": {"dx": ["M17"], "docs": ["OT_NOTE", "IMPLANT_STKR"]},         # total knee
    "27125": {"dx": ["S72", "M16", "M87"], "docs": ["OT_NOTE", "IMPLANT_STKR"]},  # hip hemiarthroplasty
    "47562": {"dx": ["K80", "K81", "K82"], "docs": ["OT_NOTE"]},           # lap chole
    "44970": {"dx": ["K35", "K36", "K37"], "docs": ["OT_NOTE"]},           # lap appendectomy
}

DOC_LABELS = {
    "CATH_RPT": "Cath lab report",
    "IMPLANT_STKR": "Implant sticker / invoice",
    "OT_NOTE": "Operation notes",
}


class Check(BaseModel):
    id: str
    label: str
    status: Literal["pass", "warn", "fail", "na"]
    detail: str
    prevents_query: str | None = None   # the TPA query reason this check prevents


def tpa_checklist(enc: Encounter) -> list[Check]:
    checks: list[Check] = []
    final = enc.final_diagnoses
    codes = [d.icd10 for d in (final or enc.diagnoses)]

    checks.append(Check(
        id="final_dx", label="Final diagnosis with ICD-10 recorded",
        status="pass" if final else "fail",
        detail=", ".join(f"{d.icd10} {d.description}" for d in final) if final
        else "Only provisional diagnosis on file - consultant must enter FINAL diagnosis",
        prevents_query="Final diagnosis does not match provisional diagnosis at pre-auth"))

    mismatches = [p for p in enc.procedures
                  if p.code in PROC_RULES and not any(c.startswith(tuple(PROC_RULES[p.code]["dx"])) for c in codes)]
    checks.append(Check(
        id="dx_proc_match", label="Procedures consistent with diagnosis",
        status="na" if not enc.procedures else ("fail" if mismatches else "pass"),
        detail="No procedures" if not enc.procedures else (
            "Mismatch: " + ", ".join(p.description for p in mismatches) if mismatches
            else f"{len(enc.procedures)} procedure(s) justified by diagnosis"),
        prevents_query="Final diagnosis does not match provisional diagnosis at pre-auth"))

    missing = []
    for p in enc.procedures:
        for doc in PROC_RULES.get(p.code, {}).get("docs", []):
            if doc not in enc.documents and doc not in missing:
                missing.append(doc)
    checks.append(Check(
        id="required_docs", label="Procedure documents attached",
        status="na" if not enc.procedures else ("fail" if missing else "pass"),
        detail="No procedures" if not enc.procedures else (
            "Missing: " + ", ".join(f"{DOC_LABELS.get(d, d)} ({d})" for d in missing) if missing
            else "Cath/OT reports and implant details on file"),
        prevents_query="Stent implant sticker / invoice not attached" if "IMPLANT_STKR" in missing
        else "Operation notes not attached"))

    pending = enc.pending_labs
    checks.append(Check(
        id="pending_reports", label="Pending reports declared",
        status="warn" if pending else "pass",
        detail=("Auto-listed in summary as pending: " + ", ".join(lab.test for lab in pending)) if pending
        else "All investigation reports final",
        prevents_query="Pending report status not mentioned in discharge summary"))

    checks.append(Check(
        id="doctor_reg", label="Treating doctor name + registration no.",
        status="pass" if enc.consultant and enc.consultant_reg_no else "fail",
        detail=f"{enc.consultant} ({enc.consultant_reg_no or 'REG NO MISSING'})",
        prevents_query="Treating doctor registration number missing"))

    incomplete = [m.drug for m in enc.discharge_meds if not (m.dose and m.frequency and m.duration)]
    checks.append(Check(
        id="discharge_meds", label="Discharge medications reconciled (pharmacy)",
        status="fail" if not enc.discharge_meds else ("warn" if incomplete else "pass"),
        detail="No discharge medications issued by pharmacy" if not enc.discharge_meds else (
            "Missing dose/frequency/duration: " + ", ".join(incomplete) if incomplete
            else f"{len(enc.discharge_meds)} medicines with dose, frequency and duration")))

    if enc.pay_mode == "CASHLESS":
        ok = bool(enc.tpa_name and enc.policy_no)
        checks.append(Check(id="policy", label="TPA + policy details", status="pass" if ok else "fail",
                            detail=f"{enc.tpa_name or '?'} / {enc.policy_no or '?'}"))
    else:
        checks.append(Check(id="policy", label="TPA + policy details", status="na", detail="Cash patient"))

    return checks


def readiness_score(checks: list[Check]) -> int:
    applicable = [c for c in checks if c.status != "na"]
    return round(100 * sum(c.status == "pass" for c in applicable) / max(len(applicable), 1))
