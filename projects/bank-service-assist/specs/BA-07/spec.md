# BA-07 — Operational data model, ownership and evidence lineage

BANK-S02-v0.4 · S02 specification refinement in progress; review candidate. No implementation acceptance.

## Business purpose

Make the owner-selected transaction-query, specialist-investigation and callback workflow implementable without ambiguity about authority, data ownership, evidence or effects. Builds on owner customer-service desktop experience and dated R01/R02/R06 role evidence. All operational records/rules are simulated.

## Detailed contract

Read [contract](../contracts/data-model.md), [permissions](../contracts/permissions.md), [data model](../contracts/data-model.md), [interface notes](../contracts/interface-notes.md), [schema registry](../contracts/agent-tools.json) and [HTTP binding](../contracts/openapi.json). These are the substantive deliverables for this story.

Requirements: DATA-01, FR-03, FR-13, FR-17, FR-22.
Dependencies: BA-06.
Estimate: Dev 1, BA 2.0, QA 0.5 person-days; total 3.5.

## Acceptance examples

- BA-07-S02-AC1: Given the S02 candidate; when reviewed against its linked requirements and examples; then Entities, keys, foreign keys, nullability and version/provenance fields are explicit. Evidence BA-07-S02-T1; structural checks separate from business acceptance.
- BA-07-S02-AC2: Given the S02 candidate; when reviewed against its linked requirements and examples; then Cross-customer links, assignment scope and private-note separation have negative cases. Evidence BA-07-S02-T2; structural checks separate from business acceptance.
- BA-07-S02-AC3: Given the S02 candidate; when reviewed against its linked requirements and examples; then Synthetic fixture manifest covers normal, duplicate, stale, missing and holiday cases. Evidence BA-07-S02-T3; structural checks separate from business acceptance.
- BA-07-S02-AC4: Given the S02 candidate; when reviewed against its linked requirements and examples; then Reference SQL limitations and actual migration/restore gates are declared. Evidence BA-07-S02-T4; structural checks separate from business acceptance.

## Decisions and Ready gate

RB-01–RB-06 are owner-accepted as D-17–D-22. The v0.4 continuation contracts incorporate those decisions. Technical fixture/contract walkthrough remains before implementation acceptance; numeric benefit targets and model budgets remain proposed. Do not ask again for the already accepted six rules.
