// Discharge Copilot: the "AI Discharge Draft" tab shown inside MediTrack's patient file.
// Built only from MediTrack's own look (fieldsets, grid tables, bevelled buttons) so that
// doctors see one new tab, not a new application.
import { useCallback, useEffect, useRef, useState } from 'react'

const api = async (path, opts) => {
  const r = await fetch(path, opts)
  const body = await r.json().catch(() => ({}))
  if (!r.ok) {
    const e = new Error(body.detail || `ERROR ${r.status}`)
    e.status = r.status
    throw e
  }
  return body
}
const send = (method, path, body) =>
  api(path, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })

// Tell MediTrack how tall we are so the tab grows to fit (no scrollbar inside a scrollbar)
function useReportHeight() {
  useEffect(() => {
    const post = () => window.parent?.postMessage({ type: 'meditrack:tab-height', height: document.documentElement.scrollHeight }, '*')
    const ro = new ResizeObserver(post)
    ro.observe(document.body)
    post()
    return () => ro.disconnect()
  }, [])
}

const STATUS = { GENERATING: 'DRAFTING...', READY: 'READY FOR REVIEW', SIGNED: 'SIGNED', ERROR: 'ERROR' }
const SOURCE = { live: 'AI (live)', cached: 'AI (cached copy)', template: 'Template (AI unavailable)' }
const RESULT = { pass: ['OK', 'OK'], fail: ['MISSING', 'FAIL'], warn: ['CHECK', 'WARN'], na: ['N/A', 'NA'] }

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

function Grid({ rows, cols }) {
  if (!rows?.length) return <div className="hint">No records found.</div>
  return (
    <table className="grid">
      <thead><tr>{cols.map(([, h]) => <th key={h}>{h}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i}>{cols.map(([k]) => <td key={k}>{r[k] ?? ''}</td>)}</tr>)}</tbody>
    </table>
  )
}

