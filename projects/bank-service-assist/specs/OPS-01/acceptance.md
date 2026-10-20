# OPS-01 — Package the application and establish CI release artifacts

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 2, BA 0, QA 0.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| OPS-01-AC01 | OPS-01-T01 | record commit/config/image digests; no unpinned latest dependency in release artifact | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Partial: API/UI images |
| OPS-01-AC02 | OPS-01-T02 | no release-candidate promotion; retain failure evidence | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Configured; failure injection pending |
| OPS-01-AC03 | OPS-01-T03 | manual UI/API operate; database is not publicly exposed; readiness waits for schema/dependencies | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (manual slice) |
| OPS-01-AC04 | OPS-01-T04 | no provider key, private customer material or raw datasets; env example contains placeholders only | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Checked (local/CI demo) |
| OPS-01-AC05 | OPS-01-T05 | state cloud CI not executed; never mark cloud build success | Pending implementation | Not executed |
| OPS-01-AC06 | OPS-01-T06 | stop promotion, preserve data and pending work; restore/forward-fix plan tested in isolated staging before release | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
