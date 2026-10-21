# DEV-10 — Build operational event marts and a reconciled Tableau view

BANK-S02-v0.4 baseline · Offline implementation under review; see [current evidence](runtime-contract.md).
Forecast: S05A | Release: B1 | Estimate: Dev 3, BA 1, QA 0.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-10-AC01 | DEV-10-T01 | deduplicate by authoritative IDs; exported totals equal fixture oracle and SQL source totals | Source/CSV oracle and replay tests | Automated pass |
| DEV-10-AC02 | DEV-10-T02 | include all started runs in outcome denominator; show unresolved and missing latency explicitly | Five run states and missing usage/latency test | Automated pass |
| DEV-10-AC03 | DEV-10-T03 | count a proposal once by defined revision/status rule; distinguish accepted unchanged from edited; exclude pending from decided-only denominator and display pending count | Multiple edits, unchanged/pending and decided denominator test | Automated pass |
| DEV-10-AC04 | DEV-10-T04 | report lifetime calls, per-plan calls, technical faults and original-window misses separately; no apparent improvement from erased history | API continuation journey and never-dialed fault test | Automated pass |
| DEV-10-AC05 | DEV-10-T05 | no measured savings/ROI shown; missing cost remains unavailable; synthetic status visible | Unavailable values and XML checks pass; Desktop blocked by lock | Partial: visual review pending |
| DEV-10-AC06 | DEV-10-T06 | stable snapshot totals reconcile; late-event adjustment and data cutoff are recorded | Stable CSV hash and late-correction fingerprint tests pass; Desktop refresh pending | Partial |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.
