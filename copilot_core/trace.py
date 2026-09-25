"""Source tracing guardrail: every drug, lab test and number in a draft must trace back to MediTrack data.

verified   - found in the patient's source data
unverified - a number we could not find in the source (needs doctor attention)
hallucinated - a drug / lab test that does not exist in this patient's record
"""
import html
import re
from typing import Literal

from pydantic import BaseModel

from .models import Encounter, SummaryDraft

FORMULARY = [
    "Aspirin", "Clopidogrel", "Ticagrelor", "Prasugrel", "Atorvastatin", "Rosuvastatin", "Metoprolol", "Bisoprolol",
    "Carvedilol", "Ramipril", "Enalapril", "Telmisartan", "Losartan", "Amlodipine", "Furosemide", "Torsemide",
    "Spironolactone", "Dapagliflozin", "Empagliflozin", "Sacubitril", "Digoxin", "Amiodarone", "Warfarin",
    "Apixaban", "Rivaroxaban", "Dabigatran", "Heparin", "Enoxaparin", "Nitroglycerin", "Isosorbide", "Ivabradine",
    "Metformin", "Glimepiride", "Sitagliptin", "Insulin", "Pantoprazole", "Omeprazole", "Ranitidine", "Ondansetron",
    "Domperidone", "Racecadotril", "Ceftriaxone", "Cefuroxime", "Cefixime", "Azithromycin", "Doxycycline",
    "Amoxicillin", "Piperacillin", "Meropenem", "Metronidazole", "Levofloxacin", "Ciprofloxacin", "Nitrofurantoin",
    "Vancomycin", "Paracetamol", "Tramadol", "Diclofenac", "Ibuprofen", "Morphine", "Salbutamol", "Ipratropium",
    "Tiotropium", "Budesonide", "Formoterol", "Montelukast", "Prednisolone", "Methylprednisolone",
    "Hydrocortisone", "Dexamethasone", "Cholecalciferol", "Calcium", "Potassium chloride", "Levothyroxine",
    "Probiotic", "Oral rehydration salts", "ORS",
]

LAB_TERMS = [
    "Troponin", "CK-MB", "Haemoglobin", "Hemoglobin", "Hb", "Creatinine", "Potassium", "Sodium", "LDL", "HbA1c",
    "LVEF", "Echo", "Lipoprotein(a)", "Lp(a)", "NT-proBNP", "BNP", "CRP", "Procalcitonin", "Platelet", "TLC",
    "Leucocyte", "SGPT", "SGOT", "Bilirubin", "Albumin", "INR", "D-dimer", "TSH", "Vitamin D", "pCO2", "pH",
    "Ketones", "NS1", "Blood culture", "Urine culture", "Lactate", "ESR", "Ferritin", "Histopathology", "HPE",
]

LAB_ALIASES = {"hemoglobin": "haemoglobin", "hb": "haemoglobin", "lp(a)": "lipoprotein(a)", "hpe": "histopathology",
               "leucocyte": "tlc", "tlc": "leucocyte", "echo": "lvef", "bnp": "nt-probnp"}

NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w])")


class Finding(BaseModel):
    text: str
    kind: Literal["drug", "lab", "number"]
    status: Literal["verified", "unverified", "hallucinated"]
    start: int
    end: int


def draft_to_text(d: SummaryDraft) -> str:
    parts = [
        f"Presenting complaints: {d.presenting_complaints}",
        "Hospital course:\n" + "\n".join(f"- {b}" for b in d.hospital_course),
        "Procedures:\n" + "\n".join(f"- {p}" for p in d.procedures_performed),
        "Key investigations:\n" + "\n".join(f"- {k.test}: {k.result} ({k.interpretation})" for k in d.key_investigations),
        f"Condition at discharge: {d.condition_at_discharge}",
        "Follow-up:\n" + "\n".join(f"- {f}" for f in d.follow_up_advice),
        "Diet & activity:\n" + "\n".join(f"- {f}" for f in d.diet_and_activity),
    ]
    return "\n\n".join(parts)


def _source_corpus(enc: Encounter) -> str:
    bits = [enc.reason_for_admission, enc.admission_date, enc.discharge_advised_date or "", str(enc.age)]
    bits += [f"{d.icd10} {d.description}" for d in enc.diagnoses]
    bits += [f"{p.code} {p.description} {p.date}" for p in enc.procedures]
    bits += [f"{lab.test} {lab.value} {lab.unit} {lab.ref_range} {lab.date}" for lab in enc.labs]
    bits += [f"{m.drug} {m.dose} {m.frequency} {m.duration}" for m in enc.inpatient_meds + enc.discharge_meds]
    bits += [f"{n.datetime} {n.text}" for n in enc.notes]
    return "\n".join(bits)


def _numbers(text: str) -> set[float]:
    out: set[float] = set()
    for n in NUM_RE.findall(text):
        v = float(n)
        out.add(v)
    for k in re.findall(r"(\d+(?:\.\d+)?)\s*k\b", text, re.I):    # "48k" == 48000
        out.add(float(k) * 1000)
    out |= {v % 100 for v in out if 2000 <= v <= 2099 and v == int(v)}  # "2026" also allows "26"
    return out


def trace(text: str, enc: Encounter) -> list[Finding]:
    corpus = _source_corpus(enc)
    corpus_l = corpus.lower()
    src_numbers = _numbers(corpus)
    patient_drugs = " ".join(m.drug.lower() for m in enc.inpatient_meds + enc.discharge_meds)
    findings: list[Finding] = []
    taken: list[tuple[int, int]] = []

    def add(m: re.Match, kind, status):
        if any(s < m.end() and m.start() < e for s, e in taken):
            return
        taken.append((m.start(), m.end()))
        findings.append(Finding(text=m.group(0), kind=kind, status=status, start=m.start(), end=m.end()))

    for drug in sorted(FORMULARY, key=len, reverse=True):
        for m in re.finditer(rf"\b{re.escape(drug)}\b", text, re.I):
            add(m, "drug", "verified" if drug.lower().split()[0] in patient_drugs or drug.lower() in corpus_l
                else "hallucinated")

    for term in sorted(LAB_TERMS, key=len, reverse=True):
        for m in re.finditer(rf"(?<![\w]){re.escape(term)}(?![\w])", text, re.I):
            t = term.lower()
            ok = t in corpus_l or LAB_ALIASES.get(t, "~") in corpus_l
            add(m, "lab", "verified" if ok else "hallucinated")

    for m in NUM_RE.finditer(text):
        v = float(m.group(1))
        add(m, "number", "verified" if v in src_numbers or v * 1000 in src_numbers else "unverified")

    return sorted(findings, key=lambda f: f.start)


COLORS = {"verified": "#c8f7c5", "unverified": "#ffe08a", "hallucinated": "#ff9b9b"}


def highlight_html(text: str, findings: list[Finding]) -> str:
    out, pos = [], 0
    for f in findings:
        out.append(html.escape(text[pos:f.start]))
        title = f"{f.kind}: {f.status}"
        out.append(f'<mark style="background:{COLORS[f.status]};padding:0 2px;border-radius:3px" title="{title}">'
                   f"{html.escape(f.text)}</mark>")
        pos = f.end
    out.append(html.escape(text[pos:]))
    return "<div style='white-space:pre-wrap;line-height:1.7;font-size:14px'>" + "".join(out) + "</div>"


def summarize(findings: list[Finding]) -> dict:
    return {
        "verified": sum(f.status == "verified" for f in findings),
        "unverified": sum(f.status == "unverified" for f in findings),
        "hallucinated": sum(f.status == "hallucinated" for f in findings),
        "total": len(findings),
    }
