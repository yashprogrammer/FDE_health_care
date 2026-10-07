# CityCare Discharge Copilot — FDE vs AI Engineer live demo

Three stages of the same feature, one branch each:

| Branch | What exists |
|---|---|
| `part-1-legacy` | **MediTrack HMS v3.2**: CityCare Hospitals' legacy hospital system (2011, UI refreshed 2018) |
| `part-2-poc` | + Standalone **Streamlit POC** of the Discharge Copilot (local, and the same app as a cloud sandbox) |
| `part-3-integrated` | + **Copilot service** integrated with MediTrack (read-only reporting login, adapter, hot-folder write-back) |

Everything runs **locally** (docker compose) or in **Azure** (azd + Bicep), with the same container images.
All people, patients, policies and TPAs are fictional.

## Quick start (local)

Needs Docker. The POC additionally needs Python 3.13 + [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env   # add GROQ_API_KEY and LOGFIRE_TOKEN (optional: without a key the Copilot uses cached drafts)
./run.sh integrated    # Postgres + MediTrack + Copilot + gateway  -> http://localhost:8001
./run.sh reset         # restore the golden demo state (in a second terminal)
./run.sh setup         # one-time, for the POC: Python venv + npm packages
./run.sh poc           # local POC                                  -> http://localhost:8501
```

`./run.sh legacy` starts MediTrack without the Copilot. `./run.sh down` stops the stack (data is kept), `./run.sh wipe` deletes it.

## Quick start (Azure)

Needs the [Azure Developer CLI](https://aka.ms/azd) and the Azure CLI, both logged in (`azd auth login`, `az login`).

```bash
./run.sh cloud-up      # first run asks for the subscription; region Central India
./run.sh cloud-urls    # MediTrack (user "citycare" + DEMO_PASSWORD) and the cloud POC
./run.sh cloud-reset   # golden demo state
./run.sh eval-foundry  # re-run the eval against the Foundry model
./run.sh cloud-down    # delete everything
```

See [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) for the full checklist and click path, and `webinar/system-explainer.md` §6 for the deployment architecture.

## Part 1 — MediTrack HMS (the legacy system)

- FastAPI backend on **PostgreSQL** (stands in for the hospital's Oracle) with cryptic legacy tables (`PT_MST`, `IP_ADM_DTL`, `LAB_RSLT`, `PHR_ISS_DTL` …) in schema `meditrack`. See `legacy_meditrack/backend/schema.sql`.
- React UI (`legacy_meditrack/ui`): a dense enterprise look from a 2018 refresh, on top of 2011 behaviour (codes, confirm dialogs, a full reload on every tab).
- `/int/*` endpoints are **internal-only**: hospital IT forbids external systems from calling them.
- Existing extension points an FDE can discover:
  - **MIS reporting views** (schema `mis`, role `mis_ro`): IT's read-only views over the clinical tables (no patient contact details, no admin tables).
  - **System Admin → External Links**: config-driven links on every patient file, shown either as a link (new window) or as an **extra patient-file tab** (embedded page). Supports `{IP_NO}` and `{UHID}` placeholders.
  - **Batch document import hot-folder**: drop `<IP_NO>_<DOC_TYP>_<YYYYMMDDHHMMSS>.pdf` and it appears in the patient's Documents tab. Locally `legacy_meditrack/data/import_hotfolder/`; in Azure an Azure Files share.
- **MIS → Discharge TAT** shows the pain: cash patients leave ~2.5 h after discharge is advised, insured (cashless) ~6.3 h, and 38% of TPA submissions come back with a query.
- Database setup is split like it would be in a hospital: `legacy_meditrack/backend/bootstrap.py` (IT, admin rights: roles and schemas) and `seed.py` (synthetic data, as the app owner).

**Golden demo patient:** `IP2609-0142`, Ramesh Kulkarni: anterior-wall STEMI, PTCA + stent, cashless via SecureHealth TPA. His stent implant sticker is *not* on file (the #1 TPA query reason).

## Part 2 — Discharge Copilot POC (Streamlit)

```bash
./run.sh poc           # http://localhost:8501 (Groq)
./run.sh eval          # the eval from the command line
./run.sh warm          # pre-generate + cache live drafts (offline safety net; needs the local stack running)
```

- **Standalone**: reads `poc/data/deidentified_encounters.json`, 11 past discharges exported through IT's read-only reporting login and de-identified by `poc/export_deidentified.py` (`./run.sh poc-export`). It touches no hospital system.
- **Two POCs, same code:** the local POC (Groq) and the **cloud POC**: the same app in its own Azure resource group (`poc/Dockerfile`), calling Azure AI Foundry, behind a password, with no access to the hospital's database.
- **`copilot_core/`** is the AI engineer's slice, reused later by Part 3:
  - `agent.py`: Pydantic AI agent on **gpt-oss-20b**, served by Groq locally or by an Azure AI Foundry deployment in the cloud (`COPILOT_PROVIDER`), with a typed `SummaryDraft` output. Fallback chain: live LLM → cached draft → template.
  - `models.py`: `Encounter` input contract and `SummaryDraft` output contract. Direct identifiers are stripped before the LLM call (`Encounter.for_llm`).
  - `trace.py`: source-trace guardrail. Every drug, lab and number is checked against the patient's data.
  - `rules.py`: TPA-readiness checklist, a deterministic rules engine (not AI).
  - `assemble.py`: final summary. Diagnoses, discharge meds and pending reports are pulled deterministically (🔒).
  - `observability.py`: Logfire tracing of every agent run (only if `LOGFIRE_TOKEN` is set).
- Tabs: **Generate** · **Source trace** (edit the draft, e.g. add "Warfarin 5 mg OD", to watch the guardrail fire) · **Eval** (completeness, hallucinations, faithfulness, key-fact recall vs the doctor's summary, latency, cost) · **Clinician feedback**

## Part 3 — Integrated Discharge Copilot

```bash
./run.sh integrated    # http://localhost:8001 (the Copilot is behind it at /copilot/)
```

MediTrack's code is **not changed**. Integration goes through three extension points the FDE found:

```
MediTrack (unchanged) ─ writes STS='DA' ─► Postgres: schema meditrack
                                              │ IT's read-only views (schema mis)
                                              ▼
          adapter (copilot/service/app.py, login copilot_svc = mis_ro) polls for STS='DA'
                    │  copilot_core: Encounter → Pydantic AI draft → trace → TPA rules
                    ▼
          schema copilot (own drafts + audit) ──► "AI Discharge Draft" tab (/copilot/, embedded in MediTrack)
                                                     │ doctor edits + signs
                                                     ▼
          signed PDF ──► MediTrack import hot-folder ──► patient's Documents tab
Entry point: MediTrack Admin → External Links → Display "Patient file tab"
             → /copilot/#/embed/review/{IP_NO}   (renders inside MediTrack)
```

- **No copy of the data**: the Copilot reads MediTrack's own database through IT's reporting views with a login that can only SELECT. Postgres grants enforce "never write to MediTrack". `copilot/bootstrap.py` is IT's one-time grant.
- **One entry point**: a Caddy gateway (`gateway/`) serves MediTrack at `/` and the Copilot at `/copilot/`, so the embedded tab is same-origin. In Azure it's the only public endpoint and carries the demo password.
- **One new feature, same UI**: the only user-facing change is an **AI Discharge Draft** tab in MediTrack's patient file. It uses MediTrack's own stylesheet (`copilot/ui/src/index.css` is copied from MediTrack), and its fields follow the order of MediTrack's paper form (MRD/DS/07). The Copilot has no separate app for users.
- **Inside the tab**: editable AI-drafted sections; LOCKED diagnoses and pharmacy medications; auto-listed pending reports; a **TPA Readiness Check** that re-reads MediTrack live, so a document uploaded in the Documents tab counts within seconds; **Source Verification** (guardrail); Print Preview; Sign Discharge Summary.
- The Copilot mounts only the import hot-folder, not the documents share: it can drop the signed PDF but cannot read patient documents.
- Every draft is traced in Logfire as `adapter.process_discharge` → `discharge_copilot.generate_draft` → agent run, plus `writeback.hotfolder`.

## Containers and infrastructure

| Path | What |
|---|---|
| `Dockerfile` | One app image for MediTrack, the Copilot and the reset job (`APP_ROLE=meditrack\|copilot\|reset`) |
| `poc/Dockerfile` | Slim POC image: `copilot_core` + `poc` only |
| `gateway/` | Caddy: routing, same-origin tab, optional basic auth |
| `docker-compose.yml` | Local stack, wired like Azure |
| `azure.yaml`, `infra/` | azd + Bicep: hospital resource group (Container Apps env, Postgres, Azure Files, Foundry, registry, reset job) and POC resource group |
| `scripts/reset.py` | IT's DB setup (both bootstraps) + reseed + clear drafts. Runs as compose `init` and as the Azure reset job. |
