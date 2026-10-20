# DEV-11 trusted specialist and feedback workflow

20 October 2026. All staff, identity proofs, findings and calls are synthetic.
No external bank, telephone or financial execution integration is enabled.

## Authority and state

The operations desk creates a separate demo staff session. Server-side queue
membership limits queue summaries to alias, concern category, work status and age/
deadline metadata. Every detail read and command checks active membership and the
current assignee. Claim uses expected work version; competing claimants cannot
both acquire the task. Reassignment immediately revokes prior detail access.
The original inbound representative need not be the feedback representative.

`accept_specialist_work`, `claim_feedback_task`, `record_specialist_result` and
`record_callback_attempt` use the canonical trusted-command contracts. Additional
human workspace schemas are in `workflow.py::SCHEMAS`; none are model tools.
`workflow.py` owns scope, safe DTOs and dispatch; `workflow_commands.py` owns trusted
transitions; `callbacks.py` owns actual-outcome recording. Migration 008 adds callback
context/review/outcome linkage and append-only material/contact follow-up records.

Publishing a result stores a versioned finding and approved customer explanation.
Private notes are inserted into a separate table: runtime SELECT is still denied,
and the feedback DTO never selects them. Specialist submissions cannot invent a
completed financial action or change an existing action's status/receipt. A new
synthetic action may only be pending. An approved narrative is not proof that
money moved. Phrase checks are conservative review aids, not semantic certification.

One shared feedback work item is created/activated per case with its initial plan.
First-callback target is eight service hours after the result; later result revisions
preserve that original target. A revised result after completed feedback enters lead
review, not a new automatic call quota. Publishing finding, feedback work/plan,
receipt, timeline, audit and outbox is atomic; retries return the stored receipt.

## Staff preparation versus customer disclosure

Claimed staff can prepare from case-relevant transactions, approved findings,
pending actions and attributed intake/follow-up. Opening a synthetic callback creates
a new contact and unverified assertion; inbound verification is never reused.
A staff review draft binds the current result version and callback contact. Approval
rechecks that result; edits create another reviewed draft. No disclosure endpoint
returns the explanation until the current callback has a fresh trusted proof and
an approved current review. Identity failure/expiry or result changes reject it.

`/v1/demo/callback-verification` is explicitly a local synthetic identity adapter,
not an ordinary model tool or production verification service. It can only change
an assertion attached to the caller's assigned callback work. Production identity
integration remains a release gate; do not expose the demo publicly.

Actual outcomes distinguish never-placed faults, no answer, failed verification,
declined contact and verified delivered feedback. A never-placed fault consumes no
attempt, does not start the three-day window and does not reset the original target.
A placed attempt starts the accepted calendar window; verified completion requires
current proof and approved current content. One callback contact has at most one
recorded actual attempt. Completion of feedback does not close the case.

## Accepted intake continuation

Specialists can request material through owned customer-service work. Responses are
append-only with actor/time and evidence references; earlier statements/intake and
original due times remain unchanged. Material unavailable/declined stays outstanding.
A contact-gap task can be resolved only by its assigned customer-service employee
with an existing active customer-scoped method reference and recorded explanation.
This does not modify the customer master. Results may arrive while the gap remains;
feedback stays owned/outstanding and callback opening is blocked until resolution.
No new automatic supplementation call quota is introduced; such contact is an owned
manual continuation under D-26, pending the dedicated plan controls.

## Verification and remaining work

141 PostgreSQL 16.2 API/integration tests and 31 Chromium browser tests passed locally.
The browser workflow creates its own synthetic enquiry so repeated testing does not
change the original read-only progress fixture. One earlier full browser run failed
because a manual walkthrough had changed that fixture; a fresh disposable database
and independent workflow case passed the complete suite. No shared data was reset.

API tests cover all six DEV-11 acceptance outcomes at the manual service boundary,
claim concurrency, result replay, outbox failure rollback, proof expiry, reassignment,
pending financial actions, material history and contact-gap/result independence.
The DTO exclusion supports later Agent input; actual Agent drafting is DEV-08.
DEV-12 adds scheduling/lead continuation/closure; DEV-13 adds timers and objections.
Owner UAT, staging recovery and real identity/telephony remain separate gates.
