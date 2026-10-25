# Live demo runbook

The demo runs either **locally** (docker compose) or in **Azure** (azd). The click path is the same; only the URLs differ.

| | Local | Azure |
|---|---|---|
| MediTrack (+ AI tab) | http://localhost:8001 | `./run.sh cloud-urls` → `MEDITRACK_URL` (user `citycare`, password `DEMO_PASSWORD`) |
| POC | http://localhost:8501 (local sandbox, Groq `gpt-oss-20b`) | `POC_URL` (cloud sandbox, Foundry `gpt-oss-120b`, password `DEMO_PASSWORD`) |
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

1. `azd auth login` and `az login` (same account). If the account has several subscriptions, pick one up front: `az account set --subscription <id>` and `azd env new citycare --location centralindia --subscription <id>` (otherwise `cloud-up` asks).
2. `./run.sh cloud-up`. Measured on a clean run: **~8 min provisioning + deploy** (Postgres ~1-5 min, image builds in ACR ~4 min). `cloud-up` first generates `DEMO_PASSWORD` and the Postgres admin password (azd needs them before its hooks run), and sets `FOUNDRY_LOCATION=southindia`.
   - **Model:** `gpt-oss-20b` is *not* deployable pay-per-token on Foundry (the catalog lists it as a fine-tune SKU only, in every region). The cloud uses **`gpt-oss-120b`** (GlobalStandard, South India; the apps stay in Central India). Same family, so the story is "same open model family, Groq locally, Azure Foundry in the customer's tenant".
   - After deploy, the reset job seeds the database and the URLs are printed. The Copilot logs `password authentication failed for copilot_svc` for ~90 s until the reset job has created that login. It retries and recovers on its own.
3. `./run.sh eval-foundry`: re-run the eval on the Foundry deployment. Measured (11 encounters, live):

   | | Groq `gpt-oss-20b` | Foundry `gpt-oss-120b` |
   |---|---|---|
   | hallucinated | 0 | 0 |
   | unverified numbers | 0 | 2 (ENC-05, see below) |
   | faithfulness | 100% | 99% |
   | key-fact recall | 75% | 76% |
   | completeness | 88% | 95% |
   | median latency | 0.8 s | 2.8 s |

   The 120b model adds clinical colour more readily: in ENC-05 it writes "SpO2 > 92% on room air", a threshold that is not in the record. The guardrail marks it **unverified** (yellow, for the doctor to check), not hallucinated. It repeats on re-runs (1-2 unverified numbers). Say so on stage: it's the guardrail doing its job, and the reason the eval is re-run per provider. If drafts come back as `template` with an error, see "If something breaks".
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
| *(Azure)* open the **cloud POC** → sidebar says "Azure sandbox (rg-…-poc)" | "Same app, now a link the hospital's doctors can open. Its own sandbox: no database login, no file shares. Same open model family (gpt-oss), but served from Azure AI Foundry, in the customer's tenant. We re-ran the eval before trusting it." |
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
- **Port busy (local)**: another compose stack often holds 8001 and 5432 (check `docker ps`). Run on other ports: `PG_PORT=5433 MEDITRACK_PORT=8011 ./run.sh integrated` (use the same variables for `reset`). Don't just `curl localhost:8001`: it can answer from the *other* stack.
- **Azure, AI tab shows template drafts**: the Foundry call failed. Check the Copilot's logs: `az containerapp logs show -n <ca-copilot-…> -g rg-<env>-hospital --tail 50`. If the endpoint path is the problem, set the Copilot's `FOUNDRY_ENDPOINT` to `https://<foundry-account>.services.ai.azure.com/openai/v1/` (Portal → Container App → Containers → Environment variables).
- **Azure, `cloud-up` fails with `715-123420 ... unusual activity`** on the model deployment: Foundry throttles repeated PUTs of the same deployment. The postdeploy hook sets `FOUNDRY_MODEL_EXISTS=true` so later runs skip it (`cloud-down` resets it). If you hit it before that is set: `azd env set FOUNDRY_MODEL_EXISTS true` if the deployment exists (`az cognitiveservices account deployment show ...`), then `./run.sh cloud-up`.
- **Azure, `Failed to provision revision ... Operation expired` for the POC**: placeholder and real image must share an ingress port (both listen on 80). Don't change the POC port without the Bicep.
- **Azure, MediTrack shows errors right after `cloud-up`**: the reset job may still be seeding. Wait a minute, or run `./run.sh cloud-reset`.
