# OPS-01 — Package the application and establish CI release artifacts

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 2, BA 0, QA 0.5 person-days. Provisional until technical review.

## Components and contracts

Build separate web/API/worker images with a common versioned application source. Database network private; provider keys server-only. CI uses minimum permissions and separate migration/runtime identities; record source commit, lock hashes and image digests. Public synthetic demo disables real phone/financial integrations and destructive reset.

## State, exceptions and evidence

Pipeline stages: static checks → offline tests → test database/migrations → critical UI smoke → image build → candidate artifacts. Public deployment remains a later OPS-02 action. Runbook documents rollback-compatible migrations, backups/restore, pending outbox replay and manual fallback; no production database rollback by dropping tables.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Dockerfiles/Compose, CI workflow, environment guide, versioned build and test artifacts. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.
