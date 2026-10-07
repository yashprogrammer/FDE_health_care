"""Generate live drafts for every POC encounter + current in-patient and cache them (demo safety net)."""
import json

from copilot_core import config
from copilot_core.agent import generate_draft
from copilot_core.encounter import connect_mis, load_encounter
from copilot_core.models import Encounter
from copilot_core.observability import setup
from poc.export_deidentified import OUT

config.WRITE_CACHE = True
setup("discharge-copilot-warm-cache")
encs = [Encounter.model_validate(e) for e in json.loads(OUT.read_text())]
conn = connect_mis()
encs += [load_encounter(conn, r["IP_NO"]) for r in conn.execute("SELECT IP_NO FROM IP_ADM_DTL WHERE STS IN ('ADM','DA')")]
for e in encs:
    r = generate_draft(e)
    print(f"{e.ip_no:12} {r.source:8} {r.latency_ms:6} ms  {r.error or ''}")
