# DEV-05 design

BANK-SDD-v0.2 baseline; inbound runtime design updated 20 October 2026.

See [runtime contract](runtime-contract.md) for the implemented deterministic PostgreSQL policy reader, pair scope, endpoint semantics and failure behavior. `services/api/bank_api/policy_lookup.py` supplies both human reads and canonical tool endpoints. No model runs in this increment.

Model-visible tools: search_policy, get_policy_section. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Author explicitly fictional policy editions and conflicting/expired examples with provenance.
- Implement metadata filtering and section retrieval before model summarization.
- Render cited sections and a manual search fallback; keep customer instructions untrusted.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.
