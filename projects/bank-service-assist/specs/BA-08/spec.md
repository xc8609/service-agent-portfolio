# BA-08 — Testable limits, reliability and operational release gates

BANK-S02-v0.4 · S02 specification refinement in progress; review candidate. No implementation acceptance.

## Business purpose

Make the owner-selected transaction-query, specialist-investigation and callback workflow implementable without ambiguity about authority, data ownership, evidence or effects. Builds on owner customer-service desktop experience and dated R01/R02/R06 role evidence. All operational records/rules are simulated.

## Detailed contract

Read [contract](../contracts/interface-notes.md), [permissions](../contracts/permissions.md), [data model](../contracts/data-model.md), [interface notes](../contracts/interface-notes.md), [schema registry](../contracts/agent-tools.json) and [HTTP binding](../contracts/openapi.json). These are the substantive deliverables for this story.

Requirements: NFR-01, NFR-02, NFR-03, MEAS-01, OR-01.
Dependencies: BA-06, BA-07.
Estimate: Dev 0.5, BA 0.5, QA 0.5 person-days; total 1.5.

## Acceptance examples

- BA-08-S02-AC1: Given the S02 candidate; when reviewed against its linked requirements and examples; then Role denial and customer disclosure rules apply during failures and restarts. Evidence BA-08-S02-T1; structural checks separate from business acceptance.
- BA-08-S02-AC2: Given the S02 candidate; when reviewed against its linked requirements and examples; then Run/time/tool budgets are numeric but labelled proposed until spike review. Evidence BA-08-S02-T2; structural checks separate from business acceptance.
- BA-08-S02-AC3: Given the S02 candidate; when reviewed against its linked requirements and examples; then Service targets use versioned calendar and never become unsupported refund promises. Evidence BA-08-S02-T3; structural checks separate from business acceptance.
- BA-08-S02-AC4: Given the S02 candidate; when reviewed against its linked requirements and examples; then Accessibility, sanitized telemetry, manual fallback and restore/rollback are required release evidence. Evidence BA-08-S02-T4; structural checks separate from business acceptance.

## Decisions and Ready gate

RB-01–RB-06 are owner-accepted as D-17–D-22. The v0.4 continuation contracts incorporate those decisions. Technical fixture/contract walkthrough remains before implementation acceptance; numeric benefit targets and model budgets remain proposed. Do not ask again for the already accepted six rules.
