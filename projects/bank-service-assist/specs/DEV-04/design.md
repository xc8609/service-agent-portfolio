# DEV-04 — Explain the recorded status and next step of an existing case

BANK-S02-v0.4 · Verified inbound read increment implemented; full story/UAT pending.
Forecast: S03 | Release: B0 | Estimate: Dev 2, BA 0.25, QA 0.5 person-days. Provisional until technical review.

## Components and contracts

Use get_case_snapshot behind the same service authorization as the UI. Render aggregate_sequence with occurred_at and recorded_at; event text is customer-safe and sourced. Pending/rejected commitment content is specialist/lead-only. Refresh ownership and versions before details and any draft commit.

## State, exceptions and evidence

Case timeline state is not merchant settlement or refund execution. Pending complaint delivery is shown as pending intake delivery; no external acknowledgement until trusted receipt.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Case timeline UI/API, state tests and UAT examples. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.

## Inbound implementation increment — 20 October 2026

[Runtime contract and CK-01–07 scenarios](runtime-contract.md) ·
[Execution evidence and remaining boundaries](implementation-evidence.md).

The current increment supports verified inbound case reads only. Assigned outbound
feedback scope, Agent delegation and referral submission are not implemented.
Existing work produces a review/reuse hint; submission-time atomic duplicate
protection remains a DEV-07 obligation. No case mutation is exposed.
