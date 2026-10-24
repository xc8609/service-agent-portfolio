import {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import type {Comparison, Derived, Source} from './types';
import './style.css';

const labels: Record<string, string> = {revenue: 'Revenue', operating_income: 'Operating income', operating_cash_flow: 'Operating cash flow'};
const defaultQuestion = 'Did revenue growth translate into operating profit and cash flow? What should I investigate next?';
type Draft = {question: string; notes: string; questions: string};
const emptyDraft = (): Draft => ({question: defaultQuestion, notes: '', questions: ''});

// Group the server's decimal text without re-calculating or losing precision.
function number(value: string) {
  const [whole, fraction] = value.split('.');
  return whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (fraction && fraction !== '00' ? `.${fraction}` : '');
}
const reasons: Record<string, string> = {
  missing_fact: 'Missing source fact', non_positive_prior: 'Prior value is zero or negative',
  non_positive_revenue: 'Revenue is zero or negative', unavailable_operating_margin: 'Operating margin unavailable',
};
function Calculation({item, suffix = ''}: {item: Derived; suffix?: string}) {
  return item.value === null
    ? <span className="unavailable">Unavailable<small>{reasons[item.reason || ''] || 'Required evidence unavailable'}</small></span>
    : <span>{number(item.value)}{suffix}</span>;
}
async function read<T>(path: string): Promise<T> {
  const response = await fetch(path, {headers: {Accept: 'application/json'}});
  let data;
  try { data = await response.json(); } catch { throw new Error('The research service did not return a usable response. Try again.'); }
  if (!response.ok) throw new Error(data.error?.safe_message || 'Source data is unavailable. Try again.');
  return data as T;
}

function App() {
  const [sources, setSources] = useState<Source[]>([]);
  const [sourceId, setSourceId] = useState('');
  const [catalogBusy, setCatalogBusy] = useState(true);
  const [catalogError, setCatalogError] = useState('');
  const [result, setResult] = useState<Comparison | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const requestVersion = useRef(0);
  const draft = drafts[sourceId] || emptyDraft();
  const selected = sources.find(source => source.id === sourceId);

  async function loadSources() {
    setCatalogBusy(true); setCatalogError('');
    try {
      const data = await read<{sources: Source[]}>('/v1/research/sources');
      setSources(data.sources); setSourceId(data.sources[0]?.id || '');
    } catch (reason) { setCatalogError(reason instanceof Error ? reason.message : 'Could not load the source list.'); }
    finally { setCatalogBusy(false); }
  }
  useEffect(() => { void loadSources(); }, []);
  function changeSource(id: string) {
    requestVersion.current++; setSourceId(id); setResult(null); setError(''); setBusy(false);
  }
  function edit(key: keyof Draft, value: string) {
    setDrafts(previous => ({...previous, [sourceId]: {...(previous[sourceId] || emptyDraft()), [key]: value}}));
  }
  async function compare() {
    if (!sourceId) return;
    const revision = ++requestVersion.current;
    setBusy(true); setError(''); setResult(null);
    try {
      const data = await read<Comparison>(`/v1/research/sources/${encodeURIComponent(sourceId)}/comparison`);
      if (revision !== requestVersion.current) return;
      if (data.source.id !== sourceId) throw new Error('The returned evidence does not match this report. Reload the comparison.');
      setResult(data);
    } catch (reason) {
      if (revision === requestVersion.current) setError(reason instanceof Error ? reason.message : 'The comparison is unavailable. Try again.');
    } finally { if (revision === requestVersion.current) setBusy(false); }
  }

  return <div className="app-shell">
    <header className="topbar"><a href="/" className="wordmark" aria-label="Investment Research Brief home"><span className="mark" aria-hidden="true">IR</span><span>Investment Research Brief</span></a><span className="topbar-note">Evidence before interpretation</span></header>
    <main>
      <div className="intro"><div><p className="eyebrow">RESEARCH WORKSPACE / ANNUAL COMPARISON</p><h1>Understand what changed.</h1><p className="lead">Check the numbers, follow the sources, and build your research view.</p></div><span className="stage">01 <span>Facts &amp; analyst notes</span></span></div>
      <div className="workspace-grid">
        <div className="research-content">
          <section className="panel" aria-labelledby="scope-heading">
            <div className="section-title"><span className="step">01</span><h2 id="scope-heading">Set the research question</h2></div>
            {catalogBusy && <p role="status">Loading available reports…</p>}
            {catalogError && <div role="alert" className="error"><p>{catalogError}</p><button className="secondary" onClick={loadSources}>Retry sources</button></div>}
            {!catalogBusy && !catalogError && sources.length === 0 && <p>No reviewed reports are available yet.</p>}
            {!!sources.length && <>
              <label>Company &amp; report<select value={sourceId} onChange={event => changeSource(event.target.value)}>{sources.map(source => <option key={source.id} value={source.id}>{source.issuer.name} · {source.title}</option>)}</select></label>
              {selected && <p className="period-line">{selected.periods.map(period => `${period.id} · ${period.start} to ${period.end}`).join('  /  ')}</p>}
              <label>Research question<textarea aria-label="Research question" rows={2} value={draft.question} onChange={event => edit('question', event.target.value)} /></label>
              <div className="action-row"><button onClick={compare} disabled={busy || !sourceId}>{busy ? 'Loading comparison…' : result ? 'Refresh comparison' : 'Load comparison'}</button><span className="muted">Figures from the selected annual report.</span></div>
            </>}
          </section>
          <section className="panel" aria-labelledby="comparison-heading" aria-busy={busy}>
            <div className="section-title"><span className="step">02</span><h2 id="comparison-heading">Compare the operating picture</h2></div>
            {busy && <p role="status">Checking source facts and calculating changes…</p>}
            {error && <div role="alert" className="error"><b>Comparison unavailable</b><p>{error}</p><p>Your question and notes are still here.</p></div>}
            {!result && !busy && !error && <div className="empty-state"><span className="empty-lines" aria-hidden="true">▤</span><p>Load the report to compare revenue, operating income and operating cash flow.</p></div>}
            {result && <>
              <p className="table-context"><b>{result.issuer.name}</b><span>{result.currency && result.unit ? `${result.currency} · ${result.unit}s` : 'Currency and scale unavailable'} · Annual periods</span></p>
              <div className="table-wrap"><table aria-label="Operating metric comparison"><thead><tr><th scope="col">Metric</th>{result.periods.map(period => <th key={period.id} scope="col">{period.id}</th>)}<th scope="col">Change</th><th scope="col">Growth</th></tr></thead><tbody>{Object.entries(labels).map(([key, label]) => <tr key={key}><th scope="row">{label}</th>{result.periods.map(period => {
                const actual = result.metrics[key].actuals[period.id];
                return <td key={period.id}>{actual ? <a href={`#${actual.fact_id}`} aria-label={`${label} ${period.id}: ${number(actual.value)}, view source`}>{number(actual.value)}</a> : <span className="unavailable">Unavailable<small>Missing source fact</small></span>}</td>;
              })}<td><Calculation item={result.metrics[key].delta}/></td><td className="growth"><Calculation item={result.metrics[key].growth_pct} suffix="%"/></td></tr>)}</tbody></table></div>
              <div className="margin-strip"><div><span>Operating margin</span><p>{result.periods.map((period, index) => <span key={period.id}>{index > 0 && <span className="arrow"> → </span>}<Calculation item={result.operating_margin_pct[period.id]} suffix="%"/><small>{period.id}</small></span>)}</p></div><div><span>Margin change</span><p><Calculation item={result.operating_margin_change_pp} suffix=" pp"/></p></div></div>
              {result.gaps.length > 0 && <div className="notice" role="status"><b>Some source facts are missing</b><ul>{result.gaps.map(gap => <li key={`${gap.metric}-${gap.period_id}`}>{labels[gap.metric] || gap.metric} · {gap.period_id}</li>)}</ul><p>Available metrics remain usable; missing values are not filled in.</p></div>}
              <details className="formulas"><summary>How the comparison is calculated</summary><p>Growth = (current − prior) ÷ prior × 100. Operating margin = operating income ÷ revenue × 100. Margin change is measured in percentage points (pp). Calculations retain full precision and round to two decimal places for display.</p><p>Growth is unavailable when the prior value is zero or negative. Source references below identify the inputs used.</p></details>
            </>}
          </section>
          <section className="panel" aria-labelledby="evidence-heading">
            <div className="section-title"><span className="step">03</span><h2 id="evidence-heading">Follow the evidence</h2></div>
            {!result ? <p className="muted">Source references appear with the loaded comparison.</p> : <>
              <div className="source-heading"><div><b>{result.source.title}</b><p className="muted">Retrieved {result.source.retrieved_at.slice(0,10)} · {result.facts.length} source facts</p></div><a className="source-link" href={result.source.url} target="_blank" rel="noreferrer">Open annual report ↗</a></div>
              <ul className="fact-list">{result.facts.map(fact => <li id={fact.id} key={fact.id} tabIndex={-1}><span>{labels[fact.metric]} · {fact.period_id}<small>{fact.locator}</small></span><b>{number(fact.value)} <small>{fact.currency} {fact.unit}</small></b></li>)}</ul>
              <p className="notice quiet">The reviewed source pack contains financial figures. Add report commentary to your notes when investigating why they changed.</p>
            </>}
          </section>
        </div>
        <aside className="notes-panel" aria-labelledby="notes-heading"><p className="eyebrow">YOUR RESEARCH</p><h2 id="notes-heading">Build the brief</h2><p>Separate what the figures show from what still needs an explanation.</p><label>Analyst notes<textarea aria-label="Analyst notes" rows={9} value={draft.notes} disabled={!sourceId} onChange={event => edit('notes', event.target.value)} placeholder="What changed? Which figures support your interpretation?"/></label><label>Open questions<textarea aria-label="Open questions" rows={5} value={draft.questions} disabled={!sourceId} onChange={event => edit('questions', event.target.value)} placeholder="What evidence would explain the change?"/></label><p className="local-note">Notes stay in this open page. Copy them before leaving.</p></aside>
      </div>
      <footer>Investment Research Brief <span>Source-linked facts · Reproducible calculations · Analyst judgment</span></footer>
    </main>
  </div>;
}

createRoot(document.getElementById('root')!).render(<App/>);
