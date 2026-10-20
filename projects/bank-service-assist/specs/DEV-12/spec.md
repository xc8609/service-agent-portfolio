# DEV-12 — Retry unanswered callbacks and guard normal closure

Current S02 forecast: **S04A**. Updated effort: Dev 3, BA 0.5, QA 1 person-days (4.5 total); dependencies DEV-11, BA-06, BA-09. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation delivered for PR review.

BANK-SDD-v0.2 · 19 October 2026
Status: Runtime implemented; owner UAT pending. Business decisions accepted only as listed; technical design/Ready gates pending.
Historical forecast superseded by the current Sprint stated above | Release: B0 manual path / B1 assisted path.
Estimate: Dev 3, BA 0.5, QA 1 person-days; total 4.5 (3.5–7), confidence low. Not actual effort.

## User story and value

As a feedback representative and queue lead, I want bounded retries and evidence-based closure, so that I can avoid abandoned feedback and false resolution.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-18, FR-19. Decisions: D-14, D-16, D-18, D-19, D-22. Dependencies: DEV-11, BA-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Record each actual call attempt with time, verification and outcome.
2. For no answer keep feedback ownership and propose the next allowed contact slot.
3. Allow at most three attempts over three service days, including the first; at most one per service date.
4. On exhaustion or elapsed window send to lead review; do not close automatically.
5. On successful feedback allow human-confirmed closure only when all required work is complete.

## Acceptance criteria

- **DEV-12-AC01** — Given The first actual callback is unanswered; when the retry is planned; then keep awaiting-feedback state and ownership; schedule only within the accepted contact window; under D-18, a placed unanswered call counts once, while a never-placed technical failure is logged without consuming quota or extending any original deadline. Evidence: DEV-12-T01 (planned, not executed).
- **DEV-12-AC02** — Given One attempt is already recorded for a service date; when a concurrent second retry is submitted; then reject the extra attempt plan for that date; actual duplicate call records remain auditable. Evidence: DEV-12-T02 (planned, not executed).
- **DEV-12-AC03** — Given Three attempts have been made or the three-service-day window has elapsed; when the next-step rule is evaluated; then enter unable-to-contact lead review with no resolved closure; a responsible lead may then approve a reasoned new contact plan or a hold with owner and review date, retaining original attempts/deadlines/approvals. Evidence: DEV-12-T03 (planned, not executed).
- **DEV-12-AC04** — Given Friday is the first attempt and Monday is a configured holiday; when a retry window is calculated; then count Friday as day 1, skip the weekend and configured Monday holiday, and end Wednesday at 17:00 America/Winnipeg; enter lead review at expiry even below three attempts, never automatic closure. Evidence: DEV-12-T04 (planned, not executed).
- **DEV-12-AC05** — Given Approved findings exist, necessary actions are complete and verified feedback leaves no unresolved work; when an authorized person confirms closure; then persist a closed disposition with references and audit evidence. Evidence: DEV-12-T05 (planned, not executed).
- **DEV-12-AC06** — Given There is an unanswered call, failed verification, pending refund, new objection or unowned work; when closure is requested; then deny closure with the unmet conditions. Evidence: DEV-12-T06 (planned, not executed).
- **DEV-12-AC07** — Given An agent suggests a fourth attempt or immediate closure; when the proposal is validated; then reject an agent-only fourth attempt, expired-plan contact or automatic closure; allow further contact only under a distinct current lead-approved plan, preserving all history. Evidence: DEV-12-T07 (planned, not executed).

## Ready gates

- D-19 freezes the three-service-date boundary. Freeze the versioned synthetic holiday fixture list before Ready; no administrative non-response closure is authorized.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).

## Accepted intake continuation — 20 October 2026

D-23–D-25 are accepted simulated rules. See the [DEV-07 intake card](../DEV-07/referral-intake-review.md)
and [readiness review](../DEV-07/referral-readiness.md). Paired unresolved
recognition must remain explicit; missing material may follow at specialist
request through customer service; unusable contact details do not block enquiry.
Customer service owns contact resolution. Preserve original deadlines and
separate investigation completion from feedback delivery; no automatic closure
for undelivered feedback. These rules do not accept implementation or extend
existing call quotas; supplementation-call accounting still needs a scoped review.

## Current delivery

See [runtime contract and executed checks](runtime-contract.md). Historical planned-test wording above is retained for traceability; owner UAT remains pending.
