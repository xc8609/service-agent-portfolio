import {useEffect, useRef, useState} from 'react';

type Work={id:string;version:string;kind:string;status:string;queue_name:string;queue_active:boolean;assignee_name:string|null;assignee_active:boolean|null;original_due_at:string|null;due_at:string|null};
type Snapshot={case_id:string;case_version:string;case_status:string;investigation_status:string;feedback_status:string;approved_customer_explanation:string|null;unresolved_items:string[];timeline:{event_id:string;sequence:number;occurred_at:string;recorded_at:string;customer_safe_summary:string;source_ref:{section:string}}[];progress_commitments:{id:string;status:string;approved_update_at:string|null;customer_safe_progress:string}[]};
type Case={reference:string;concern:string;status_as_of:string;owner_queue_name:string;owner_queue_active:boolean;coverage:string;review_hint:string;matched_transaction_ids:string[];work_items:Work[];snapshot:Snapshot};
type Response={cases:Case[];as_of:string;review_state:string};
const time=(value:string|null)=>value?new Date(value).toISOString().replace('T',' ').replace('.000Z',' UTC'):'Not recorded';
const label=(value:string)=>value.replaceAll('_',' ');
const hints:Record<string,string>={potential_existing_enquiry:'Potential existing enquiry: this active duplicate-charge case covers the selection. Review and continue existing work before considering another submission.',review_closed_case:'Closed related case: review its outcome and the current concern. Never reopen automatically or infer a refund; if the customer disputes the outcome, record the disagreement for independent re-review.',review_overlap_and_concern:'Related work needs review: transaction overlap alone does not establish the same concern. Do not automatically reuse or reject a new enquiry.'};

