# DEV-13 design

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-SDD-v0.2 · Architecture baseline; see [implemented boundary](runtime-contract.md).

Model-visible tools: get_case_snapshot, get_service_targets, get_contact_attempts, search_policy, create_proposal. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Add deduplicated deadline events and progress-update proposals with original due timestamps.
- Add objection/re-review linkage and proposal invalidation on new evidence.
- Build lead review UI; keep detailed exception routing disabled until rules are accepted.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.

## Accepted responsibility and parallel continuation

Overdue investigation retains its original specialist and original deadline. Notify the responsible lead and create customer progress work in the feedback queue. The specialist proposes the next update time; the responsible lead confirms it. Preserve original overdue history. The agent may gather evidence, remind and draft, but cannot commit a completion date.

Feedback staff preserve the customer statement and new evidence, and route disputed findings to specialist re-review. An explicit complaint request creates an independent complaint-intake record without waiting for re-review. Both tracks link to the original case and keep independent ownership/status. Objection or silence never implies resolved closure.

See [D-20/D-21 contract addendum](../contracts/continuation-addendum.md) for required schema completion and planned negative/concurrency tests before Ready.

## Current delivery

[Runtime behavior and executed checks](runtime-contract.md) supersede historical implementation-pending wording. Agent drafting and owner UAT remain separate gates.
