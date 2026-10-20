# DEV-06 — Review, edit and commit a contact note safely

BANK-S02-v0.4 · Inbound note implementation under PR review; owner UAT pending.
Forecast: S04 | Release: B0 | Estimate: Dev 5, BA 0.5, QA 1 person-days. Provisional until technical review.

## Business purpose and scope

As a representative, I want to edit and approve a supported note so that the saved service record is accurate and remains under my control.

Value: Target after-contact documentation effort without reducing record quality. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

A drafted statement that work was completed never counts as proof of execution. All operational scenarios and records are synthetic.

Requirements: FR-07, FR-08, FR-11, FR-13, NFR-02, NFR-03. Dependencies: DEV-02, DEV-03, DEV-04, BA-09.

## Delivery flow

1. Implement versioned draft and approval endpoints with actor, source versions and operation key.
2. Commit note and audit/outbox event atomically; preserve edits on stale-version conflicts.
3. Build editable note preview with clear unsaved/committed status; deterministic manual template first.

## Acceptance criteria

- **DEV-06-AC01** — Given A manual draft with customer allegation and supported facts; when staff edits and approves current proposal revision; then save exactly reviewed content, labelled allegations, actor/time, source versions and durable receipt. Evidence: DEV-06-T01, planned/not executed.
- **DEV-06-AC02** — Given Source or assignment changes after draft; when approve; then reject stale/unauthorized commit; preserve user edits for deliberate rebase, never silently overwrite. Evidence: DEV-06-T02, planned/not executed.
- **DEV-06-AC03** — Given Two edits target same proposal version; when save both; then one version advances, second conflicts; revision history remains auditable. Evidence: DEV-06-T03, planned/not executed.
- **DEV-06-AC04** — Given Same approval key/payload is retried after response loss; when retry; then return same committed note and receipt; no duplicate note/outbox event. Evidence: DEV-06-T04, planned/not executed.
- **DEV-06-AC05** — Given Same operation key with changed content; when retry; then IDEMPOTENCY_CONFLICT with original content untouched. Evidence: DEV-06-T05, planned/not executed.
- **DEV-06-AC06** — Given Note says refund completed but there is no completion evidence; when review/commit; then flag unsupported action claim; statement may only be stored as attributed customer allegation, not confirmed execution. Evidence: DEV-06-T06, planned/not executed.
- **DEV-06-AC07** — Given Model or unscoped employee invokes edit or commit; when submit; then deny; create_proposal remains draft-only; server authority does not come from body fields. Evidence: DEV-06-T07, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)
