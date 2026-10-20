# DEV-10 — Build operational event marts and a reconciled Tableau view

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S05A | Release: B1 | Estimate: Dev 3, BA 1, QA 0.5 person-days. Provisional until technical review.

## Components and contracts

Authoritative event facts are keyed by operation/run/proposal/attempt/work IDs. Produce SQL views at run, proposal-decision, callback-attempt and work-obligation grain, then aggregate CSV for Tableau. Join after deduplication at each grain to avoid fan-out. Separate synthetic demo, offline evaluation and qualified live-test segments. Existing CFPB counts remain a separate public-data analysis.

## State, exceptions and evidence

Metric definitions: success rate=successful terminal runs/all started runs at cutoff, with pending shown; acceptance=approved proposals/decided proposals (approved+rejected), with draft/stale/pending shown separately; edit rate=approved proposals whose reviewed source hash changed/approved proposals. Callback counts exclude D-18 not_placed faults but report them separately. Overdue uses original obligation due time, not latest plan. Handling effort uses separately collected participant timing only.

Shared invariants: server-derived identity/assignment; source and record versions; typed safe errors; idempotent command receipts; no model approval/financial authority; database business/audit/outbox atomicity. Trace only sanitized IDs, versions, outcome, latency and usage provenance. Customer content is untrusted input.

## Delivery and recovery

Metric dictionary, SQL marts, reconciliation report, Tableau workbook and findings note. Reproduce in disposable local/test environment; document exact versions and skipped suites. Runtime/deployment evidence remains pending.
