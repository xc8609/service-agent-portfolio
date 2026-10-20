# DEV-13 — Handle overdue investigations and customer objections with linked work

Current S02 forecast: **S04A**. Updated effort: Dev 4, BA 1, QA 1 person-days (6 total); dependencies DEV-11, BA-06, BA-09. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation pending.

BANK-SDD-v0.2 · 19 October 2026
Status: Detailed specification candidate; implementation not started. Business decisions accepted only as listed; technical design/Ready gates pending.
Historical forecast superseded by the current Sprint stated above | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 1, QA 1 person-days; total 6 (4.5–9), confidence low. Not actual effort.

## User story and value

As a service lead and representative, I want current evidence and accountable exception continuation, so that I can avoid silent delays and lost customer objections.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-20, FR-21. Decisions: D-14, D-15, D-20, D-21. Dependencies: DEV-11, BA-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Scheduler detects overdue work and rechecks latest state.
2. Agent gathers recorded blockers and commitments; drafts escalation and progress update.
3. Keep original deadlines and specialist ownership; a human confirms new commitments.
4. Capture objection verbatim, compare with old evidence and propose clarification, linked re-review or complaint review.
5. Preserve prior findings and any complaint request independently of re-review.

## Acceptance criteria

- **DEV-13-AC01** — Given A routine investigation exceeds the two-service-day target; when the timer event arrives; then retain original investigation due time and specialist ownership; notify the responsible lead and create feedback-queue progress work; only a lead-confirmed specialist proposal can establish the next update time, without replacing overdue history. Evidence: DEV-13-T01 (planned, not executed).
- **DEV-13-AC02** — Given The same overdue event is delivered twice; when the worker handles it; then produce one escalation per case, deadline and escalation level. Evidence: DEV-13-T02 (planned, not executed).
- **DEV-13-AC03** — Given No blocker reason is recorded; when the agent drafts an update; then label the reason unknown; do not invent merchant or bank explanations or promise an unapproved date. Evidence: DEV-13-T03 (planned, not executed).
- **DEV-13-AC04** — Given An investigation completes while an escalation is being approved; when the backend rechecks state; then invalidate the outdated escalation and continue with the current result. Evidence: DEV-13-T04 (planned, not executed).
- **DEV-13-AC05** — Given A customer provides a different transaction or new evidence; when a re-review is approved; then link the new work to the original case and preserve old findings/versions. Evidence: DEV-13-T05 (planned, not executed).
- **DEV-13-AC06** — Given A customer explicitly requests complaint handling while re-review remains open; when the objection is assessed; then create independently tracked complaint intake linked to the original case and objection, without waiting for specialist re-review; preserve distinct owners/statuses and do not duplicate intake on replay. Evidence: DEV-13-T06 (planned, not executed).
- **DEV-13-AC07** — Given A customer disagrees without new evidence; when the agent proposes next steps; then preserve the disagreement and route specialist re-review even without new evidence; clarification may accompany it; no coercion, financial action or automatic resolved closure. Evidence: DEV-13-T07 (planned, not executed).

## Ready gates

- D-20/D-21 accept overdue responsibility, next-update approval and parallel re-review/complaint intake. Typed commitment/approval, progress-without-result and complaint linkage/receipt contracts are authored in v0.4; walkthrough and configured lead/intake queues remain before Ready. Additional escalation levels and fixed update cadence are not accepted.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
