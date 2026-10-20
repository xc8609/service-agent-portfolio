# DEV-10 — Build operational event marts and a reconciled Tableau view

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S05A | Release: B1 | Estimate: Dev 3, BA 1, QA 0.5 person-days. Provisional until technical review.

## Business purpose and scope

As an operations analyst, I want trustworthy workflow metrics so that I can inspect failures, corrections and handoffs without confusing model output with business results.

Value: Connect the data analyst portfolio to the same service question. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

Dashboard creation and validation are future work, not completed by this plan. All operational scenarios and records are synthetic.

Requirements: BR-01, MEAS-01. Dependencies: DEV-06, DEV-07, DEV-08, BA-07.

## Delivery flow

1. Record run/contact/proposal/action IDs and authoritative timestamps without sensitive payloads.
2. Build SQL marts and aggregate exports for Tableau; retain existing CFPB descriptive analysis separately.
3. Add reconciliation totals and labelled synthetic/live-test segmentation. Report cost unavailable if usage is missing.

## Acceptance criteria

- **DEV-10-AC01** — Given A known synthetic event ledger with duplicate delivery; when build marts; then deduplicate by authoritative IDs; exported totals equal fixture oracle and SQL source totals. Evidence: DEV-10-T01, planned/not executed.
- **DEV-10-AC02** — Given Completed, cancelled, failed and abandoned runs; when calculate run metrics; then include all started runs in outcome denominator; show unresolved and missing latency explicitly. Evidence: DEV-10-T02, planned/not executed.
- **DEV-10-AC03** — Given Draft edited multiple times then approved once; when calculate proposal metrics; then count a proposal once by defined revision/status rule; distinguish accepted unchanged from edited; exclude pending from decided-only denominator and display pending count. Evidence: DEV-10-T03, planned/not executed.
- **DEV-10-AC04** — Given Original contact plan followed by lead-approved plan; when calculate callback metrics; then report lifetime calls, per-plan calls, technical faults and original-window misses separately; no apparent improvement from erased history. Evidence: DEV-10-T04, planned/not executed.
- **DEV-10-AC05** — Given No human effort study or provider usage missing; when render Tableau; then no measured savings/ROI shown; missing cost remains unavailable; synthetic status visible. Evidence: DEV-10-T05, planned/not executed.
- **DEV-10-AC06** — Given Same data refresh is repeated, including late events; when export and refresh workbook; then stable snapshot totals reconcile; late-event adjustment and data cutoff are recorded. Evidence: DEV-10-T06, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)
