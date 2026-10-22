# Core-flow clarity — DEV-08 / DEV-12

22 October 2026. Small owner-requested follow-up to the PR #25 walkthrough.
All records and business procedures are synthetic. No new workflow state, service,
model API, financial operation or automatic closure is introduced.

## Problem and behaviour

A representative who has delivered an approved result needs to see what remains
before closing the enquiry. Previously the UI still said “awaiting feedback” and
an attempted closure returned a generic evidence-conflict message. The Agent
also mixed facts, uncertainty and instructions in one paragraph.

- **DEV-12:** assigned feedback staff see the outstanding closure requirements
  and follow-up queue. Verified delivery, the latest result, required-action
  receipts and other work are checked by the same backend function on read and
  on the trusted closure command. The UI disables known-blocked closure; the
  server remains authoritative. Missing business prerequisites return
  `CLOSURE_BLOCKED`; stale versions still return `CONFLICT`.
- **DEV-04/12:** when stored case status is `awaiting_feedback` but the feedback
  work is completed, display “Feedback delivered · case remains open”. Do not
  override `under_review` or `closed`, or infer resolution. The persisted case
  state and history are unchanged.
- **DEV-08:** the offline draft and provider instruction use **Facts → To confirm
  → Next step**. Customer recognition is attributed to the saved report; similar
  entries do not establish a duplicate. Existing work is preferred to another
  enquiry, missing rules require review, and verified delivery prompts a closure
  checklist review rather than another callback. Approved customer wording is
  preserved verbatim inside the staff draft. Citations/review checks are expandable.

## Acceptance and regression evidence

| ID | Expected behaviour | Automated coverage |
|---|---|---|
| CF-01 | Show required-action and open-work blockers with the follow-up role/queue; keep the case open | `test_closure_denies_pending_work_then_requires_current_verified_result`, WF-06 |
| CF-02 | A completed label cannot replace a latest-result feedback receipt or an external action receipt | `test_completed_labels_cannot_hide_missing_closure_evidence` (two cases) |
| CF-03 | Unauthorized details remain denied; stale closure submissions remain conflicts | CF-02 permission assertion; `test_closure_still_distinguishes_stale_versions_from_business_blockers` |
| CF-04 | Delivery displays an open case, then authorized receipt recording permits explicit closure; closed label wins | WF-06; Agent completed-feedback regression |
| CF-05 | Separate facts, uncertainty and next step; preserve citations, draft editing, current-scope and recognition checks | `test_agent`, `test_agent_portfolio`, AG-01/02 |

Implementation stays in `bank_api/continuation.py`, existing workflow detail,
the small UI status formatter and bounded Agent fixture. The Agent's string
summary contract remains compatible with saved note drafts and existing replays.
This presentation format is not a model qualification or a new safety evaluator.

Execution evidence is recorded in the PR and the [delegated retest](../../../../docs/uat/2026-10-22-core-clarity.md).
Owner acceptance, human benefit measurement and live-model qualification remain separate.
