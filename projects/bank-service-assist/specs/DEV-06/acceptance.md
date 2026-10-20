# DEV-06 — Review, edit and commit a contact note safely

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S04 | Release: B0 | Estimate: Dev 5, BA 0.5, QA 1 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-06-AC01 | DEV-06-T01 | save exactly reviewed content, labelled allegations, actor/time, source versions and durable receipt | Pending implementation | Not executed |
| DEV-06-AC02 | DEV-06-T02 | reject stale/unauthorized commit; preserve user edits for deliberate rebase, never silently overwrite | Pending implementation | Not executed |
| DEV-06-AC03 | DEV-06-T03 | one version advances, second conflicts; revision history remains auditable | Pending implementation | Not executed |
| DEV-06-AC04 | DEV-06-T04 | return same committed note and receipt; no duplicate note/outbox event | Pending implementation | Not executed |
| DEV-06-AC05 | DEV-06-T05 | IDEMPOTENCY_CONFLICT with original content untouched | Pending implementation | Not executed |
| DEV-06-AC06 | DEV-06-T06 | flag unsupported action claim; statement may only be stored as attributed customer allegation, not confirmed execution | Pending implementation | Not executed |
| DEV-06-AC07 | DEV-06-T07 | deny; create_proposal remains draft-only; server authority does not come from body fields | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.
