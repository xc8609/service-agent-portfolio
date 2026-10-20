# BA-06 — Rules, role permissions and transition decisions

BANK-S02-v0.4 · S02 specification refinement in progress; review candidate. No implementation acceptance.

## Business purpose

Make the owner-selected transaction-query, specialist-investigation and callback workflow implementable without ambiguity about authority, data ownership, evidence or effects. Builds on owner customer-service desktop experience and dated R01/R02/R06 role evidence. All operational records/rules are simulated.

## Detailed contract

Read [contract](../contracts/permissions.md), [permissions](../contracts/permissions.md), [data model](../contracts/data-model.md), [interface notes](../contracts/interface-notes.md), [schema registry](../contracts/agent-tools.json) and [HTTP binding](../contracts/openapi.json). These are the substantive deliverables for this story.

Requirements: FR-01, FR-16, FR-18, FR-19, FR-20, FR-21.
Dependencies: BA-04, BA-05.
Estimate: Dev 1, BA 2.5, QA 0.5 person-days; total 4.0.

## Acceptance examples

- BA-06-S02-AC1: Given the S02 candidate; when reviewed against its linked requirements and examples; then Permission matrix specifies allow/deny predicates for every role/action. Evidence BA-06-S02-T1; structural checks separate from business acceptance.
- BA-06-S02-AC2: Given the S02 candidate; when reviewed against its linked requirements and examples; then Staff preparation is distinct from customer disclosure; RB-01/D-17 reflected in cases. Evidence BA-06-S02-T2; structural checks separate from business acceptance.
- BA-06-S02-AC3: Given the S02 candidate; when reviewed against its linked requirements and examples; then Case/work/result/proposal/contact states have actor/guard/side-effect contracts. Evidence BA-06-S02-T3; structural checks separate from business acceptance.
- BA-06-S02-AC4: Given the S02 candidate; when reviewed against its linked requirements and examples; then All accepted rules D-17–D-22 trace to explicit permission/state/interface examples; no automatic closure or hidden counter reset. Evidence BA-06-S02-T4; structural checks separate from business acceptance.

## Decisions and Ready gate

RB-01–RB-06 are owner-accepted as D-17–D-22. The v0.4 continuation contracts incorporate those decisions. Technical fixture/contract walkthrough remains before implementation acceptance; numeric benefit targets and model budgets remain proposed. Do not ask again for the already accepted six rules.
