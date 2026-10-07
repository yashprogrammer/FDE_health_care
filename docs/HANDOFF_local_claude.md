# Handoff: deploy and verify CityCare v2 from a local machine

Context for a Claude Code session running on the developer's Mac, with their own `az` / `azd` login.
Branch: **`claude/serene-cori-14xpa7`** (based on `part-3-integrated`). Read `docs/v2-decisions.md` first: it is the decision record for all of this.

## What v2 is

1. **UI**: MediTrack reskinned to a ~2018 enterprise look ("Clarity" theme). The AI Discharge Draft tab copies MediTrack's stylesheet verbatim (`copilot/ui/src/index.css`), so it matches.
2. **Postgres instead of SQLite.** MediTrack's tables are in schema `meditrack`. IT's read-only reporting views are in schema `mis` (role `mis_ro`; no patient mobile or address). The Copilot logs in as `copilot_svc` (member of `mis_ro`, owner of schema `copilot`). **No replica or copy:** `replica_sync.py` is gone. DB setup lives in `legacy_meditrack/backend/bootstrap.py` and `copilot/bootstrap.py` (admin rights), plus `seed.py` (app owner). `scripts/reset.py` runs all three.
3. **Containers.**
   - `Dockerfile` is one app image; `APP_ROLE=meditrack|copilot|reset` picks the role (via `scripts/serve.py`).
   - `poc/Dockerfile` is the slim Streamlit POC.
   - `gateway/` is Caddy: `/` → MediTrack, `/copilot/*` → Copilot (same origin for the iframe tab), with basic auth when `DEMO_PASSWORD` is set.
   - `docker-compose.yml` is the local stack, wired like Azure.
4. **LLM.** gpt-oss-20b everywhere: Groq locally (`COPILOT_PROVIDER=groq`), Azure AI Foundry in the cloud (`COPILOT_PROVIDER=foundry`, OpenAI-compatible `FOUNDRY_ENDPOINT` ending in `/openai/v1/`). See `copilot_core/config.py` and `agent.py`.
5. **Azure** (`azure.yaml`, `infra/`, region Central India):
   - `rg-<env>-hospital`:
     - one Container Apps environment: gateway (external), meditrack and copilot (internal, `allowInsecure: true`, min = max = 1 replica because of background threads), reset Container Apps Job
     - PostgreSQL Flexible Server B1ms, db `citycare`, firewall allows Azure services
     - Storage with two Azure Files shares: `documents` (MediTrack only) and `import-hotfolder` (MediTrack + Copilot)
     - Foundry `AIServices` account with a gpt-oss-20b deployment
     - ACR Basic; user-assigned identity with AcrPull
   - `rg-<env>-poc`: its own environment and identity; the POC app gets the Foundry key and nothing else.
   - Hooks:
     - `infra/hooks/preprovision.sh`: generates `PG_ADMIN_PASSWORD` and `DEMO_PASSWORD`, then asks `az cognitiveservices model list` for gpt-oss-20b's format, version and SKU in the Foundry region.
     - `postdeploy.sh`: points the reset job at the deployed image and runs it in "only if empty" mode.
     - `reset.sh`: runs the reset job and waits.

## Already verified (in a Linux sandbox)

- **Screens:** screenshots of all MediTrack screens and the AI tab.
- **Postgres port:** MIS numbers unchanged (2.5 h / 6.3 h / 38.1%). The de-identified export is byte-identical to the committed `poc/data/deidentified_encounters.json`.
- **Permissions:** `mis_report` and `copilot_svc` are denied on `meditrack.*` tables and denied writes.
- **docker compose, through the gateway:**
  - Discharge Advised → draft → TPA readiness 71% → upload the sticker → 86% → sign → PDF imported as `BATCH_IMPORT`
  - basic auth: 401 without the password, 200 with it
  - reset: full and if-empty modes
- **Eval** (cached drafts): 0 hallucinations, 100% faithful, 75% recall, 90% complete.
- **Foundry code path,** against a fake OpenAI-compatible server: a `json_schema` response_format request with `reasoning_effort=low` is sent and parsed.
- **`infra/main.bicep`** compiles with Bicep 0.48 with no warnings.

## Not yet verified (your job)

- **Docker builds:** `./run.sh integrated` from the repo's own Dockerfiles. The sandbox needed a proxy CA injected; a Mac shouldn't.
- **Live models:** no live Groq call and no live Foundry call yet.
- **Azure:** nothing has been deployed. `azd up` and the hooks have never run.

## Steps

