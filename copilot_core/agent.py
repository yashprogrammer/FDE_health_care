"""The AI engineer's slice: a Pydantic AI agent that drafts the narrative sections of a discharge summary.

Fallback chain (so a live demo never dies): live LLM -> cached draft -> template draft from source data.
"""
import json
import time

import logfire
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.groq import GroqModelSettings

from . import config
from .models import DraftResult, Encounter, KeyInvestigation, SummaryDraft

INSTRUCTIONS = """\
You are a clinical documentation assistant at CityCare Hospitals, Pune (India).
Draft the narrative sections of a hospital DISCHARGE SUMMARY for the treating doctor to review and sign.

Hard rules:
- Use ONLY facts present in the encounter data. Never invent drugs, doses, lab values, dates, diagnoses or procedures.
- Copy numbers exactly as they appear in the data (values, units, LVEF, stent sizes).
- Do NOT write a discharge medication list - it is added separately from the pharmacy system.
- If a report is PENDING, mention in the hospital course that it is awaited.
- Hospital course: 4-7 short chronological bullets in the clinical style Indian doctors use
  (abbreviations like CAG, PTCA, DES, LVEF, TIMI are fine).
- Follow-up and diet/activity: only what the notes say. If nothing is stated, write "As advised by treating consultant".
- procedures_performed: list EVERY procedure in the data (one item each, with date and key findings). Empty only if none.
- Write dates as DD/MM/YYYY. Do not state or predict a discharge date - the system adds it.
- Fill every field of the output schema.
"""

# NativeOutput = provider-enforced JSON schema. Groq rejects gpt-oss tool-call output
# ("output_parse_failed"), but its native structured outputs work reliably.
agent = Agent(
    config.MODEL,
    output_type=NativeOutput(SummaryDraft),
    instructions=INSTRUCTIONS,
    name="discharge_copilot",
    retries=2,
    defer_model_check=True,
    # gpt-oss is a reasoning model: cap reasoning so it can't burn the whole token budget
    model_settings=GroqModelSettings(max_tokens=6000, temperature=0.2, groq_reasoning_effort="low"),
)
LLM_ATTEMPTS = 2   # provider-side schema rejections (HTTP 400) are not retried by the agent itself


def _cost(inp: int, out: int) -> float:
    return inp / 1e6 * config.PRICE_IN + out / 1e6 * config.PRICE_OUT


def _cache_path(ip_no: str):
    return config.CACHE_DIR / f"{ip_no}.json"


def save_cache(result: DraftResult) -> None:
    config.CACHE_DIR.mkdir(exist_ok=True)
    _cache_path(result.ip_no).write_text(result.model_dump_json(indent=2))


def load_cache(ip_no: str) -> DraftResult | None:
    p = _cache_path(ip_no)
    if not p.exists():
        return None
    return DraftResult.model_validate_json(p.read_text()).model_copy(update={"source": "cached"})


def template_draft(enc: Encounter) -> SummaryDraft:
    """Deterministic, no-AI draft built straight from source data. Last-resort fallback."""
    return SummaryDraft(
        presenting_complaints=enc.reason_for_admission,
        hospital_course=[n.text for n in enc.notes if n.type == "DR"][:6],
        procedures_performed=[f"{p.description} ({p.date[:10]})" for p in enc.procedures],
        key_investigations=[KeyInvestigation(test=lab.test, result=f"{lab.value} {lab.unit}".strip(),
                                             interpretation={"H": "high", "L": "low"}.get(lab.flag, "noted"))
                            for lab in enc.labs if lab.flag and lab.status == "FINAL"],
        condition_at_discharge="To be completed by treating doctor",
        follow_up_advice=["As advised by treating consultant"],
        diet_and_activity=["As advised by treating consultant"],
    )


def generate_draft(enc: Encounter, use_cache_first: bool = False) -> DraftResult:
    with logfire.span("discharge_copilot.generate_draft", ip_no=enc.ip_no, pay_mode=enc.pay_mode,
                      speciality=enc.consultant_speciality):
        if use_cache_first and (cached := load_cache(enc.ip_no)):
            return cached
        error = None
        if not config.OFFLINE:
            t0 = time.perf_counter()
            try:
                prompt = "Encounter data (JSON):\n" + json.dumps(enc.for_llm(), indent=1)
                for attempt in range(1, LLM_ATTEMPTS + 1):
                    try:
                        run = agent.run_sync(prompt)
                        break
                    except Exception as e:
                        if attempt == LLM_ATTEMPTS:
                            raise
                        logfire.warn("LLM attempt failed, retrying", attempt=attempt, error=str(e)[:200])
                usage = run.usage() if callable(run.usage) else run.usage
                result = DraftResult(
                    ip_no=enc.ip_no, draft=run.output, source="live", model=config.MODEL,
                    latency_ms=int((time.perf_counter() - t0) * 1000),
                    input_tokens=usage.input_tokens or 0, output_tokens=usage.output_tokens or 0,
                    cost_usd=_cost(usage.input_tokens or 0, usage.output_tokens or 0),
                )
                if config.WRITE_CACHE:
                    save_cache(result)
                return result
            except Exception as e:  # network / rate limit / validation - fall through to cache
                error = f"{type(e).__name__}: {e}"[:300]
                logfire.warn("LLM call failed, falling back", error=error)
        else:
            error = "offline mode (no GROQ_API_KEY or COPILOT_OFFLINE=1)"
        if cached := load_cache(enc.ip_no):
            return cached.model_copy(update={"error": error})
        return DraftResult(ip_no=enc.ip_no, draft=template_draft(enc), source="template", model="none", error=error)
