# Project Summary: "Same Feature, Two Engineers" Webinar + CityCare Discharge Copilot

A complete record of what was planned, decided, built, found and fixed while preparing the FDE vs AI Engineer webinar and its live demo.

> All hospitals, people, patients, policies and TPAs in this project are **fictional**. Business numbers are **illustrative**.

---

## Contents

1. [Goal](#1-goal)
2. [Timeline of the work](#2-timeline-of-the-work)
3. [Webinar content](#3-webinar-content)
4. [Design decisions (grill-me session)](#4-design-decisions-grill-me-session)
5. [What was built](#5-what-was-built)
6. [Making the live LLM work: problems and fixes](#6-making-the-live-llm-work-problems-and-fixes)
7. [How the integrated UI evolved](#7-how-the-integrated-ui-evolved)
8. [All bugs found and fixed](#8-all-bugs-found-and-fixed)
9. [Eval results (final)](#9-eval-results-final)
10. [Legacy system architecture (MediTrack)](#10-legacy-system-architecture-meditrack)
11. [Why the External Link is needed](#11-why-the-external-link-is-needed)
12. [How to run everything](#12-how-to-run-everything)
13. [Live demo flow](#13-live-demo-flow)
14. [Repository and branch map](#14-repository-and-branch-map)
15. [Documents produced](#15-documents-produced)
16. [Known limitations and caveats](#16-known-limitations-and-caveats)
17. [Sources used for the FDE job-description research](#17-sources-used-for-the-fde-job-description-research)

---

## 1. Goal

A live webinar showing **the same application and feature built from two points of view**:

| | Forward Deployed Engineer (FDE) | AI Engineer |
|---|---|---|
| Owns | The whole problem: domain and legacy-system understanding, problem discovery, brainstorming, stakeholder meetings, HLD/LLD, business pitch, value proposition, POC, integration with the legacy system | The AI component: agent, prompts, structured output, guardrails, evals, observability |
| Core question | "What should we build, why, and how does it survive in *their* world?" | "How do I build this well?" |

The key message is **not** that the AI engineer does less. The work is *different*: the FDE carries the heavy, ambiguous work around the AI.

**Running example:** *Discharge Copilot*, an AI feature added to **MediTrack HMS v3.2**, the 14-year-old hospital system at the fictional **CityCare Hospitals, Pune**. It was built in three stages (legacy → POC → integrated) so the audience can see each stage.

---

## 2. Timeline of the work

| # | Phase | Outcome |
|---|---|---|
| 1 | Webinar content | Researched real FDE job postings (Google, AWS, Microsoft, OpenAI, Anthropic, Palantir) and wrote content for all 10 webinar sections → `webinar/webinar-content.md` |
| 2 | `/grill-me` design session | Locked the scenario, timeline, stack, LLM, POC scope, observability, integration design, run/reset and git strategy (see §4) |
| 3 | Part 1 build | MediTrack legacy HMS: FastAPI + SQLite + React UI made to look like 2011, with seeded data that reproduces the story's numbers |
| 4 | Part 2 build | Streamlit POC + shared AI core (`copilot_core`) with Pydantic AI, Logfire, a guardrail, a rules engine and evals |
| 5 | Part 3 build | Integrated system: replica sync, adapter, Copilot service, PDF write-back to MediTrack's hot-folder |
| 6 | Docs | README, DEMO_RUNBOOK; webinar story aligned with what was built |
| 7 | Live LLM bring-up | Groq keys added → found and fixed the structured-output, token-budget, prompt and guardrail issues (§6) |
| 8 | System explainer | Hospital cycle, glossary, problem, legacy mapping, POC and integrated explainer → `webinar/system-explainer.md` |
| 9 | UI: "tab, not a new app" | The AI review moved *inside* MediTrack as a patient-file tab added by configuration |
| 10 | UI: "same UI + one feature" | Separate modern Copilot app removed. The tab is rebuilt from MediTrack's own stylesheet and layout. A date bug was found and fixed. |
| 11 | Explanations | How to run each part, why the External Link is needed, detailed legacy architecture |
| – | *(separate session)* | HLD and LLD design PDFs added under `docs/` (§15) |

---

## 3. Webinar content

File: **`webinar/webinar-content.md`** (about 75 minutes plus Q&A)

| # | Section | Time | Highlights |
|---|---|---|---|
| 1 | Hook: same feature, two POVs | 7 min | Two calendars side by side: AI engineer = a 10-day ticket, FDE = a 10-week engagement. An iceberg visual where the AI engineer owns the tip and the FDE owns the whole iceberg. |
| 2 | What is an FDE | 6 min | Definition; origin (military term; Palantir "Deltas" and "Echos"); why now (≈95% of GenAI pilots show no impact; FDE postings up ≈800% in Jan–Sep 2025) |
| 3 | Roles, from real job postings | 8 min | Google, AWS, Microsoft AI (Mayo Clinic, healthcare legacy systems), OpenAI, Anthropic, Palantir → 8 core responsibilities, skills, reported pay ranges |
| 4 | FDE vs AI Engineer | 6 min | Comparison table plus two myths ("FDE = AI eng + soft skills", "AI eng = junior FDE") |
| 5 | Analogy | 7 min | **Renovating a house while the family still lives in it**: architect-cum-site-lead = FDE, smart-home/electrical specialist = AI engineer. Grandma's knees = the hidden real need. Load-bearing walls = the legacy core. |
| 6 | Lifecycle matrix | 7 min | 19 activities from "human problem" to "software". The AI engineer *owns* about 4 of them. |
| 7 | Role confusion | 6 min | Consultant, project manager, solutions architect, sales engineer, product manager, business analyst, customer success/TAM, implementation engineer, ML engineer, plus a memory-hook slide |
| 8 | The story | 18 min | Ananya (FDE) at CityCare, chapters 0–6, with the artifacts produced in each chapter |
| 9 | The reveal | 4 min | Grey out everything except the AI engineer's slice (POC AI pipeline + model monitoring) |
| 10 | Quiz | 6–8 min | 4 medium-level multiple-choice questions with explanations |

**Story arc (Chapter 0–6):** the CEO asks for "ChatGPT for discharge summaries" → ward shadowing and legacy archaeology → data shows insured patients wait **6.3 h** vs 2.5 h for cash patients, and **38%** of insurer submissions get a query → options analysis (no auto-send, no HMS replacement) → technical and business meetings (HLD, LLD, business case ≈ ₹5.7 crore/year potential, illustrative) → POC and verification → integration through MediTrack's existing extension points, a **tab and not a new app**, shadow mode, pilot, expansion.

---

## 4. Design decisions (grill-me session)

| Question | Decision |
|---|---|
| Scenario | **Discharge Copilot**, exactly as in the story |
| Timeline / delivery | Build the same day; live demo; scripted golden patient; offline fallback |
| Legacy stack | User preferred FastAPI, Streamlit and React (not Flask) → **FastAPI + SQLite + React styled like 2011** |
| POC stack | **Streamlit** (realistic: FDEs often prototype in Streamlit) |
| Integrated stack | **FastAPI** service + **React** UI (later reduced to a single MediTrack-native tab, §7) |
| LLM provider / model | **Groq**, model **`openai/gpt-oss-20b`** (user's choice) |
| AI framework / observability | **Pydantic AI** agent with typed output + **Logfire** traces (POC and integrated) |
| POC scope | 4 tabs: **Generate, Source trace, Eval, Clinician feedback** |
| Data | ~8 current in-patients (1 golden patient) + ~10 past discharges with doctor-written summaries (ended up as **11**) |
| Integration design | Replica sync → polling adapter → config-based entry point → **hot-folder PDF write-back** |
| Run / reset | `./run.sh legacy / poc / integrated / reset / warm`. The External Link is added **live on stage** (the "Suresh moment"). |
| Git | Local repo, **stacked branches**: `part-1-legacy` → `part-2-poc` → `part-3-integrated` (`main` = webinar docs) |

---

## 5. What was built

### Part 1: MediTrack HMS v3.2 (legacy), branch `part-1-legacy`

- **FastAPI** backend (`legacy_meditrack/backend/app.py`) with *internal-only* `/int/*` endpoints
- **SQLite** with 13 cryptic tables (`PT_MST`, `IP_ADM_DTL`, `LAB_RSLT`, `PHR_ISS_DTL`, …)
- **React** UI made to look like 2011: Tahoma 11px, grey bevels, navy tables, maintenance ticker, "Best viewed in IE 8"
- Screens: IPD Census, Discharged Patients, Patient File (9 tabs + configured tabs), MIS Discharge TAT, External Links admin, Audit Trail
- Seed data:
  - **8 current patients**, including the golden patient **IP2609-0142, Ramesh Kulkarni** (anterior STEMI, PTCA + stent, cashless; stent implant sticker deliberately missing)
  - **11 past discharges** with doctor-written summaries
  - **140 historic** MIS rows that reproduce **cash 2.5 h, cashless 6.3 h, 38.1% TPA queries**
- Existing extension points: **External Links** (link *or* patient-file tab), **document import hot-folder** (polled every 3 s), and the MIS replica concept
- Later additions on this branch:
  - Display mode `LINK` / `TAB` for External Links
  - Every tab click reloads the data
  - Embedded tabs auto-size to their content via `postMessage`
  - `index.html` served with `no-cache`

### Part 2: Streamlit POC + AI core, branch `part-2-poc`

- `poc/export_deidentified.py`: read-only export of 11 past discharges with names masked, UHID hashed and policy hidden → `poc/data/deidentified_encounters.json`
- **`copilot_core/`** (the AI engineer's slice, reused by Part 3):

| Module | Role |
|---|---|
| `models.py` | `Encounter` input contract and `SummaryDraft` output contract. `for_llm()` strips identifiers and pre-formats dates as DD/MM/YYYY. |
| `encounter.py` | Adapter from MediTrack tables → `Encounter`, plus `deidentify()` |
| `agent.py` | Pydantic AI agent, `groq:openai/gpt-oss-20b`, `NativeOutput(SummaryDraft)`, reasoning effort set to low, `max_tokens=6000`, one retry. Fallback chain **live → cached → template**. |
| `trace.py` | Guardrail. Every drug, lab test, **whole date** and number is checked against the patient's record (verified / unverified / not in record). |
| `rules.py` | TPA-readiness checklist (deterministic): final diagnosis, diagnosis–procedure match, required documents (cath report, implant sticker, OT notes), pending reports, doctor registration number, discharge meds, policy |
| `assemble.py` | Final summary = 🔒 deterministic facts (diagnoses, discharge meds, pending reports) + AI narrative |
| `observability.py` | Logfire setup (only when `LOGFIRE_TOKEN` is set) |

- **What the AI may NOT write:** diagnoses and ICD codes, discharge medications, pending reports. These are always pulled from MediTrack data.
- POC tabs:
  - **Generate**: draft, metrics (source, latency, tokens, ₹ cost, TPA %), TPA checklist
  - **Source trace**: editable text with highlighting. Type "Warfarin 5 mg OD" to see it flagged.
  - **Eval**: all 11 encounters scored
  - **Clinician feedback**: ratings and "would you sign?"
- `scripts/warm_cache.py` (`./run.sh warm`) is the **only** thing that writes the committed fallback drafts in `copilot_core/cache/`

### Part 3: integrated system, branch `part-3-integrated`

```
MediTrack (unchanged)  ─ STS='DA' ─►  replica_sync (every 3 s) ─► replica.db (read-only)
                                                                      │
                               adapter polls every 2 s (copilot/service/app.py)
                                                                      ▼
                   copilot_core: Encounter → agent → guardrail → TPA rules → copilot.db
                                                                      │
   MediTrack patient file ── tab "AI Discharge Draft" (config row, iframe) ◄── /#/embed/review/{IP_NO}
                                                                      │ doctor edits + signs
   MediTrack Documents tab ◄── hot-folder importer ◄── signed PDF IPNO_DSCHSUMM_<ts>.pdf
```

- `copilot/replica_sync.py`: atomic SQLite backup every 3 s. It stands in for IT's Oracle Data Guard MIS replica.
- `copilot/service/app.py`:
  - background adapter
  - API: `/api/drafts`, `/api/drafts/{ip}`, `/checks`, `PUT` edit, `/regenerate`, `/sign`, `/pdf`, `/metrics`
  - its own `copilot.db` for drafts and audit events
- `copilot/service/pdf.py`: renders the signed summary (fpdf2) and writes it to MediTrack's hot-folder as a `.part` file, then renames it so the importer never sees a half-written file
- `copilot/ui`: **one screen only**, the AI Discharge Draft tab, built with MediTrack's own stylesheet (copied verbatim) and following the field order of MediTrack's discharge summary form (MRD/DS/07)
- Logfire spans: `adapter.process_discharge` → `discharge_copilot.generate_draft` → agent run → `writeback.hotfolder`

---

## 6. Making the live LLM work: problems and fixes

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | Every draft silently fell back to the template | Groq rejected gpt-oss-20b output in Pydantic AI's default *tool-call* output mode (`output_parse_failed`) | Switched to **`NativeOutput`** (Groq's JSON-schema structured outputs). Result: about 1–2 s per draft. |
| 2 | 3 of 19 drafts failed | (a) The model omitted list fields, so Groq rejected the schema. (b) On the richest record, reasoning used up the whole token budget. | List fields given defaults (optional in the schema); `groq_reasoning_effort="low"`, `max_tokens=6000`, `temperature=0.2`; one retry. Result: **19 of 19 live**. |
| 3 | Golden draft had an empty Procedures section, a predicted (wrong) discharge date, and two-digit years | Prompt too loose | Prompt rules: list *every* procedure, never state or predict a discharge date, fill every field |
| 4 | Guardrail false alarms | CPT codes weren't in the source corpus, and two-digit years were flagged | Added procedure codes to the corpus; years 20xx also accept "xx" |
| 5 | Live draft wrote **09/09/2026** for a 21/09/2026 procedure, and the guardrail missed it | The model had to convert ISO dates to DD/MM; the guardrail checked numbers one at a time | **Dates are pre-formatted DD/MM/YYYY** before reaching the model. The guardrail verifies **whole dates**. Result: 3 of 3 golden runs had correct dates. |
| 6 | "1.7" (creatinine) flagged as a date | The date pattern allowed `.` as a separator | Date separators limited to `/`, plus `-` only when a year is present |
| 7 | Git branch switching blocked after demos | Live runs overwrote the committed cache files | Only `./run.sh warm` writes the cache (`config.WRITE_CACHE`) |

**Teaching lessons from these fixes:**
- Test with the real model and provider, not just the framework.
- Prevent problems at the input *and* catch them at the output, and keep a doctor's signature at the end.
- Missing follow-up advice is a **process gap** (doctors don't write it in the notes), not a model bug.

---

## 7. How the integrated UI evolved

| Version | What it was | Why it changed |
|---|---|---|
| v1 | Separate modern Copilot app on :8002 (worklist, review, monitor), opened from a MediTrack *link* | A new app means logins, training and resistance for hospital staff |
| v2 | Review screen embedded as a MediTrack **tab** (by configuration) with a "classic-looking" skin | User: the integrated UI still looked very different from MediTrack |
| **v3 (final)** | **Same MediTrack UI + one feature.** The tab uses MediTrack's own stylesheet, fieldsets, grid tables, status strip and button wording, in the MRD/DS/07 form order. The separate modern app is **removed**; :8002 has no screens of its own. | Minimal retraining: the only new habit is "after Discharge Advised, open the AI tab" |

Final tab contents:
- **Status strip:** draft status, prepared by, prep time, TPA readiness, advised, ready, signed by/on
- **Buttons:** Save Draft · Prepare New Draft · Print Preview · Sign Discharge Summary
- **Main column:** Diagnosis (LOCKED grid) → Presenting complaints → Hospital course → Procedures → Investigations → Pending reports (AUTO) → Condition → Discharge medications (LOCKED grid) → Follow-up → Diet & activity
- **Side column:** TPA Readiness Check (OK / MISSING / CHECK) · Source Verification (Verified / Check / Not in file)

---

## 8. All bugs found and fixed

| Area | Bug | Fix |
|---|---|---|
| Seed | fpdf2 "not enough horizontal space" | Reset the x position after `multi_cell` |
| Seed | Historic numbers didn't match the story | Tuned the generator → 6.3 h / 2.5 h / 38.1% |
| Copilot UI | Textarea lost focus on every keystroke | `Field` component → plain render function |
| LLM | See §6, issues 1–6 | – |
| Cache | Runtime overwrites blocked branch switching | Warm-only cache writes |
| Tab | Inner scrollbars | `postMessage` auto-height |
| Tab | TPA table overflowed | Override MediTrack's nowrap rule in the side column |
| Browser | Stale UI after rebuilds | `Cache-Control: no-cache` on both `index.html` files |

---

## 9. Eval results (final)

Live `gpt-oss-20b`, 11 de-identified past discharges:

| Metric | Result |
|---|---|
| Hallucinated drugs/tests | **0** |
| Unverified numbers/dates | **0** |
| Faithfulness (verified ÷ all entities) | **100%** |
| Key-fact recall vs the doctor's summary (excluding the med list) | **75%** |
| Completeness (required sections) | **90%** (gaps are mostly follow-up advice that isn't in the notes) |
| Median latency | **~0.8 s** |
| Cost per summary | **~$0.0002 (≈ ₹0.02)** |

Golden patient (IP2609-0142), integrated, live: draft in about 1 s, 58–70 entities all verified, **TPA readiness 71% → 86%** after the stent sticker is uploaded in MediTrack.

---

## 10. Legacy system architecture (MediTrack)

**Layers:** React UI made to look like 2011 (Story: JSP) → FastAPI `/int/*` internal API (Story: Java monolith on Tomcat) → SQLite with 13 tables (Story: Oracle with 400+ tables + a Data Guard MIS replica) → file stores (`documents/`, `import_hotfolder/`, `rejected/`). Plus a background **hot-folder importer** thread (every 3 s).

**Context:**
- **Users:** doctors, nurses, pharmacy, TPA desk, IT (Suresh), management
- **Connected systems:** LIS via HL7 v2 (Story); PACS via an External Link; the MRD scanner via the hot-folder

**Data model:**
- `IP_ADM_DTL` is the hub, with one row per hospital stay. It links to `PT_MST` and `DR_MST`.
- Child tables: `IP_DIAG_DTL`, `IP_PROC_DTL`, `LAB_RSLT`, `PHR_ISS_DTL`, `CLN_NOTE`, `PT_DOC`, `IP_DSCH_SUMM`, `TPA_CLM_DTL`
- Global tables: `SYS_EXT_LNK`, `SYS_AUDIT`
- There are no foreign keys; relationships are by convention on `IP_NO`.

**Admission state machine:**

```
(none) ─admit─► ADM ─[Discharge Advised]─► DA ─[Final Discharge]─► DSCH
```

Discharge TAT = `DSCH_DT − DSCH_ADV_DT`.

**API (internal only):**

| Endpoint(s) | Purpose |
|---|---|
| `GET /int/census`, `GET /int/discharged` | Patient lists |
| `GET /int/ip/{ip}` | Whole patient file + configured links |
| `POST /int/ip/{ip}/discharge-advise`, `/discharge` | ADM → DA → DSCH |
| `POST /int/ip/{ip}/manual-summary` | Hand-typed summary |
| `GET /int/ip/{ip}/summary-template` | Blank MRD/DS/07 form |
| `POST /int/ip/{ip}/docs`, `GET /int/docs/{id}` | Documents |
| `GET`/`POST /int/admin/extlinks`, `…/{id}/toggle` | External Links admin |
| `GET /int/mis/discharge-tat` | MIS report |
| `GET /int/audit` | Audit trail |

**Hot-folder importer:**
- A filename `^(IP\d{4}-\d{4})_([A-Z_]+?)_(\d{14})\.pdf$` with a known `IP_NO` → moved to `documents/`, plus a `PT_DOC` row with `UPL_BY='BATCH_IMPORT'` and an audit entry
- Anything else → moved to `rejected/`
- Non-`.pdf` files (e.g. `.part`) are ignored

**Integration surfaces:**

| Surface | Status |
|---|---|
| `/int/*` endpoints | ❌ Forbidden for external use |
| Primary DB | ❌ Never written |
| **MIS replica** | ✅ Read-only |
| **External Links** | ✅ Config (link or tab) |
| **Hot-folder** | ✅ Drop files |
| HL7 from LIS | Inbound only |

**Deliberate legacy traits:**
- cryptic names and no docs
- one-person knowledge (Suresh)
- no SSO (hard-coded `rmo.karan`)
- no foreign keys or migrations
- data scattered across 6 tabs
- free-text notes
- polling and file-based integration
- dated UX and maintenance windows

---

## 11. Why the External Link is needed

The Copilot is a **separate application** (:8002), and MediTrack doesn't know it exists. The team **cannot change MediTrack's code**: the vendor is gone, there's no source code, IT forbids it, and the risk to a live hospital is too high. MediTrack *already* has an admin-configurable **External Links** feature (built in 2016 for the PACS viewer). One configuration row tells MediTrack:

| Field | Value | Effect |
|---|---|---|
| Label | `AI Discharge Draft` | Tab name |
| URL | `http://localhost:8002/#/embed/review/{IP_NO}` | Where the content comes from. `{IP_NO}` passes **patient context**. |
| Display | `Patient file tab` | Shown *inside* the patient file, so doctors never leave MediTrack |
| Active | `Y` | **Kill switch:** Disable = instant rollback |

Together with the **MIS replica** (data out) and the **hot-folder** (result back in), the integration needs **zero MediTrack code changes**. This mirrors the real-world pattern **SMART on FHIR "EHR launch"** (Epic, Oracle Health/Cerner). It's the "Suresh moment" in the story: the FDE's value was *finding* this door.

**Security caveat:** the demo URL carries only the IP number, with no authentication. In production, use a signed, short-lived launch token or SSO, and limit the pilot to the Cardiology ward.

---

## 12. How to run everything

Project folder: `/Users/yashpatil/Developer/AI/FDE/Live_session`. `.env` must contain `GROQ_API_KEY` and `LOGFIRE_TOKEN`. It's git-ignored; see `.env.example`.

| Goal | Commands | URL |
|---|---|---|
| One-time setup | `./run.sh setup` | – |
| Part 1, legacy | `git checkout part-1-legacy` → `./run.sh legacy` | http://localhost:8001 |
| Part 2, POC | `git checkout part-2-poc` → `./run.sh poc` | http://localhost:8501 |
| Part 3, integrated | `git checkout part-3-integrated` → `./run.sh integrated` | http://localhost:8001 (MediTrack; the Copilot runs behind it on :8002) |
| Webinar (all parts) | Stay on `part-3-integrated`. Terminal 1: `./run.sh integrated`. Terminal 2: `./run.sh poc`. | :8001 + :8501 |
| Reset demo state | `./run.sh reset` (reseeds MediTrack, clears drafts, removes the AI tab link) | – |
| Refresh offline fallback | `./run.sh warm` (live LLM for all 19 patients) | – |
| Free busy ports | `lsof -ti :8001 -ti :8002 -ti :8501 \| xargs kill` | – |

**Rules of thumb:**
- Stop servers before switching branches.
- Commit or stash any edits before `git checkout`.
- Hard-refresh the browser once after an update (Cmd+Shift+R).

---

## 13. Live demo flow

Full script: **`DEMO_RUNBOOK.md`**

1. **Legacy (Story Ch. 1–2):** Census → Ramesh's file → click through the scattered tabs → empty Discharge Summary tab + Word template → **MIS: 2.5 h vs 6.3 h, 38% queries** → External Links admin ("remember this").
2. **POC (Ch. 5):**
   - ENC-01 Generate (🔒 sections)
   - Source trace: add "Warfarin 5 mg OD" → red; change a date → yellow
   - Run the eval
   - Clinician feedback
   - Logfire trace
3. **Integrated (Ch. 6):**
   1. Add the External Link live (Display = Patient file tab).
   2. Open IP2609-0142 → **AI Discharge Draft** tab ("No draft yet").
   3. Click **Discharge Advised** → the draft appears in about 5–10 s.
   4. TPA **71%**: implant sticker missing.
   5. Documents → upload `demo_assets/IP2609-0142_stent_implant_sticker.pdf` as `IMPLANT_STKR` → back to the AI tab → **86%**.
   6. Edit a line → **Sign Discharge Summary** → Documents shows a yellow `DSCHSUMM … BATCH_IMPORT` row → open the PDF.
   7. Logfire trace.

**If something breaks:** LLM or network down → cached draft, then the template, automatically. Messed-up state → `./run.sh reset`.

---

## 14. Repository and branch map

```
main                → webinar docs only
└─ part-1-legacy    → + MediTrack
   └─ part-2-poc    → + copilot_core + Streamlit POC
      └─ part-3-integrated → + Copilot service, replica sync, embedded tab, write-back
```

Doc changes are made on `main` and merged into all three branches. Code changes are made on the lowest branch that owns them and merged upward.

```
Live_session/
├── run.sh                    setup | reset | legacy | poc | integrated | warm
├── requirements.txt          fastapi, uvicorn, python-multipart, fpdf2, pydantic-ai-slim[groq,logfire], logfire, streamlit, pandas, python-dotenv
├── .env.example              GROQ_API_KEY, LOGFIRE_TOKEN, COPILOT_MODEL, prices, USD_INR, COPILOT_OFFLINE, LOGFIRE_PROJECT_URL
├── README.md · DEMO_RUNBOOK.md
├── legacy_meditrack/         backend/ (schema, db, app, seed, seed_data) · ui/ (React, 2011 theme) · data/ (runtime)
├── copilot_core/             models · encounter · agent · trace · rules · assemble · observability · config · cache/
├── poc/                      app.py (Streamlit) · evaluation.py · export_deidentified.py · data/
├── copilot/                  replica_sync.py · service/ (app, store, pdf) · ui/ (embedded tab)
├── scripts/warm_cache.py
├── demo_assets/IP2609-0142_stent_implant_sticker.pdf
├── docs/                     HLD/LLD PDFs + HTML/Mermaid sources (added in a separate session)
└── webinar/                  webinar-content.md · system-explainer.md · conversation-summary.md (this file)
```

---

## 15. Documents produced

| File | What it is |
|---|---|
| `webinar/webinar-content.md` | The full webinar: 10 sections, script, visuals, story, quiz, sources |
| `webinar/system-explainer.md` | Hospital discharge cycle, glossary, stakeholders, problem, legacy mapping, POC and integrated explainer, cheat sheet |
| `webinar/conversation-summary.md` | This document |
| `README.md` | Project overview per part, architecture, commands |
| `DEMO_RUNBOOK.md` | Pre-webinar checklist, click-by-click demo script with talking points, recovery steps |
| `docs/CityCare_Discharge_Copilot_HLD_LLD.pdf` | 10-page plain-language HLD/LLD *(added in a separate session)* |
| `docs/CityCare_Discharge_Copilot_HLD_LLD_detailed.pdf` | Detailed HLD/LLD reference *(added in a separate session)* |
| `docs/design/*.html`, `build_pdf.sh` | HTML/Mermaid sources and PDF build script for the design docs |

---

## 16. Known limitations and caveats

- **Simulation, not production:** SQLite stands in for Oracle, a file copy stands in for Data Guard, and lab data is seeded instead of arriving over HL7.
- **No authentication** on MediTrack or the embedded tab URL (demo only). Production needs SSO or a signed launch token.
- **The AI tab shows on every patient file.** A real pilot would scope it to one ward.
- **Pilot metrics** (`/api/metrics`) still exist in the API but have no screen since the modern Monitor page was removed. They could be added as a MediTrack MIS report if needed.
- **Prices** are approximate (Groq pricing set in `.env`). Business-case figures are illustrative.
- **LLM output is nondeterministic.** The guardrail, rules engine, doctor sign-off and cached fallback exist for that reason.
- The **"MediTrack" vendor, CityCare, all people and TPAs are fictional.** Say so on stage.

---

## 17. Sources used for the FDE job-description research

- [OpenAI: Forward Deployed Engineer](https://openai.com/careers/forward-deployed-engineer-(fde)-sf-san-francisco/)
- [Anthropic: Forward Deployed Engineer](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)
- [Google Cloud: Forward Deployed Engineer](https://careers.google.com/jobs/results/106365505090003654-forward-deployed-engineer/)
- [AWS: Sr Forward Deployed Engineer](https://www.amazon.jobs/en/jobs/10517491/sr-forward-deployed-engineer-aws-forward-deployed-engineering)
- [Microsoft AI: Forward Deployed AI Engineer, Health](https://microsoft.ai/careers/job/4407776009/forward-deployed-ai-engineer-health/)
- [Palantir: Forward Deployed Software Engineer](https://jobs.lever.co/palantir/dab396d4-2f14-4796-aac0-0d82883dccf0)
- [Palantir blog: A Day in the Life of an FDSE](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)
- [Fast Company: Postings for this AI job are up 800%](https://www.fastcompany.com/91435680/postings-for-this-ai-job-are-up-800)
- [The Pragmatic Engineer: Forward Deployed Engineers](https://newsletter.pragmaticengineer.com/p/forward-deployed-engineers)
- [The New Stack: FDE is AI's hottest job](https://thenewstack.io/forward-deployed-engineer-fde-openai-google/)
