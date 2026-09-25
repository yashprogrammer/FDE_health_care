# How It All Works: Hospital → Legacy → POC → Integrated

A study guide for the presenter. Read it top to bottom once and you can answer almost any audience question.

1. [The hospital discharge cycle (the domain)](#1-the-hospital-discharge-cycle)
2. [The problem we are solving](#2-the-problem)
3. [How MediTrack (the legacy system) models the cycle](#3-meditrack-the-legacy-system)
4. [The Streamlit POC](#4-the-streamlit-poc)
5. [The integrated system](#5-the-integrated-system)
6. [One-page cheat sheet](#6-cheat-sheet)

---

## 1. The hospital discharge cycle

### 1.1 The in-patient journey, end to end

An **in-patient** (IPD, in-patient department) is anyone admitted to a bed, as opposed to an out-patient (OPD) who visits and goes home the same day.

```
 ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   ┌──────────────────┐
 │ 1. ADMISSION │──►│ 2. PRE-AUTH  │──►│ 3. TREATMENT (days)  │──►│ 4. DISCHARGE     │
 │ ER or planned│   │ (insured     │   │ doctors, nurses, lab,│   │    ADVISED       │
 │ UHID + IP No │   │  patients)   │   │ pharmacy, procedures │   │ ~10 AM rounds    │
 └──────────────┘   └──────────────┘   └──────────────────────┘   └────────┬─────────┘
                                                                          │
      ┌───────────────────────────────────────────────────────────────────┘
      ▼
 ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
 │ 5. DISCHARGE     │──►│ 6. PHARMACY      │──►│ 7. FINAL BILL    │──►│ 8. TPA FINAL     │
 │    SUMMARY       │   │    RECONCILIATION│   │                  │   │    APPROVAL      │
 │ written by       │   │ unused meds back,│   │ room, procedures,│   │ (cashless only)  │
 │ resident doctor  │   │ discharge meds   │   │ implants, meds   │   │ approve / QUERY  │
 └──────────────────┘   └──────────────────┘   └──────────────────┘   └────────┬─────────┘
                                                                              │
                                              ┌───────────────────────────────┘
                                              ▼
                                   ┌──────────────────┐   ┌──────────────────┐
                                   │ 9. PATIENT LEAVES│──►│ 10. BED CLEANED, │
                                   │ with summary +   │   │ NEXT PATIENT IN  │
                                   │ prescriptions    │   │ (bed turnover)   │
                                   └──────────────────┘   └──────────────────┘
```

**Step by step:**

1. **Admission.** The patient arrives through the Emergency Room (e.g. chest pain) or as a planned admission (e.g. knee replacement). The hospital creates or reuses a **UHID** (a lifelong patient ID) and opens an **IP No** (the ID for this one stay). The patient gets a ward and bed and a treating **consultant**.
2. **Pre-authorization** (insured patients only). For a **cashless** admission, the hospital's TPA desk sends the diagnosis and estimated cost to the patient's insurer (via the **TPA**) and gets an initial approval amount.
3. **Treatment.** For several days, data piles up in different places:
   - Doctors write **progress notes** and order tests and procedures.
   - Nurses write **nursing notes** (vitals, wound care, diet).
   - The **lab** sends results. Some go to outside labs and stay **pending** for days.
   - The **pharmacy** issues drugs to the ward.
   - Procedures (angioplasty, surgery) produce **cath lab reports** or **OT notes**, and use **implants** (stents, knee joints) that come with a sticker showing brand, size and lot number.
4. **Discharge advised.** On morning rounds (~10 AM) the consultant says "OK to go home today." This is the clock-start for **discharge TAT**.
5. **Discharge summary.** A resident doctor (RMO) writes the legal and clinical summary of the stay: diagnosis, presenting complaints, hospital course, procedures, investigations, condition at discharge, discharge medications and follow-up. Today this means copy-pasting from 5+ screens into a Word template, about 35–45 minutes per patient.
6. **Pharmacy reconciliation.** Unused ward medicines go back, and discharge medicines are issued.
7. **Final bill.** Billing adds up room charges, procedures, implants, medicines and consumables.
8. **TPA final approval** (cashless only). The TPA desk sends the **final bill + discharge summary + supporting documents** to the TPA. The insurer's reviewer either **approves**, or raises a **query** such as "stent sticker missing" or "final diagnosis doesn't match pre-auth". Every query means fixing the document, resubmitting and waiting again, which adds about 2–4 hours.
9. **Patient leaves**, with the signed summary and prescriptions.
10. **The bed is cleaned and the next patient is admitted.** Until step 9 happens, the ER patient waiting for this bed stays on a trolley.

### 1.2 Glossary (terms the audience will hear)

| Term | Meaning |
|---|---|
| **IPD / OPD** | In-patient (admitted) / out-patient (visit only) department |
| **UHID** | Unique Health ID: the patient's lifelong ID at this hospital |
| **IP No** | In-patient number: one per admission (one patient can have many) |
| **ADT** | Admit–Discharge–Transfer: the core events of a hospital stay |
| **Consultant** | The senior treating doctor responsible for the patient |
| **RMO / Resident** | Resident Medical Officer: junior doctor who does most of the paperwork |
| **Progress / nursing notes** | Free-text notes written by doctors / nurses during the stay |
| **ICD-10** | International diagnosis codes (e.g. `I21.0` = anterior-wall heart attack). Insurers use them. |
| **CPT** | Procedure codes (e.g. `92928` = coronary stent). Used for billing and insurance. |
| **Provisional vs final diagnosis** | The first guess at admission vs the confirmed diagnosis at discharge. Insurers compare them. |
| **LIS / HL7** | Lab Information System; HL7 v2 is the 1980s-era message format labs use to send results |
| **Pending report** | A test sent (often outside) whose result hasn't come back by discharge |
| **Discharge summary** | The legal and clinical record of the stay, given to the patient and the insurer |
| **Cash vs cashless** | Cash: patient pays and may claim later. Cashless: the insurer pays the hospital directly, which needs approvals. |
| **Insurer / TPA** | The insurer holds the policy. The TPA (Third-Party Administrator) processes claims for the insurer. |
| **Pre-auth** | Approval at admission for an estimated amount |
| **Final approval** | Approval at discharge for the final bill. Required before a cashless patient can leave. |
| **TPA query** | The insurer's pushback asking for missing or clarifying information. Adds hours. |
| **Implant sticker** | The label from a stent or joint box (brand, size, lot). Insurers insist on it. |
| **MRD** | Medical Records Department: scans and files documents |
| **MIS** | Management Information System: the reporting side of the HMS |
| **NABH** | Indian hospital accreditation body, which sets documentation standards |
| **Discharge TAT** | Turn-around time from "discharge advised" to "patient leaves" |
| **ARPOB** | Average Revenue Per Occupied Bed per day: how hospitals value bed time |
| **DPDP Act** | India's Digital Personal Data Protection Act, 2023: governs patient data |

### 1.3 The people involved (stakeholders)

| Who | What they care about | What they touch |
|---|---|---|
| Consultant (Dr. Anjali Mehta) | Clinical accuracy, signing responsibility | Reviews and signs the summary |
| Resident / RMO (Dr. Karan Shah) | Time. They write most summaries. | MediTrack, the Word template |
| Nurses | Patient flow, handover | Nursing notes |
| Pharmacy | Correct discharge meds | Pharmacy issue screen |
| TPA desk (Mrs. Kapoor) | Fewer insurer queries | Collects documents, submits to TPA |
| Billing | Complete bill | Final bill |
| Hospital IT (Suresh) | "Don't break MediTrack", security | MediTrack admin, replica |
| CEO / CFO | Bed turnover, revenue, complaints | MIS reports |
| Patient and family | Going home on time | Waiting in the room |

---

## 2. The problem

### 2.1 What the CEO asked for vs what is actually wrong

- **Asked:** "Doctors are drowning in paperwork. Build us a ChatGPT for discharge summaries."
- **Found (by the FDE, from the data):** insured patients wait **~6.3 hours** after discharge is advised, versus **~2.5 hours** for cash patients. The difference comes almost entirely from steps 5 and 8:
  1. **The summary is slow**: 35–45 min of copy-paste from 5 screens, and it isn't started until rounds are over.
  2. **The summary is often incomplete for the insurer**: **38%** of TPA submissions come back with a query. Top reasons: stent sticker not attached, operation notes missing, diagnosis/procedure mismatch, pending report not mentioned, doctor's registration number missing.

> **Real problem statement:** Insured patients wait over 6 hours to go home because discharge summaries are slow to write *and* often incomplete for insurers. That blocks beds and frustrates patients.

### 2.2 Why it matters (the business case, illustrative)

- 60 discharges/day × 60% insured = 36 insured discharges/day
- ~3 hours saved each ≈ 108 bed-hours/day ≈ **4.5 beds freed every day**
- × ₹35,000 ARPOB (illustrative) ≈ **₹5.7 crore/year potential**, *if* there's waiting demand (ER boarding, elective backlog)
- Plus ~28 resident-hours/day back to patient care, and the #1 patient complaint addressed

### 2.3 The solution in one line

**Discharge Copilot:** the moment discharge is advised, an AI drafts the summary from data already in MediTrack, a **rules engine** checks it against what insurers query, and the **doctor reviews, edits and signs** inside MediTrack. The signed PDF goes back into MediTrack automatically.

---

## 3. MediTrack: the legacy system

**Run:** `./run.sh legacy` → http://localhost:8001 (branch `part-1-legacy`)

### 3.1 What it is

MediTrack HMS v3.2 was built in 2011 by a vendor that no longer exists. In the story it runs on Oracle; in our demo it's **FastAPI + SQLite + a React UI styled like 2011**. Only Suresh in IT understands it. The table names are cryptic (`PT_MST`, `IP_ADM_DTL`…) because nobody documented them.

### 3.2 Mapping the hospital cycle to MediTrack

| Cycle step | Where it lives in MediTrack (screen) | Table(s) | Demo data for golden patient Ramesh Kulkarni (IP2609-0142) |
|---|---|---|---|
| 1. Admission | IPD Census, patient file header | `PT_MST` (patient), `IP_ADM_DTL` (admission) | Admitted 21/09 06:40 via ER, Ward 4B-CARD bed 12, Dr. Anjali Mehta |
| 2. Pre-auth / payment | Header: Pay Mode, TPA, Policy No | `IP_ADM_DTL.PAY_MODE, TPA_NM, POL_NO` | CASHLESS · SecureHealth TPA |
| 3a. Diagnoses | **Diagnosis** tab | `IP_DIAG_DTL` (PROV / FINAL) | STEMI `I21.0`, hypertension `I10`, hyperlipidaemia `E78.5` |
| 3b. Procedures | **Procedures** tab | `IP_PROC_DTL` (CPT codes) | Angiography `93458`, stent `92928` |
| 3c. Labs (from LIS via HL7) | **Lab Results** tab | `LAB_RSLT` (FINAL / PENDING) | Troponin 12.4 → 3.1, LVEF 40%, **Lp(a) PENDING** |
| 3d. Pharmacy | **Pharmacy** tab | `PHR_ISS_DTL` (INPATIENT / DISCHARGE) | 7 in-patient drugs, 7 discharge drugs |
| 3e. Notes | **Clinical Notes** tab | `CLN_NOTE` (DR / NRS) | 5 doctor notes + 3 nursing notes |
| 3f. Documents | **Documents** tab (+ upload) | `PT_DOC` | ID proof, consent, cath report. **Implant sticker missing.** |
| 4. Discharge advised | **Discharge Advised** button | `IP_ADM_DTL.STS = 'DA'`, `DSCH_ADV_DT` | You click it during the demo |
| 5. Discharge summary | **Discharge Summary** tab + "Download DS Template (.doc)" | `IP_DSCH_SUMM` | Empty. The resident would type it by hand. |
| 8. TPA approval | **TPA** tab | `TPA_CLM_DTL` (APPROVED / QUERY + reason) | Past patients show real query reasons |
| 9. Patient leaves | **Final Discharge** button | `IP_ADM_DTL.STS = 'DSCH'`, `DSCH_DT` | |
| Management view | **Reports → MIS: Discharge TAT** | Aggregates the above | **2.5 h cash / 6.3 h cashless / 38.1% queries** |

**The pain, as seen in MediTrack:** the information for one summary sits in **6 different tabs** (Diagnosis, Procedures, Lab Results, Pharmacy, Clinical Notes, Documents). The Discharge Summary tab is a blank text box plus a Word template.

### 3.3 The seeded data

| Set | Count | Purpose |
|---|---|---|
| Current in-patients | 8 | The census you demo. Mix of Cardiology, Medicine, Ortho and Surgery, and of cash and cashless. Includes the **golden patient**, one patient with only a *provisional* diagnosis (Vikram Patil), and one surgery with OT notes missing (Priya Iyer). |
| Past discharges with doctor-written summaries | 11 | Exported (de-identified) for the POC. The doctor summaries are the "ground truth" for evals. |
| Historic MIS rows | 140 | ~3 months of admissions with timestamps and TPA claim outcomes, which produce the 6.3 h / 38% baseline |

### 3.4 The extension points an FDE discovers (with Suresh)

The FDE can't modify MediTrack's code (vendor gone, no source, IT forbids it). But MediTrack already has three doors:

| Extension point | Built for | How the Copilot uses it |
|---|---|---|
| **MIS reporting replica** (read-only copy of the DB) | Monthly management reports | The Copilot *reads* patient data from here, never from the live DB |
| **System Admin → External Links**, which can show as a link *or* as a **patient-file tab** | Opening the PACS X-ray viewer (2016) | The "AI Discharge Draft" tab is added *by configuration* |
| **Batch document import hot-folder** | MRD's document scanner (2013). Drop `IPNO_DOCTYPE_TIMESTAMP.pdf` and it's filed. | The signed summary PDF is written back here |

The `/int/*` APIs exist, but they're **internal**: used only by MediTrack's own screens, undocumented, and off-limits to other systems by IT policy.

---

## 4. The Streamlit POC

**Run:** `./run.sh poc` → http://localhost:8501 (branch `part-2-poc`)

### 4.1 Why a POC first

Before touching a live hospital system, prove on **past, de-identified data** that:
1. the AI can draft summaries **accurately** (no invented facts),
2. it's **fast and cheap** enough,
3. **doctors and the TPA desk** find it useful.

It's deliberately standalone: it reads a JSON file and connects to nothing.

### 4.2 Data

`poc/export_deidentified.py` ("the export Suresh ran for us") reads the 11 past discharges **read-only**, then masks names (`Patient ENC-01`), hashes the UHID and hides the policy number, and writes `poc/data/deidentified_encounters.json`. Each record includes the doctor's original summary for comparison.

### 4.3 The AI core (`copilot_core/`): the AI engineer's slice

```
Encounter (clean JSON contract)          <- built from MediTrack tables by encounter.py
   │  for_llm(): strips name, UHID, policy, meds list
   ▼
Pydantic AI agent (agent.py)             <- groq:openai/gpt-oss-20b, NativeOutput(SummaryDraft)
   │  typed output, schema-enforced by Groq
   ▼
SummaryDraft (narrative sections only)
   │
   ├─► trace.py       guardrail: every drug / lab / number checked against source data
   ├─► rules.py       TPA-readiness checklist (deterministic rules, no AI)
   └─► assemble.py    final summary = 🔒 deterministic facts + AI narrative
```

**The most important design decision is what the AI is *not* allowed to write:**

| Section | Who writes it | Why |
|---|---|---|
| Final diagnosis + ICD codes | 🔒 MediTrack data | Legal and insurance fact. Already coded. |
| Discharge medications | 🔒 Pharmacy data | A hallucinated dose is a patient-safety event |
| Pending reports | 🔒 Lab data | Insurers query when these are missing |
| Presenting complaints, hospital course, procedure findings, key investigations, condition, follow-up, diet | 🤖 AI draft, doctor-editable | Turning messy notes into a clear narrative is what LLMs are good at |
| TPA readiness | ⚙️ Rules engine | The insurer's rules are known, so use code, not AI |

**Other safety features:**
- **Fallback chain:** live LLM → cached draft (from `./run.sh warm`) → template built from the data. The demo never dies.
- **Retry and limits:** one retry on provider errors; reasoning effort capped so the model can't use its whole token budget.
- **Logfire:** every run is traced (prompt, tokens, latency, output).

### 4.4 The four tabs

| Tab | What it shows | What to point out |
|---|---|---|
| **⚡ Generate** | Source data (expander) → **Generate** → metric strip (source, latency, tokens, ₹ cost, TPA %) → assembled summary + TPA checklist | 🔒 sections are pulled, not generated. The checklist is rules, not AI. |
| **🔍 Source trace** | The draft as editable text, with every drug / lab / number highlighted: 🟩 verified · 🟨 unverified number · 🟥 not in record | Type `Warfarin 5 mg OD` → it turns red. Change a date to `09/09/2026` → it turns yellow (not a date in this patient's record). |
| **📊 Eval** | Runs all 11 encounters and scores each one | See the metrics below |
| **👩‍⚕️ Clinician feedback** | AI draft vs the doctor's original, side by side. Reviewers rate accuracy, completeness and usefulness, and say whether they'd sign. | This is the *business* verification step from the story |

### 4.5 Eval metrics and the latest live results (gpt-oss-20b)

| Metric | Definition | Result |
|---|---|---|
| Hallucinated | Drugs / lab tests not in the patient's record | **0** |
| Faithfulness | Verified entities ÷ all entities | **100%** |
| Key-fact recall | Share of facts (drugs, tests, numbers) in the doctor's summary that the AI draft also mentions (excluding the med list) | **75%** |
| Completeness | Required sections present | **90%** |
| Latency | Per draft | **~0.8 s median** |
| Cost | Per draft | **~$0.0002 (≈ ₹0.02)** |

**What the POC taught us** (these are good stories to tell the audience):
1. **The model's first output mode failed.** Groq rejected gpt-oss-20b's tool-call output, and every draft silently fell back to the template. Switching to *native structured output* fixed it. *Lesson: test with the real model and provider, not just the framework.*
2. **The model got dates wrong** (e.g. "09/09/2026" for a 21/09/2026 procedure) because it had to convert the data's `2026-09-21` into Indian DD/MM format. Worse, the first guardrail missed it, because it checked numbers one at a time and 09 appears elsewhere in the record. Two fixes: dates are handed to the model **already in DD/MM/YYYY** (it copies instead of converting), and the guardrail now verifies **whole dates** against the record. *Lesson: prevent at the input, catch at the output, and a doctor still signs.*
3. **Follow-up advice is often missing**, because doctors don't write the follow-up plan in the notes. It only exists in their head when they write the summary. *This is an FDE finding, not a model bug: the fix is a process change (add a follow-up line to the final ward note).*

---

## 5. The integrated system

**Run:** `./run.sh integrated` → open MediTrack at http://localhost:8001. The Copilot service runs on :8002 but has **no screens of its own**: users only ever see MediTrack. (Branch `part-3-integrated`.)

### 5.1 Architecture

```
                    ┌────────────────────────────── MediTrack (unchanged code) ───────────────────────────┐
                    │                                                                                      │
 Doctor clicks ───► │  Patient file ─ [Discharge Advised]        tabs: Diagnosis … TPA │ AI Discharge Draft │ │
                    │        │ writes STS='DA'                                           (config: External  │
                    │        ▼                                                             Links → TAB)     │
                    │   meditrack.db (primary) ◄── never touched by Copilot                     │           │
                    │        │                                          import hot-folder ◄─────┼──────┐    │
                    └────────┼──────────────────────────────────────────────────────────────────┼──────┼────┘
                             │ replica_sync.py (IT's MIS replica, every 3 s)                     │      │
                             ▼                                                                   │      │
                      replica.db (READ-ONLY) ◄──────────┐                                        │      │
                             │ adapter polls every 2 s  │ TPA checks re-read live                │      │
                             ▼                          │                                        │      │
             ┌──────────── Discharge Copilot service (FastAPI :8002) ────────────┐               │      │
             │  adapter: new STS='DA' → load_encounter → agent → trace → store    │               │      │
             │  copilot.db (own drafts + audit)                                   │               │      │
             │  API: /api/drafts, /checks, PUT edit, /sign, /pdf, /metrics        │               │      │
             │  UI:  #/embed/review/{IP_NO}  ── shown inside MediTrack tab ───────┼───────────────┘      │
             │  sign → render PDF → IPNO_DSCHSUMM_<ts>.pdf ───────────────────────┼──────────────────────┘
             └──────────────────────────── traces → Logfire ──────────────────────┘
```

### 5.2 The golden path, second by second

| t | Where | What happens |
|---|---|---|
| 0 s | MediTrack | Doctor clicks **Discharge Advised** for Ramesh (MediTrack sets `STS='DA'`, as it always has) |
| ≤3 s | replica_sync | The change is copied into `replica.db` |
| ≤2 s | Copilot adapter | Sees a new `DA` patient, logs `DISCHARGE_ADVISED_DETECTED` |
| ~1 s | copilot_core | Builds the Encounter from the replica → Pydantic AI agent → draft (≈3.4k tokens) → guardrail → saved |
| **~5–7 s total** | MediTrack **AI Discharge Draft** tab | "Waiting" turns into the full draft, with **TPA readiness 71%**: ❌ implant sticker missing |
| | MediTrack Documents tab | Cath lab uploads the stent sticker (`demo_assets/…pdf`, type `IMPLANT_STKR`) the old way |
| ≤3 s later | AI tab | TPA panel re-reads the replica and updates to **86%** |
| | AI tab | Doctor edits a line → **Sign Discharge Summary** (warns if checks still fail) |
| ≤3 s | MediTrack importer | PDF picked up from the hot-folder → **Documents tab** shows `DSCHSUMM … BATCH_IMPORT` (yellow row) |
| | Logfire | One trace shows the whole chain: replica read → agent → guardrail → PDF write-back |

### 5.3 Components

| Component | File | Role |
|---|---|---|
| Replica sync | `copilot/replica_sync.py` | Stands in for IT's MIS replica (in reality, Oracle Data Guard). Atomic copy every 3 s. |
| Adapter | `copilot/service/app.py` (`adapter_loop`) | Watches for `STS='DA'` and drafts each patient once |
| AI core | `copilot_core/*` | Same code as the POC, promoted to production |
| Copilot store | `copilot/data/copilot.db` | Drafts, edits, signatures, audit events. Separate from MediTrack by design. |
| AI Discharge Draft tab | `copilot/ui` → `#/embed/review/{IP_NO}` | **The only new screen.** Rendered inside MediTrack using MediTrack's own stylesheet (copied verbatim), with fields in the order of MediTrack's paper form MRD/DS/07 |
| PDF write-back | `copilot/service/pdf.py` + hot-folder | Signed summary returns to MediTrack's own records |
| Observability | Logfire | Spans: `adapter.process_discharge` → `discharge_copilot.generate_draft` → agent run → `writeback.hotfolder` |

### 5.4 What changed in MediTrack? Configuration only

| Change | Type | Who does it | Training impact |
|---|---|---|---|
| One row in **System Admin → External Links**: `AI Discharge Draft`, URL `http://localhost:8002/#/embed/review/{IP_NO}`, Display = **Patient file tab** | Configuration | Hospital IT (Suresh), 1 minute | None |
| New tab in the patient file, **identical in look and layout** to the other tabs (same stylesheet, grid tables, status strip, bevelled buttons, form MRD/DS/07 order) | Appears automatically | – | ~5 minutes: "open the tab, check, edit, sign" |
| "Discharge Advised" button, Documents tab, everything else | **Unchanged** | – | None |

**Why a tab and not a new app:** 300 doctors and nurses already know MediTrack. A new app means new logins, new training and resistance. A tab that looks native means the only new habit is *"after Discharge Advised, open the AI tab."* Adoption is part of the FDE's job, not an afterthought.

### 5.5 Safety and trust design (what IT and compliance will ask)

| Question | Answer |
|---|---|
| Can it break MediTrack? | No. It only reads the replica and writes through MediTrack's own import folder. MediTrack's DB is never written. |
| Does patient data go to the LLM? | Only clinical facts. Name, UHID, policy number and the med list are stripped (`Encounter.for_llm`). In production: zero-data-retention endpoints or a region-approved host. |
| What if the AI is wrong? | Guardrails flag unverified facts, the rules engine checks completeness, and **a doctor must sign**. Nothing is sent automatically. |
| What if the LLM or network is down? | Cached draft → template. Doctors can always fall back to the old Word template. |
| Audit? | Every detection, draft, edit (with % changed) and signature is logged in `copilot.db` and traced in Logfire |

---

## 6. Cheat sheet

- **Domain in one line:** cashless patients wait for the insurer's final approval, which needs a complete discharge summary. Slow and incomplete summaries → 6.3 h waits, 38% queries.
- **Legacy in one line:** data lives in 6 MediTrack tabs. The summary is typed by hand. Three hidden doors: replica, External Links (link/tab), document hot-folder.
- **POC in one line:** Pydantic AI + gpt-oss-20b drafts the narrative. Diagnoses and meds are pulled, never generated. A guardrail and evals prove it: 0 hallucinations, 100% faithful, ₹0.02 per summary.
- **Integrated in one line:** same MediTrack UI plus one new tab. Click "Discharge Advised" as usual → a draft appears in the AI Discharge Draft tab within seconds → doctor signs → PDF lands in the Documents tab. Added by configuration.
- **FDE vs AI engineer in one line:** the AI engineer built `copilot_core`. The FDE found the real problem, the three doors, the "tab not app" adoption decision and the business case, and made it all work in the hospital.
