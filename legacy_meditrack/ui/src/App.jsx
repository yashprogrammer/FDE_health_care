import { useCallback, useEffect, useRef, useState } from 'react'

const api = async (path, opts) => {
  const r = await fetch(path, opts)
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `ERROR ${r.status}`)
  return r.json()
}
const post = (path, body) =>
  api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })

function useHash() {
  const [hash, setHash] = useState(window.location.hash || '#/census')
  useEffect(() => {
    const on = () => setHash(window.location.hash || '#/census')
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return hash
}

function useLoad(fn, deps) {
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)
  const reload = useCallback(() => {
    fn().then(setData).catch((e) => setErr(e.message))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  useEffect(reload, [reload])
  return [data, err, reload]
}

const Sts = ({ s }) => <span className={`sts ${s}`}>{{ ADM: 'ADMITTED', DA: 'DISCH. ADVISED', DSCH: 'DISCHARGED' }[s] || s}</span>

// ------------------------------------------------------------------ Census
function Census() {
  const [data, err] = useLoad(() => api('/int/census'), [])
  return (
    <fieldset>
      <legend>IPD Census - Current In-Patients</legend>
      {err && <div className="err">{err}</div>}
      <table className="grid compact">
        <thead>
          <tr><th>IP No</th><th>UHID</th><th>Patient Name</th><th>Age/Sex</th><th>Ward</th><th>Bed</th><th>Consultant</th><th>Pay Mode</th><th>TPA</th><th>Adm. Date</th><th>Status</th></tr>
        </thead>
        <tbody>
          {data?.map((r) => (
            <tr key={r.IP_NO}>
              <td><a href={`#/ip/${r.IP_NO}`}>{r.IP_NO}</a></td>
              <td>{r.UHID}</td><td className="wrap">{r.PT_NM.toUpperCase()}</td><td>{r.PT_AGE}/{r.PT_SEX}</td>
              <td>{r.WRD_CD}</td><td>{r.BED_NO}</td><td className="wrap">{r.DR_NM}</td><td>{r.PAY_MODE}</td><td className="wrap">{r.TPA_NM || '-'}</td>
              <td>{r.ADM_DT}</td><td><Sts s={r.STS} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="hint">Total in-patients: {data?.length ?? '...'}. Click IP No to open patient file.</p>
    </fieldset>
  )
}

// ------------------------------------------------------------------ Discharged
function Discharged() {
  const [data] = useLoad(() => api('/int/discharged'), [])
  return (
    <fieldset>
      <legend>Discharged Patients (last 60)</legend>
      <table className="grid compact">
        <thead><tr><th>IP No</th><th>UHID</th><th>Patient</th><th>Ward</th><th>Consultant</th><th>Pay Mode</th><th>Disch. Advised</th><th>Discharged</th><th>DS on file</th></tr></thead>
        <tbody>
          {data?.map((r) => (
            <tr key={r.IP_NO}>
              <td><a href={`#/ip/${r.IP_NO}`}>{r.IP_NO}</a></td><td>{r.UHID}</td><td className="wrap">{r.PT_NM.toUpperCase()}</td><td>{r.WRD_CD}</td>
              <td className="wrap">{r.DR_NM}</td><td>{r.PAY_MODE}</td><td>{r.DSCH_ADV_DT}</td><td>{r.DSCH_DT}</td><td>{r.HAS_SUMM ? 'Y' : 'N'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </fieldset>
  )
}

// ------------------------------------------------------------------ Patient file
const TABS = ['Diagnosis', 'Procedures', 'Lab Results', 'Pharmacy', 'Clinical Notes', 'Documents', 'Discharge Summary', 'TPA']

function Patient({ ip }) {
  const [d, err, reload] = useLoad(() => api(`/int/ip/${ip}`), [ip])
  const [tab, setTab] = useState('Diagnosis')
  const [msg, setMsg] = useState('')

  const act = async (path, confirmMsg) => {
    if (!window.confirm(confirmMsg)) return
    try { await post(path); setMsg('Saved successfully.'); reload() } catch (e) { setMsg(e.message) }
  }

  if (err) return <div className="err">{err}</div>
  if (!d) return <div>Loading patient file...</div>
  const a = d.adm
  const linkItems = d.links.filter((l) => l.DISP_MD !== 'TAB')
  const customTabs = d.links.filter((l) => l.DISP_MD === 'TAB')
  const openTab = (t) => { setTab(t); reload() }   // every tab click is a fresh server round-trip, like 2011
  const custom = customTabs.find((l) => l.LNK_LBL === tab)
  return (
    <>
      <fieldset>
        <legend>Patient File - {a.IP_NO}</legend>
        <div className="pt-strip">
          <span><b>Name:</b> {a.PT_NM.toUpperCase()}</span><span><b>UHID:</b> {a.UHID}</span>
          <span><b>Age/Sex:</b> {a.PT_AGE}/{a.PT_SEX}</span><span><b>Mobile:</b> {a.PT_MOB}</span>
          <span><b>Adm. Date:</b> {a.ADM_DT}</span><span><b>Ward/Bed:</b> {a.WRD_CD} / {a.BED_NO}</span>
          <span><b>Consultant:</b> {a.DR_NM}</span><span><b>Status:</b> <Sts s={a.STS} /></span>
          <span><b>Pay Mode:</b> {a.PAY_MODE}</span><span><b>TPA:</b> {a.TPA_NM || '-'}</span>
          <span><b>Policy No:</b> {a.POL_NO || '-'}</span><span><b>Disch. Advised:</b> {a.DSCH_ADV_DT || '-'}</span>
        </div>
        <div><b>Reason for admission:</b> {a.ADM_RSN}</div>
        <div style={{ marginTop: 10, display: 'flex', gap: 8, alignItems: 'center' }}>
          <button className="primary" disabled={a.STS !== 'ADM'} onClick={() => act(`/int/ip/${ip}/discharge-advise`, 'Mark patient as DISCHARGE ADVISED?')}>Discharge Advised</button>
          <button disabled={a.STS !== 'DA'} onClick={() => act(`/int/ip/${ip}/discharge`, 'Confirm FINAL DISCHARGE (bill settled)?')}>Final Discharge</button>
          <a className="btn" href={`/int/ip/${ip}/summary-template`}>Download DS Template (.doc)</a>
          <button onClick={() => window.print()}>Print</button>
          {msg && <span className="err">{msg}</span>}
        </div>
        {linkItems.length > 0 && (
          <div className="links">
            <b>External Links:</b>{' '}
            {linkItems.map((l) => <a key={l.LNK_ID} href={l.HREF} target="_blank" rel="noreferrer" style={{ marginRight: 14 }}>{l.LNK_LBL} &#8599;</a>)}
          </div>
        )}
      </fieldset>

      <div className="tabs">
        {TABS.map((t) => <button key={t} className={t === tab ? 'cur' : ''} onClick={() => openTab(t)}>{t}</button>)}
        {customTabs.map((l) => <button key={l.LNK_ID} className={l.LNK_LBL === tab ? 'cur' : ''} onClick={() => openTab(l.LNK_LBL)}>{l.LNK_LBL}</button>)}
      </div>
      <div className="tabbody">
        {tab === 'Diagnosis' && <Grid rows={d.diags} cols={[['DIAG_TYP', 'Type'], ['ICD_CD', 'ICD-10'], ['DIAG_DESC', 'Description']]} />}
        {tab === 'Procedures' && <Grid rows={d.procs} cols={[['PROC_DT', 'Date'], ['PROC_CD', 'CPT'], ['PROC_DESC', 'Procedure'], ['SURGEON', 'Surgeon']]} />}
        {tab === 'Lab Results' && <Labs labs={d.labs} />}
        {tab === 'Pharmacy' && <Grid rows={d.meds} cols={[['ISS_TYP', 'Issue Type'], ['DRUG_NM', 'Drug'], ['DOSE', 'Dose'], ['FREQ', 'Freq'], ['ROUTE', 'Route'], ['DUR', 'Duration']]} />}
        {tab === 'Clinical Notes' && <Grid rows={d.notes} cols={[['NOTE_DT', 'Date/Time'], ['NOTE_TYP', 'Type'], ['AUTH', 'Author'], ['NOTE_TXT', 'Note']]} />}
        {tab === 'Documents' && <Documents ip={ip} docs={d.docs} reload={reload} />}
        {tab === 'Discharge Summary' && <SummaryTab ip={ip} summary={d.summary} reload={reload} />}
        {custom && <EmbeddedTab key={custom.LNK_ID} title={custom.LNK_LBL} src={custom.HREF} />}
        {tab === 'TPA' && <Grid rows={d.claims} cols={[['SUBM_DT', 'Submitted'], ['CLM_STS', 'Status'], ['QRY_RSN', 'Query Reason'], ['APPR_DT', 'Approved']]} />}
      </div>
    </>
  )
}

// Configured "Patient file tab" links render the page inside the tab body.
// The embedded page may report its height (postMessage 'meditrack:tab-height') so the tab grows to fit.
function EmbeddedTab({ title, src }) {
  const ref = useRef(null)
  const [height, setHeight] = useState(600)
  useEffect(() => {
    const on = (e) => {
      if (e.source === ref.current?.contentWindow && e.data?.type === 'meditrack:tab-height') setHeight(Math.max(300, e.data.height + 4))
    }
    window.addEventListener('message', on)
    return () => window.removeEventListener('message', on)
  }, [])
  return <iframe ref={ref} title={title} src={src} style={{ width: '100%', height, border: 0, display: 'block' }} />
}

function Grid({ rows, cols }) {
  if (!rows?.length) return <div className="hint">No records found.</div>
  return (
    <table className="grid">
      <thead><tr>{cols.map(([, h]) => <th key={h}>{h}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i}>{cols.map(([k]) => <td key={k}>{r[k] ?? ''}</td>)}</tr>)}</tbody>
    </table>
  )
}

function Labs({ labs }) {
  if (!labs.length) return <div className="hint">No records found.</div>
  return (
    <table className="grid">
      <thead><tr><th>Date</th><th>Test</th><th>Result</th><th>Unit</th><th>Ref. Range</th><th>Status</th></tr></thead>
      <tbody>
        {labs.map((l) => (
          <tr key={l.ID}>
            <td>{l.RSLT_DT}</td><td>{l.TST_NM}</td>
            <td className={l.FLG ? `flag-${l.FLG}` : ''}>{l.RSLT_VAL} {l.FLG && `(${l.FLG})`}</td>
            <td>{l.UOM}</td><td>{l.REF_RNG}</td>
            <td className={l.STS === 'PENDING' ? 'pending' : ''}>{l.STS}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

const DOC_TYPES = ['IMPLANT_STKR', 'CATH_RPT', 'OT_NOTE', 'CONSENT', 'LAB_RPT', 'ID_PROOF', 'OTHER']

function Documents({ ip, docs, reload }) {
  const [typ, setTyp] = useState(DOC_TYPES[0])
  const [file, setFile] = useState(null)
  const [msg, setMsg] = useState('')
  const upload = async () => {
    if (!file) return setMsg('SELECT FILE FIRST')
    const fd = new FormData()
    fd.append('doc_typ', typ)
    fd.append('file', file)
    try { await api(`/int/ip/${ip}/docs`, { method: 'POST', body: fd }); setMsg('Uploaded.'); reload() } catch (e) { setMsg(e.message) }
  }
  return (
    <>
      <table className="grid">
        <thead><tr><th>Doc ID</th><th>Type</th><th>File</th><th>Uploaded</th><th>By</th></tr></thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.DOC_ID} className={d.UPL_BY === 'BATCH_IMPORT' ? 'hl' : ''}>
              <td>{d.DOC_ID}</td><td>{d.DOC_TYP}</td>
              <td><a href={`/int/docs/${d.DOC_ID}`} target="_blank" rel="noreferrer">{d.FILE_NM}</a></td>
              <td>{d.UPL_DT}</td><td>{d.UPL_BY}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <fieldset style={{ marginTop: 8 }}>
        <legend>Upload Document</legend>
        <div className="formrow">
          Type: <select value={typ} onChange={(e) => setTyp(e.target.value)}>{DOC_TYPES.map((t) => <option key={t}>{t}</option>)}</select>
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
          <button className="primary" onClick={upload}>Upload</button> <span className="err">{msg}</span>
        </div>
      </fieldset>
    </>
  )
}

function SummaryTab({ ip, summary, reload }) {
  const [text, setText] = useState('')
  const save = async () => { await post(`/int/ip/${ip}/manual-summary`, { text }); reload() }
  if (summary) {
    return (
      <>
        <div className="hint">Typed by {summary.CRT_BY} on {summary.CRT_DT}</div>
        <pre className="summ">{summary.SUMM_TXT}</pre>
      </>
    )
  }
  return (
    <>
      <div className="hint">
        No discharge summary on file. Download the DS template (Form MRD/DS/07), then copy details from the
        Diagnosis, Procedures, Lab Results, Pharmacy and Clinical Notes screens.
      </div>
      <textarea rows={16} value={text} onChange={(e) => setText(e.target.value)}
        placeholder={'Diagnosis:\nPresenting complaints:\nHospital course:\nProcedures:\nInvestigations:\nCondition at discharge:\nDischarge medications:\nFollow-up:'} />
      <div style={{ marginTop: 8 }}><button className="primary" onClick={save} disabled={!text.trim()}>Save Summary</button></div>
    </>
  )
}

// ------------------------------------------------------------------ Admin: external links
function ExtLinks() {
  const [data, , reload] = useLoad(() => api('/int/admin/extlinks'), [])
  const [label, setLabel] = useState('')
  const [url, setUrl] = useState('')
  const [mode, setMode] = useState('LINK')
  const add = async () => { await post('/int/admin/extlinks', { label, url, mode }); setLabel(''); setUrl(''); setMode('LINK'); reload() }
  const toggle = async (id) => { await post(`/int/admin/extlinks/${id}/toggle`); reload() }
  return (
    <fieldset>
      <legend>System Admin - External Links (Patient File)</legend>
      <p className="hint">Links configured here appear on every patient file, either as a link or as an extra tab. Placeholders: {'{IP_NO}'}, {'{UHID}'}</p>
      <table className="grid">
        <thead><tr><th>ID</th><th>Label</th><th>URL</th><th>Display</th><th>Active</th><th>Created By</th><th>Created</th><th></th></tr></thead>
        <tbody>
          {data?.map((l) => (
            <tr key={l.LNK_ID}>
              <td>{l.LNK_ID}</td><td>{l.LNK_LBL}</td><td>{l.LNK_URL}</td><td>{l.DISP_MD === 'TAB' ? 'Patient file tab' : 'New window'}</td><td>{l.IS_ACTV ? 'Y' : 'N'}</td>
              <td>{l.CRT_BY}</td><td>{l.CRT_DT}</td><td><button onClick={() => toggle(l.LNK_ID)}>{l.IS_ACTV ? 'Disable' : 'Enable'}</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      <fieldset style={{ marginTop: 8 }}>
        <legend>Add New Link</legend>
        <div className="formrow">
          Label: <input type="text" size={22} value={label} onChange={(e) => setLabel(e.target.value)} />
          URL: <input type="text" size={48} value={url} onChange={(e) => setUrl(e.target.value)} />
          Display: <select value={mode} onChange={(e) => setMode(e.target.value)}><option value="LINK">New window</option><option value="TAB">Patient file tab</option></select>
          <button className="primary" disabled={!label || !url} onClick={add}>Add</button>
        </div>
      </fieldset>
    </fieldset>
  )
}

// ------------------------------------------------------------------ MIS
function Mis() {
  const [d] = useLoad(() => api('/int/mis/discharge-tat'), [])
  if (!d) return <div>Generating report...</div>
  return (
    <fieldset>
      <legend>MIS Report - Discharge Turnaround (Discharge Advised to Patient Out)</legend>
      <div style={{ margin: '2px 0 4px' }}>
        {d.by_mode.map((m) => <span className="kpi" key={m.PAY_MODE}><b>{m.AVG_TAT_HRS} hrs</b>{m.PAY_MODE} ({m.N} pts)</span>)}
        <span className="kpi"><b>{d.claims.QUERY_PCT}%</b>TPA claims with query ({d.claims.QUERIES}/{d.claims.N})</span>
      </div>
      <Grid rows={d.reasons} cols={[['QRY_RSN', 'TPA Query Reason'], ['N', 'Count']]} />
    </fieldset>
  )
}

function Audit() {
  const [data] = useLoad(() => api('/int/audit'), [])
  return <fieldset><legend>Audit Trail (last 50)</legend><Grid rows={data} cols={[['TS', 'Time'], ['USR', 'User'], ['ACTN', 'Action'], ['REF', 'Ref']]} /></fieldset>
}

// ------------------------------------------------------------------ Shell
export default function App() {
  const hash = useHash()
  const ipMatch = hash.match(/^#\/ip\/(.+)$/)
  const nav = [
    ['In-Patient (IPD)', [['#/census', 'IPD Census'], ['#/discharged', 'Discharged Patients']]],
    ['Reports', [['#/mis', 'MIS: Discharge TAT']]],
    ['System Admin', [['#/admin/links', 'External Links'], ['#/audit', 'Audit Trail']]],
  ]
  return (
    <>
      <div className="banner">
        <span className="logo">MediTrack HMS<small>v3.2.4 &middot; CityCare Hospitals, Pune</small></span>
        <span className="user">rmo.karan &middot; Ward: ALL &middot; {new Date().toLocaleDateString('en-GB')} &middot; <a href="#/census">Logout</a></span>
      </div>
      <div className="ticker">&#9888; Scheduled server maintenance: Sunday 02:00-04:00 AM. Please save your work. &middot; Lab results interface (HL7) delayed by 15 min on weekends. &middot; Contact IT ext. 2204 (Suresh) for password reset.</div>
      <div className="layout">
        <div className="nav">
          {nav.map(([g, items]) => (
            <div key={g}>
              <div className="grp">{g}</div>
              {items.map(([h, l]) => <a key={h} href={h} className={hash === h ? 'cur' : ''}>{l}</a>)}
            </div>
          ))}
        </div>
        <div className="main">
          {ipMatch ? <Patient ip={ipMatch[1]} key={ipMatch[1]} />
            : hash === '#/discharged' ? <Discharged />
            : hash === '#/admin/links' ? <ExtLinks />
            : hash === '#/mis' ? <Mis />
            : hash === '#/audit' ? <Audit />
            : <Census />}
        </div>
      </div>
      <div className="footer">&copy; 2011-2018 Medisoft Solutions Pvt. Ltd. &middot; MediTrack HMS v3.2.4 (Clarity UI) &middot; Best viewed in Google Chrome at 1366x768.</div>
    </>
  )
}
