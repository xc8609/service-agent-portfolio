# DEV-13 runtime delivery — 20 October 2026

The trusted specialist proposes a future update and the responsible queue lead
approves/rejects it. Current case/work/commitment versions and ongoing investigation
are rechecked. A later finding invalidates approval of an obsolete proposal.
Original investigation deadline, assignee and previous commitments remain intact.

`python -m bank_api.worker --once` evaluates current persisted deadlines and then
atomically delivers pending outbox events to the local notification store. The
Compose worker repeats every 30 seconds. One due transition per work/deadline/kind;
replay does not duplicate progress work. Delivery means **local notification only**,
not external email, a phone call or complaint-system acknowledgement. Application
identity cannot call a scheduler endpoint. Run with restricted bank_app credentials.

An overdue specialist investigation creates separately owned feedback progress work.
Claim it, open a synthetic progress contact, verify current identity, review the
approved commitment (or explicit unknown/no approved date), and record delivery.
This manual progress path does not consume/reset the final-result call quota.
Unsuccessful supplementation/progress continuation remains owned manual work under
D-26; no new automatic call allowance is invented.

A verified callback can capture verbatim objection and optional current evidence.
Same-customer additional transactions may be linked; foreign-customer data is denied.
Re-review starts even without new evidence. An explicit complaint request atomically
creates a separate complaint-intake work item and recorded intake, with no invented
external acknowledgement. Original findings are immutable. Closure remains blocked
by outstanding linked work. New findings after completed feedback require lead
continuation of the retained plan rather than resetting quota.

## Evidence

152 PostgreSQL 16.2 API tests; 31 Chromium tests including objection plus parallel
complaint in the end-to-end staff journey. Ruff and TypeScript/Vite build passed.
`test_exceptions.py` maps AC01/02 to duplicate timer delivery and original ownership;
AC03 to unknown-reason progress; AC04 to stale commitment; AC05–07 to new evidence,
foreign-customer rejection, no-evidence disagreement and parallel idempotent complaint.
DEV-08 adds model drafting; no live model, business benefit, bank integration or owner
UAT acceptance is claimed. External complaint adjudication remains outside scope.

## Integration correction: result supersedes interim progress work

DEV-13-AC04: Publishing a specialist finding atomically cancels only unfinished
progress_callback children of that investigation and advances their versions. It
supersedes pending/approved update commitments, preserving existing approval fields;
a pending proposal records supersession by the publishing specialist, not lead approval.
Original due events, deadlines, completed contacts and historical result versions remain.
The existing final-feedback task is created/reused. An already-open interim contact
can no longer disclose or record outdated progress, and cancelled work cannot block
normal closure. Replayed publication does not repeat this transition.

Regression evidence: test_result_supersedes_open_progress_contact_without_erasing_overdue_history
and the extended pending-commitment test in test_exceptions.py. Full local verification: 181 PostgreSQL API tests and 32 Chromium tests passed; no new external integration or business rule is introduced.

## Review follow-up: one escalation per deadline and post-closure objections

Independent review (20 October 2026) found two gaps, now corrected:

- The progress task created by an overdue investigation inherited the missed deadline,
  so the next worker tick escalated the same case/deadline again. It now has its own
  one-service-day target; `test_overdue_deduplicates_and_keeps_original_owner_and_deadline`
  asserts one due event and one `work.overdue` timeline entry per case.
- ST-13 allows `closed → under_review`, but objections could only be captured inside an
  open callback. `capture_customer_objection` now also accepts a verified **inbound**
  contact (same customer, card scope and timeline checks as the case read) when a
  finding has been published. A closed case reopens with a `case_reopenings` record;
  the original closure row is retained and a later closure must cite a newer result
  (migration `012_objection_reopen.sql`, forward-only). The callback path now also
  checks that the payload case matches the callback's case.

## Complaint delivery and external action receipts (ST-22/23)

The worker moves `recorded` or `delivery_failed` complaint intakes to
`pending_delivery` and writes a local outbox event; no external system is called.
A complaint coordinator records the complaint unit's answer through the synthetic
`/v1/demo/complaint-receipt` adapter: an acknowledgement with a `SYN-` reference
completes the intake task (the complaint continues under that reference, independent
of contact closure, FR-11); a failure keeps the request for the next delivery attempt.
Acknowledgement is impossible before delivery is requested, and never inferred.

Required financial actions stay outside this application. The case specialist can
record a synthetic external system receipt (`/v1/demo/action-receipt`); only then does
closure accept the action as completed. Nothing is executed here.
Evidence: `test_complaint_delivery_is_requested_by_worker_and_acknowledged_by_receipt`,
`test_external_action_receipt_completes_required_action_and_unblocks_closure`.

