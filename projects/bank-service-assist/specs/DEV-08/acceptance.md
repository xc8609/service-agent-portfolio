# DEV-08 acceptance record

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

[Merchant descriptor change and MD-01–05 acceptance](merchant-evidence.md) extend
AC01/03/05 with the owner-approved minimum read-only field; execution evidence is
recorded separately from semantic model qualification.

BANK-SDD-v0.2

Offline implementation delivered; current runtime evidence is linked below. Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-08-AC01 | DEV-08-T01 | execute dependent scoped tools and return fact/policy citations, missing facts and a typed next-step proposal | test_agent: draft-only scoped tool sequence | Offline pass; live quality deferred |
| DEV-08-AC02 | DEV-08-T02 | load committed latest state rather than relying on chat history or a live multi-day run | test_agent: replay/restart and current feedback state | Offline pass |
| DEV-08-AC03 | DEV-08-T03 | reject stale evidence and request refreshed review | test_agent + test_notes: stale sources reject reuse/approval | Automated pass |
| DEV-08-AC04 | DEV-08-T04 | honour budgets, return a typed failure and preserve manual access and all committed work | test_agent: typed failure, step/time budgets, cancellation | Offline pass |
| DEV-08-AC05 | DEV-08-T05 | reject it in the allowlist/backend and record a sanitized denial | test_agent: forbidden tool/arguments and invented references | Offline pass; live prompt evaluation deferred |
| DEV-08-AC06 | DEV-08-T06 | deduplicate effects and reconcile operations before retrying writes | test_agent: allowlisted business event replay | Offline pass; unsupervised dispatch not enabled |
| DEV-08-AC07 | DEV-08-T07 | report correct completion, active checking time, corrections and known cost; no invented savings | DEV-10 instrumentation only; no participant timing study | Not executed: human evaluation pending |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current offline delivery

See [implemented runtime, executed tests and remaining gates](runtime-contract.md). Historical live-provider/streaming/effort-study acceptance is not marked complete.

## Core context increment — 22 October

[Staff question and scoped transaction context](core-context.md) defines CC-01–09,
implementation boundaries and actual verification evidence for the simplified portfolio.

CC-07–09: 15 added API cases and browser AG-02 passed in the final 262-API/43-browser
suite. The [subscription exercise](../../evaluation/r2/subscription-results-20261022.md)
records the separate 12 answer simulations and AI review; owner UAT remains pending.
