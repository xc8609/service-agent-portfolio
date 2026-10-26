import {useEffect, useRef, useState} from 'react';
import type {Comparison, ResearchDraft} from './types';

function draftText(draft: ResearchDraft) {
  const lines = [`Research draft — ${draft.question}`];
  for (const [kind, heading] of [['calculated_fact', 'Facts'], ['reported_explanation', 'Company explanations (summarized)']]) {
    lines.push('', heading);
    for (const finding of draft.findings.filter(item => item.kind === kind)) {
      lines.push(`- ${finding.text}`);
      for (const citation of finding.citations) lines.push(`  Source: ${citation.label} — ${citation.locator} (${citation.url})`);
    }
  }
  lines.push('', 'Open questions', ...draft.open_questions.map(question => `- ${question}`));
  return lines.join('\n');
}

export function AgentDraft({comparison, question, onAppend}: {comparison: Comparison | null; question: string; onAppend: (text: string) => void}) {
  const [draft, setDraft] = useState<ResearchDraft | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [appended, setAppended] = useState(false);
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);

  async function generate() {
    if (!comparison || !question.trim()) return;
    active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    const asked = question.trim();
    setBusy(true); setError(''); setDraft(null); setAppended(false);
    try {
      const response = await fetch('/v1/research/runs', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, signal: controller.signal,
        body: JSON.stringify({source_id: comparison.source.id, question: asked, expected_source_hash: comparison.source.sha256}),
      });
      // A proxy or server error page is not JSON; keep the user-facing message plain.
      const data = await response.json().catch(() => ({}));
      if (controller.signal.aborted) return;
      if (!response.ok) throw new Error(data.error?.safe_message || 'The research draft could not be generated. Try again.');
      if (data.source_id !== comparison.source.id || data.source_hash !== comparison.source.sha256 || data.question !== asked)
        throw new Error('The returned draft does not match the current report and question. Generate it again.');
      if (!['draft', 'incomplete'].includes(data.status) || !Array.isArray(data.findings) || !Array.isArray(data.open_questions) || !Array.isArray(data.trace) || !Array.isArray(data.issues))
        throw new Error('The research service returned an unusable draft. Try again.');
      setDraft(data);
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'The research draft is unavailable. Try again.');
    } finally { if (!controller.signal.aborted) setBusy(false); }
  }

  return <section className="panel agent-panel" aria-labelledby="agent-heading" aria-busy={busy}>
    <div className="section-title"><span className="step">04</span><h2 id="agent-heading">Draft the research brief</h2><span className="draft-badge">Demo draft</span></div>
    <p className="muted">Connect the question to financial changes and report explanations, with sources to check.</p>
    <button onClick={generate} disabled={!comparison || !question.trim() || busy}>{busy ? 'Preparing research draft…' : draft ? 'Regenerate research draft' : 'Generate research draft'}</button>
    {!comparison && <p className="muted">Load the comparison to prepare a draft.</p>}
    {busy && <p role="status">Retrieving evidence and assembling the brief…</p>}
    {error && <div role="alert" className="error"><b>Draft unavailable</b><p>{error}</p><p>Your comparison and analyst notes remain available.</p></div>}
    {draft && <div className="research-draft" aria-label="Research draft">
      <p className="draft-question"><b>Research question</b><br/>{draft.question}</p>
      {draft.status === 'incomplete' && <div className="notice" role="status"><b>Draft incomplete</b><p>Some evidence or steps are unavailable. Review the issues and continue with the source material or your notes.</p></div>}
      {draft.issues.length > 0 && <ul className="draft-issues">{draft.issues.map((issue, index) => <li key={index}>{issue.message}</li>)}</ul>}
      {(['calculated_fact', 'reported_explanation'] as const).map(kind => <section className="draft-section" key={kind} aria-label={kind === 'calculated_fact' ? 'Draft facts' : 'Draft company explanations'}>
        <h3>{kind === 'calculated_fact' ? 'Facts' : 'Company explanations (summarized)'}</h3>
        {draft.findings.filter(item => item.kind === kind).length === 0 && <p className="muted">No supported {kind === 'calculated_fact' ? 'finding' : 'explanation'} returned for this question.</p>}
        {draft.findings.filter(item => item.kind === kind).map((finding, index) => <article className="draft-finding" key={index}>
          <p>{finding.text}</p><ul className="draft-citations">{finding.citations.map(citation => <li key={citation.id}><a href={citation.url} target="_blank" rel="noreferrer">{citation.label}</a><small>{citation.locator}</small></li>)}</ul>
        </article>)}
      </section>)}
      <section className="draft-section" aria-label="Draft open questions"><h3>Open questions</h3>{draft.open_questions.length ? <ul>{draft.open_questions.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p className="muted">No additional question was returned. Add your own research follow-up.</p>}</section>
      <details className="formulas"><summary>Evidence retrieval steps</summary><p>Runtime: {draft.provider}. This demonstration uses scripted tool selection and source-backed text.</p><ol>{draft.trace.map((step, index) => <li key={index}>{step.tool} · {step.status}</li>)}</ol></details>
      <div className="action-row"><button className="secondary" disabled={draft.status !== 'draft' || appended} onClick={() => {onAppend(draftText(draft)); setAppended(true);}}>{appended ? 'Appended to notes' : 'Append draft to notes'}</button><span className="muted">Review and edit the text in your notes.</span></div>
    </div>}
  </section>;
}
