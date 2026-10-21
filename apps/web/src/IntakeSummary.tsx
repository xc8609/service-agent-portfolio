export type Intake = {
  id: string;
  committed_at: string;
  payload: {
    concern: string;
    requested_review: string;
    transaction_ids: string[];
    missing_evidence: string[];
    intake: {
      statement_revision: number;
      recognition: string;
      recognized_transaction_id: string | null;
      customer_summary_confirmed: boolean;
      mode: string;
      distinct_work_reason: string | null;
      material_gaps: {item: string; state: string; owner: string; next_action: string; review_trigger: string}[];
      clarifications: Record<string, {state: string; value: unknown}>;
      contact: {state: string; reason: string | null};
    };
  };
};

const recognition: Record<string, string> = {
  one_purchase_unresolved: 'One purchase recognized; which entry is additional remains unresolved.',
  specific_entry: 'One specified entry recognized; this is a customer report, not a ledger finding.',
  both: 'Both entries recognized by the customer.',
  neither: 'Neither entry recognized by the customer.',
};

export function IntakeSummary({intakes}: {intakes: Intake[]}) {
  return <section aria-label="Submitted intake history">
    <h4>Submitted intake history</h4>
    <p>Customer-reported information, not verified transaction conclusions. Each submission retains its original context; later follow-up is recorded separately.</p>
    {!intakes.length && <p>No submitted intake is recorded for this seeded case.</p>}
    {intakes.map(({id, committed_at, payload}) => <article key={id} aria-label={`Intake ${id}`}>
      <h5>Statement revision {payload.intake.statement_revision} · {payload.intake.mode === 'link_existing' ? 'Linked investigation' : 'New investigation'}</h5>
      <p>Intake {id} · submitted {committed_at}</p>
      <dl>
        <dt>Customer statement</dt><dd>{payload.concern}</dd>
        <dt>Recognition scope</dt><dd>{recognition[payload.intake.recognition] ?? payload.intake.recognition}</dd>
        <dt>Recognized entry</dt><dd>{payload.intake.recognized_transaction_id ?? 'Not specified; do not infer an entry.'}</dd>
        <dt>Selected transaction references</dt><dd>{payload.transaction_ids.join(' · ')}</dd>
        <dt>Requested specialist review</dt><dd>{payload.requested_review}</dd>
        <dt>Customer confirmed summary</dt><dd>{payload.intake.customer_summary_confirmed ? 'Yes' : 'Not recorded'}</dd>
        {payload.intake.distinct_work_reason && <><dt>Reason for distinct work</dt><dd>{payload.intake.distinct_work_reason}</dd></>}
        <dt>Evidence gaps</dt><dd>{payload.missing_evidence.join('; ') || 'None recorded'}</dd>
        <dt>Material gaps</dt><dd>{payload.intake.material_gaps.map(g => `${g.item}: ${g.state}; owner ${g.owner}; next ${g.next_action}; review ${g.review_trigger}`).join('; ') || 'None recorded'}</dd>
        <dt>Contact readiness at submission</dt><dd>{payload.intake.contact.state}{payload.intake.contact.reason ? ` — ${payload.intake.contact.reason}` : ''}</dd>
      </dl>
      <ul>{Object.entries(payload.intake.clarifications).map(([field, answer]) =>
        <li key={field}>{field.replaceAll('_', ' ')}: {answer.state}{answer.value == null ? '' : ` — ${String(answer.value)}`}</li>)}</ul>
      <p>Specialist assesses missing material; customer service owns requests and contact resolution. Gaps do not reset original deadlines or close outstanding feedback.</p>
    </article>)}
  </section>;
}
