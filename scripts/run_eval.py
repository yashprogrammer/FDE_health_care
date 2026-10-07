"""Run the POC eval from the command line against the configured provider (no cache), e.g. to re-validate on Foundry.

  ./run.sh eval            Groq (local .env)
  ./run.sh eval-foundry    Azure AI Foundry deployment created by `azd up`
"""
import json
import statistics

from copilot_core import config
from copilot_core.agent import generate_draft
from copilot_core.models import Encounter
from copilot_core.observability import setup
from poc.evaluation import evaluate
from poc.export_deidentified import OUT

setup("discharge-copilot-eval")
print(f"Model: {config.MODEL}  ({'OFFLINE - cache/template only' if config.OFFLINE else 'live'})\n")
rows = []
for e in (Encounter.model_validate(x) for x in json.loads(OUT.read_text())):
    r = generate_draft(e)
    rows.append(evaluate(e, r))
    print(f"{e.ip_no}  {r.source:8} {r.latency_ms:6} ms  faithful {rows[-1]['faithfulness_%']:3}%  "
          f"hallucinated {rows[-1]['hallucinated']}  {r.error or ''}")

live = [x for x in rows if x["source"] == "live"]
recall = [x["key_fact_recall_%"] for x in rows if x["key_fact_recall_%"] is not None]
print(f"""
live drafts          {len(live)}/{len(rows)}
hallucinated         {sum(x['hallucinated'] for x in rows)}
unverified numbers   {sum(x['unverified_numbers'] for x in rows)}
faithfulness         {statistics.mean(x['faithfulness_%'] for x in rows):.0f}%
key-fact recall      {statistics.mean(recall):.0f}%
completeness         {statistics.mean(x['completeness_%'] for x in rows):.0f}%
median latency       {statistics.median(x['latency_s'] for x in live) if live else '-'} s""")
