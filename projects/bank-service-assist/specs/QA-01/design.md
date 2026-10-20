# QA-01 — Implement layered verification and requirement-to-test coverage

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 1.5, BA 0.5, QA 1.5 person-days. Provisional until technical review.

## Components and contracts

Separate fast pure-rule/contract tests, real PostgreSQL API/transaction tests, browser critical-path tests, adversarial prompt/tool boundary tests, provider qualification, recovery and human UAT. A schema example is not a realistic bank dataset or model holdout. Keep test records synthetic with fixed expected results.

## State, exceptions and evidence

PR gates: lint/types, offline contract/rule suite and isolated DB integration once implemented; critical UI journey before release. Model evaluation uses frozen labelled scenarios and failure slices, not training/tuning against the final holdout. Live-provider tests are explicitly triggered with budget and credential controls.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Test strategy, traceability matrix, automated suites, defect severity/triage rules and evidence template. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.
