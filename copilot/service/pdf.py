"""Render the signed discharge summary as a PDF for MediTrack's document hot-folder."""
from fpdf import FPDF

from copilot_core.assemble import diagnoses_lines, med_line
from copilot_core.models import Encounter, SummaryDraft

_REPL = {"–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"', "•": "-",
         "→": "->", "≥": ">=", "≤": "<=", "µ": "u", "₹": "Rs."}


def _t(s: str) -> str:
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


def render(enc: Encounter, d: SummaryDraft, signed_by: str, signed_at: str, path) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "CITYCARE HOSPITALS, PUNE", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "NABH Accredited | Department of " + _t(enc.consultant_speciality), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "DISCHARGE SUMMARY", align="C", border="TB", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 9.5)
    rows = [("Patient", f"{enc.patient_name} ({enc.age}/{enc.sex})", "UHID / IP No", f"{enc.uhid} / {enc.ip_no}"),
            ("Admitted", enc.admission_date, "Discharge advised", enc.discharge_advised_date or "-"),
            ("Consultant", enc.consultant, "Reg. No", enc.consultant_reg_no or "-"),
            ("Ward / Bed", f"{enc.ward} / {enc.bed}", "Payment", f"{enc.pay_mode} {enc.tpa_name or ''}".strip())]
    for a, b, c, e in rows:
        pdf.set_font("Helvetica", "B", 9.5); pdf.cell(28, 6, a)
        pdf.set_font("Helvetica", "", 9.5); pdf.cell(67, 6, _t(b))
        pdf.set_font("Helvetica", "B", 9.5); pdf.cell(32, 6, c)
        pdf.set_font("Helvetica", "", 9.5); pdf.cell(0, 6, _t(e), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    def section(title: str, lines: list[str] | str):
        if not lines:
            return
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_fill_color(230, 236, 245)
        pdf.cell(0, 6, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        for line in ([lines] if isinstance(lines, str) else [f"- {x}" for x in lines]):
            pdf.multi_cell(0, 5, _t(line), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

    section("Final Diagnosis", diagnoses_lines(enc))
    section("Presenting Complaints", d.presenting_complaints)
    section("Hospital Course", d.hospital_course)
    section("Procedures", d.procedures_performed)
    section("Key Investigations", [f"{k.test}: {k.result} ({k.interpretation})" for k in d.key_investigations])
    section("Reports Pending at Discharge",
            [f"{lab.test} (sent {lab.date[:10]}) - to be reviewed at follow-up" for lab in enc.pending_labs])
    section("Condition at Discharge", d.condition_at_discharge)
    section("Discharge Medications", [med_line(m) for m in enc.discharge_meds])
    section("Follow-up", d.follow_up_advice)
    section("Diet & Activity", d.diet_and_activity)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, _t(f"Electronically signed by {signed_by} ({enc.consultant_reg_no or '-'}) on {signed_at}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Drafted with CityCare Discharge Copilot (AI-assisted); reviewed, edited and signed by the treating doctor.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))
