# DEV-02 acceptance record

BANK-SDD-v0.2

Implementation: bounded read slice in PR #1. Selected runtime tests executed; see current evidence below. Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-02-AC01 | DEV-02-T01 | return only the permitted card/account context with source timestamp and version | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (inbound) |
| DEV-02-AC02 | DEV-02-T02 | deny without returning private fields and offer the verification route | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (inbound) |
| DEV-02-AC03 | DEV-02-T03 | derive scope from the session and disclose no out-of-scope existence or details | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (inbound) |
| DEV-02-AC04 | DEV-02-T04 | reject the action; read access does not grant financial authority | [Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md) (30 API/PostgreSQL tests, 3 browser journeys; CI linked) | Passed (endpoint absent) |
| DEV-02-AC05 | DEV-02-T05 | reject with AUTH_REQUIRED and preserve the editable draft | Pending implementation | Not executed |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.

## QA-03 lookup follow-up — 22 October 2026

[LG-01–04 acceptance and regression map](../DEV-08/lookup-gap-follow-up.md) addresses the observed
transaction display and customer-context gaps. Historical results above remain unchanged;
owner acceptance and human effort measurement remain pending.
