# Live demo runbook

The demo runs either **locally** (docker compose) or in **Azure** (azd). The click path is the same; only the URLs differ.

| | Local | Azure |
|---|---|---|
| MediTrack (+ AI tab) | http://localhost:8001 | `./run.sh cloud-urls` → `MEDITRACK_URL` (user `citycare`, password `DEMO_PASSWORD`) |
| POC | http://localhost:8501 (local sandbox, Groq) | `POC_URL` (cloud sandbox, Foundry, password `DEMO_PASSWORD`) |
| AI tab link URL | `/copilot/#/embed/review/{IP_NO}` | the same |

## Before the webinar: local (T-30 min)

1. Put `GROQ_API_KEY` and `LOGFIRE_TOKEN` in `.env` (optionally `LOGFIRE_PROJECT_URL`).
2. `git checkout part-3-integrated` (contains all three parts).
3. Terminal 1: `./run.sh integrated` (first time builds the images, ~2 min).
4. Terminal 2: `./run.sh warm`. It generates and caches live drafts for every patient. If Wi-Fi or Groq fails on stage, the Copilot silently serves these cached drafts. Then rebuild once so the containers have the new cache: stop terminal 1 (Ctrl-C) and run `./run.sh integrated` again.
5. `./run.sh reset`: fresh golden state.
6. Terminal 2: `./run.sh poc`.
7. Open tabs: MediTrack `localhost:8001`, POC `localhost:8501`, Logfire.
8. Keep `demo_assets/IP2609-0142_stent_implant_sticker.pdf` handy for the upload.

## Before the webinar: Azure (T-60 min)

1. `azd auth login` and `az login` (same account).
2. `./run.sh cloud-up`. The first run asks for the subscription. It takes ~15 min (Postgres is the slow part). The preprovision hook:
   - generates `DEMO_PASSWORD` and the Postgres admin password,
   - checks that **gpt-oss-20b** is offered in Central India. If not, it stops and tells you to run `azd env set FOUNDRY_LOCATION <region>` (e.g. `eastus2`, `swedencentral`; the apps stay in Pune), then `./run.sh cloud-up` again.

   After deploy, the reset job seeds the database and the URLs are printed.
3. `./run.sh eval-foundry`: re-run the eval on the Foundry deployment. Expect 0 hallucinations and 100% faithfulness, like on Groq. If drafts come back as `template` with an error, see "If something breaks".
4. Open `MEDITRACK_URL` and `POC_URL` once (login), and the Logfire project.
5. `./run.sh cloud-reset` just before going live.

To spend almost nothing between webinars, run `./run.sh cloud-down` (deletes everything) and `cloud-up` again next time.

## Part 1: the legacy world (Story Ch. 1–2)

| Click | Say |
|---|---|
| MediTrack → **IPD Census** | "This is CityCare's HMS. Built 2011, reskinned 2018. Vendor gone. Suresh is the only one who knows it." |
| Open **IP2609-0142** (Ramesh Kulkarni) → click through Lab / Pharmacy / Notes tabs | "To write one discharge summary, a resident copy-pastes from these 5 screens." |
| **Discharge Summary** tab | "A Word template from 2011. 35–45 minutes per patient." |
| **Reports → MIS: Discharge TAT** | "The FDE's discovery: cash 2.5 h, insured **6.3 h**, **38%** of TPA submissions bounce. Top reason: stent sticker not attached." |
| **System Admin → External Links** | "Notice this: MediTrack can show configurable links on every patient file. Remember it." |

*(Azure)* Optional aside: Azure portal → `rg-<env>-hospital`. "MediTrack's app server, its database and its file shares. This is 'their world'."

## Part 2: the POC (Story Ch. 5, the AI engineer's showcase)

| Click | Say |
|---|---|
| POC → pick **ENC-01** → **Generate** | "Standalone Streamlit, 11 de-identified past discharges. No hospital system touched." |
| Point at 🔒 sections | "Diagnoses, meds and pending reports are **not** generated. They're pulled from source." |
| **Source trace** → add `Warfarin 5 mg OD` to the text | "Guardrail: that drug isn't in this patient's record. Red." |
| **Eval** → Run eval | "Completeness, hallucinations, faithfulness, recall vs the doctor's summary, latency, cost in rupees." |
| **Clinician feedback** | "Business verification: doctors and the TPA desk score it." |
| *(Azure)* open the **cloud POC** → sidebar says "Azure sandbox (rg-…-poc)" | "Same app, now a link the hospital's doctors can open. Its own sandbox: no database login, no file shares. Same gpt-oss-20b, but served from Azure AI Foundry, in the customer's tenant. We re-ran the eval before trusting it." |
| Logfire | "Every agent run is traced: prompt, tokens, latency, structured output." |

## Part 3: integration (Story Ch. 6)

| Click | Say |
|---|---|
| MediTrack → **External Links** → Label `AI Discharge Draft`, URL `/copilot/#/embed/review/{IP_NO}`, Display **Patient file tab** → Add | "The Suresh moment: integration by *configuration*, not code. And no new app for doctors to learn, just one more tab." |
| Open **IP2609-0142** → point at the new **AI Discharge Draft** tab → click it | "It looks like every other MediTrack screen: same fonts, same buttons. Training for 300 doctors and nurses: about 5 minutes." |
| Click **Discharge Advised** (top of the patient file) | "The doctor does exactly what they did yesterday." |
| Watch the tab: *No draft yet* → draft appears | "The Copilot reads MediTrack through IT's read-only reporting login, not a copy. A draft in seconds." |
| TPA panel shows **MISSING: Implant sticker** (71%) | "This is the #1 reason insurers bounced claims last quarter. Caught *before* submission." |
| Back in MediTrack → **Documents** → upload the stent sticker PDF as `IMPLANT_STKR` | "The cath lab uploads it the old way…" |
| Back to **AI Discharge Draft** tab → TPA panel now **86%** | "…and the Copilot sees it within seconds." |
| Edit a hospital-course line → **Sign Discharge Summary** | "The doctor stays in charge. Nothing is sent without their signature." |
| **Documents** tab → yellow `DSCHSUMM … BATCH_IMPORT` row → open PDF | "Delivered through MediTrack's 2013 scanner import folder." |
| Logfire → the trace for IP2609-0142 | "Behind that one tab: database read → agent → guardrail → PDF write-back, every step observable." |
| *(Azure)* portal → `rg-<env>-hospital` → Container Apps environment | "The Copilot runs *next to* MediTrack in the same environment, internal only. One public door, the gateway. And it shares MediTrack's database server, but its login can only read the reporting views." |

## If something breaks

- **LLM or network down**: nothing to do. Drafts fall back to cached (after `./run.sh warm`), then to a template. The "Prepared By" field shows which one was used.
- **Messed-up state**: `./run.sh reset` (local) or `./run.sh cloud-reset` (Azure, ~1 min), then re-advise the patient.
- **Port busy (local)**: `MEDITRACK_PORT=8011 ./run.sh integrated`, or free it: `lsof -ti :8001 -ti :5432 -ti :8501 | xargs kill`.
- **Azure, AI tab shows template drafts**: the Foundry call failed. Check the Copilot's logs: `az containerapp logs show -n <ca-copilot-…> -g rg-<env>-hospital --tail 50`. If the endpoint path is the problem, set the Copilot's `FOUNDRY_ENDPOINT` to `https://<foundry-account>.services.ai.azure.com/openai/v1/` (Portal → Container App → Containers → Environment variables).
- **Azure, MediTrack shows errors right after `cloud-up`**: the reset job may still be seeding. Wait a minute, or run `./run.sh cloud-reset`.
