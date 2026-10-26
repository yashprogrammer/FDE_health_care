"""Render the signed discharge summary as a PDF for MediTrack's document hot-folder.

Layout follows a typical hospital discharge summary: header strip (UHID, logo, form code), a framed page with a
General Information key/value block, History of Present Illness, clinical sections and tables, signature block,
and a footer band on every page. Facts (identity, diagnoses, medications, pending reports) are pulled from
MediTrack; only the narrative sections come from the draft.
"""
from datetime import datetime

from fpdf import FPDF
from fpdf.fonts import FontFace

from copilot_core.assemble import diagnoses_lines
from copilot_core.models import Encounter, SummaryDraft

_REPL = {"–": "-", "—": "-", "‐": "-", "‑": "-", "‒": "-", "−": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
         "•": "-", "→": "->", "≥": ">=", "≤": "<=", "µ": "u", "₹": "Rs.", "×": "x", "°": " deg", " ": " "}

NAVY = (23, 52, 94)
TEAL = (22, 101, 120)
GREY = (90, 90, 90)
LIGHT = (238, 242, 247)

LEFT, RIGHT = 16, 194          # content margins inside the frame
LABEL_X, VALUE_X = 22, 76      # key/value columns
VALUE_W = RIGHT - VALUE_X - 2

# Hospital identity (fictional, as in the rest of the demo)
HOSPITAL = "CityCare"
FORM_CODE = "CC - QF - DS - 07"
ENQUIRY = "For enquiries, appointments & Telemedicine consultations contact: 020 - 5550 1066"
REG_OFFICE = ["Registered Office: CITYCARE HOSPITALS PRIVATE LIMITED, 12 Demo Road, Pune - 411 001. Phone: 020 5550 1000",
              "e-mail: enquiry@citycare.example    Website: www.citycare.example"]


def _t(s: str) -> str:
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


def _date(s: str | None) -> str:
    """'2026-09-21 06:40' -> '21-Sep-2026'"""
    if not s:
        return "-"
    try:
        return datetime.fromisoformat(s.strip().replace("Z", "")[:19]).strftime("%d-%b-%Y")
    except ValueError:
        return s[:10]


def _history(enc: Encounter, prefixes: tuple[str, ...]) -> str:
    hit = any(d.icd10.upper().startswith(prefixes) for d in enc.diagnoses)
    return "Yes (as per diagnosis list)" if hit else "Not recorded"


