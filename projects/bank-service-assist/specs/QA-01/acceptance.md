# QA-01 — Implement layered verification and requirement-to-test coverage

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 1.5, BA 0.5, QA 1.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| QA-01-AC01 | QA-01-T01 | each maps to planned layer, fixture, independent oracle and release gate; missing mapping fails validation | Pending implementation | Not executed |
| QA-01-AC02 | QA-01-T02 | access is denied at API/service boundary; no secret/internal detail in response or trace | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Partial: read boundary |
| QA-01-AC03 | QA-01-T03 | one effect/receipt, preserved audit, recoverable pending work; report actual database version | Pending implementation | Not executed |
| QA-01-AC04 | QA-01-T04 | test fails for the expected business reason; remove mutation after demonstration | Pending implementation | Not executed |
| QA-01-AC05 | QA-01-T05 | affected suites explicitly skipped with reason; schema checks never relabelled runtime/UAT pass | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (scope report) |
| QA-01-AC06 | QA-01-T06 | block promotion regardless of average score or total passing-test count | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
