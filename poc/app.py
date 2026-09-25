"""Discharge Copilot - POC (Part 2). Standalone: reads a de-identified export, touches no hospital system.

Run: ./run.sh poc
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from copilot_core import config, observability  # noqa: E402
from copilot_core.agent import generate_draft  # noqa: E402
from copilot_core.assemble import to_markdown  # noqa: E402
from copilot_core.models import DraftResult, Encounter  # noqa: E402
from copilot_core.rules import readiness_score, tpa_checklist  # noqa: E402
from copilot_core.trace import COLORS, draft_to_text, highlight_html, summarize, trace  # noqa: E402
from poc.evaluation import evaluate  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
EVAL_FILE = DATA / "eval_results.json"
FEEDBACK_FILE = DATA / "feedback.jsonl"
ICON = {"pass": "✅", "warn": "⚠️", "fail": "❌", "na": "➖"}

st.set_page_config(page_title="Discharge Copilot POC", page_icon="🩺", layout="wide")


@st.cache_resource
def _obs() -> bool:
    return observability.setup("discharge-copilot-poc")


@st.cache_data
def load_encounters() -> dict[str, Encounter]:
    raw = json.loads((DATA / "deidentified_encounters.json").read_text())
    return {e["ip_no"]: Encounter.model_validate(e) for e in raw}


logfire_on = _obs()
encs = load_encounters()
drafts: dict[str, DraftResult] = st.session_state.setdefault("drafts", {})
if EVAL_FILE.exists() and not drafts:
    for ip, r in json.loads(EVAL_FILE.read_text()).get("drafts", {}).items():
        drafts[ip] = DraftResult.model_validate(r)


def inr(usd: float) -> str:
    return f"₹{usd * config.USD_INR:.3f}"


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("🩺 Discharge Copilot")
    st.caption("POC · Week 4 · CityCare Hospitals")
    st.markdown(f"**Model:** `{config.MODEL}`")
    st.markdown(f"**LLM mode:** {'🔴 offline (cache/template)' if config.OFFLINE else '🟢 live'}")
    st.markdown(f"**Logfire tracing:** {'🟢 on' if logfire_on else '⚪ off (no token)'}")
    st.divider()
    ip = st.selectbox("Encounter (de-identified)", list(encs),
                      format_func=lambda k: f"{k} · {(encs[k].final_diagnoses or encs[k].diagnoses)[0].description[:28]}")
    enc = encs[ip]
    st.caption(f"{enc.age}/{enc.sex} · {enc.consultant_speciality} · {enc.pay_mode}")
    st.divider()
    st.caption("Data: 11 past discharges exported from MediTrack's reporting replica and de-identified. "
               "This POC is not connected to any hospital system.")

st.title("Discharge Copilot: Proof of Concept")
tab_gen, tab_trace, tab_eval, tab_fb = st.tabs(["⚡ Generate", "🔍 Source trace", "📊 Eval", "👩‍⚕️ Clinician feedback"])

# ------------------------------------------------------------------ 1. Generate
with tab_gen:
    with st.expander("Source data for this encounter (what the AI sees)"):
        c1, c2 = st.columns(2)
        c1.markdown("**Diagnoses**")
        c1.dataframe(pd.DataFrame([d.model_dump() for d in enc.diagnoses]), hide_index=True)
        c1.markdown("**Labs**")
        c1.dataframe(pd.DataFrame([lab.model_dump() for lab in enc.labs]), hide_index=True)
        c2.markdown("**Clinical notes**")
        c2.dataframe(pd.DataFrame([n.model_dump() for n in enc.notes]), hide_index=True)
        c2.markdown("**Medications**")
        c2.dataframe(pd.DataFrame([m.model_dump() | {"type": "inpatient"} for m in enc.inpatient_meds]
                                  + [m.model_dump() | {"type": "discharge"} for m in enc.discharge_meds]), hide_index=True)

    if st.button("⚡ Generate discharge summary draft", type="primary"):
        with st.spinner("Drafting with Pydantic AI agent..."):
            drafts[ip] = generate_draft(enc)

    res = drafts.get(ip)
    if res:
        m = st.columns(5)
        m[0].metric("Source", {"live": "🟢 live LLM", "cached": "🟡 cached", "template": "⚪ template"}[res.source])
        m[1].metric("Latency", f"{res.latency_ms / 1000:.1f}s")
        m[2].metric("Tokens", f"{res.input_tokens + res.output_tokens:,}")
        m[3].metric("Cost / summary", inr(res.cost_usd))
        checks = tpa_checklist(enc)
        m[4].metric("TPA readiness", f"{readiness_score(checks)}%")
        if res.error:
            st.caption(f"Fallback reason: {res.error}")
        left, right = st.columns([3, 2])
        with left:
            st.subheader("Draft discharge summary")
            st.caption("🔒 = pulled deterministically from hospital data, never generated")
            st.markdown(to_markdown(enc, res.draft))
        with right:
            st.subheader("TPA-readiness checklist")
            st.caption("Rules engine, not AI")
            for c in checks:
                st.markdown(f"{ICON[c.status]} **{c.label}**  \n<small>{c.detail}</small>", unsafe_allow_html=True)
    else:
        st.info("Pick an encounter in the sidebar and generate a draft.")

# ------------------------------------------------------------------ 2. Source trace
with tab_trace:
    res = drafts.get(ip)
    if not res:
        st.info("Generate a draft first.")
    else:
        st.markdown("Every **drug**, **lab test** and **number** in the draft is checked against this patient's "
                    "source data. Edit the text to test the guardrail, e.g. add *\"Warfarin 5 mg OD\"*.")
        text = st.text_area("Draft text (editable)", draft_to_text(res.draft), height=260, key=f"trace_{ip}")
        findings = trace(text, enc)
        s = summarize(findings)
        c = st.columns(4)
        c[0].metric("✅ Verified", s["verified"])
        c[1].metric("🟨 Unverified numbers", s["unverified"])
        c[2].metric("🟥 Hallucinated", s["hallucinated"])
        c[3].metric("Faithfulness", f"{round(100 * s['verified'] / s['total']) if s['total'] else 100}%")
        st.markdown(" ".join(f"<span style='background:{v};padding:2px 8px;border-radius:4px;color:#000'>{k}</span>"
                             for k, v in COLORS.items()), unsafe_allow_html=True)
        st.markdown(highlight_html(text, findings), unsafe_allow_html=True)
        bad = [f for f in findings if f.status != "verified"]
        if bad:
            st.dataframe(pd.DataFrame([f.model_dump(exclude={"start", "end"}) for f in bad]), hide_index=True)

# ------------------------------------------------------------------ 3. Eval
with tab_eval:
    st.markdown("Run the copilot on **all past discharges** and score it against the doctors' own summaries.")
    col_a, col_b = st.columns([1, 3])
    use_cache = col_a.toggle("Reuse cached drafts", value=False, help="Skip LLM calls where a cached draft exists")
    if col_b.button("▶ Run eval", type="primary"):
        bar = st.progress(0.0, "Running...")
        rows = []
        for i, (k, e) in enumerate(encs.items(), 1):
            drafts[k] = generate_draft(e, use_cache_first=use_cache)
            rows.append(evaluate(e, drafts[k]))
            bar.progress(i / len(encs), f"{k} done")
        EVAL_FILE.write_text(json.dumps({"run_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "rows": rows,
                                         "drafts": {k: v.model_dump() for k, v in drafts.items()}}, indent=1))
        bar.empty()
    if EVAL_FILE.exists():
        ev = json.loads(EVAL_FILE.read_text())
        df = pd.DataFrame(ev["rows"])
        st.caption(f"Last run: {ev['run_at']} · {len(df)} encounters")
        k = st.columns(6)
        k[0].metric("Completeness", f"{df['completeness_%'].mean():.0f}%")
        k[1].metric("Hallucinations", int(df["hallucinated"].sum()))
        k[2].metric("Faithfulness", f"{df['faithfulness_%'].mean():.0f}%")
        k[3].metric("Key-fact recall", f"{df['key_fact_recall_%'].dropna().mean():.0f}%")
        k[4].metric("Median latency", f"{df['latency_s'].median():.1f}s")
        k[5].metric("Avg cost / summary", inr(df["cost_usd"].mean()))
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.caption("Faithfulness = verified entities / all entities. Key-fact recall = share of drugs, tests and "
                   "numbers in the doctor's summary (excluding the medication list) that the draft also mentions.")

# ------------------------------------------------------------------ 4. Clinician feedback
with tab_fb:
    res = drafts.get(ip)
    if not res:
        st.info("Generate a draft (or run the eval) first.")
    else:
        a, b = st.columns(2)
        with a:
            st.subheader("🤖 AI draft")
            st.markdown(to_markdown(enc, res.draft))
        with b:
            st.subheader("✍️ Doctor's original summary")
            st.text(enc.reference_summary or "-")
        st.divider()
        with st.form(f"fb_{ip}", clear_on_submit=True):
            reviewer = st.selectbox("Reviewer", ["Dr. Anjali Mehta (Cardiology)", "Dr. Rajesh Gokhale (Medicine)",
                                                 "Dr. Sameer Bhide (Ortho)", "Dr. Neha Rao (Surgery)",
                                                 "Mrs. Shalini Kapoor (TPA desk lead)"])
            r = st.columns(3)
            acc = r[0].slider("Clinical accuracy", 1, 5, 4)
            comp = r[1].slider("Completeness", 1, 5, 4)
            use = r[2].slider("Time saved / usefulness", 1, 5, 4)
            sign = st.radio("Would you sign this after minor edits?", ["Yes", "No"], horizontal=True)
            comments = st.text_area("Comments", placeholder="e.g. Prefer hospital course as bullets; highlight pending reports")
            if st.form_submit_button("Submit feedback", type="primary"):
                with FEEDBACK_FILE.open("a") as f:
                    f.write(json.dumps({"ts": datetime.now().isoformat(timespec="seconds"), "encounter": ip,
                                        "reviewer": reviewer, "accuracy": acc, "completeness": comp,
                                        "usefulness": use, "would_sign": sign == "Yes", "comments": comments}) + "\n")
                st.success("Thanks! Feedback recorded.")
        if FEEDBACK_FILE.exists():
            fb = pd.DataFrame([json.loads(line) for line in FEEDBACK_FILE.read_text().splitlines() if line.strip()])
            st.subheader(f"Feedback so far ({len(fb)} reviews)")
            k = st.columns(4)
            k[0].metric("Accuracy", f"{fb['accuracy'].mean():.1f}/5")
            k[1].metric("Completeness", f"{fb['completeness'].mean():.1f}/5")
            k[2].metric("Usefulness", f"{fb['usefulness'].mean():.1f}/5")
            k[3].metric("Would sign", f"{100 * fb['would_sign'].mean():.0f}%")
            st.dataframe(fb, hide_index=True, use_container_width=True)
