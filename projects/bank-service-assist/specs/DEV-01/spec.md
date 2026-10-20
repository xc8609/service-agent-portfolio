# DEV-01 — Create the application skeleton and deterministic demo environment

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0 | Estimate: Dev 3, BA 0.25, QA 0.5 person-days. Provisional until technical review.

## Business purpose and scope

As a contributor, I want a repeatable local environment so that I can develop and review the manual service workflow without a model key.

Value: Provide reproducible engineering evidence while keeping domain decisions visible. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

No business story marked complete just because services start. All operational scenarios and records are synthetic.

Requirements: FR-12, DATA-01. Dependencies: BA-07, BA-08, BA-09.

## Delivery flow

1. Create React/TypeScript UI, FastAPI service, PostgreSQL migration setup and health/readiness endpoints.
2. Add isolated synthetic seed/reset command, configuration validation and safe .env.example.
3. Keep Python 3.9 evaluation modules separate from Python 3.12 application dependencies; lock versions after compatibility checks.

## Acceptance criteria

- **DEV-01-AC01** — Given A clean supported checkout with empty demo database; when run documented migration and seed commands twice; then second run changes no fixture IDs or counts; API and UI display labelled synthetic scenario and schema version. Evidence: DEV-01-T01, planned/not executed.
- **DEV-01-AC02** — Given No model credentials; when start UI/API/worker and complete manual lookup; then manual path remains usable; agent availability is explicitly disabled. Evidence: DEV-01-T02, planned/not executed.
- **DEV-01-AC03** — Given Database is unavailable or a required configuration value is malformed; when check liveness and readiness; then process liveness is separate from dependency readiness; readiness is non-success with sanitized correlation ID. Evidence: DEV-01-T03, planned/not executed.
- **DEV-01-AC04** — Given Reset is aimed at a database not explicitly marked disposable demo; when request reset; then refuse without deleting records; reset requires matching environment guard and explicit demo target. Evidence: DEV-01-T04, planned/not executed.
- **DEV-01-AC05** — Given Repository existing Python 3.9 evaluation suite; when install Python 3.12 application dependencies in separate environment; then legacy suite remains independently runnable; app lock and setup record supported versions. Evidence: DEV-01-T05, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
