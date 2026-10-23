import {useEffect,useRef,useState} from 'react';

type AgentProps = {
  token:string;
  context:{contact_id:string|null;case_id:string|null;work_item_id:string|null;transaction_ids:string[]};
  contextKey:string;
  disabled?:boolean;
  onSuggestion?:(s:string)=>void;
};

export function AgentPanel(props:AgentProps){
  // A new query/identity owns a new panel before it becomes interactive. A passive
  // reset effect could otherwise clear a click made on the freshly rendered scope.
  return <ScopedAgentPanel key={JSON.stringify([props.token,props.contextKey])} {...props}/>;
}

function ScopedAgentPanel({token,context,disabled=false,onSuggestion}:AgentProps){
  const [result,setResult]=useState<any>(null);
  const [question,setQuestion]=useState('Explain these charges and suggest the next step for staff review.');
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  const active=useRef(true),trigger=useRef<string|null>(null);
  useEffect(()=>{active.current=true;return()=>{active.current=false;};},[]);
  const canRun=!!question.trim()&&!disabled&&(!!context.work_item_id||context.transaction_ids.length===2);

  async function call(action:string,payload:unknown){
    const response=await fetch('/v1/assistant/'+action,{
      method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},
      body:JSON.stringify(payload),
    });
    const data=await response.json();
    if(!response.ok)throw new Error(data.error?.code??'Service unavailable');
    return data;
  }
  async function start(){
    if(!canRun||busy)return;
    setBusy(true);setError('');trigger.current??=crypto.randomUUID();
    try{
      const data=await call('run',{...context,trigger_key:trigger.current,staff_question:question});
      if(active.current)setResult(data);
    }catch(e){if(active.current)setError(String(e));}
    finally{if(active.current)setBusy(false);}
  }
  async function reload(){
    if(!canRun||busy||!result)return;
    setBusy(true);setError('');
    try{
      const data=await call('get_run',{run_id:result.run_id});
      if(active.current)setResult(data);
    }catch(e){if(active.current){setResult(null);setError(String(e));}}
    finally{if(active.current)setBusy(false);}
  }

  return <section aria-label="Bounded evidence assistant">
    <h3>Offline evidence assistant</h3>
    <p>Scripted provider fixture — demonstrates scoped tools and durable workflow, not live AI quality. Maximum four steps and 20 seconds. Business actions still require staff approval.</p>
    <label>Question for the assistant
      <textarea value={question} maxLength={1000} disabled={busy||disabled} onChange={e=>{
        setQuestion(e.target.value);setResult(null);setError('');trigger.current=null;
      }}/>
    </label>
    <p>The offline fixture demonstrates evidence flow only; a configured model receives your question. Changing it starts a new run.</p>
    <button disabled={busy||!canRun} onClick={start}>{busy?'Gathering permitted evidence…':'Run scoped offline assistant'}</button>
    {disabled&&<p>Inspect the current evidence and finish any report save before starting the assistant.</p>}
    {error&&<p role="alert">{error}. Manual controls remain available. Retry uses the same trigger.</p>}
    {result&&<>
      <p>Run {result.run_id} · {result.status} · usage {result.usage?JSON.stringify(result.usage):'unavailable'}</p>
      {result.error_code&&<p role="alert">{result.error_code}; refresh evidence and start a new bounded run.</p>}
      {result.output&&<>
        {result.output.customer_report&&<div className="notice" aria-label="Saved customer statement">
          <b>Customer-reported · report v{result.output.customer_report.revision}</b>
          <p>{result.output.customer_report.statement}</p>
          <p>Customer statement, not a verified outcome. Retain reported material gaps for customer-service follow-up; review before committing.</p>
        </div>}
        <div aria-label="Assistant summary" style={{whiteSpace:'pre-wrap'}}>{result.output.summary}</div>
        <details><summary>Sources and review checks</summary>
          <ul>{result.output.citations.map((citation:string)=><li key={citation}>{citation}</li>)}</ul>
          <ul>{result.output.gaps.map((gap:string)=><li key={gap}>{gap}</li>)}</ul>
        </details>
        {result.output.proposal_id&&<p>Uncommitted note draft {result.output.proposal_id}. Load note history below, review the saved draft, and approve only after checking evidence.</p>}
        {onSuggestion&&<button disabled={busy||!canRun} onClick={()=>onSuggestion(result.output.summary)}>Use as editable review text</button>}
      </>}
      <button disabled={busy||!canRun} onClick={reload}>Reload durable run</button>
      <button disabled={busy||!canRun} onClick={()=>{trigger.current=null;setResult(null);setError('');}}>Prepare new run from current evidence</button>
    </>}
  </section>;
}
