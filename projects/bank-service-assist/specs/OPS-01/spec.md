# OPS-01 — Package the application and establish CI release artifacts

BANK-S02-v0.4 · Read slice implemented in PR #1; full story acceptance pending.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 2, BA 0, QA 0.5 person-days. Provisional until technical review.

## Business purpose and scope

As a maintainer, I want reproducible build artifacts so that a reviewed change can be tested and deployed consistently.

Value: Demonstrate engineering completion beyond notebooks. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

No cloud resource purchase or public publication is performed by creating this plan. All operational scenarios and records are synthetic.

Requirements: OR-01. Dependencies: DEV-01, QA-01.

## Delivery flow

1. Build versioned frontend/API/worker images and Compose configuration with private database networking.
2. Configure CI lint/type/fast tests and isolated integration checks; retain Python 3.9/3.12 pure evaluation coverage.
3. Keep secrets server-side, provide validated .env.example, scan for accidental keys/data and record image/config versions.

## Acceptance criteria

- **OPS-01-AC01** — Given Clean checkout with approved locks; when build frontend/API/worker artifacts; then record commit/config/image digests; no unpinned latest dependency in release artifact. Evidence: OPS-01-T01, planned/not executed.
- **OPS-01-AC02** — Given Any required lint/type/contract/integration check fails; when run pipeline; then no release-candidate promotion; retain failure evidence. Evidence: OPS-01-T02, planned/not executed.
- **OPS-01-AC03** — Given No model key and private database network; when start Compose demo; then manual UI/API operate; database is not publicly exposed; readiness waits for schema/dependencies. Evidence: OPS-01-T03, planned/not executed.
- **OPS-01-AC04** — Given Browser assets, images and logs inspected; when check secret/data exclusions; then no provider key, private customer material or raw datasets; env example contains placeholders only. Evidence: OPS-01-T04, planned/not executed.
- **OPS-01-AC05** — Given Only local checks executed, GitHub not connected; when write release evidence; then state cloud CI not executed; never mark cloud build success. Evidence: OPS-01-T05, planned/not executed.
- **OPS-01-AC06** — Given Migrations or workers fail during staging rollout; when follow runbook; then stop promotion, preserve data and pending work; restore/forward-fix plan tested in isolated staging before release. Evidence: OPS-01-T06, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
