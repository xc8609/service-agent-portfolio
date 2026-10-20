# DEV-07 — Submit a reviewed specialist enquiry with accountable ownership

Current S02 forecast: **S04**. Updated effort: Dev 4, BA 0.5, QA 1 person-days (5.5 total); dependencies DEV-06, BA-06. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation pending.

BANK-SDD-v0.2 · 19 October 2026
Status: Detailed specification candidate; implementation not started. Business decisions accepted only as listed; technical design/Ready gates pending.
Forecast: S04 | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 0.5, QA 1 person-days; total 5.5 (4–8.5), confidence medium. Not actual effort.

## User story and value

As a representative, I want a complete specialist-review request, so that I can reduce rework while preserving actual submission state.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-09, FR-10, FR-13, FR-16. Decisions: D-12, D-13. Dependencies: DEV-03, DEV-05, DEV-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Check related work and choose explanation-only, link-existing or justified new review.
2. Draft the concern, transaction references, checked facts, missing evidence and requested review.
3. Person approves; backend rechecks scope, versions, queue eligibility and duplicate keys.
4. Commit Case, WorkItem, Audit and Outbox atomically; display the real operation receipt.

## Acceptance criteria

- **DEV-07-AC01** — Given The enquiry has a supported answer and no remaining action; when the contact is recorded; then allow a note without forcing a specialist case. Evidence: DEV-07-T01 (planned, not executed).
- **DEV-07-AC02** — Given The same issue already has active specialist work; when a new proposal is reviewed; then link existing work or require an explicit distinct-work reason. Evidence: DEV-07-T02 (planned, not executed).
- **DEV-07-AC03** — Given A person approves a fresh complete request; when submission succeeds; then return one case/work reference with accountable queue; do not claim a specialist has accepted it. Evidence: DEV-07-T03 (planned, not executed).
- **DEV-07-AC04** — Given Submission succeeds but its response is lost; when the client retries or reconciles; then return the original receipt and create no second case or outbox effect. Evidence: DEV-07-T04 (planned, not executed).
- **DEV-07-AC05** — Given The recipient queue is invalid or authorization changed; when approval is committed; then reject without partial business writes and preserve the draft. Evidence: DEV-07-T05 (planned, not executed).
- **DEV-07-AC06** — Given The model states a request was submitted without a receipt; when the UI renders the result; then show a draft or unknown operation state, never a false submitted status. Evidence: DEV-07-T06 (planned, not executed).

## Ready gates

- Queue routing configuration and permitted referral reasons need BA-06 sign-off.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
