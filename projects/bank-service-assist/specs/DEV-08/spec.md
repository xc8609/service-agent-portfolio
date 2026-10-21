# DEV-08 — Run a bounded evidence agent across persisted workflow stages

Current S02 forecast: **S05**. Updated effort: Dev 9, BA 1, QA 2.0 person-days (12.0 total); dependencies DEV-03, DEV-05, DEV-06, DEV-07, DEV-09, DEV-11, DEV-12, DEV-13, BA-09. This supersedes older forecast/estimate lines below. Contract version 0.4; offline runtime implemented for PR review.

BANK-SDD-v0.2 · 19 October 2026
Status: Offline runtime implemented; owner UAT and live qualification pending. Business decisions accepted only as listed; technical design/Ready gates pending.
Forecast: S05 | Release: B0 manual path / B1 assisted path.
Estimate: Dev 7, BA 1, QA 1.5 person-days; total 9.5 (7–14.5), confidence medium. Not actual effort.

## User story and value

As a representative, I want an agent that resumes from current case evidence, so that I can reduce evidence assembly and drafting effort across handoffs.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-06, FR-07, FR-12, FR-14, FR-22. Decisions: D-15. Dependencies: DEV-07, DEV-09, DEV-11, DEV-12, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Start a run from a permitted user request or allowlisted business event.
2. Rehydrate current scoped business state and select only permitted evidence tools.
3. Fetch facts and applicable policy, identify gaps and produce a typed cited proposal.
4. Stop awaiting human action; resume later in a new bounded run from refreshed evidence.
5. Approval and deterministic workflow execution remain outside model authority.

## Acceptance criteria

- **DEV-08-AC01** — Given A duplicate-charge question needs records then policy; when the agent runs; then execute dependent scoped tools and return fact/policy citations, missing facts and a typed next-step proposal. Evidence: DEV-08-T01 (planned, not executed).
- **DEV-08-AC02** — Given A case waits across a process restart; when a later event starts assistance; then load committed latest state rather than relying on chat history or a live multi-day run. Evidence: DEV-08-T02 (planned, not executed).
- **DEV-08-AC03** — Given A source or customer fact changes after proposal creation; when approval is attempted; then reject stale evidence and request refreshed review. Evidence: DEV-08-T03 (planned, not executed).
- **DEV-08-AC04** — Given The provider times out or returns invalid tool arguments; when the run terminates; then honour budgets, return a typed failure and preserve manual access and all committed work. Evidence: DEV-08-T04 (planned, not executed).
- **DEV-08-AC05** — Given A prompt or tool result requests a refund or widened access; when the agent attempts a forbidden action; then reject it in the allowlist/backend and record a sanitized denial. Evidence: DEV-08-T05 (planned, not executed).
- **DEV-08-AC06** — Given The same business event is redelivered; when assistance resumes; then deduplicate effects and reconcile operations before retrying writes. Evidence: DEV-08-T06 (planned, not executed).
- **DEV-08-AC07** — Given A reviewer compares assisted and guided-search tasks; when evaluation is performed; then report correct completion, active checking time, corrections and known cost; no invented savings. Evidence: DEV-08-T07 (planned, not executed).

## Ready gates

- Tool schemas, model capability qualification and numerical run budgets are Ready gates; DEV-13 business branches are accepted as D-20/D-21; implementation and provider capability remain gates.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).

## Current offline delivery

See [implemented runtime, executed tests and remaining gates](runtime-contract.md). Historical live-provider/streaming/effort-study acceptance is not marked complete.
