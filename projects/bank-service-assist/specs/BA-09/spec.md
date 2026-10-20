# BA-09 — Agent tools, human commands and versioned API contract

BANK-S02-v0.4 · S02 specification refinement in progress; review candidate. No implementation acceptance.

## Business purpose

Make the owner-selected transaction-query, specialist-investigation and callback workflow implementable without ambiguity about authority, data ownership, evidence or effects. Builds on owner customer-service desktop experience and dated R01/R02/R06 role evidence. All operational records/rules are simulated.

## Detailed contract

Read [contract](../contracts/agent-tools.md), [permissions](../contracts/permissions.md), [data model](../contracts/data-model.md), [interface notes](../contracts/interface-notes.md), [schema registry](../contracts/agent-tools.json) and [HTTP binding](../contracts/openapi.json). These are the substantive deliverables for this story.

Requirements: FR-06, FR-13, FR-14, FR-22.
Dependencies: BA-05, BA-06, BA-07, BA-08.
Estimate: Dev 1, BA 1, QA 0.5 person-days; total 2.5.

## Acceptance examples

- BA-09-S02-AC1: Given the S02 candidate; when reviewed against its linked requirements and examples; then Ten model tools and seven human/system commands have input/output JSON schemas. Evidence BA-09-S02-T1; structural checks separate from business acceptance.
- BA-09-S02-AC2: Given the S02 candidate; when reviewed against its linked requirements and examples; then The model registry excludes claim/approval/actual-call/result-publication commands. Evidence BA-09-S02-T2; structural checks separate from business acceptance.
- BA-09-S02-AC3: Given the S02 candidate; when reviewed against its linked requirements and examples; then Positive and negative payload examples validate; semantic guards are separate from JSON shape. Evidence BA-09-S02-T3; structural checks separate from business acceptance.
- BA-09-S02-AC4: Given the S02 candidate; when reviewed against its linked requirements and examples; then HTTP binding, errors, source versions, idempotency and unknown-outcome reconciliation are explicit. Evidence BA-09-S02-T4; structural checks separate from business acceptance.

## Decisions and Ready gate

RB-01–RB-06 are owner-accepted as D-17–D-22. The v0.4 continuation contracts incorporate those decisions. Technical fixture/contract walkthrough remains before implementation acceptance; numeric benefit targets and model budgets remain proposed. Do not ask again for the already accepted six rules.
