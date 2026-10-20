# DEV-04 — Explain the recorded status and next step of an existing case

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S03 | Release: B0 | Estimate: Dev 2, BA 0.25, QA 0.5 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-04-AC01 | DEV-04-T01 | show recorded request, owner, source time and original due date without inventing progress | Pending implementation | Not executed |
| DEV-04-AC02 | DEV-04-T02 | show next update unknown and completion date unknown separately; pending commitment is not displayed as approved | Pending implementation | Not executed |
| DEV-04-AC03 | DEV-04-T03 | use stable aggregate sequence and show both timestamps; do not overwrite prior finding with late ingestion | Pending implementation | Not executed |
| DEV-04-AC04 | DEV-04-T04 | deny with uniform FORBIDDEN_OR_NOT_FOUND; no existence disclosure and no retained stale detail | Pending implementation | Not executed |
| DEV-04-AC05 | DEV-04-T05 | show separate owners/statuses and original case link; completion of one does not mark the other resolved | Pending implementation | Not executed |
| DEV-04-AC06 | DEV-04-T06 | show unavailable/conflict rather than no case or closed; retain last-view freshness label and disable unsafe commit | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.