0. Prerequisites: Docker Desktop, `brew install azure-cli azd uv node`, Python 3.13. Then `azd auth login` and `az login` with the same account. `.env` needs `GROQ_API_KEY` (and `LOGFIRE_TOKEN`), copied from `.env.example`.
1. **Local stack:**
   1. `./run.sh integrated`, then in another terminal `./run.sh reset`.
   2. Follow the Part 3 click path in `DEMO_RUNBOOK.md` at http://localhost:8001. The AI tab link URL is `/copilot/#/embed/review/{IP_NO}`, Display = Patient file tab.
   3. With a Groq key, "Prepared By" should say `AI (live)`.
   4. `./run.sh setup`, then `./run.sh poc` and `./run.sh eval` (live Groq).
2. **Azure:**
   1. `./run.sh cloud-up` (creates azd env `citycare` in centralindia, then `azd up`).
   2. Then `./run.sh cloud-urls`, open both URLs, and run the Part 3 click path again on the cloud URL.
   3. `./run.sh eval-foundry` must give 0 hallucinations and 100% faithfulness. Compare with Groq.
3. When it works: update `DEMO_RUNBOOK.md` and `webinar/system-explainer.md` §6 with anything learned (region, timings, real costs), commit and push to the same branch.
4. Tear down with `./run.sh cloud-down` unless the user wants it kept up.

## Likely problems and where to look

| Symptom | Likely cause | Fix |
|---|---|---|
| preprovision: "gpt-oss-20b is not offered … centralindia" | Model not in that region for this subscription | `azd env set FOUNDRY_LOCATION eastus2` (or another region listed in the Foundry model catalog); the apps stay in Central India |
| Provision fails on `Microsoft.CognitiveServices/accounts/deployments` | Wrong format, version or SKU, or no quota | Check `az cognitiveservices model list -l <region> --query "[?model.name=='gpt-oss-20b']"`; set `FOUNDRY_MODEL_FORMAT`, `FOUNDRY_MODEL_VERSION`, `FOUNDRY_SKU` and `FOUNDRY_CAPACITY` with `azd env set`. Check whether the preprovision hook's `azd env set` values were picked up (if not, run `sh infra/hooks/preprovision.sh` and then `azd provision`). |
| AI tab drafts say "Template (AI unavailable)" in Azure | The Foundry call failed | `az containerapp logs show -n ca-copilot-<token> -g rg-<env>-hospital --tail 100`. Try `FOUNDRY_ENDPOINT=https://<account>.services.ai.azure.com/openai/v1/`. Check `copilot_core/agent.py` `_model_and_settings()`; gpt-oss may reject `temperature` or need `max_completion_tokens`. |
| Gateway 502 / 404 for `/` or `/copilot/` in Azure | Caddy can't reach the internal apps by short name, or the Host header | `gateway/entrypoint.sh` uses `http://<app-name>` with `header_up Host {upstream_hostport}`. Try the internal FQDN (`<app>.internal.<env-default-domain>`), set via the `MEDITRACK_UPSTREAM` / `COPILOT_UPSTREAM` env vars in `infra/modules/hospital.bicep`. |
| MediTrack 500s right after deploy | DB not seeded yet, or the reset job failed | `./run.sh cloud-reset`. Logs: `az containerapp job execution list -n job-reset-<token> -g rg-<env>-hospital`, then `az containerapp job logs show …`. |
| Reset job fails on GRANT / CREATE SCHEMA | Azure's admin is not a superuser | `bootstrap.py` grants `meditrack` / `copilot_svc` to the admin before creating schemas; check the PG16 role membership flags (`SET`/`INHERIT`). |
| `azd deploy` for `poc` can't find the app | `resourceGroup: ${AZURE_POC_RESOURCE_GROUP}` in `azure.yaml` not expanded | Check `azd env get-values`; hard-code the RG name temporarily if needed |
| Streamlit POC stuck "Connecting…" | Websocket through ingress | Add `--server.enableXsrfProtection false --server.enableCORS false` to `poc/Dockerfile` CMD |

## Rules

- Never commit `.env`, `.azure/`, passwords or keys. `.gitignore` covers `.env` and `.azure/`.
- Don't put model identifiers in commits, PRs or code comments.
- Keep MediTrack's code "unchanged" in the story: integration changes belong in `copilot/`, `gateway/` and `infra/`, not `legacy_meditrack/` (except the DB layer, which is Part 1).
- Commit messages tag `[part-1]` / `[part-2]` / `[part-3]` / `[docs]`. Later the work is split back into the stacked branches (`main` → `part-1-legacy` → `part-2-poc` → `part-3-integrated`).
- Known doc gap: `webinar/webinar-content.md` story chapters still say "MIS replica". The explainer and runbook now say "read-only reporting login". Ask the user before changing the story.
