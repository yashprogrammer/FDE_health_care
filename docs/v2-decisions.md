# v2 decisions: modern UI + Azure deployment

Decisions from the second `/grill-me` session (2026-10-07). Everything here is **fictional / illustrative**, as in v1.

## Goals

1. **UI:** MediTrack should look less like 2011. The *architecture* stays legacy; the *look* becomes a clean ~2018 enterprise reskin.
2. **Deployment:**
   - **Legacy MediTrack** is deployed to the cloud, both compute and data.
   - There are **two POCs**: the same Streamlit app run locally and deployed in the cloud.
   - The **integrated Copilot** is deployed in the cloud, in the **same cloud space** as MediTrack.

## Decisions

| # | Topic | Decision |
|---|---|---|
| 1 | UI style | **Clean enterprise, ~2018**: flat colours, 14px system font, a sidebar, cards and readable tables. Still a bit dense and dated, so the legacy story holds. The AI tab keeps using MediTrack's own stylesheet (the v3 "same UI + one feature" rule still applies). |
| 2 | Cloud | **Azure**, region **Central India (Pune)**: data residency (DPDP) story, low latency for the audience |
| 3 | Compute | **Azure Container Apps**. The hospital environment is one Container Apps environment shared by MediTrack, the Copilot and the gateway. `minReplicas = maxReplicas = 1` for apps with background threads (hot-folder importer, adapter). |
| 4 | Legacy data | **One Azure Database for PostgreSQL Flexible Server, Burstable B1ms** (stands in for Oracle). SQLite is retired. Stopped between webinars. |
| 5 | Replica | **No replica and no copy.** The Copilot reads MediTrack's **own database** as the `copilot_ro` role: SELECT only, on a `mis` schema of views over MediTrack's tables. The Copilot's drafts and audit live in a separate `copilot` schema. `replica_sync.py` is removed. Story line: *"IT gave us a read-only reporting login."* |
| 6 | Hot-folder | **Azure Files share** mounted in both MediTrack and the Copilot (`import_hotfolder/`, plus `documents/` for MediTrack). The importer code doesn't change: zero MediTrack code changes to the integration contract. |
| 7 | Networking | A **Caddy gateway** container is the only public endpoint: `/` → MediTrack, `/copilot/*` → Copilot (internal ingress). Same origin, so there are no iframe cross-origin issues. The External Link URL becomes relative: `/copilot/#/embed/review/{IP_NO}`. |
| 8 | Access | Public URL behind a **basic-auth demo password** (in Caddy). Locally the same Caddy runs without a password. |
| 9 | LLM | **`gpt-oss-20b` everywhere.** Local runs use **Groq**. Cloud runs (cloud POC and integrated) use **Azure AI Foundry**. Choosing the provider is configuration in `copilot_core`. **Re-run the eval on Foundry** before trusting it (NativeOutput / JSON-schema behaviour can differ by provider). |
| 10 | Cloud POC | The same Streamlit app with the **de-identified data baked into the image**, in a **separate resource group** (`rg-citycare-poc`) with its own Container Apps environment and URL. It has no network path to the hospital environment, which keeps the sandbox boundary visible. Streamlit's own password gate. |
| 11 | Local mode | **docker compose**: one Postgres, MediTrack, Copilot, Caddy (Streamlit POC runs as before). `./run.sh` wraps compose, so the same images run locally and in Azure. |
| 12 | IaC | **azd + Bicep.** `azd up` before a webinar, `azd down --purge` after. Postgres can also be stopped in between. |
| 13 | Uptime / cost | Up only around webinars. Rough cost while up: Postgres B1ms ≈ $0.02/h; Container Apps mostly within the free grant; Azure Files and Foundry tokens are cents. |
| 14 | Cloud reset | **Container Apps Job** (MediTrack image, runs `seed` + clears the Azure Files folders + Copilot schema), triggered by `./run.sh cloud-reset` and run automatically after `azd up`. |
| 15 | Observability | Logfire is unchanged (token from Key Vault / Container Apps secret in the cloud). |
| 16 | Offline fallback | The cached drafts are baked into the image; the live → cached → template chain is unchanged. |
| 17 | Docs | Update **README + DEMO_RUNBOOK**; add a **deployment architecture** section to `webinar/system-explainer.md`. Story, quiz and HLD/LLD PDFs are unchanged. |
| 18 | Branches | Stacked as before, so `main`, `part-1-legacy` and `part-2-poc` must be pushed to GitHub. UI + Postgres → `part-1-legacy`; POC container + Foundry switch → `part-2-poc`; Copilot, gateway, Bicep → `part-3-integrated`; merged upward. |

## Build order (checkpoint after each)

1. **UI reskin.** MediTrack plus the AI tab, ~2018 enterprise look. Still SQLite and local, so it can be checked straight away.
2. **Postgres + compose.**
   - SQLite → Postgres port.
   - `mis` views and the `copilot_ro` role; `copilot` schema.
   - Remove `replica_sync`.
   - Dockerfiles, docker compose and Caddy; `./run.sh` updated.
3. **Azure.**
   - Bicep / azd: the hospital RG (Container Apps env, Postgres, Azure Files, gateway, Copilot, MediTrack, reset job) and the POC RG.
   - Foundry provider switch, plus re-running the eval on Foundry.
   - Docs.

## Things to keep in mind

- Container Apps' **scale-to-zero would stop the background threads**. Keep `minReplicas = 1` while up.
- A **stopped** Flexible Server auto-starts after 7 days. `azd down` is the real "off" switch.
- Check that **gpt-oss-20b is available on Foundry in Central India**. If it isn't, the model deployment can live in another region while the apps stay in Pune; say so on stage.
- The Copilot's access is now a **DB login on the primary**, so the "never write to MediTrack" rule is enforced by Postgres grants, not by a copy.
- The `azd up` deployment can't be run from Claude's sandbox (no Azure credentials). Bicep is validated with `az bicep build` / `azd provision --preview`; you run the real `azd up`.
