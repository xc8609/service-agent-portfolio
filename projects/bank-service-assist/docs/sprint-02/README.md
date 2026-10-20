# Sprint 02 — authority, data and agent contracts

BANK-S02-v0.4 · Started specification refinement on 19 October 2026 at the owner's request, before its illustrative calendar slot. S01 remains open for repository/acceptance work. The first inbound lookup slice is under implementation/PR review; see the current scope and evidence below.

## Deliverables

- [Permission matrix](../../specs/contracts/permissions.md) and [machine-readable predicates/cases](../../specs/contracts/permissions.json): seven roles, explicit assignment and customer disclosure boundaries. D-17 accepted.
- [Data model](../../specs/contracts/data-model.md), [structured model](../../specs/contracts/data-model.json), [reference SQL](../../specs/contracts/schema-reference.sql): 32 entities; SQL not executed.
- [Tool schema registry](../../specs/contracts/agent-tools.json), [interface notes](../../specs/contracts/interface-notes.md), [OpenAPI](../../specs/contracts/openapi.json): ten model-visible tools and twelve trusted commands. Actual implementation/provider qualification pending.
- [Business review register](business-review.json): all six items RB-01–RB-06 accepted as D-17–D-22 on 19 October 2026. This completes this review set, not all project business or technical acceptance.
- [Reforecast rationale](forecast-impact.md), [current Sprint plan](../../../../docs/backlog/sprints.md), [machine-readable capacity](../../../../docs/backlog/sprint-forecast.json).
- BA-06/07/08/09 each have spec/design/tasks/acceptance files; DEV story metadata updated to current forecast.

## Engineering and business gates

Contract validation, reference integrity and capacity arithmetic are author checks. They do not prove runtime authorization, actual customer outcomes, database migrations, provider interoperability or deployment. No critical pending business branch is silently accepted. Complete schema/fixture review and use executed evidence for Ready/Done decisions.

## Forecast summary

12 delivery iterations / 24 weeks plus two reserve iterations, retaining stable IDs through inserted S04A and S05A. Bank B1 at week 16, phone B2 week 20, retail R1 week 24. All dates illustrative and not adjusted for actual holiday/leave availability; total 170.5 person-days, not elapsed duration. See role capacities and dependency-sensitive slices before commitment.

## Verification and publication

[Validation report](validation.json): 45 schemas meta-validated, 91 generated schema payload examples, entity/reference checks and role/lane capacity checks passed. [State transitions](../../specs/contracts/state-transitions.md) adds explicit guard/effect review. SQL, APIs, live models and runtime UAT are not executed.

[Earlier v0.3 Trello sync](trello-sync.json): 35 cards saved/verified; roadmap order verified; 56 cards in registry. [Current v0.4 sync](v04-trello-sync.json): 20 existing cards updated and verified. No card marked Done.

Reproduce contract checks: install projects/bank-service-assist/requirements-contract.txt in a development environment, then run `python projects/bank-service-assist/scripts/validate_s02_contracts.py` from repository root. This run used Python 3.9 and jsonschema 4.25.1 installed in a temporary directory, without changing the project environment.

## Accepted review baseline

| Decision | Rule | Main trace |
|---|---|---|
| D-17 / RB-01 | Masked summary before claim; necessary detail after claim; fresh verification before disclosure | Permission matrix, DEV-11 |
| D-18 / RB-02 | Never-placed fault does not consume quota or extend deadlines; placed unanswered call counts | DEV-12-AC01/T01 |
| D-19 / RB-03 | First placed-call service date is day 1; third service date ends at 17:00 local, excluding configured holidays | DEV-12-AC04/T04 |
| D-20 / RB-04 | Existing specialist retains investigation; lead confirms next update; feedback queue contacts customer | DEV-13-AC01–04/T01–04 |
| D-21 / RB-05 | Re-review and explicit complaint intake proceed independently with original-case links | DEV-13-AC05–07/T05–07 |
| D-22 / RB-06 | Lead may approve reasoned new plan or owned/date-bound review hold; no erased history or automatic resolution | DEV-12-AC03/07 and T03/07 |

## Specification completion and remaining gates

The [continuation specification](../../specs/contracts/continuation-addendum.md) is now backed by JSON Schema/OpenAPI, role predicates, 32-entity relational model and reference DDL. The registry contains 10 model tools and 12 trusted commands. New manual note/progress draft variants do not add model authority.

Detailed four-file packages now cover BA-01–09, DEV-01–13, QA-01 and OPS-01: **24 packages**. [Seven newly detailed stories](delivery-specs.json) add 43 planned acceptance cases alongside the existing eight workflow stories' 49 cases. These are specification counts, not passed application tests. Later QA/release/voice/retail stories retain planning-level cards.

| Gate | Current state | Next evidence |
|---|---|---|
| RB-01–RB-06 business rules | Accepted D-17–D-22 | No repeat approval needed |
| Continuation data/permissions/interfaces | Authored v0.4, offline checks | Walkthrough of typed payloads and story fixtures |
| Calendar/date examples | Four authored synthetic examples, explicit holiday/DST expectations | Implement service calendar; run cutoff/retry integration tests |
| Engineering foundation | DEV-01, QA-01, OPS-01 fully specified | Reproducible setup, migrations, CI and no-key manual smoke |
| Benefit target and model budgets | Proposed, not silently accepted | Freeze experiment target before evaluation; qualify budgets in DEV-09 spike |
| Runtime database/API/UI/security | Not executed | Implement and run meaningful transaction/permission/UI tests |
| Live model and deployment | Not executed | Qualified routes, UAT/recovery and staging evidence |
| Public GitHub repository | Published with MIT; offline CI passed | First runtime PR and branch protection verification |

Sprint allocation and provisional effort remain unchanged in this specification pass. Before committing S04A capacity, check the continuation implementation against the existing DEV-12/13 estimates; record a change/reforecast if integration expands. S01 remains open for repository/acceptance work. Draft specs and accepted business rules do not mark a Sprint Done.

Current completion evidence: [specification handoff](spec-completion.md), [validation](validation.json), [52 targeted schema boundary cases](../../specs/contracts/continuation-schema-cases.json), and [four calendar examples](../../specs/contracts/calendar-fixtures.json). All are offline artifact checks; application acceptance remains pending.

## Current runtime increment — 20 October 2026

[Authorized lookup slice](implementation/lookup-slice.md) implements a bounded DEV-01/02/03 path with QA-01/OPS-01 evidence. [Execution record](implementation/lookup-evidence.md) supersedes earlier blanket runtime-not-executed wording for this slice only. DEV-02/03 read work is pulled forward from S03; remaining stories, estimates and later workflow scope are retained. Parent stories/Sprints remain in progress.
