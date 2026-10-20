# DEV-10 — Build operational event marts and a reconciled Tableau view

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S05A | Release: B1 | Estimate: Dev 3, BA 1, QA 0.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-10-AC01 | DEV-10-T01 | deduplicate by authoritative IDs; exported totals equal fixture oracle and SQL source totals | Pending implementation | Not executed |
| DEV-10-AC02 | DEV-10-T02 | include all started runs in outcome denominator; show unresolved and missing latency explicitly | Pending implementation | Not executed |
| DEV-10-AC03 | DEV-10-T03 | count a proposal once by defined revision/status rule; distinguish accepted unchanged from edited; exclude pending from decided-only denominator and display pending count | Pending implementation | Not executed |
| DEV-10-AC04 | DEV-10-T04 | report lifetime calls, per-plan calls, technical faults and original-window misses separately; no apparent improvement from erased history | Pending implementation | Not executed |
| DEV-10-AC05 | DEV-10-T05 | no measured savings/ROI shown; missing cost remains unavailable; synthetic status visible | Pending implementation | Not executed |
| DEV-10-AC06 | DEV-10-T06 | stable snapshot totals reconcile; late-event adjustment and data cutoff are recorded | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.
