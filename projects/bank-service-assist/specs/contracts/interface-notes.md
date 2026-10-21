# S02 interface contract v0.4

BANK-S02-v0.4 · Specification candidate, not deployed APIs. [Tool registry](agent-tools.json), [OpenAPI](openapi.json), [permissions](permissions.md), [data](data-model.md) and [state transitions](state-transitions.md) form one review set.

## Transport and authority

Ten model tools use `/v1/agent-tools/{name}`; twelve trusted commands use `/v1/commands/{name}`. Never bind commands into the model registry. POST inputs use strict JSON Schemas; unknown fields and roles supplied in request bodies are rejected. Services derive authenticated actor, queue membership, assignment and customer scope. A model call cannot approve, claim work, record an actual call or execute funds.

A staff-authenticated queue list is required for DEV-02/11: proposed `GET /v1/feedback-work` returns masked alias/card last4, concern category, work ID, status, age and due time. Bound pagination and queue scope server-side; omit merchant, amount, phone and finding. Detailed preparation follows atomic claim. The queue UI route is a presentation adapter, not a model search capability.

## Read and write sequence

Authenticate/authorize → look up actor+command+operation key → compare normalized request hash → return authorized prior receipt for identical replay, or conflict for changed payload. For a new operation, validate payload, scope, source/record versions and state/calendar guards → commit domain/audit/outbox/receipt atomically. The effect transaction must enforce key uniqueness and row/version locks. An old expected version must not break a legitimate identical replay after a committed effect; authorization is still rechecked. Query operation status after uncertain delivery.

Errors: AUTH_REQUIRED; uniform FORBIDDEN_OR_NOT_FOUND; VALIDATION_ERROR (schema or semantic, safe field/reason only); STALE_VERSION; IDEMPOTENCY_CONFLICT; OUTCOME_UNKNOWN. No tokens, phone numbers or internal notes in errors/traces. Every current-case proposal approval requires non-null case/work versions where applicable. New notes without a case are scoped to the active contact and its context version.

## D-17–D-22 behavior

- Staff preparation requires current assignment; customer disclosure requires current-contact verification. Never reuse old inbound verification for a callback.
- Not-placed technical faults are audited without consuming contact quota or extending deadlines. Placed unanswered calls count. Unknown/contradictory evidence requires reconciliation rather than assumed failure.
- Initial contact plan starts its three-service-date window on first actual placed call; third eligible date ends at 17:00 America/Winnipeg. Original first-callback target exists before that call. Scheduler handles expiry even below three attempts.
- The original specialist retains overdue investigation; responsible lead confirms a specialist-proposed next-update time. Update is not completion promise; original due history remains. Agent may draft a progress update without a completed finding using approved customer-safe facts only.
- Objection capture persists exact words and creates durable specialist re-review work. Explicit complaint requests also create independent internal intake and queue work atomically; delivery acknowledgement is separate and requires a trusted adapter receipt. Both tracks link to the original case.
- Only `decide_contact_continuation` authorizes an exceptional bounded new plan or owned/date-bound hold. Ordinary retry proposal approval cannot bypass exhausted limits. Historical attempts remain linked to their plan and lifetime totals. At most one actual placed call per case/service date still applies across plans.

## Note editing and receipts

`create_proposal(kind=note)` is draft only; manual and agent drafts use the same schema. `edit_proposal` is staff-only and changes no kind/customer/case/contact linkage. Preserve revisions in audit, including edits that become stale. `approve_and_commit_proposal` saves exactly the reviewed note version in contact_notes plus audit/outbox/receipt. Distinguish reported allegations from facts; never treat text as proof that an operational action occurred.

## Async, denial and recovery

Timers and source events persist durable work before any model run. Claims/approvals and result changes invalidate stale scope and proposals. Workers refresh current permissions/state, use leases and deduplicate events; restart preserves unfinished work. Long waits are persisted state, not open model sessions. Denied reads reveal no cross-customer existence; disconnected upstreams are not empty results. Manual services operate without an LLM key.

## Limits and release gates

Proposed engineering limits remain 8 tool calls, 4 model turns, 10 seconds per read and 60 seconds per run; validate in the provider spike before B1. The proposed 15% business lookup improvement is a review hypothesis, not an accepted result or requirement already met. Readiness depends on reviewed fixtures/configuration and runtime evidence at the appropriate stage. Contract schema checks do not test PostgreSQL, actual permissions, live providers, UI, UAT or deployment.

## Accepted intake extension pending contract revision

D-23–D-25 are accepted simulated business rules: paired unresolved recognition,
deferred supporting material with specialist-requested/customer-service follow-up,
and enquiry with customer-service-owned contact resolution. Preserve original
deadlines and never automatically close undelivered feedback. See the
[readiness gap review](../DEV-07/referral-readiness.md). Current v0.4 schemas do
not yet implement this full extension; field/state changes must be propagated
together through schemas, OpenAPI, persistence, permissions and tests.
