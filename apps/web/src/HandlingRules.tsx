import {useEffect,useRef,useState} from 'react';

type Rule={title:string;text:string;applicability:string[];source_label:string;is_simulated:true;policy_ref:{id:string;version:string;section:string};next_steps:string[]};
type Result={data:{state:'applicable'|'gap'|'conflict';policy_as_of:string;rules:Rule[];gaps:string[];boundary:string;context:{product:string;jurisdiction:string|null;transaction_pattern:string|null;same_account:boolean}};meta:{as_of:string}};
export function HandlingRules({auth,records}:{auth:{token:string;contact:string};records:{id:string;version:string}[]}){
  const [result,setResult]=useState<Result|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(false);
  const revision=useRef(0);
  async function refresh(){
    const current=++revision.current;setResult(null);setError('');setLoading(true);
    try{
      const response=await fetch('/v1/workspace/get_handling_rules',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${auth.token}`},body:JSON.stringify({contact_id:auth.contact,transaction_ids:records.map(r=>r.id),expected_versions:Object.fromEntries(records.map(r=>[r.id,r.version]))})});
      const value=await response.json();if(current!==revision.current)return;
      if(!response.ok)throw new Error(`${value.error?.code??'UNAVAILABLE'}: ${value.error?.safe_message??'Policy lookup unavailable.'}${value.request_id?' Reference '+value.request_id:''}`);
      setResult(value);
    }catch(e){if(current===revision.current)setError(e instanceof Error?e.message:'Policy lookup unavailable.');}
    finally{if(current===revision.current)setLoading(false);}
  }
  useEffect(()=>{if(records.length===2)void refresh();return()=>{revision.current++;};},[auth.token,auth.contact,JSON.stringify(records)]);
  return <section aria-labelledby="rules-heading"><div className="section-head"><h2 id="rules-heading">Handling rules · Simulated procedures</h2><button onClick={refresh} disabled={loading||records.length!==2}>Refresh handling rules</button></div>
    <p>Read-only guidance for the selected pair. No automated decision, referral or refund.</p>
    {records.length!==2&&<p>Select and inspect exactly two entries to check pair-specific handling rules.</p>}
    {loading&&<p aria-live="polite">Checking permitted rules… Previous guidance cleared.</p>}
    {error&&<div role="alert" className="error"><p>{error}</p><p>Rule lookup incomplete. Reinspect changed evidence or use the service lead/manual policy review route. Do not rely on previous guidance.</p></div>}
    {result&&<><p>Policy effective at contact start: {result.data.policy_as_of}. Retrieved: {result.meta.as_of}.</p><p>Product: {result.data.context.product} · Jurisdiction: {result.data.context.jurisdiction??'Unknown'} · Pair: {result.data.context.transaction_pattern?.replaceAll('_',' ')??'Unsupported'}</p>
      {result.data.gaps.map(g=><p key={g} role="alert" className="notice">{g}</p>)}
      {result.data.rules.map(r=><article key={`${r.policy_ref.id}/${r.policy_ref.section}`} aria-label={`Rule ${r.title}`}><h3>{r.title}</h3>
        <p className="muted">{r.source_label}</p><p>Policy {r.policy_ref.id} · version {r.policy_ref.version} · section {r.policy_ref.section}</p>
        <h4>Applicability conditions</h4><ul>{r.applicability.map(c=><li key={c}>{c}</li>)}</ul>
        <details><summary>Read exact source section</summary><p style={{whiteSpace:'pre-wrap'}}>{r.text}</p></details>
        {result.data.state==='applicable'&&<><h4>Suggested next steps · Representative review required</h4><ol>{r.next_steps.map(s=><li key={s}>{s}</li>)}</ol></>}
      </article>)}<p>{result.data.boundary}</p></>}
  </section>;
}
