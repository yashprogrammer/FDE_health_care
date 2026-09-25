# CityCare Discharge Copilot — FDE vs AI Engineer live demo

Three stages of the same feature, one branch each:

| Branch | What exists |
|---|---|
| `part-1-legacy` | **MediTrack HMS v3.2** — CityCare Hospitals' 2011-era hospital system |
| `part-2-poc` | + Standalone **Streamlit POC** of the Discharge Copilot |
| `part-3-integrated` | + **Copilot service** integrated with MediTrack (replica, adapter, hot-folder write-back) |

All people, patients, policies and TPAs are fictional.

## Quick start

```bash
./run.sh setup     # venv + deps + seed data (first time)
./run.sh legacy    # MediTrack -> http://localhost:8001
./run.sh reset     # restore golden demo state
```

## Part 1 — MediTrack HMS (the legacy system)

- FastAPI + SQLite backend with cryptic legacy tables (`PT_MST`, `IP_ADM_DTL`, `LAB_RSLT`, `PHR_ISS_DTL` …) — see `legacy_meditrack/backend/schema.sql`
- React UI styled like 2011 (`legacy_meditrack/ui`)
- `/int/*` endpoints are **internal-only** — hospital IT forbids external systems from calling them
- Existing extension points an FDE can discover:
  - **System Admin → External Links**: config-driven links on every patient file (`{IP_NO}`, `{UHID}` placeholders)
  - **Batch document import hot-folder** (`legacy_meditrack/data/import_hotfolder/`): drop `<IP_NO>_<DOC_TYP>_<YYYYMMDDHHMMSS>.pdf` and it appears in the patient's Documents tab
- **MIS → Discharge TAT** shows the pain: cash patients leave ~2.5 h after discharge is advised, insured (cashless) ~6.3 h, and 38% of TPA submissions come back with a query

**Golden demo patient:** `IP2609-0142` — Ramesh Kulkarni, anterior-wall STEMI, PTCA + stent, cashless via SecureHealth TPA. His stent implant sticker is *not* on file (the #1 TPA query reason).

## Part 2 — Discharge Copilot POC (Streamlit)

```bash
cp .env.example .env   # add GROQ_API_KEY and LOGFIRE_TOKEN
./run.sh poc           # http://localhost:8501
./run.sh warm          # pre-generate + cache live drafts (offline safety net)
```

- **Standalone**: reads `poc/data/deidentified_encounters.json`, 11 past discharges exported (read-only) from MediTrack and de-identified by `poc/export_deidentified.py`. It touches no hospital system.
- **`copilot_core/`** is the AI engineer's slice, reused later by Part 3:
  - `agent.py`: Pydantic AI agent (`groq:openai/gpt-oss-20b`) with a typed `SummaryDraft` output. Fallback chain: live LLM → cached draft → template.
  - `models.py`: `Encounter` input contract and `SummaryDraft` output contract. Direct identifiers are stripped before the LLM call (`Encounter.for_llm`).
  - `trace.py`: source-trace guardrail. Every drug, lab and number is checked against the patient's data.
  - `rules.py`: TPA-readiness checklist, a deterministic rules engine (not AI).
  - `assemble.py`: final summary. Diagnoses, discharge meds and pending reports are pulled deterministically (🔒).
  - `observability.py`: Logfire tracing of every agent run (only if `LOGFIRE_TOKEN` is set).
- Tabs: **Generate** · **Source trace** (edit the draft, e.g. add "Warfarin 5 mg OD", to watch the guardrail fire) · **Eval** (completeness, hallucinations, faithfulness, key-fact recall vs the doctor's summary, latency, cost) · **Clinician feedback**
