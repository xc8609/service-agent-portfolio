# DEV-02 — Open an authorized contact and assemble permitted customer context

Current S02 forecast: **S03**. Updated effort: Dev 3, BA 0.25, QA 0.5 person-days (3.75 total); dependencies DEV-01, BA-09. This supersedes older forecast/estimate lines below. Contract version 0.4; runtime implementation pending.

BANK-SDD-v0.2 · 19 October 2026
Status: Detailed specification candidate; implementation not started. Business decisions accepted only as listed; technical design/Ready gates pending.
Forecast: S03 | Release: B0 manual path / B1 assisted path.
Estimate: Dev 3, BA 0.25, QA 0.5 person-days; total 3.75 (3–6), confidence medium. Not actual effort.

## User story and value

As a ordinary representative, I want a scoped customer and card context, so that I can avoid repeated page navigation without expanding access.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-01, NFR-01. Decisions: D-09, D-11. Dependencies: DEV-01, BA-07, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Read identity-verification result and session role from trusted services.
2. Select an authorized card; show masked identifiers, context timestamp and permitted actions.
3. Deny cross-customer reads before model/tool output; retain a manual verification route.

## Acceptance criteria

- **DEV-02-AC01** — Given An authenticated ordinary representative and verified customer context; when the selected card is loaded; then return only the permitted card/account context with source timestamp and version. Evidence: DEV-02-T01 (planned, not executed).
- **DEV-02-AC02** — Given An unverified or expired customer context; when any private lookup is requested; then deny without returning private fields and offer the verification route. Evidence: DEV-02-T02 (planned, not executed).
- **DEV-02-AC03** — Given A prompt supplies a different customer ID or asks for administrator privileges; when the tool is invoked; then derive scope from the session and disclose no out-of-scope existence or details. Evidence: DEV-02-T03 (planned, not executed).
- **DEV-02-AC04** — Given An ordinary representative can read transactions; when a refund or other privileged action is requested; then reject the action; read access does not grant financial authority. Evidence: DEV-02-T04 (planned, not executed).
- **DEV-02-AC05** — Given Scope expires between a proposal and approval; when the person attempts to commit; then reject with AUTH_REQUIRED and preserve the editable draft. Evidence: DEV-02-T05 (planned, not executed).

## Ready gates

- Finalize role/action matrix and identity-proofing fixture; no real identity provider is claimed.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
