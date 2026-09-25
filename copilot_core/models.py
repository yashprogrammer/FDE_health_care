"""Data contracts: the Encounter (input, built from MediTrack data) and the SummaryDraft (LLM output)."""
from typing import Literal

from pydantic import BaseModel, Field


# ------------------------------------------------------------------ input: Encounter
class Diagnosis(BaseModel):
    icd10: str
    description: str
    type: Literal["PROV", "FINAL"]


class Procedure(BaseModel):
    code: str
    description: str
    date: str
    surgeon: str | None = None


class LabResult(BaseModel):
    test: str
    value: str
    unit: str = ""
    ref_range: str = ""
    flag: str = ""
    date: str
    status: Literal["FINAL", "PENDING"]


class Medication(BaseModel):
    drug: str
    dose: str
    frequency: str
    route: str
    duration: str = ""


class ClinicalNote(BaseModel):
    datetime: str
    type: Literal["DR", "NRS"]
    author: str
    text: str


class Encounter(BaseModel):
    ip_no: str
    uhid: str
    patient_name: str
    age: int
    sex: str
    admission_date: str
    discharge_advised_date: str | None = None
    ward: str
    bed: str
    consultant: str
    consultant_speciality: str
    consultant_reg_no: str | None = None
    pay_mode: Literal["CASH", "CASHLESS"]
    tpa_name: str | None = None
    policy_no: str | None = None
    reason_for_admission: str
    diagnoses: list[Diagnosis] = []
    procedures: list[Procedure] = []
    labs: list[LabResult] = []
    inpatient_meds: list[Medication] = []
    discharge_meds: list[Medication] = []
    notes: list[ClinicalNote] = []
    documents: list[str] = []            # document types on file, e.g. CATH_RPT, IMPLANT_STKR
    reference_summary: str | None = None  # doctor-written summary (past discharges only)

    @property
    def final_diagnoses(self) -> list[Diagnosis]:
        return [d for d in self.diagnoses if d.type == "FINAL"]

    @property
    def pending_labs(self) -> list[LabResult]:
        return [lab for lab in self.labs if lab.status == "PENDING"]

    def for_llm(self) -> dict:
        """What the model is allowed to see: clinical facts only, no direct identifiers."""
        return self.model_dump(
            exclude={"ip_no", "uhid", "patient_name", "policy_no", "tpa_name", "reference_summary",
                     "discharge_meds", "documents", "consultant_reg_no"},
        )


# ------------------------------------------------------------------ output: what the LLM drafts
class KeyInvestigation(BaseModel):
    test: str = Field(description="Test name exactly as in the lab data")
    result: str = Field(description="Result value with unit, copied from the lab data")
    interpretation: str = Field(description="Short clinical interpretation, e.g. 'elevated', 'downtrending'")


class SummaryDraft(BaseModel):
    """Narrative sections of a discharge summary. Diagnoses, discharge medications and
    pending reports are NOT generated - they are pulled deterministically from MediTrack."""

    presenting_complaints: str = Field(description="One or two lines: chief complaints and duration")
    hospital_course: list[str] = Field(description="4-7 concise chronological bullet points")
    procedures_performed: list[str] = Field(description="Each procedure with date and key findings; empty if none")
    key_investigations: list[KeyInvestigation] = Field(description="Only clinically significant results")
    condition_at_discharge: str
    follow_up_advice: list[str] = Field(description="Follow-up visits and instructions stated in the notes")
    diet_and_activity: list[str] = Field(description="Diet / activity / lifestyle advice stated in the notes")


class DraftResult(BaseModel):
    ip_no: str
    draft: SummaryDraft
    source: Literal["live", "cached", "template"]
    model: str
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    error: str | None = None
