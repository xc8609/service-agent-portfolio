# DEV-07 design

BANK-SDD-v0.2 · Candidate architecture; no runtime implementation.

Model-visible tools: get_case_snapshot, create_proposal, get_operation_status. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Add referral payload and unique operation key, queue ownership and case/work-item versions.
- Build review/edit UI with draft/submitting/queued/failed/unknown states.
- Implement outbox replay and operation reconciliation without duplicate work.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.

## Intake refinement design gate

D-23–D-25 are accepted; [readiness review](referral-readiness.md) identifies
missing typed fields, append-only evidence, customer-service contact-gap work,
independent feedback state and migration/permission tests. Proposed engineering
shape is not a deployed contract. Extend shared schemas and persistence together
before accepting referral writes; keep commands outside model tools.
