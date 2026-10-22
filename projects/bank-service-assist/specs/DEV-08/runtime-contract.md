# DEV-08 offline runtime delivery — 20 October 2026

Owner explicitly deferred real-model verification. The application now executes a
bounded evidence/draft loop using a labelled scripted provider. This demonstrates
permission, persistence, tool ordering and human review, not model intelligence or
measured productivity. Live providers remain disabled/unqualified under DEV-09.

Inbound: current verified contact → selected posted pair and customer report →
applicable scoped rule → typed cited draft → existing versioned note proposal.
No fabricated recognition or transaction choice. Model arguments cannot choose a
customer, widen the selected pair or invoke a business-write command. Existing
manual intake/referral remains the route for a reviewed enquiry.

Assigned specialist/feedback/progress stages rehydrate current work, approved
findings and commitments. Private notes/contact details are omitted. Output becomes
editable review text, never customer disclosure. Fresh callback verification,
current finding approval and trusted workflow commands remain necessary.

All runs/steps are durable. Per-run limits: four steps, 20 seconds; each HTTP adapter
also has a 15-second timeout, bounded inputs/outputs and no automatic retry. Tools
are read_evidence, read_rules and draft_recommendation, each strict-schema validated.
Only complete calls execute. Unknown/forbidden tools, invented references, detected
financial completion claims, changed evidence, revoked access, cancellation and
budget exhaustion stop without business effects. Claim checking is conservative,
not a general proof of model truthfulness. New live-provider testing must include
prompt injection, unsupported factual claims and customer-safe output quality.

Same actor/trigger is replay-safe. Restart can read completed runs. An expired
running lease is explicitly interrupted; the operator can inspect durable note
history and start a new run from current evidence. No multi-day model conversation
or autonomous financial/action authority. User-triggered continuation includes validated `event:<outbox-id>` triggers for current scoped result/overdue/objection/continuation events;
unsupervised event-triggered Agent runs and live streaming are not enabled.

## Verification

174 PostgreSQL 16.2 API tests passed, including 12 Agent tests for draft-only effects,
replay/restart, revoked/foreign scope, stale versions, typed tool failures, budgets,
cancellation and fabricated citations. Provider tests are offline. 32 Chromium tests passed. Browser evidence
covers run → durable reload → note review → context-change invalidation. Owner UAT,
B0/B1 human effort study and live model qualification remain unexecuted; DEV-10
provides the measurement infrastructure rather than invented savings.

## Evidence refresh and asynchronous UI state

Inbound launch requires completed inspection and no report save in progress.
Run and reload displays belong to one identity/query context; late success or
failure cannot restore the old context. [Regression design and executed evidence](ui-state-regression.md)
connect this correction to DEV-03-AC04 and DEV-08-AC03/04. Authority and human
approval remain server-enforced; this UI guard does not grant new permissions.

## Core context increment — 22 October

[Staff question and scoped transaction context](core-context.md) defines CC-01–06,
implementation boundaries and actual verification evidence for the simplified portfolio.
