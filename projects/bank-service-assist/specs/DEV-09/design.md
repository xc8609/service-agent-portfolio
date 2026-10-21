# DEV-09 — Qualify model runtime and provider adapters with a bounded spike

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-S02-v0.4 · Offline implementation delivered for PR review; live qualification deferred by owner.
Forecast: S04 | Release: B1 | Estimate: Dev 4, BA 0.25, QA 1 person-days. Provisional until technical review.

## Components and contracts

Provider interface emits text_delta, tool_call_delta, tool_call_ready, usage, error and completed/cancelled events. Normalize run/call IDs and usage provenance; enforce server-owned tool allowlist and budgets outside SDK. Adapter never owns transaction boundaries. Select runtime via bounded spike/ADR after required capabilities are tested; do not assume any SDK or OpenAI-compatible endpoint supports every schema.

## State, exceptions and evidence

Required capability matrix: tool schemas and dependent calls, streaming argument assembly, cancellation, retries/timeouts, usage availability, endpoint allowlist and policy-compliant data boundary. Start with fake provider; two live routes are B1 evidence, not prerequisite for B0. DeepSeek/self-hosted endpoint remains planned unless separately qualified.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

ADR, capability matrix, locked dependencies, adapter contract tests and live spike report. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.

## Offline delivery decision

See [implemented boundary and remaining qualification gates](runtime-contract.md). Live tests are not executed; no public provider is enabled.
