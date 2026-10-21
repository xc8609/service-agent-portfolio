import React, {useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
import {InvestigationPanel} from './InvestigationPanel';
import {RelatedCases} from './RelatedCases';
import {HandlingRules} from './HandlingRules';
import {NotePanel} from './NotePanel';
import {ReferralPanel} from './ReferralPanel';
import {OperationsDesk} from './OperationsDesk';

type RecordRow={id:string;version:string;amount_minor:number;currency:string;merchant_description:string;status:string;occurred_at:string;posted_at:string|null};
type Meta={as_of:string;scope_ref:string;sources:{kind:string;id:string;version:string;section:string|null}[]};
type Context={masked_card_refs:string[];verification:string;allowed_actions:string[]};
type Evidence={records:RecordRow[];relationships:{left_id:string;right_id:string;relation:string;evidence_ref:{section:string}}[];related_case_ids:string[];missing_evidence:string[]};
const formatMoney=(r:RecordRow)=>new Intl.NumberFormat('en-CA',{style:'currency',currency:r.currency}).format(r.amount_minor/100);

function App(){
  const [persona,setPersona]=useState('verified');
  const [auth,setAuth]=useState<{token:string;contact:string}|null>(null);
  const [context,setContext]=useState<Context|null>(null);
  const [schema,setSchema]=useState('Not checked');
  const [card,setCard]=useState('');
  const [from,setFrom]=useState('2026-10-01'),[to,setTo]=useState('2026-10-31');
  const [merchant,setMerchant]=useState(''),[amount,setAmount]=useState('');
  const [rows,setRows]=useState<RecordRow[]>([]),[selection,setSelection]=useState<string[]>([]);
  const [evidence,setEvidence]=useState<Evidence|null>(null),[meta,setMeta]=useState<Meta|null>(null);
  const [searched,setSearched]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const revision=useRef(0);
  const [saving,setSaving]=useState(false),[stale,setStale]=useState('');
  function invalidateQuery(){revision.current++;clear();setBusy(false);setStale('Query changed. Previous results, selection and evidence are invalid. Search again.');}
  function invalidateStatement(){revision.current++;setBusy(false);setEvidence(null);setMeta(null);setStale('Customer statement changed or history reloaded. Previous evidence is invalid; inspect the selection again.');}
  async function request(path:string,body?:unknown,token?:string){
    const r=await fetch(path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})});
    const data=await r.json();
    if(!r.ok)throw new Error(`${data.error?.code??'UNAVAILABLE'}: ${data.error?.safe_message??'Service unavailable; use the manual support route.'}${data.request_id?' Reference '+data.request_id:''}`);
    return data;
  }
  function clear(){setRows([]);setSelection([]);setEvidence(null);setMeta(null);setSearched(false);setError('');setStale('');}
  function changePersona(value:string){revision.current++;setPersona(value);setAuth(null);setContext(null);setCard('');setBusy(false);setSaving(false);clear();}
  async function start(){
    const rev=++revision.current;clear();setAuth(null);setContext(null);setCard('');setBusy(true);
    try{
      const ready=await request('/health/ready');if(rev!==revision.current)return;setSchema(ready.schema_version);
      const session=await request('/v1/demo/session',{persona});if(rev!==revision.current)return;
      const response=await request('/v1/agent-tools/get_contact_context',{contact_id:session.contact_id},session.access_token);if(rev!==revision.current)return;
      setAuth({token:session.access_token,contact:session.contact_id});setContext(response.data);setCard(response.data.masked_card_refs[0]);
    }catch(e){if(rev===revision.current)setError(e instanceof Error?e.message:'Service unavailable.');}
    finally{if(rev===revision.current)setBusy(false);}
  }
  async function search(event:React.FormEvent){
    event.preventDefault();if(!auth)return;clear();setBusy(true);const rev=++revision.current;
    try{
      const response=await request('/v1/agent-tools/search_transactions',{contact_id:auth.contact,card_ref:card,date_from:from,date_to:to,amount_minor:amount===''?null:Number(amount),merchant_query:merchant||null,cursor:null,limit:50},auth.token);
      if(rev!==revision.current)return;setRows(response.data.records);setMeta(response.meta);setSearched(true);
      if(response.data.next_cursor)setError('More than 50 matches. Narrow the date, amount or merchant filter.');
    }catch(e){if(rev===revision.current){setError(e instanceof Error?e.message:'Service unavailable.');setContext(null);setAuth(null);}}
    finally{if(rev===revision.current)setBusy(false);}
  }
  async function inspect(){
    if(!auth)return;setEvidence(null);setMeta(null);setStale('');setError('');setBusy(true);const rev=++revision.current;
    try{
      const response=await request('/v1/agent-tools/get_transaction_evidence',{contact_id:auth.contact,transaction_ids:selection},auth.token);
      if(rev!==revision.current)return;setEvidence(response.data);setMeta(response.meta);
    }catch(e){if(rev===revision.current){setRows([]);setSelection([]);setEvidence(null);setMeta(null);setAuth(null);setContext(null);setError(e instanceof Error?e.message:'Service unavailable.');}}
    finally{if(rev===revision.current)setBusy(false);}
  }
  return <div className="layout">
    <aside><div className="brand">SERVICE / LAB</div><h2>Bank workspace</h2><p className="muted">Credit-card enquiries</p><nav><strong>01 · Transaction investigation</strong><span>02 · Policy evidence</span><span>03 · Specialist referral — planned</span></nav><div className="demo"><b>Synthetic demo only</b><p>No bank connection, real customers or financial operations.</p><p>Agent: disabled<br/>Manual lookup: available</p></div></aside>
    <main><header><div><p className="eyebrow">INBOUND SERVICE · B0 MANUAL BASELINE</p><h1>Understand the charge.</h1><p>Gather permitted facts, inspect source evidence, and keep uncertainty visible.</p></div><span className="badge">MANUAL INVESTIGATION</span></header>
      <section aria-labelledby="session-heading"><div className="section-head"><h2 id="session-heading">1. Establish an authorized contact</h2><span>Schema: {schema}</span></div><p>Local simulation of trusted identity input. This selector is not a production sign-in.</p><div className="controls"><label>Demo scenario<select value={persona} disabled={saving} onChange={e=>changePersona(e.target.value)}><option value="verified">Verified inbound representative</option><option value="unverified">Customer not verified — deny</option><option value="expired">Customer proof expired — deny</option><option value="feedback_unclaimed">Feedback representative, unclaimed — deny</option><option value="agent">Agent without delegation — deny</option><option value="other_customer">Other customer's authorized contact</option></select></label><button onClick={start} disabled={busy||saving}>Start demo contact</button></div>{context&&<p className="success" role="status">Verified contact · {context.masked_card_refs.join(', ')} · Authorized transaction read · Customer report capture</p>}</section>
      {error&&<div role="alert" className="error">{error}</div>}
      <section aria-labelledby="search-heading"><h2 id="search-heading">2. Find candidate transactions</h2><form onSubmit={search}><fieldset disabled={!auth||saving}><div className="filters"><label>Authorized card<select value={card} onChange={e=>{setCard(e.target.value);invalidateQuery();}}>{context?.masked_card_refs.map(c=><option key={c}>{c}</option>)}</select></label><label>From (UTC date)<input type="date" value={from} onChange={e=>{setFrom(e.target.value);invalidateQuery();}} required/></label><label>To (UTC date)<input type="date" value={to} onChange={e=>{setTo(e.target.value);invalidateQuery();}} required/></label><label>Amount (cents, optional)<input type="number" step="1" value={amount} onChange={e=>{setAmount(e.target.value);invalidateQuery();}}/></label><label>Merchant (optional)<input maxLength={120} value={merchant} onChange={e=>{setMerchant(e.target.value);invalidateQuery();}} placeholder="e.g. DEMO STORE"/></label></div><button type="submit" disabled={busy}>Search transactions</button></fieldset></form>
      {searched&&rows.length===0&&<p>No matching transactions in the authorized scope.</p>}
      {rows.length>0&&<><p>{rows.length} candidates. Select up to 10 entries to inspect; matching amounts do not establish a duplicate.</p><div className="table-wrap"><table><thead><tr><th>Select</th><th>Merchant / source reference</th><th>Amount</th><th>Status</th><th>Occurred (UTC)</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td><input type="checkbox" aria-label={`Select ${r.id}`} checked={selection.includes(r.id)} disabled={busy||saving||(!selection.includes(r.id)&&selection.length>=10)} onChange={e=>{revision.current++;setEvidence(null);setMeta(null);setStale('Selection changed. Inspect again before recording recognition.');setSelection(e.target.checked?[...selection,r.id]:selection.filter(id=>id!==r.id));}}/></td><td>{r.merchant_description}<small>{r.id} · v{r.version}</small></td><td>{formatMoney(r)}</td><td><span className={`status ${r.status}`}>{r.status}</span></td><td>{r.occurred_at.slice(0,10)}</td></tr>)}</tbody></table></div><button onClick={inspect} disabled={busy||saving||selection.length===0}>Inspect selected evidence ({selection.length})</button></>}
      </section>
      {stale&&<p className="notice" aria-live="polite">{stale}</p>}
      <section aria-labelledby="evidence-heading"><h2 id="evidence-heading">3. Review evidence and gaps</h2>{!evidence?<p className="muted">Select transactions above. No explanation or financial action is generated automatically.</p>:<><p><b>Selected source statuses:</b> {evidence.records.map(r=>r.status).join(' · ')}</p>{evidence.relationships.length?<ul>{evidence.relationships.map((r,i)=><li key={i}>{r.relation}<small>Evidence: {r.evidence_ref.section}</small></li>)}</ul>:<p>No source relationship recorded.</p>}{evidence.missing_evidence.map(g=><p className="notice" key={g}>{g}</p>)}<p>Related case references: {evidence.related_case_ids.join(', ')||'None returned for these entries.'}</p><p className="muted">This screen does not determine whether a charge is a duplicate or authorize a refund.</p></>}
      {meta&&<details><summary>Source provenance · {meta.as_of}</summary><ul>{meta.sources.map((s,i)=><li key={i}>{s.kind} · {s.id} · version {s.version}{s.section?' · '+s.section:''}</li>)}</ul></details>}</section>
      {auth&&evidence&&<RelatedCases key={`cases:${meta?.as_of}`} auth={auth} transactionIds={evidence.records.map(r=>r.id)}/>}
      {auth&&<InvestigationPanel key={auth.token} auth={auth} evidence={evidence} busy={busy} onStatementChange={invalidateStatement} onSaving={setSaving}/>}
      {auth&&evidence&&<HandlingRules key={`rules:${meta?.as_of}`} auth={auth} records={evidence.records}/>}
      {auth&&<NotePanel key={`note:${auth.token}`} auth={auth} records={evidence?.records??null} contextKey={`${meta?.as_of}:${stale}`}/>}
      {auth&&<ReferralPanel key={`referral:${auth.token}`} auth={auth} records={evidence?.records??null} contextKey={`${meta?.as_of}:${stale}`}/>}
      <footer aria-live="polite">{busy?'Retrieving authorized evidence…':'Local synthetic workflow. No measured savings or production readiness claimed.'}</footer>
      <OperationsDesk/>
    </main></div>;
}
createRoot(document.getElementById('root')!).render(<App/>);