function DraftTab({ ip }) {
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
  useReportHeight()

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

  // until the draft exists (discharge not yet advised / still drafting), keep checking
  useEffect(() => {
    if (!(waiting || data?.meta.status === 'GENERATING')) return
    const t = setInterval(load, 2000)
    return () => clearInterval(t)
  }, [waiting, data?.meta.status, load])

  // TPA checks are re-read from MediTrack data, so a document uploaded in the Documents tab counts within seconds
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
      setMsg({ kind: 'info', text: `Draft saved. ${r.edit_pct}% of the AI text changed by doctor.` })
    } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  const regenerate = async () => {
    if (!window.confirm('DISCARD YOUR EDITS AND PREPARE A NEW DRAFT?')) return
    setBusy('regen')
    try { await send('POST', `/api/drafts/${ip}/regenerate`); await load(); setMsg({ kind: 'info', text: 'New draft prepared.' }) } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  const sign = async () => {
    const failing = checks.checks.filter((c) => c.status === 'fail')
    const warn = failing.length ? `\n\nWARNING: ${failing.length} TPA CHECK(S) FAILING:\n- ${failing.map((c) => c.detail).join('\n- ')}\n\nINSURER MAY RAISE A QUERY.` : ''
    if (!window.confirm(`SIGN DISCHARGE SUMMARY AS ${data.encounter.consultant.toUpperCase()}?${warn}`)) return
    setBusy('sign')
    try {
      if (dirty) await send('PUT', `/api/drafts/${ip}`, { draft: fromForm(form) })
      await send('POST', `/api/drafts/${ip}/sign`, { signed_by: data.encounter.consultant })
      await load()
      setMsg({ kind: 'ok', text: 'Discharge summary signed. PDF will appear in the Documents tab shortly.' })
    } catch (e) { setMsg({ kind: 'err', text: e.message }) }
    setBusy('')
  }

  if (waiting) {
    return (
      <fieldset>
        <legend>AI Discharge Draft</legend>
        <p>No draft prepared yet for <b>{ip}</b>.</p>
        <p className="hint">Click <b>Discharge Advised</b> at the top of the patient file. The discharge summary draft will be prepared
          from this patient's Diagnosis, Procedures, Lab Results, Pharmacy and Clinical Notes and shown here within a few seconds.</p>
      </fieldset>
    )
  }
  if (!data) return <div>Loading...</div>

  const { meta, encounter: enc } = data
  const signed = meta.status === 'SIGNED'
  const score = checks?.readiness ?? data.readiness
  const t = traceInfo?.summary || { verified: 0, unverified: 0, hallucinated: 0 }
  const finalDx = enc.diagnoses.filter((d) => d.type === 'FINAL')
  const dx = finalDx.length ? finalDx : enc.diagnoses
  const pending = enc.labs.filter((l) => l.status === 'PENDING')
  const nOk = checks?.checks.filter((c) => c.status === 'pass').length ?? 0
  const nApplicable = checks?.checks.filter((c) => c.status !== 'na').length ?? 0

  const field = (k, label, rows) => (
    <>
      <div className="lbl">{label} <span className="src ai">AI DRAFT</span></div>
      <textarea rows={rows} value={form[k]} onChange={set(k)} disabled={signed} />
    </>
  )

  return (
    <div className="mt-embed">
      {msg && <div className={`msgbar ${msg.kind}`}>{msg.text}</div>}
      <fieldset>
        <legend>AI Discharge Draft - {ip}</legend>
        <div className="pt-strip">
          <span><b>Draft Status:</b> <span className={`sts ${meta.status}`}>{STATUS[meta.status]}</span></span>
          <span><b>Prepared By:</b> {SOURCE[meta.source] || '-'}</span>
          <span><b>Prep. Time:</b> {meta.latency_ms ? `${(meta.latency_ms / 1000).toFixed(1)} sec` : '-'}</span>
          <span><b>TPA Readiness:</b> {score}%</span>
          <span><b>Disch. Advised:</b> {meta.advised_at || '-'}</span>
          <span><b>Draft Ready:</b> {meta.ready_at || '-'}</span>
          <span><b>Signed By:</b> {meta.signed_by || '-'}</span>
          <span><b>Signed On:</b> {meta.signed_at || '-'}</span>
        </div>
        <div className="hint">
          Draft prepared from MediTrack data. Please review and edit before signing. Fields marked LOCKED are copied
          from MediTrack and must be corrected in their own tab.
        </div>
        {!signed && meta.status === 'READY' && (
          <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
            <button disabled={!dirty || !!busy} onClick={save}>{busy === 'save' ? 'Saving...' : 'Save Draft'}</button>
            <button disabled={!!busy} onClick={regenerate}>{busy === 'regen' ? 'Preparing...' : 'Prepare New Draft'}</button>
            <a className="btn" href={`/api/drafts/${ip}/pdf`} target="_blank" rel="noreferrer">Print Preview</a>
            <button className="primary" disabled={!!busy} onClick={sign}>{busy === 'sign' ? 'Signing...' : 'Sign Discharge Summary'}</button>
          </div>
        )}
      </fieldset>

      {meta.status === 'GENERATING' || !form ? (
        <fieldset><legend>Discharge Summary (Draft)</legend><div>Preparing draft, please wait...</div></fieldset>
      ) : (
        <div className="cols">
          <div className="colmain">
            <fieldset>
              <legend>Discharge Summary (Draft) - Form MRD/DS/07</legend>
              <div className="lbl">Diagnosis: <span className="src lock">LOCKED - DIAGNOSIS TAB</span></div>
              <Grid rows={dx.map((d) => ({ ...d, type: d.type === 'PROV' ? 'PROV (!)' : d.type }))}
                cols={[['type', 'Type'], ['icd10', 'ICD-10'], ['description', 'Description']]} />
              {field('presenting_complaints', 'Presenting complaints:', 2)}
              {field('hospital_course', 'Hospital course: (one point per line)', 7)}
              {(enc.procedures.length > 0 || form.procedures_performed) && field('procedures_performed', 'Procedures:', 3)}
              {field('key_investigations', 'Investigations:', 6)}
              {pending.length > 0 && (
                <>
                  <div className="lbl">Reports pending at discharge: <span className="src auto">AUTO - LAB RESULTS TAB</span></div>
                  <Grid rows={pending.map((l) => ({ ...l, sent: l.date.slice(0, 10), note: 'To be reviewed at follow-up' }))}
                    cols={[['test', 'Test'], ['sent', 'Sent On'], ['status', 'Status'], ['note', 'Remark']]} />
                </>
              )}
              {field('condition_at_discharge', 'Condition at discharge:', 2)}
              <div className="lbl">Discharge medications: <span className="src lock">LOCKED - PHARMACY TAB</span></div>
              <Grid rows={enc.discharge_meds} cols={[['drug', 'Drug'], ['dose', 'Dose'], ['frequency', 'Freq'], ['route', 'Route'], ['duration', 'Duration']]} />
              {field('follow_up_advice', 'Follow-up:', 3)}
              {field('diet_and_activity', 'Diet & activity:', 3)}
            </fieldset>
          </div>

          <div className="colside">
            <fieldset className={flash ? 'flashbox' : ''}>
              <legend>TPA Readiness Check</legend>
              <div style={{ marginBottom: 6 }}>
                <span className="kpi"><b>{score}%</b>{nOk} of {nApplicable} checks OK</span>
              </div>
              <table className="grid">
                <thead><tr><th>Check</th><th>Result</th></tr></thead>
                <tbody>
                  {checks?.checks.map((c) => (
                    <tr key={c.id} className={c.status === 'fail' ? 'hl' : ''}>
                      <td>{c.label}<div className="hint">{c.detail}</div></td>
                      <td className={`res-${RESULT[c.status][1]}`}>{RESULT[c.status][0]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="hint" style={{ marginTop: 4 }}>Rechecked automatically when documents are added in the Documents tab.</div>
            </fieldset>

            <fieldset>
              <legend>Source Verification</legend>
              <div style={{ marginBottom: 6 }}>
                <span className="kpi"><b className="res-OK">{t.verified}</b>Verified</span>
                <span className="kpi"><b className="res-WARN">{t.unverified}</b>Check</span>
                <span className="kpi"><b className="res-FAIL">{t.hallucinated}</b>Not in file</span>
              </div>
              {traceInfo?.flags.length ? (
                <table className="grid">
                  <thead><tr><th>Text in draft</th><th>Type</th><th>Result</th></tr></thead>
                  <tbody>
                    {traceInfo.flags.slice(0, 10).map((f, i) => (
                      <tr key={i}><td><b>{f.text}</b></td><td>{f.kind}</td>
                        <td className={f.status === 'hallucinated' ? 'res-FAIL' : 'res-WARN'}>{f.status === 'hallucinated' ? 'NOT IN FILE' : 'CHECK'}</td></tr>
                    ))}
                  </tbody>
                </table>
              ) : <div className="hint">Every medicine, test and number in the draft matches this patient's file.</div>}
            </fieldset>
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [hash, setHash] = useState(window.location.hash)
  useEffect(() => {
    const on = () => setHash(window.location.hash)
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  const m = hash.match(/^#\/embed\/review\/(.+)$/)
  if (m) return <DraftTab ip={decodeURIComponent(m[1])} key={m[1]} />
  return (
    <fieldset style={{ margin: 10 }}>
      <legend>Discharge Copilot service</legend>
      This service has no screens of its own. It appears inside MediTrack as the <b>AI Discharge Draft</b> tab of each patient file.
      <div className="hint">MediTrack System Admin &gt; External Links: URL http://localhost:8002/#/embed/review/{'{IP_NO}'}, Display = Patient file tab</div>
    </fieldset>
  )
}
