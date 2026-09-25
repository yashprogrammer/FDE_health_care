import { useCallback, useEffect, useRef, useState } from 'react'

const MEDITRACK = 'http://localhost:8001'

const api = async (path, opts) => {
  const r = await fetch(path, opts)
  const body = await r.json().catch(() => ({}))
  if (!r.ok) {
    const e = new Error(body.detail || `HTTP ${r.status}`)
    e.status = r.status
    throw e
  }
  return body
}
const send = (method, path, body) =>
  api(path, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })

function useHash() {
  const [h, setH] = useState(window.location.hash || '#/')
  useEffect(() => {
    const on = () => setH(window.location.hash || '#/')
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return h
}

function usePoll(fn, ms, deps) {
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)
  const load = useCallback(() => fn().then((d) => { setData(d); setErr(null) }).catch(setErr), deps) // eslint-disable-line
  useEffect(() => {
    load()
    const t = setInterval(load, ms)
    return () => clearInterval(t)
  }, [load, ms])
  return [data, err, load]
}

const STATUS = { GENERATING: 'Drafting…', READY: 'Ready for review', SIGNED: 'Signed', ERROR: 'Error' }
const Chip = ({ s }) => <span className={`chip ${s}`}>{s === 'GENERATING' && <span className="spin" />}{STATUS[s] || s}</span>
const SrcChip = ({ s }) => s ? <span className={`chip src-${s}`}>{{ live: '● live LLM', cached: '● cached draft', template: '● template fallback' }[s]}</span> : null
const ICON = { pass: '✅', warn: '⚠️', fail: '❌', na: '➖' }

// ------------------------------------------------------------------ Worklist
function Worklist() {
  const [rows] = usePoll(() => api('/api/drafts'), 2000, [])
  return (
    <div className="page">
      <h1>Discharge worklist</h1>
      <p className="sub">Drafts appear automatically seconds after a doctor marks <b>Discharge Advised</b> in MediTrack.</p>
      <div className="card">
        {!rows?.length ? (
          <div className="empty">No discharges advised yet. Waiting for MediTrack…</div>
        ) : (
          <table className="list">
            <thead><tr><th>Patient</th><th>IP No</th><th>Ward / Bed</th><th>Consultant</th><th>Payment</th><th>Advised</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.ip_no}>
                  <td><b>{r.PT_NM}</b><div className="sub" style={{ margin: 0 }}>{r.PT_AGE}/{r.PT_SEX}</div></td>
                  <td className="mono">{r.ip_no}</td>
                  <td>{r.WRD_CD} / {r.BED_NO}</td>
                  <td>{r.DR_NM}</td>
                  <td>{r.PAY_MODE === 'CASHLESS' ? `Cashless · ${r.TPA_NM}` : 'Cash'}</td>
                  <td className="mono">{r.advised_at}</td>
                  <td><Chip s={r.status} /></td>
                  <td><a className="btn" href={`#/review/${r.ip_no}`}>Review →</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

// ------------------------------------------------------------------ Review
const LIST_FIELDS = ['hospital_course', 'procedures_performed', 'follow_up_advice', 'diet_and_activity']
const toForm = (d) => ({
  presenting_complaints: d.presenting_complaints,
  condition_at_discharge: d.condition_at_discharge,
  ...Object.fromEntries(LIST_FIELDS.map((f) => [f, d[f].join('\n')])),
  key_investigations: d.key_investigations.map((k) => `${k.test}: ${k.result} (${k.interpretation})`).join('\n'),
})
const fromForm = (f) => ({
  presenting_complaints: f.presenting_complaints,
  condition_at_discharge: f.condition_at_discharge,
  ...Object.fromEntries(LIST_FIELDS.map((k) => [k, f[k].split('\n').map((s) => s.trim()).filter(Boolean)])),
  key_investigations: f.key_investigations.split('\n').map((s) => s.trim()).filter(Boolean).map((line) => {
    const m = line.match(/^(.*?):\s*(.*?)\s*\((.*)\)\s*$/) || line.match(/^(.*?):\s*(.*)$/)
    return m ? { test: m[1], result: m[2], interpretation: m[3] || '' } : { test: line, result: '', interpretation: '' }
  }),
})

function Review({ ip, embed = false }) {
  const [data, setData] = useState(null)
  const [waiting, setWaiting] = useState(false)
  const [form, setForm] = useState(null)
  const [dirty, setDirty] = useState(false)
  const [traceInfo, setTraceInfo] = useState(null)
  const [checks, setChecks] = useState(null)
  const [flash, setFlash] = useState(false)
  const [busy, setBusy] = useState('')
  const [msg, setMsg] = useState(null)
  const prevScore = useRef(null)

  const load = useCallback(async () => {
    try {
      const d = await api(`/api/drafts/${ip}`)
      setWaiting(false)
      setData(d)
      setTraceInfo(d.trace)
      setChecks({ checks: d.checks, readiness: d.readiness })
      prevScore.current = d.readiness
      if (d.draft) { setForm(toForm(d.draft)); setDirty(false) }
    } catch (e) {
      if (e.status === 404) setWaiting(true)
      else setMsg({ kind: 'err', text: e.message })
    }
  }, [ip])

  useEffect(() => { load() }, [load])

  // wait for draft (not advised yet / still generating)
  useEffect(() => {
    if (!(waiting || data?.meta.status === 'GENERATING')) return
    const t = setInterval(load, 2000)
    return () => clearInterval(t)
  }, [waiting, data?.meta.status, load])

  // live TPA checks: re-read from MediTrack replica, so uploads in MediTrack show up here
  useEffect(() => {
    if (!data || data.meta.status === 'SIGNED') return
    const t = setInterval(async () => {
      const c = await api(`/api/drafts/${ip}/checks`).catch(() => null)
      if (!c) return
      if (prevScore.current !== null && c.readiness !== prevScore.current) { setFlash(true); setTimeout(() => setFlash(false), 1700) }
      prevScore.current = c.readiness
      setChecks(c)
    }, 3000)
    return () => clearInterval(t)
  }, [data, ip])

  const set = (k) => (e) => { setForm({ ...form, [k]: e.target.value }); setDirty(true) }

  const save = async () => {
    setBusy('save')
    try {
      const r = await send('PUT', `/api/drafts/${ip}`, { draft: fromForm(form) })
      setTraceInfo(r.trace); setDirty(false)
      setMsg({ kind: 'info', text: `Edits saved · ${r.edit_pct}% of the draft changed by doctor` })
    } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  const regenerate = async () => {
    if (!window.confirm('Discard edits and regenerate the draft?')) return
    setBusy('regen')
    try { await send('POST', `/api/drafts/${ip}/regenerate`); await load(); setMsg({ kind: 'info', text: 'Draft regenerated' }) } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  const signNow = async () => {
    const failing = checks.checks.filter((c) => c.status === 'fail')
    const warn = failing.length ? `\n\n⚠ ${failing.length} TPA check(s) failing:\n- ${failing.map((c) => c.detail).join('\n- ')}\n\nThe insurer is likely to raise a query.` : ''
    if (!window.confirm(`Sign as ${data.encounter.consultant} and send to MediTrack?${warn}`)) return
    setBusy('sign')
    try {
      if (dirty) await send('PUT', `/api/drafts/${ip}`, { draft: fromForm(form) })
      const r = await send('POST', `/api/drafts/${ip}/sign`, { signed_by: data.encounter.consultant })
      await load()
      setMsg({ kind: 'ok', text: embed
        ? `Signed ✓  The discharge summary PDF will appear in this patient's Documents tab within seconds.`
        : `Signed ✓  ${r.file} dropped into MediTrack's document import folder. It will appear in the patient's Documents tab within seconds.` })
    } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  if (waiting) {
    return (
      <div className="page">
        <div className="card empty">
          <span className="chip GENERATING"><span className="spin" />Waiting</span>
          {embed
            ? <p>No AI draft yet. Click <b>Discharge Advised</b> above when the patient is ready to go home. A draft discharge summary will appear in this tab within seconds.</p>
            : <p>No draft for <b className="mono">{ip}</b> yet. Mark the patient <b>Discharge Advised</b> in MediTrack. The draft appears here automatically.</p>}
        </div>
      </div>
    )
  }
  if (!data) return <div className="page">Loading…</div>

  const { meta, encounter: enc } = data
  const signed = meta.status === 'SIGNED'
  const score = checks?.readiness ?? data.readiness
  const scoreColor = score >= 90 ? 'var(--ok)' : score >= 70 ? 'var(--warn)' : 'var(--bad)'
  const t = traceInfo?.summary || { verified: 0, unverified: 0, hallucinated: 0 }
  const finalDx = enc.diagnoses.filter((d) => d.type === 'FINAL')
  const dx = finalDx.length ? finalDx : enc.diagnoses
  const pending = enc.labs.filter((l) => l.status === 'PENDING')

  const field = (k, label, rows = 3) => (
    <div className="sec">
      <label>{label} <span className="tag ai">AI draft · editable</span></label>
      <textarea rows={rows} value={form[k]} onChange={set(k)} disabled={signed} />
    </div>
  )

  return (
    <div className="page">
      {msg && <div className={`banner ${msg.kind}`}>{msg.text}</div>}
      {embed ? (
        <div className="embed-head">
          <b>AI Discharge Draft</b> · <Chip s={meta.status} /> <SrcChip s={meta.source} />
          {meta.latency_ms > 0 && <span> drafted in {(meta.latency_ms / 1000).toFixed(1)}s</span>}
          <span className="hint"> · Review, edit and sign. Nothing reaches the patient or insurer without your signature.</span>
        </div>
      ) : (
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <h1>{enc.patient_name} <span style={{ color: 'var(--muted)', fontWeight: 500 }}>· {enc.age}/{enc.sex}</span></h1>
            <div className="pt-head">
              <span>IP <b className="mono">{enc.ip_no}</b></span><span>UHID <b>{enc.uhid}</b></span>
              <span>Ward <b>{enc.ward}/{enc.bed}</b></span><span>Consultant <b>{enc.consultant}</b></span>
              <span>Payment <b>{enc.pay_mode === 'CASHLESS' ? `Cashless · ${enc.tpa_name}` : 'Cash'}</b></span>
              <span>Advised <b>{meta.advised_at}</b></span>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <Chip s={meta.status} />
            <div className="meta-row" style={{ justifyContent: 'flex-end' }}>
              <SrcChip s={meta.source} />
              {meta.latency_ms > 0 && <span>{(meta.latency_ms / 1000).toFixed(1)}s</span>}
              {meta.input_tokens > 0 && <span>{meta.input_tokens + meta.output_tokens} tokens</span>}
              <a href={`${MEDITRACK}/#/ip/${ip}`} target="meditrack">Open in MediTrack ↗</a>
            </div>
          </div>
        </div>
      </div>
      )}

      {meta.status === 'GENERATING' || !form ? (
        <div className="card empty"><span className="chip GENERATING"><span className="spin" />Drafting with AI…</span></div>
      ) : (
        <div className="review">
          <div className="card">
            <div className="sec">
              <label>Final diagnosis <span className="tag lock">🔒 from MediTrack</span></label>
              <div className="locked"><ul>{dx.map((d, i) => <li key={i}>{d.description} <span className="mono">({d.icd10})</span>{d.type === 'PROV' && <b style={{ color: 'var(--bad)' }}> · PROVISIONAL</b>}</li>)}</ul></div>
            </div>
            {field('presenting_complaints', 'Presenting complaints', 2)}
            {field('hospital_course', 'Hospital course (one point per line)', 7)}
            {(enc.procedures.length > 0 || form.procedures_performed) && field('procedures_performed', 'Procedures', 3)}
            {field('key_investigations', 'Key investigations', 6)}
            {pending.length > 0 && (
              <div className="sec">
                <label>Reports pending at discharge <span className="tag pending">⚠ auto-listed</span></label>
                <div className="locked"><ul>{pending.map((l, i) => <li key={i}>{l.test} (sent {l.date.slice(0, 10)}): to be reviewed at follow-up</li>)}</ul></div>
              </div>
            )}
            {field('condition_at_discharge', 'Condition at discharge', 2)}
            <div className="sec">
              <label>Discharge medications <span className="tag lock">🔒 from pharmacy, never AI-generated</span></label>
              <div className="locked"><ul>{enc.discharge_meds.map((m, i) => <li key={i}><b>{m.drug}</b> {m.dose} · {m.frequency} · {m.route}{m.duration && ` · ${m.duration}`}</li>)}</ul></div>
            </div>
            {field('follow_up_advice', 'Follow-up', 3)}
            {field('diet_and_activity', 'Diet & activity', 3)}
            {!signed && (
              <div className="actions">
                <button className="btn" disabled={!dirty || !!busy} onClick={save}>{busy === 'save' ? 'Saving…' : 'Save edits'}</button>
                <button className="btn" disabled={!!busy} onClick={regenerate}>{busy === 'regen' ? 'Regenerating…' : '↻ Regenerate'}</button>
                <a className="btn" href={`/api/drafts/${ip}/pdf`} target="_blank" rel="noreferrer">Preview PDF</a>
                <span style={{ flex: 1 }} />
                <button className="btn primary" disabled={!!busy} onClick={signNow}>{busy === 'sign' ? 'Signing…' : '✍ Sign & send to MediTrack'}</button>
              </div>
            )}
            {signed && <div className="banner ok" style={{ margin: 0 }}>Signed by {meta.signed_by} at {meta.signed_at} · <span className="mono">{meta.pdf_file}</span> {embed ? 'is in the Documents tab' : <>sent to MediTrack · <a href={`${MEDITRACK}/#/ip/${ip}`} target="meditrack">view in MediTrack ↗</a></>}</div>}
          </div>

          <div className="side">
            <div className={`card ${flash ? 'flash' : ''}`}>
              <h3>TPA readiness <span className="tag lock">rules engine · live from MediTrack</span></h3>
              <div className="score">
                <span className="num" style={{ color: scoreColor }}>{score}%</span>
                <div className="bar"><div style={{ width: `${score}%`, background: scoreColor }} /></div>
              </div>
              {checks?.checks.map((c) => (
                <div key={c.id} className={`check ${c.status}`}>
                  <span className="ic">{ICON[c.status]}</span>
                  <div>{c.label}<small>{c.detail}</small></div>
                </div>
              ))}
            </div>
            <div className="card">
              <h3>Source trace <span className="tag ai">guardrail</span></h3>
              <div className="tr-counts">
                <div className="v"><b>{t.verified}</b>verified</div>
                <div className="u"><b>{t.unverified}</b>unverified</div>
                <div className="h"><b>{t.hallucinated}</b>not in record</div>
              </div>
              {traceInfo?.flags.length ? traceInfo.flags.slice(0, 8).map((f, i) => (
                <div key={i} className="check"><span className="ic">{f.status === 'hallucinated' ? '🟥' : '🟨'}</span><div><b>{f.text}</b><small>{f.kind} · {f.status === 'hallucinated' ? 'not found in patient record' : 'number not found in source data'}</small></div></div>
              )) : <div className="sub" style={{ margin: 0 }}>Every drug, test and number traces back to MediTrack data.</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ------------------------------------------------------------------ Monitor
function Monitor() {
  const [m] = usePoll(() => api('/api/metrics'), 3000, [])
  if (!m) return <div className="page">Loading…</div>
  const { baseline: b, pilot: p } = m
  const fmt = (v, s = '') => (v === null || v === undefined ? '-' : `${v}${s}`)
  return (
    <div className="page">
      <h1>Pilot monitor · Cardiology Ward 4B</h1>
      <p className="sub">Baseline computed from MediTrack's MIS replica ({b.discharges} discharges, last quarter). Pilot metrics from the Copilot.</p>
      <div className="kpis">
        <div className="kpi base"><div className="l">Baseline · cashless discharge TAT</div><div className="n">{fmt(b.cashless_tat_hrs, ' h')}</div><div className="d">cash patients: {fmt(b.cash_tat_hrs, ' h')}</div></div>
        <div className="kpi base"><div className="l">Baseline · TPA query rate</div><div className="n">{fmt(b.tpa_query_pct, '%')}</div><div className="d">each query adds ~2-4 h</div></div>
        <div className="kpi pilot"><div className="l">Pilot · draft ready after advice</div><div className="n">{fmt(p.median_draft_s, ' s')}</div><div className="d">was 35-45 min of typing</div></div>
        <div className="kpi pilot"><div className="l">Pilot · advised → signed</div><div className="n">{fmt(p.median_advised_to_signed_min, ' min')}</div><div className="d">{p.signed} signed / {p.drafted} drafted</div></div>
        <div className="kpi pilot"><div className="l">TPA readiness at sign</div><div className="n">{fmt(p.avg_tpa_readiness_at_sign, '%')}</div><div className="d">rules engine score</div></div>
        <div className="kpi pilot"><div className="l">Doctor edits</div><div className="n">{fmt(p.avg_edit_pct, '%')}</div><div className="d">of draft text changed</div></div>
        <div className="kpi pilot"><div className="l">Guardrail flags</div><div className="n">{p.trace_flags}</div><div className="d">unverified or not-in-record items</div></div>
        <div className="kpi pilot"><div className="l">AI cost (pilot total)</div><div className="n">${p.ai_cost_usd}</div><div className="d">live {p.sources.live} · cached {p.sources.cached} · template {p.sources.template}</div></div>
      </div>
      <div className="grid2">
        <div className="card">
          <h3>Why insurers sent claims back last quarter</h3>
          <table className="list">
            <thead><tr><th>TPA query reason</th><th>Count</th></tr></thead>
            <tbody>{b.query_reasons.map((r) => <tr key={r.reason}><td>{r.reason}</td><td>{r.n}</td></tr>)}</tbody>
          </table>
          <p className="sub" style={{ margin: '10px 0 0' }}>Each reason maps to a rule in the TPA-readiness checklist, so the gap is caught before submission.</p>
        </div>
        <div className="card">
          <h3>Activity <a style={{ marginLeft: 'auto', fontSize: 13 }} href={m.logfire_url} target="_blank" rel="noreferrer">Open traces in Logfire ↗</a></h3>
          <table className="list">
            <tbody>{m.events.map((e) => <tr key={e.id}><td className="mono">{e.ts.slice(11)}</td><td className="mono">{e.ip_no}</td><td><b>{e.action}</b><div className="sub" style={{ margin: 0 }}>{e.actor} · {e.detail}</div></td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const h = useHash()
  const rev = h.match(/^#\/review\/(.+)$/)
  const emb = h.match(/^#\/embed\/review\/(.+)$/)
  // Embedded in MediTrack's patient-file tab: classic look, no Copilot chrome
  if (emb) return <div className="classic"><Review ip={decodeURIComponent(emb[1])} embed key={emb[1]} /></div>
  return (
    <>
      <div className="top">
        <div className="brand"><span className="dot">✚</span>Discharge Copilot</div>
        <nav>
          <a href="#/" className={!rev && h !== '#/monitor' ? 'cur' : ''}>Worklist</a>
          <a href="#/monitor" className={h === '#/monitor' ? 'cur' : ''}>Monitor</a>
        </nav>
        <span className="sp" />
        <span className="who">CityCare Hospitals · Cardiology pilot</span>
      </div>
      {rev ? <Review ip={decodeURIComponent(rev[1])} key={rev[1]} /> : h === '#/monitor' ? <Monitor /> : <Worklist />}
    </>
  )
}
