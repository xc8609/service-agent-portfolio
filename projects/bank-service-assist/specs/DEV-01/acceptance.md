# DEV-01 — Create the application skeleton and deterministic demo environment

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0 | Estimate: Dev 3, BA 0.25, QA 0.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-01-AC01 | DEV-01-T01 | second run changes no fixture IDs or counts; API and UI display labelled synthetic scenario and schema version | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-01-AC02 | DEV-01-T02 | manual path remains usable; agent availability is explicitly disabled | Pending implementation | Not executed |
| DEV-01-AC03 | DEV-01-T03 | process liveness is separate from dependency readiness; readiness is non-success with sanitized correlation ID | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-01-AC04 | DEV-01-T04 | refuse without deleting records; reset requires matching environment guard and explicit demo target | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-01-AC05 | DEV-01-T05 | legacy suite remains independently runnable; app lock and setup record supported versions | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