function Disagreement({auth,caseId,version,onSaved}:{auth:{token:string;contact:string};caseId:string;version:string;onSaved:()=>void}){
  const [statement,setStatement]=useState(''),[complaint,setComplaint]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
  const pending=useRef<{key:string;body:string}|null>(null);
  async function submit(){
    setBusy(true);setMessage('');
    // Keep one operation key until the server answers, so a lost reply is retried safely.
    pending.current??={key:crypto.randomUUID(),body:statement};
    try{
      const r=await fetch('/v1/commands/capture_customer_objection',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${auth.token}`},body:JSON.stringify({case_id:caseId,contact_id:auth.contact,expected_case_version:Number(version),customer_statement:pending.current.body,evidence_refs:[],complaint_requested:complaint,operation_key:pending.current.key})});
      const d=await r.json();
      if(!r.ok){if(r.status<500)pending.current=null;throw new Error(`${d.error?.code}: ${d.error?.safe_message}`);}
      pending.current=null;setStatement('');setMessage(`Disagreement recorded for independent re-review · receipt ${d.data.operation_key}. No outcome or refund has changed.`);onSaved();
    }catch(e){setMessage(e instanceof Error?e.message:'Unavailable. Retry keeps the same operation.');}
    finally{setBusy(false);}
  }
  return <fieldset disabled={busy}><legend>Customer disputes this outcome</legend><label>Customer statement (verbatim)<textarea value={statement} maxLength={4000} onChange={e=>{setStatement(e.target.value);pending.current=null;}}/></label><label><input type="checkbox" checked={complaint} onChange={e=>setComplaint(e.target.checked)}/> Customer explicitly requests a complaint</label><button onClick={submit} disabled={!statement.trim()}>Record disagreement for re-review</button>{message&&<p aria-live="polite">{message}</p>}</fieldset>;
}

export function RelatedCases({auth,transactionIds}:{auth:{token:string;contact:string};transactionIds:string[]}){
  const [data,setData]=useState<Response|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(false),[lastSuccess,setLastSuccess]=useState<string|null>(null);
  const revision=useRef(0);
  async function refresh(){
    const current=++revision.current;setLoading(true);setData(null);setError('');
    try{
      const response=await fetch('/v1/workspace/get_related_cases',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${auth.token}`},body:JSON.stringify({contact_id:auth.contact,transaction_ids:transactionIds})});
      const value=await response.json();if(current!==revision.current)return;
      if(!response.ok)throw new Error(`${value.error?.code??'UNAVAILABLE'}: ${value.error?.safe_message??'Case lookup unavailable.'}${value.request_id?' Reference '+value.request_id:''}`);
      setData(value);setLastSuccess(value.as_of);
    }catch(e){if(current===revision.current)setError(e instanceof Error?e.message:'Case lookup unavailable.');}
    finally{if(current===revision.current)setLoading(false);}
  }
  useEffect(()=>{void refresh();return()=>{revision.current++;};},[auth.token,transactionIds.join(',')]);
  return <section aria-labelledby="cases-heading"><div className="section-head"><h2 id="cases-heading">Related cases · Review before a new enquiry</h2><button onClick={refresh} disabled={loading}>Refresh related cases</button></div>
    <p>Querying or saving a customer report does not submit a new case. No referral submission is available in this increment.</p>
    {loading&&<p aria-live="polite">Checking existing work… Previous details are not current until refresh succeeds.</p>}
    {error&&<div role="alert" className="error"><p>{error}</p><p>Duplicate check incomplete. Use manual case review; do not treat this as no existing case.</p>{lastSuccess&&<p>Last successful lookup (stale): {time(lastSuccess)}. Details cleared.</p>}</div>}
    {data&&<><p className="muted">Case lookup as of {time(data.as_of)}</p>{data.cases.length===0?<p>No linked case found for the selected transactions. This is not an authorization to submit; recheck at referral time.</p>:<p className="notice">Existing related work found. Confirm the concern and coverage before opening another enquiry.</p>}
      {data.cases.map(c=><article key={c.snapshot.case_id} aria-label={`Case ${c.reference}`}>
        <h3>{c.reference} · {label(c.snapshot.case_status)}</h3><p>{c.concern}</p><p className="notice">{hints[c.review_hint]}</p>
        <p>Selection coverage: {label(c.coverage)} · {c.matched_transaction_ids.length} selected entries linked.</p>
        <p>Accountable queue: <b>{c.owner_queue_name}</b>{!c.owner_queue_active?' (inactive — manual reassignment review needed)':''}</p>
        <p>Status recorded: {time(c.status_as_of)} · Case version {c.snapshot.case_version}</p>
        <p>Investigation: {label(c.snapshot.investigation_status)} · Customer feedback: {label(c.snapshot.feedback_status)}</p>
        <h4>Work ownership and progress</h4>{c.work_items.length===0?<p>No work ownership recorded. Request manual review.</p>:<ul>{c.work_items.map(w=><li key={w.id}><b>{label(w.kind)} · {label(w.status)}</b><p>Responsible: {w.assignee_name??'Unassigned'}{w.assignee_active===false?' (inactive)':''} · Queue: {w.queue_name}{!w.queue_active?' (inactive)':''}</p><p>Original due: {time(w.original_due_at)} · Current due: {time(w.due_at)}</p><small>Work {w.id} · version {w.version}</small></li>)}</ul>}
        <h4>Outstanding requirements</h4>{c.snapshot.unresolved_items.length?<ul>{c.snapshot.unresolved_items.map((item,i)=><li key={i}>{item}</li>)}</ul>:<p>No outstanding requirement recorded.</p>}
        <h4>Customer-safe update</h4><p>{c.snapshot.approved_customer_explanation??'No published explanation recorded.'}</p>
        {c.snapshot.approved_customer_explanation&&<Disagreement auth={auth} caseId={c.snapshot.case_id} version={c.snapshot.case_version} onSaved={()=>void refresh()}/>}
        {!c.snapshot.progress_commitments.some(x=>x.status==='approved')&&<p>Next approved update: Unknown.</p>}
        {c.snapshot.progress_commitments.map(x=><p key={x.id}>{label(x.status)} update: {time(x.approved_update_at)} · {x.customer_safe_progress}</p>)}<p>Completion estimate: Unknown. Due dates and update commitments are not completion promises.</p>
        <details><summary>Recorded timeline · {c.snapshot.timeline.length} events</summary><ol>{c.snapshot.timeline.map(e=><li key={e.event_id}><b>#{e.sequence} · {e.customer_safe_summary}</b><p>Occurred: {time(e.occurred_at)} · Recorded: {time(e.recorded_at)}</p><small>Source: {e.source_ref.section}</small></li>)}</ol></details>
      </article>)}
    </>}
  </section>;
}
