# DEV-08 design

BANK-SDD-v0.2 · Candidate architecture; no runtime implementation.

Model-visible tools: get_contact_context, search_transactions, get_transaction_evidence, get_case_snapshot, search_policy, get_policy_section, get_contact_attempts, get_service_targets, create_proposal, get_operation_status. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Slice A (3 developer-days): runtime adapter, tool allowlist, bounded execution and deterministic fake-provider tests.
- Slice B (4 developer-days): durable run/proposal records, streamed evidence UI, resume and failure recovery; evaluate actual integration overhead after contracts.
- Instrument safe run/tool/operation correlations; normalize provider output and never treat model prose as execution proof.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.
