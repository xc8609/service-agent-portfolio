# DEV-03 design

BANK-SDD-v0.2 · Full-story architecture below; implemented increments are linked separately.

Model-visible tools: search_transactions, get_transaction_evidence, get_case_snapshot. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Create deterministic synthetic ledger and statement-view fixtures including unlinked equal amounts.
- Implement filtered/paginated search and a selected-record comparison UI.
- Invalidate affected proposals after transaction selection or customer correction changes.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.

## Manual statement and recognition increment — 20 October 2026

[Detailed runtime contract and SI-01–06 acceptance scenarios](investigation-contract.md)
cover customer statement revisions, explicit recognition including D-23 unresolved
pairs, and immediate invalidation after query/selection/statement changes.
See [execution evidence](implementation-evidence.md) for tested scope and limits.
