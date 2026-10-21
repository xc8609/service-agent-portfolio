# DEV-03 acceptance record

BANK-SDD-v0.2

Implementation: bounded read slice in PR #1. Selected runtime tests executed; see current evidence below. Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-03-AC01 | DEV-03-T01 | show statuses and uncertainty; do not infer a duplicate or a shared purchase | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-03-AC02 | DEV-03-T02 | cite both states without promising automatic reversal or a refund | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-03-AC03 | DEV-03-T03 | require clarification or explicit selection before a case-specific proposal | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (read slice) |
| DEV-03-AC04 | DEV-03-T04 | retain the original statement and mark affected advice stale; offer the reviewed manual risk path | Pending implementation | Not executed |
| DEV-03-AC05 | DEV-03-T05 | show unavailable rather than no transactions; permit manual continuation | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (slice) |
| DEV-03-AC06 | DEV-03-T06 | show its actual reference/status and do not silently create a duplicate | Pending implementation | Not executed |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
