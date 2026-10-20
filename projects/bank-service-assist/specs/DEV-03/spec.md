# DEV-03 — Identify a card charge and investigate apparent duplicate entries

Current S02 forecast: **S03**. Updated effort: Dev 3, BA 0.5, QA 0.5 person-days (4 total); dependencies DEV-02, BA-06. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation pending.

BANK-SDD-v0.2 · 19 October 2026
Status: Detailed specification candidate; implementation not started. Business decisions accepted only as listed; technical design/Ready gates pending.
Forecast: S03 | Release: B0 manual path / B1 assisted path.
Estimate: Dev 3, BA 0.5, QA 0.5 person-days; total 4 (3–6), confidence medium. Not actual effort.

## User story and value

As a representative, I want transaction evidence in one investigation view, so that I can explain a charge or refer a genuine evidence gap.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-02, FR-03, FR-06, FR-07. Decisions: D-10, D-11. Dependencies: DEV-02, BA-07.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Capture customer statement separately from verified records.
2. Find candidate transactions by permitted card/date/amount/merchant and ask for selection if ambiguous.
3. Inspect status, provenance, reliable relationship evidence and related work.
4. Prepare an explanation or unresolved question, not a duplicate/refund determination.

## Acceptance criteria

- **DEV-03-AC01** — Given Two entries have equal amount and merchant but no relationship evidence; when the representative or agent reviews them; then show statuses and uncertainty; do not infer a duplicate or a shared purchase. Evidence: DEV-03-T01 (planned, not executed).
- **DEV-03-AC02** — Given One entry is pending and another posted; when evidence is summarized; then cite both states without promising automatic reversal or a refund. Evidence: DEV-03-T02 (planned, not executed).
- **DEV-03-AC03** — Given Several transactions match the customer description; when search returns candidates; then require clarification or explicit selection before a case-specific proposal. Evidence: DEV-03-T03 (planned, not executed).
- **DEV-03-AC04** — Given A customer corrects the transaction or denies the purchase; when the correction is saved; then retain the original statement and mark affected advice stale; offer the reviewed manual risk path. Evidence: DEV-03-T04 (planned, not executed).
- **DEV-03-AC05** — Given Source retrieval times out; when the investigation cannot complete; then show unavailable rather than no transactions; permit manual continuation. Evidence: DEV-03-T05 (planned, not executed).
- **DEV-03-AC06** — Given An existing case covers the selected transaction concern; when related work is displayed; then show its actual reference/status and do not silently create a duplicate. Evidence: DEV-03-T06 (planned, not executed).

## Ready gates

- The initial job is accepted; exact synthetic transaction fields and out-of-scope risk handoff need contract review.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
