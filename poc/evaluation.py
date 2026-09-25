"""Offline eval for the Discharge Copilot: faithfulness, completeness, key-fact recall vs the doctor's summary."""
import re

from copilot_core.models import DraftResult, Encounter
from copilot_core.rules import readiness_score, tpa_checklist
from copilot_core.trace import FORMULARY, LAB_TERMS, NUM_RE, draft_to_text, summarize, trace


def _key_facts(text: str) -> set[str]:
    """Clinical facts (drugs, lab tests, numbers) mentioned in a text."""
    facts = {n for n in NUM_RE.findall(text)}
    low = text.lower()
    facts |= {t.lower() for t in LAB_TERMS + FORMULARY if re.search(rf"(?<!\w){re.escape(t.lower())}(?!\w)", low)}
    return facts


def key_fact_recall(reference: str, draft_text: str) -> float | None:
    # medications are deterministic (pharmacy), so exclude the reference's medication line
    ref = "\n".join(line for line in reference.splitlines() if not line.lower().startswith("discharge medications"))
    ref_facts = _key_facts(ref)
    if not ref_facts:
        return None
    return len(ref_facts & _key_facts(draft_text)) / len(ref_facts)


def evaluate(enc: Encounter, res: DraftResult) -> dict:
    d = res.draft
    text = draft_to_text(d)
    required = {
        "presenting_complaints": bool(d.presenting_complaints.strip()),
        "hospital_course": len(d.hospital_course) >= 3,
        "key_investigations": bool(d.key_investigations),
        "condition_at_discharge": bool(d.condition_at_discharge.strip()),
        "follow_up_advice": bool(d.follow_up_advice),
    }
    if enc.procedures:
        required["procedures_performed"] = bool(d.procedures_performed)
    t = summarize(trace(text, enc))
    recall = key_fact_recall(enc.reference_summary or "", text)
    return {
        "encounter": enc.ip_no,
        "diagnosis": (enc.final_diagnoses or enc.diagnoses)[0].description[:40],
        "source": res.source,
        "completeness_%": round(100 * sum(required.values()) / len(required)),
        "hallucinated": t["hallucinated"],
        "unverified_numbers": t["unverified"],
        "faithfulness_%": round(100 * t["verified"] / t["total"]) if t["total"] else 100,
        "key_fact_recall_%": round(100 * recall) if recall is not None else None,
        "tpa_readiness_%": readiness_score(tpa_checklist(enc)),
        "latency_s": round(res.latency_ms / 1000, 1),
        "tokens": res.input_tokens + res.output_tokens,
        "cost_usd": round(res.cost_usd, 5),
    }
