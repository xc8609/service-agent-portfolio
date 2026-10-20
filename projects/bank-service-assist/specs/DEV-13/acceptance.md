# DEV-13 acceptance record

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-SDD-v0.2

Implementation: delivered for PR review. Runtime tests: see [current evidence](runtime-contract.md). Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-13-AC01 | DEV-13-T01 | retain original investigation due time and specialist ownership; notify the responsible lead and create feedback-queue progress work; only a lead-confirmed specialist proposal can establish the next update time, without replacing overdue history | test_exceptions: overdue history and specialist/lead responsibility | Automated pass |
| DEV-13-AC02 | DEV-13-T02 | produce one escalation per case, deadline and escalation level | test_exceptions: repeated worker tick creates one due event | Automated pass |
| DEV-13-AC03 | DEV-13-T03 | label the reason unknown; do not invent merchant or bank explanations or promise an unapproved date | test_exceptions: verified unknown-progress disclosure | Automated pass |
| DEV-13-AC04 | DEV-13-T04 | invalidate the outdated escalation and continue with the current result | Stale commitment rejection passed; obsolete progress-task cleanup being corrected | Partial: integration fix pending |
| DEV-13-AC05 | DEV-13-T05 | link the new work to the original case and preserve old findings/versions | test_exceptions: same-customer new evidence retains findings | Automated pass |
| DEV-13-AC06 | DEV-13-T06 | create independently tracked complaint intake linked to the original case and objection, without waiting for specialist re-review; preserve distinct owners/statuses and do not duplicate intake on replay | test_exceptions: explicit parallel complaint and idempotent receipt | Automated pass |
| DEV-13-AC07 | DEV-13-T07 | preserve the disagreement and route specialist re-review even without new evidence; clarification may accompany it; no coercion, financial action or automatic resolved closure | test_exceptions: objection without evidence preserves open case | Automated pass |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current delivery

[Runtime behavior and executed checks](runtime-contract.md) supersede historical implementation-pending wording. Agent drafting and owner UAT remain separate gates.
