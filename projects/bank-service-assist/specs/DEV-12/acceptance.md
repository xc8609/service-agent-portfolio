# DEV-12 acceptance record

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-SDD-v0.2

Implementation: delivered for PR review. Runtime tests: see [current delivery evidence](runtime-contract.md). Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-12-AC01 | DEV-12-T01 | keep awaiting-feedback state and ownership; schedule only within the accepted contact window; under D-18, a placed unanswered call counts once, while a never-placed technical failure is logged without consuming quota or extending any original deadline | test_workflow + test_continuation: no-answer/fault/history guards | Automated pass; manual calls |
| DEV-12-AC02 | DEV-12-T02 | reject the extra attempt plan for that date; actual duplicate call records remain auditable | test_continuation: reservation uniqueness and actual duplicate audit | Automated pass |
| DEV-12-AC03 | DEV-12-T03 | enter unable-to-contact lead review with no resolved closure; a responsible lead may then approve a reasoned new contact plan or a hold with owner and review date, retaining original attempts/deadlines/approvals | test_continuation: expiry, owned hold and distinct approved plan | Automated pass |
| DEV-12-AC04 | DEV-12-T04 | count Friday as day 1, skip the weekend and configured Monday holiday, and end Wednesday at 17:00 America/Winnipeg; enter lead review at expiry even below three attempts, never automatic closure | test_continuation: holiday/DST calendar and expiry | Automated pass |
| DEV-12-AC05 | DEV-12-T05 | persist a closed disposition with references and audit evidence | test_continuation: current verified result and closure receipt | Automated pass |
| DEV-12-AC06 | DEV-12-T06 | deny closure with the unmet conditions | test_continuation: pending work/action closure rejection | Automated pass |
| DEV-12-AC07 | DEV-12-T07 | reject an agent-only fourth attempt, expired-plan contact or automatic closure; allow further contact only under a distinct current lead-approved plan, preserving all history | test_continuation + Agent allowlist: explicit lead plan required | Automated pass |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current delivery

See [runtime contract and executed checks](runtime-contract.md). Historical planned-test wording above is retained for traceability; owner UAT remains pending.
