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
