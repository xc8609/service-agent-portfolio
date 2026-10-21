# DEV-06 — Review, edit and commit a contact note safely

BANK-S02-v0.4 · Inbound note implementation under PR review; owner UAT pending.
Forecast: S04 | Release: B0 | Estimate: Dev 5, BA 0.5, QA 1 person-days. Provisional until technical review.

## Components and contracts

create_proposal(kind=note) creates a draft from deterministic manual template or agent input; edit_proposal replaces only reviewed content with expected proposal/source versions. approve_and_commit_proposal writes contact_notes, audit_events and outbox atomically. Authorization precedes replay lookup; exact prior replay returns receipt before stale version rejection for a new effect.

## State, exceptions and evidence

UI shows draft, modified, saving, stale, failed and committed distinctly. On source change retain user text, display evidence difference and require re-review. Proposal kind, contact and case cannot be changed via edit. Audit holds prior revision; no silent autosave counted as commit.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Note editor/API, audit schema, concurrency/idempotency tests and traceability. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.
