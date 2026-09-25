"""Assemble the final discharge summary: deterministic facts from MediTrack + LLM-drafted narrative."""
from .models import Encounter, SummaryDraft


def diagnoses_lines(enc: Encounter) -> list[str]:
    final = enc.final_diagnoses
    if final:
        return [f"{d.description} (ICD-10 {d.icd10})" for d in final]
    return [f"{d.description} (ICD-10 {d.icd10}) - PROVISIONAL" for d in enc.diagnoses]


def med_line(m) -> str:
    return f"{m.drug} {m.dose} - {m.frequency} - {m.route}" + (f" - {m.duration}" if m.duration else "")


def to_markdown(enc: Encounter, d: SummaryDraft) -> str:
    L = [
        f"**Patient:** {enc.patient_name} | {enc.age}/{enc.sex} | UHID {enc.uhid} | IP {enc.ip_no}  ",
        f"**Admitted:** {enc.admission_date} | **Discharge advised:** {enc.discharge_advised_date or '-'} | "
        f"**Ward:** {enc.ward}/{enc.bed}  ",
        f"**Consultant:** {enc.consultant} ({enc.consultant_speciality}, Reg. {enc.consultant_reg_no})",
        "",
        "#### Final diagnosis 🔒",
        *[f"- {x}" for x in diagnoses_lines(enc)],
        "#### Presenting complaints",
        d.presenting_complaints,
        "#### Hospital course",
        *[f"- {b}" for b in d.hospital_course],
    ]
    if d.procedures_performed:
        L += ["#### Procedures", *[f"- {p}" for p in d.procedures_performed]]
    L += ["#### Key investigations", *[f"- **{k.test}:** {k.result} - {k.interpretation}" for k in d.key_investigations]]
    if enc.pending_labs:
        L += ["#### ⚠️ Reports pending at discharge 🔒",
              *[f"- {lab.test} (sent {lab.date[:10]}) - to be reviewed at follow-up" for lab in enc.pending_labs]]
    L += ["#### Condition at discharge", d.condition_at_discharge,
          "#### Discharge medications 🔒 *(from pharmacy system, not AI)*",
          *[f"- {med_line(m)}" for m in enc.discharge_meds],
          "#### Follow-up", *[f"- {f}" for f in d.follow_up_advice],
          "#### Diet & activity", *[f"- {f}" for f in d.diet_and_activity]]
    return "\n".join(L)
