# DEV-13 acceptance record

BANK-SDD-v0.2

Implementation: delivered for PR review. Runtime tests: see [current evidence](runtime-contract.md). Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-13-AC01 | DEV-13-T01 | retain original investigation due time and specialist ownership; notify the responsible lead and create feedback-queue progress work; only a lead-confirmed specialist proposal can establish the next update time, without replacing overdue history | Pending implementation | Not executed |
| DEV-13-AC02 | DEV-13-T02 | produce one escalation per case, deadline and escalation level | Pending implementation | Not executed |
| DEV-13-AC03 | DEV-13-T03 | label the reason unknown; do not invent merchant or bank explanations or promise an unapproved date | Pending implementation | Not executed |
| DEV-13-AC04 | DEV-13-T04 | invalidate the outdated escalation and continue with the current result | Pending implementation | Not executed |
| DEV-13-AC05 | DEV-13-T05 | link the new work to the original case and preserve old findings/versions | Pending implementation | Not executed |
| DEV-13-AC06 | DEV-13-T06 | create independently tracked complaint intake linked to the original case and objection, without waiting for specialist re-review; preserve distinct owners/statuses and do not duplicate intake on replay | Pending implementation | Not executed |
| DEV-13-AC07 | DEV-13-T07 | preserve the disagreement and route specialist re-review even without new evidence; clarification may accompany it; no coercion, financial action or automatic resolved closure | Pending implementation | Not executed |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.

## Current delivery

[Runtime behavior and executed checks](runtime-contract.md) supersede historical implementation-pending wording. Agent drafting and owner UAT remain separate gates.
