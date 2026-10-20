# DEV-04 — Explain the recorded status and next step of an existing case

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S03 | Release: B0 | Estimate: Dev 2, BA 0.25, QA 0.5 person-days. Provisional until technical review.

## Business purpose and scope

As a representative, I want a trustworthy case timeline so that I can explain current status and outstanding work without inventing progress or dates.

Value: Support actual follow-up only when an existing case requires it. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

Merchant refund status is a separate concept and must not be inferred from a bank case label. All operational scenarios and records are synthetic.

Requirements: FR-02, FR-04. Dependencies: DEV-02, BA-06.

## Delivery flow

1. Implement scoped case/timeline endpoints and ordered event history.
2. Render status source timestamp, pending requirement and ownership; distinguish no case from unavailable data.
3. Handle conflicting events explicitly; don't silently pick a convenient narrative.

## Acceptance criteria

- **DEV-04-AC01** — Given Assigned feedback task and case awaiting documents; when open timeline; then show recorded request, owner, source time and original due date without inventing progress. Evidence: DEV-04-T01, planned/not executed.
- **DEV-04-AC02** — Given No approved next update or completion estimate; when request customer explanation; then show next update unknown and completion date unknown separately; pending commitment is not displayed as approved. Evidence: DEV-04-T02, planned/not executed.
- **DEV-04-AC03** — Given Two events arrive out of order with distinct occurrence/recording times; when render case history; then use stable aggregate sequence and show both timestamps; do not overwrite prior finding with late ingestion. Evidence: DEV-04-T03, planned/not executed.
- **DEV-04-AC04** — Given A case ID belongs to another customer or task has been reassigned; when read case; then deny with uniform FORBIDDEN_OR_NOT_FOUND; no existence disclosure and no retained stale detail. Evidence: DEV-04-T04, planned/not executed.
- **DEV-04-AC05** — Given Re-review and complaint intake coexist; when read linked work; then show separate owners/statuses and original case link; completion of one does not mark the other resolved. Evidence: DEV-04-T05, planned/not executed.
- **DEV-04-AC06** — Given Unavailable upstream or conflicting current versions; when refresh; then show unavailable/conflict rather than no case or closed; retain last-view freshness label and disable unsafe commit. Evidence: DEV-04-T06, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)
