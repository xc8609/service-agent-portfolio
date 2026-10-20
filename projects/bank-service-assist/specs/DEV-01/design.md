# DEV-01 — Create the application skeleton and deterministic demo environment

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0 | Estimate: Dev 3, BA 0.25, QA 0.5 person-days. Provisional until technical review.

## Components and contracts

apps/web (React/TypeScript), services/api (FastAPI/Python 3.12), worker entrypoint, PostgreSQL and migrations form one Compose development boundary. Version locks follow a compatibility smoke run; none is claimed installed by this spec. /health/live reports process life; /health/ready reports database/schema readiness without credentials. Configuration loads server-side; fake identity adapter uses fixed synthetic principals and cannot be enabled in public mode.

## State, exceptions and evidence

Named seed fixtures: posted plus pending pair, two posted equal amounts without proof, reversed charge, missing merchant context and forbidden second customer. Seed/reset requires disposable-demo database marker, not merely an environment-name string.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Runnable skeleton, migrations, seed tooling, environment guide and architecture ADR. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
