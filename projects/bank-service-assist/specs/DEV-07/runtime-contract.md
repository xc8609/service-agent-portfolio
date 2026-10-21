# DEV-07 runtime contract — v0.5 intake extension

20 October 2026. Simulated procedure; no bank approval or actual savings claimed.
This supersedes the v0.4 missing-intake design gate for initial enquiry submission.
Supplementation and contact resolution after intake integrate with DEV-11–13.

## Review and authority

`prepare_referral` is a human workspace read that rechecks the selected two posted
transactions, current saved customer report, all related-case heads and applicable
policy editions. Customer recognition must be specific-entry or one-purchase
unresolved; a denied-both report requires a separately reviewed risk path. Records
must share an authorized account. No text can grant scope or financial authority.

Canonical `create_proposal(kind=referral)` and `edit_proposal` now require typed
`intake`. The v0.5 JSON Schema and OpenAPI are changed together. Drafts remain
side-effect-free. `approve_and_commit_proposal` revalidates the exact draft and
requires explicit customer-summary confirmation, independent of staff approval.
No new model tool can submit a case.

| Intake field | Meaning / guard |
|---|---|
| statement_revision, recognition, recognized_transaction_id | Must match the latest persisted report and pair versions; unresolved means no chosen entry |
| clarifications | purchase_date/count/amount/prior_contact each distinguish answered, unknown, declined and not_asked; only answered carries a value |
| material_gaps | Item, unavailable/not_requested/declined, specialist owner, assess_need action and specialist_acceptance review trigger; no invented attachment/request |
| contact | available requires an active authorized method reference/version; unavailable/unknown require an explicit reason and no new phone number |
| mode, related_case_id, distinct_work_reason | Link matching active investigation, or justify distinct new work; failed lookup never becomes absence |
| customer_summary_confirmed | Required before commit, not a consent to refund |
| route_version, route_basis | Server-configured destination and feedback queue/lead; applicable_policy or explicit manual_policy_review for missing/conflicting rules |

## Persistence and consistency

Migration 007 adds `service_routes` (configured specialist/feedback queues and lead),
`customer_contact_methods` (synthetic masked reference only), `referral_pair_guards`
(serialization per customer/pair), `referral_intakes` (immutable reviewed payload,
source refs, actor/time, proposal, case/work and operation links), and
`work_items.acceptance_due_at`. Runtime may read configuration, not change it.
Runtime inserts intake/case/work/timeline/outbox records; it cannot execute ledger
operations. The reference v0.4 model remains the baseline; this migration and this
addendum specify the initial-intake additions. They do not claim all reference
entities are implemented.

A new enquiry creates a case and queued specialist work, acceptance due after eight
service hours and investigation due after sixteen. Service hours use the pinned
synthetic calendar (tzdata 2025.2, weekdays 09:00–17:00 America/Winnipeg). Existing
work is linked without recreating it or changing its due time. Contact gaps create
owned customer-service work with the same original investigation deadline. Later
follow-up must not reset it. Referral, receipt, audit and outbox commit atomically;
the intake operation FK is deferred to transaction end. An aggregate guard makes
competing operations serialize rather than both passing a stale duplicate check.

The receipt's domain_ref is the case. `get_referrals` returns scoped intake history,
actual work ID, queue, disposition and original due time. “Queued” does not mean
accepted. A note-only path remains available. Current outbox events are durable
local facts; no external notification delivery is implied.

## Recovery and remaining integration

Retry the exact uncertain request/key. Changed input under the same key conflicts.
Refresh a stale intake from current evidence and review again. UI retains failed
content and tells the operator that fresh preparation replaces the form. Source
outage or missing routing configuration blocks submission without partial records.

Missing materials are accepted and persisted. Specialist requests/received evidence,
contact-resolution completion, undelivered-feedback handling and overdue escalation
are dependent DEV-11–13 behavior, not silently marked complete by this intake PR.
No upload service, customer-master modification, financial action or actual call
exists in this increment. Owner UAT remains required.
