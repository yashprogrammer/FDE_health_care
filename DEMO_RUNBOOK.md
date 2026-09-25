# Live demo runbook

## Before the webinar (T-30 min)

1. Put `GROQ_API_KEY` and `LOGFIRE_TOKEN` in `.env` (optionally `LOGFIRE_PROJECT_URL`).
2. `git checkout part-3-integrated` (contains all three parts).
3. `./run.sh warm`: generates and caches live drafts for every patient. If Wi-Fi or Groq fails on stage, the Copilot silently serves these cached drafts.
4. `./run.sh reset`: fresh golden state.
5. Open tabs: MediTrack `localhost:8001`, POC `localhost:8501` (`./run.sh poc` in a second terminal), Copilot `localhost:8002`, Logfire.
6. Keep `demo_assets/IP2609-0142_stent_implant_sticker.pdf` handy for the upload.

Start everything: terminal 1 `./run.sh integrated`, terminal 2 `./run.sh poc`.

## Part 1: the legacy world (Story Ch. 1–2)

| Click | Say |
|---|---|
| MediTrack → **IPD Census** | "This is CityCare's HMS. Built 2011. Vendor gone. Suresh is the only one who knows it." |
| Open **IP2609-0142** (Ramesh Kulkarni) → click through Lab / Pharmacy / Notes tabs | "To write one discharge summary, a resident copy-pastes from these 5 screens." |
| **Discharge Summary** tab | "A Word template from 2011. 35–45 minutes per patient." |
| **Reports → MIS: Discharge TAT** | "The FDE's discovery: cash 2.5 h, insured **6.3 h**, **38%** of TPA submissions bounce. Top reason: stent sticker not attached." |
| **System Admin → External Links** | "Notice this: MediTrack can show configurable links on every patient file. Remember it." |

## Part 2: the POC (Story Ch. 5, the AI engineer's showcase)

| Click | Say |
|---|---|
| POC → pick **ENC-01** → **Generate** | "Standalone Streamlit, 11 de-identified past discharges. No hospital system touched." |
| Point at 🔒 sections | "Diagnoses, meds and pending reports are **not** generated. They're pulled from source." |
| **Source trace** → add `Warfarin 5 mg OD` to the text | "Guardrail: that drug isn't in this patient's record. Red." |
| **Eval** → Run eval | "Completeness, hallucinations, faithfulness, recall vs the doctor's summary, latency, cost in rupees." |
| **Clinician feedback** | "Business verification: doctors and the TPA desk score it." |
| Logfire | "Every agent run is traced: prompt, tokens, latency, structured output." |

## Part 3: integration (Story Ch. 6)

| Click | Say |
|---|---|
| MediTrack → **External Links** → add label `Discharge Copilot`, URL `http://localhost:8002/#/review/{IP_NO}` | "The Suresh moment: integration by *configuration*, not code." |
| Open **IP2609-0142** → **Discharge Advised** | "The doctor does exactly what they did yesterday." |
| Click **[Discharge Copilot]** link | "Replica → adapter → agent. A draft in seconds." |
| TPA panel shows ❌ **Implant sticker missing** (71%) | "This is the #1 reason insurers bounced claims last quarter. Caught *before* submission." |
| Back in MediTrack → **Documents** → upload the stent sticker PDF as `IMPLANT_STKR` | "The cath lab uploads it the old way…" |
| Copilot TPA panel flashes → **86%** | "…and the Copilot sees it within seconds, via the replica." |
| Edit a hospital-course bullet → **Sign & send to MediTrack** | "The doctor stays in charge. Nothing is sent without their signature." |
| MediTrack → **Documents** tab → yellow `DSCHSUMM … BATCH_IMPORT` row → open PDF | "Delivered through MediTrack's 2013 scanner import folder. Zero changes to MediTrack." |
| Copilot → **Monitor** | "Baseline 6.3 h and 38%, versus the pilot. And the Logfire traces." |

## If something breaks

- **LLM or network down**: nothing to do. Drafts fall back to cached (after `./run.sh warm`), then to a template. The source chip shows which one was used.
- **Messed-up state**: `./run.sh reset` (≈1 s), then re-advise the patient.
- **Port busy**: `lsof -ti :8001 -ti :8002 -ti :8501 | xargs kill`