class _Summary(FPDF):
    def __init__(self, enc: Encounter):
        super().__init__(format="A4")
        self.enc = enc
        self.set_auto_page_break(True, margin=30)
        self.set_margins(LEFT, 26, 210 - RIGHT)
        self.alias_nb_pages()

    # ---------------------------------------------------------- page furniture (repeated on every page)
    def header(self):
        e = self.enc
        self.set_text_color(0)
        self.set_font("Helvetica", "", 8.5)
        self.set_xy(14, 9)
        self.cell(60, 5, _t(f"UHID: {e.uhid}"))
        # logo: rounded square with a white cross + wordmark
        lx = 84
        self.set_fill_color(*NAVY)
        self.rect(lx, 7, 11, 11, style="F", round_corners=True, corner_radius=2)
        self.set_fill_color(255, 255, 255)
        self.rect(lx + 4.6, 9, 1.8, 7, style="F")
        self.rect(lx + 2.5, 11.6, 6, 1.8, style="F")
        self.set_text_color(*NAVY)
        self.set_font("Helvetica", "B", 15)
        self.set_xy(lx + 13, 6.5)
        self.cell(30, 7, HOSPITAL)
        self.set_font("Helvetica", "", 6.5)
        self.set_xy(lx + 13, 13)
        self.cell(30, 4, "H O S P I T A L S   |   P U N E")
        # form code + emergency box
        self.set_text_color(0)
        self.set_font("Helvetica", "", 8.5)
        self.set_xy(146, 7)
        self.cell(0, 4, FORM_CODE)
        self.set_fill_color(214, 69, 39)
        self.rect(146, 12.5, 50, 8, style="F", round_corners=True, corner_radius=1.2)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 6.5)
        self.set_xy(148, 13.2)
        self.cell(0, 3, "EMERGENCY 24 x 7")
        self.set_font("Helvetica", "B", 9.5)
        self.set_xy(148, 16.3)
        self.cell(0, 4, "020 - 5550 1066")
        # page frame
        self.set_draw_color(70, 70, 70)
        self.set_line_width(0.3)
        self.rect(10, 23, 190, 246, style="D", round_corners=True, corner_radius=4)
        self.set_text_color(0)
        self.set_xy(LEFT, 27)

    def footer(self):
        self.set_text_color(0)
        self.set_font("Helvetica", "I", 8)
        self.set_xy(10, 270.5)
        self.cell(190, 4, "Keep the records carefully and bring them along during your next visit to our hospital", align="R")
        self.set_fill_color(*TEAL)
        self.rect(0, 276, 210, 8, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.set_xy(0, 277.6)
        self.cell(210, 5, ENQUIRY, align="C")
        self.set_text_color(0)
        self.set_font("Helvetica", "B", 6.3)
        for i, line in enumerate(REG_OFFICE):
            self.set_xy(0, 285.5 + i * 3.4)
            self.cell(210, 3.2, line, align="C")
        self.set_font("Helvetica", "", 7)
        self.set_xy(10, 291.5)
        self.cell(190, 3, f"Page {self.page_no()} of {{nb}}", align="R")

    # ---------------------------------------------------------- building blocks
    def heading(self, text: str, size: float = 12.5, gap_before: float = 2.2):
        self.ln(gap_before)
        if self.will_page_break(14):
            self.add_page()
        self.set_font("Helvetica", "B", size)
        self.set_text_color(0)
        self.set_x(LEFT)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def kv(self, label: str, value: str, bold: bool = False):
        value = _t(value) or "-"
        self.set_font("Helvetica", "B" if bold else "", 9)
        n_lines = max(1, len(self.multi_cell(VALUE_W, 4.6, value, dry_run=True, output="LINES")))
        if self.will_page_break(n_lines * 4.6 + 2):
            self.add_page()
        y = self.get_y()
        self.set_xy(LABEL_X, y)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*GREY)
        self.cell(VALUE_X - LABEL_X, 4.6, label)
        self.set_text_color(0)
        self.set_font("Helvetica", "B" if bold else "", 9)
        self.set_xy(VALUE_X, y)
        self.multi_cell(VALUE_W, 4.6, value, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.6)

    def bullets(self, lines: list[str]):
        self.set_font("Helvetica", "", 9)
        for line in lines:
            line = _t(line)
            n = max(1, len(self.multi_cell(RIGHT - LABEL_X - 6, 4.6, line, dry_run=True, output="LINES")))
            if self.will_page_break(n * 4.6 + 1):
                self.add_page()
            y = self.get_y()
            self.set_fill_color(*NAVY)
            self.ellipse(LABEL_X + 0.6, y + 1.7, 1.4, 1.4, style="F")
            self.set_xy(LABEL_X + 5, y)
            self.multi_cell(RIGHT - LABEL_X - 6, 4.6, line, new_x="LMARGIN", new_y="NEXT")
            self.ln(0.8)

    def paragraph(self, text: str):
        self.set_font("Helvetica", "", 9)
        self.set_x(LABEL_X)
        self.multi_cell(RIGHT - LABEL_X - 2, 4.6, _t(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def grid(self, head: list[str], rows: list[list[str]], widths: list[float]):
        self.set_font("Helvetica", "", 8.5)
        self.set_fill_color(255, 255, 255)      # bullets leave the navy fill set; table rows must be plain
        self.set_draw_color(150, 150, 150)
        self.set_line_width(0.2)
        self.set_x(LABEL_X)
        with self.table(col_widths=widths, width=sum(widths), line_height=4.6, text_align="LEFT", first_row_as_headings=True,
                        headings_style=FontFace(emphasis="BOLD", fill_color=LIGHT),
                        borders_layout="ALL", align="L", padding=(1, 1.5)) as t:
            r = t.row()
            for h in head:
                r.cell(h)
            for row in rows:
                r = t.row()
                for c in row:
                    r.cell(_t(c))
        self.ln(2)


def render(enc: Encounter, d: SummaryDraft, signed_by: str, signed_at: str, path) -> None:
    pdf = _Summary(enc)
    pdf.add_page()

    # ---- title block
    pdf.set_font("Helvetica", "BU", 20)
    pdf.cell(0, 10, "Discharge Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 8, _t(f"Dept. of {enc.consultant_speciality.upper()}"), new_x="LMARGIN", new_y="NEXT")

    # ---- GENERAL INFORMATION
    pdf.heading("GENERAL INFORMATION", 12.5, gap_before=2)
    surgery_dates = sorted({_date(p.date) for p in enc.procedures})
    pdf.kv("UHID", enc.uhid)
    pdf.kv("Patient Identifier", enc.ip_no)
    pdf.kv("Ward/Bed No", f"{enc.ward}, Bed no: {enc.bed}")
    pdf.kv("Name", f"{'Mr.' if enc.sex.upper().startswith('M') else 'Ms.'} {enc.patient_name.upper()}")
    pdf.kv("Age", f"{enc.age} Yrs")
    pdf.kv("Sex", "Male" if enc.sex.upper().startswith("M") else "Female" if enc.sex.upper().startswith("F") else enc.sex)
    pdf.kv("Address", "As per registration record (not accessed by the AI)")
    pdf.kv("Primary Consultant", f"{enc.consultant}\nReg. No: {enc.consultant_reg_no or '-'}\n{enc.consultant_speciality.upper()}")
    pdf.kv("Payment", f"{enc.pay_mode.title()}" + (f" - {enc.tpa_name}" if enc.tpa_name else "")
           + (f" (Policy {enc.policy_no})" if enc.policy_no else ""))
    pdf.kv("Date of Admission", _date(enc.admission_date))
    if surgery_dates:
        pdf.kv("Date of Surgery", ", ".join(surgery_dates))
    pdf.kv("Date of Discharge", _date(enc.discharge_advised_date))
    pdf.kv("Allergies", "Not recorded in MediTrack - to be confirmed by the treating doctor")
    pdf.kv("Diagnosis", "\n".join(diagnoses_lines(enc)), bold=True)
    if enc.procedures:
        pdf.kv("Surgery / Procedures", "\n".join(p.description for p in enc.procedures))

    # ---- HISTORY OF PRESENT ILLNESS
    pdf.heading("History of Present Illness", 11.5, gap_before=2.5)
    pdf.kv("Chief Complaints", d.presenting_complaints)
    pdf.kv("History of Diabetes Mellitus", _history(enc, ("E10", "E11", "E12", "E13", "E14")))
    pdf.kv("History of Hypertension", _history(enc, ("I10", "I11", "I12", "I13", "I15")))

    # ---- clinical sections
    pdf.heading("Course in Hospital", 11.5)
    pdf.bullets(d.hospital_course)

    if d.procedures_performed:
        pdf.heading("Procedures Performed", 11.5)
        pdf.bullets(d.procedures_performed)

    if d.key_investigations:
        pdf.heading("Key Investigations", 11.5)
        pdf.grid(["Test", "Result", "Interpretation"],
                 [[k.test, k.result, k.interpretation] for k in d.key_investigations], [66, 56, 46])

    if enc.pending_labs:
        pdf.heading("Reports Pending at Discharge", 11.5)
        pdf.bullets([f"{lab.test} (sent {_date(lab.date)}) - to be reviewed at follow-up" for lab in enc.pending_labs])

    pdf.heading("Condition at Discharge", 11.5)
    pdf.paragraph(d.condition_at_discharge)

    if enc.discharge_meds:
        pdf.heading("Discharge Medications", 11.5)
        pdf.grid(["Drug", "Dose", "Route", "Frequency", "Duration"],
                 [[m.drug, m.dose, m.route, m.frequency, m.duration or "-"] for m in enc.discharge_meds],
                 [48, 26, 26, 30, 38])

    if d.follow_up_advice:
        pdf.heading("Follow-up Advice", 11.5)
        pdf.bullets(d.follow_up_advice)
    if d.diet_and_activity:
        pdf.heading("Diet & Activity", 11.5)
        pdf.bullets(d.diet_and_activity)

    # ---- signature block (kept together on one page)
    if pdf.will_page_break(19):
        pdf.add_page()
    pdf.ln(3)
    y = pdf.get_y()
    pdf.set_draw_color(120, 120, 120)
    pdf.line(130, y + 2, RIGHT - 2, y + 2)
    pdf.set_xy(130, y + 3)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(RIGHT - 132, 4.6, _t(signed_by), new_x="LEFT", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_x(130)
    pdf.cell(RIGHT - 132, 4.2, _t(f"{enc.consultant_speciality} | Reg. No: {enc.consultant_reg_no or '-'}"), new_x="LEFT", new_y="NEXT")
    pdf.set_x(130)
    pdf.cell(RIGHT - 132, 4.2, _t(f"Electronically signed on {signed_at}"), new_x="LEFT", new_y="NEXT")
    pdf.set_xy(LABEL_X, y + 3)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*GREY)
    pdf.multi_cell(96, 3.8, "Drafted with CityCare Discharge Copilot (AI-assisted). Diagnoses, medications and pending "
                   "reports are copied from MediTrack; the narrative was reviewed, edited and signed by the treating doctor.",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))
