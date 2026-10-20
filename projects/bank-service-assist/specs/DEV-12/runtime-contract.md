# DEV-12 runtime delivery — 20 October 2026

Implemented on top of DEV-11. Synthetic service calendar `demo-calendar-v1`,
America/Winnipeg with pinned tzdata 2025.2, Mon–Fri 09:00–17:00 and explicitly
configured synthetic holiday 2026-10-12. This is not a statutory bank calendar.

- `reserve_callback`: owned work, current version, explicit current plan; one
  reserved/actually-counted date per case; future permitted slot and plan quota.
- `record_callback_attempt`: preserves actual outcomes, including accidental
  duplicates/out-of-window calls as anomalies requiring lead review. Never-placed
  faults do not consume quota, start a window or extend the original due time.
- `evaluate_contact_window`: trusted staff boundary; expiry/exhaustion enters lead
  review without closing. DEV-13 adds scheduled evaluation. Third service date
  ends at 17:00; original first-contact due applies before first placed call.
- `decide_contact_continuation`: responsible queue lead only. A reasoned hold
  requires an eligible owner and future review date. A new plan requires explicit
  dates, permitted distinct slots, quota and feedback owner; preserves predecessor
  plan, attempts, original due time and approval history. UI offers one explicitly
  approved additional contact; API accepts bounded explicitly supplied slots.
- `close_case`: assigned feedback representative, current case/work versions,
  latest specialist result with verified feedback, all required actions completed
  with receipts, no outstanding work. Atomic closure record, audit, outbox and
  replay receipt. No financial execution endpoint exists.

Case/work/plan mutations use repeatable-read conflict detection; reservation
uniqueness prevents concurrent duplicate plans. Preparation of a callback context
is not an actual dial; actual out-of-hours activity remains auditable.

## Verification and acceptance mapping

PostgreSQL 16.2: 146 API tests passed. Chromium: 31 browser regressions passed.
Ruff and TypeScript/Vite build passed. `test_continuation.py` covers AC01–07:
weekend/holiday/DST boundaries, three daily attempts, expiry below quota, duplicate
reservation and actual duplicate preservation, reasoned hold/new-plan authorization,
original history and negative/positive closure. Existing workflow tests cover faults,
failed/expired verification and current-result approval. No owner UAT, production
calendar certification, real outbound call or live-model evaluation is claimed.
