# DEV-11 — Receive specialist findings and complete a verified customer callback

Current S02 forecast: **S04A**. Updated effort: Dev 4, BA 0.5, QA 1 person-days (5.5 total); dependencies DEV-07, DEV-06, BA-09. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation pending.

BANK-SDD-v0.2 · 19 October 2026
Status: Detailed specification candidate; implementation not started. Business decisions accepted only as listed; technical design/Ready gates pending.
Historical forecast superseded by the current Sprint stated above | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 0.5, QA 1 person-days; total 5.5 (4–8), confidence low. Not actual effort.

## User story and value

As a feedback representative, I want approved findings and a callback task, so that I can continue the case without requiring the original representative.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-17, FR-18. Decisions: D-13, D-14. Dependencies: DEV-07, DEV-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Specialist accepts work; use a role-protected synthetic result entry or signed adapter event.
2. Store finding, evidence, approved customer explanation, action status and version separately.
3. Create one feedback task for the shared queue; assign a person when work begins.
4. Draft from approved customer-visible content; person calls, verifies identity and records actual outcome.

## Acceptance criteria

- **DEV-11-AC01** — Given An authorized specialist submits an approved result; when the event is processed twice; then persist one result version and one corresponding feedback task. Evidence: DEV-11-T01 (planned, not executed).
- **DEV-11-AC02** — Given The original representative is unavailable; when another authorized feedback representative claims the task; then provide scoped history and retain clear ownership. Evidence: DEV-11-T02 (planned, not executed).
- **DEV-11-AC03** — Given A result contains internal-only notes and approved explanation; when the agent drafts customer feedback; then use only approved customer-visible content for the explanation. Evidence: DEV-11-T03 (planned, not executed).
- **DEV-11-AC04** — Given A customer answers but identity verification fails; when the callback is recorded; then record verification failure, disclose no transaction detail and do not mark feedback complete. Evidence: DEV-11-T04 (planned, not executed).
- **DEV-11-AC05** — Given The specialist result changes after draft review; when feedback approval is attempted; then reject stale content and preserve edits for refresh. Evidence: DEV-11-T05 (planned, not executed).
- **DEV-11-AC06** — Given A financial action is only approved or pending; when the agent summarizes the result; then do not state funds moved or that the financial issue is resolved. Evidence: DEV-11-T06 (planned, not executed).

## Ready gates

- Result payload and callback outcome codes need schema review; real outbound telephony is excluded.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
