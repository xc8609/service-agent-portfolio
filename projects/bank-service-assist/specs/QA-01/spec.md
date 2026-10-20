# QA-01 — Implement layered verification and requirement-to-test coverage

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 1.5, BA 0.5, QA 1.5 person-days. Provisional until technical review.

## Business purpose and scope

As a tester, I want independent checks at the appropriate layer so that correct wording cannot hide invalid data access or execution.

Value: Demonstrate a test strategy connected to business risk. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

Passing unit tests does not validate real-data SQL, live providers or cloud deployment. All operational scenarios and records are synthetic.

Requirements: NFR-03. Dependencies: BA-09, DEV-01.

## Delivery flow

1. Use pytest for pure rules/API tests, isolated PostgreSQL integration tests and Playwright for critical UI journeys.
2. Implement fault cases: denied scope, invalid payload, stale version, duplicate request, worker crash, policy gap and provider failure.
3. Make CI run meaningful fast checks on PRs; live-model, full data and deployment checks are separate explicitly triggered suites.

## Acceptance criteria

- **QA-01-AC01** — Given Current Must requirements and story AC IDs; when build coverage manifest; then each maps to planned layer, fixture, independent oracle and release gate; missing mapping fails validation. Evidence: QA-01-T01, planned/not executed.
- **QA-01-AC02** — Given Cross-customer read or agent-approved write is attempted; when run authorization integration suite; then access is denied at API/service boundary; no secret/internal detail in response or trace. Evidence: QA-01-T02, planned/not executed.
- **QA-01-AC03** — Given Duplicate requests, stale versions and worker restart; when run real test-Postgres transaction suite; then one effect/receipt, preserved audit, recoverable pending work; report actual database version. Evidence: QA-01-T03, planned/not executed.
- **QA-01-AC04** — Given A deliberately invalid transition is injected in isolated test; when execute suite; then test fails for the expected business reason; remove mutation after demonstration. Evidence: QA-01-T04, planned/not executed.
- **QA-01-AC05** — Given Live models/cloud/database are unavailable; when publish test report; then affected suites explicitly skipped with reason; schema checks never relabelled runtime/UAT pass. Evidence: QA-01-T05, planned/not executed.
- **QA-01-AC06** — Given A critical authorization/closure case fails; when evaluate release gate; then block promotion regardless of average score or total passing-test count. Evidence: QA-01-T06, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
