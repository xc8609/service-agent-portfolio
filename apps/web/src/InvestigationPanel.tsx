import {useEffect, useRef, useState} from 'react';

type Transaction = {id:string;version:string;merchant_description:string;amount_minor:number;currency:string;status:string};
type Revision = {revision:number;statement:string;recognition:string;transaction_versions:{id:string;version:string}[];recognized_transaction_id:string|null;recorded_at:string};
type History = {current_revision:number;saved_revision:number|null;history:Revision[]};
const modes:Record<string,string>={not_recorded:'Recognition not yet recorded',specific_entry:'Recognizes one specified entry',one_purchase_unresolved:'Recognizes one purchase; entry mapping unresolved',both:'Recognizes both entries',neither:'Does not recognize either entry'};

export function InvestigationPanel({auth,evidence,busy,onStatementChange,onSaving}:{auth:{token:string;contact:string};evidence:{records:Transaction[]}|null;busy:boolean;onStatementChange:()=>void;onSaving:(value:boolean)=>void}){
  const [statement,setStatement]=useState('');
  const [history,setHistory]=useState<History|null>(null);
  // A choice belongs to this inspected snapshot, never to a later render/effect.
  const [choice,setChoice]=useState<{evidence:typeof evidence;recognition:string;recognized:string}|null>(null);
  const currentChoice=choice?.evidence===evidence?choice:null;
  const recognition=currentChoice?.recognition??'not_recorded';
  const recognized=currentChoice?.recognized??'';
  const [error,setError]=useState('');
  const [notice,setNotice]=useState('');
  const [saving,setSaving]=useState(false);
  const [loading,setLoading]=useState(true);
  const pending=useRef<{fingerprint:string;key:string}|null>(null);
  const active=useRef(true);
  const pair=evidence?.records.length===2?evidence.records:null;
  async function call(name:string,payload:unknown):Promise<History>{
    const response=await fetch('/v1/workspace/'+name,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${auth.token}`},body:JSON.stringify(payload)});
    const data=await response.json();
    if(!response.ok)throw new Error(`${data.error?.code??'UNAVAILABLE'}: ${data.error?.safe_message??'Save unavailable. Keep your edits and retry or reload history.'}`);
    return data;
  }
  async function load(initial=false){
    setLoading(true);setError('');
    try{const data=await call('get_investigation',{contact_id:auth.contact});if(!active.current)return;setHistory(data);if(initial)setStatement(data.history.at(-1)?.statement??'');else setNotice('History reloaded. Your local statement was kept; inspect evidence again before saving.');}
    catch(e){if(active.current)setError((e as Error).message);}
    finally{if(active.current)setLoading(false);}
  }
  useEffect(()=>{active.current=true;void load(true);return()=>{active.current=false;};},[auth.token]);
  useEffect(()=>{setNotice('');},[evidence]);
  async function save(){
    if(!history)return;
    const input={contact_id:auth.contact,expected_revision:history.current_revision,statement,recognition,transaction_versions:recognition==='not_recorded'?[]:(pair??[]).map(({id,version})=>({id,version})),recognized_transaction_id:recognition==='specific_entry'?recognized:null};
    const fingerprint=JSON.stringify(input);
    if(pending.current?.fingerprint!==fingerprint)pending.current={fingerprint,key:crypto.randomUUID()};
    setSaving(true);onSaving(true);setError('');setNotice('');
    try{const data=await call('save_investigation',{...input,operation_key:pending.current.key});if(!active.current)return;setHistory(data);setNotice(`Saved customer report revision ${data.saved_revision}. This is not a specialist enquiry or a verified ledger conclusion.`);pending.current=null;}
    catch(e){if(active.current)setError((e as Error).message);}
    finally{if(active.current){setSaving(false);onSaving(false);}}
  }
  return <section aria-labelledby="statement-heading"><h2 id="statement-heading">4. Record the customer's account</h2>
    <p>Customer-reported information is separate from source facts. Record only synthetic details in this demo.</p>
    <label>Customer statement<textarea maxLength={2000} rows={4} value={statement} disabled={saving||loading} onChange={e=>{setStatement(e.target.value);setNotice('');onStatementChange();}}/></label>
    <p className="muted">Editing the statement invalidates earlier evidence and recognition. Reinspect the selected pair before recording recognition.</p>
    <label>Customer recognition<select value={recognition} disabled={!pair||saving||busy} onChange={e=>{setChoice({evidence,recognition:e.target.value,recognized:''});setNotice('');}}>{Object.entries(modes).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
    {!pair&&<p>Inspect exactly two entries to record their recognition scope. You can save the statement first.</p>}
    {recognition==='specific_entry'&&<label>Recognized entry<select value={recognized} disabled={saving||busy} onChange={e=>setChoice({evidence,recognition,recognized:e.target.value})}><option value="">Choose the entry identified by the customer</option>{pair?.map(r=><option key={r.id} value={r.id}>{r.merchant_description} · {r.currency} {(r.amount_minor/100).toFixed(2)} · {r.status} · {r.id}</option>)}</select></label>}
    {recognition==='one_purchase_unresolved'&&<p className="notice">Both entries will be recorded together. Which entry is additional remains unresolved; no disputed entry is inferred.</p>}
    {recognition==='neither'&&<p className="notice">Manual risk review: clarify the customer's denial and follow the approved risk-handling process with an authorized colleague. No fraud case, refund or transfer is created here.</p>}
    <div className="controls"><button onClick={save} disabled={!history||loading||saving||busy||!statement.trim()||(recognition!=='not_recorded'&&!pair)||(recognition==='specific_entry'&&!recognized)}>{saving?'Saving customer report…':'Save customer report'}</button><button onClick={()=>{onStatementChange();void load();}} disabled={saving||loading||busy}>Reload saved history</button></div>
    {error&&<p role="alert" className="error">{error} Your local statement has been kept. If the outcome is uncertain, retry unchanged input or reload history before editing.</p>}
    {notice&&<p className="success" aria-live="polite">{notice}</p>}
    <details><summary>Saved customer report history ({history?.history.length??0})</summary><p>Historical snapshots only; they are not current evidence. Later revisions supersede earlier reports. Fresh investigation is required for any future referral.</p>{history?.history.map(r=><article key={r.revision}><h3>Revision {r.revision}{r.revision<history.current_revision?' · Superseded':''}</h3><p>{r.statement}</p><p>{modes[r.recognition]}</p><small>{r.recorded_at} · {r.transaction_versions.map(t=>`${t.id} v${t.version}`).join(' · ')||'No pair recorded'}{r.recognized_transaction_id?` · Recognized: ${r.recognized_transaction_id}`:''}</small></article>)}</details>
  </section>;
}
