# DEV-05 — Retrieve applicable handling rules with verifiable citations

Current S02 forecast: **S03**. Updated effort: Dev 4, BA 0.25, QA 1 person-days (5.25 total); dependencies DEV-01, BA-06, BA-07. This supersedes older forecast/estimate lines below. Contract version 0.4; inbound deterministic rule lookup implemented, under review.

BANK-SDD-v0.2 · 19 October 2026
Status: Inbound rule lookup implemented; technical evidence below. Owner UAT, delegated Agent/assigned feedback scope and release acceptance remain pending.
Forecast: S03 | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 0.25, QA 1 person-days; total 5.25 (4–8), confidence medium. Not actual effort.

## User story and value

As a representative, I want context-specific rules and missing-information prompts, so that I can reduce knowledge-base search and learning effort.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-05, FR-06, FR-15. Decisions: D-01, D-09, D-10. Dependencies: BA-06, BA-07, DEV-02.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Build applicability filters from verified product/jurisdiction/transaction context.
2. Search permitted policy material as of the contact time.
3. Read the exact section and show applicability, version and evidence gaps next to the suggested step.

## Acceptance criteria

- **DEV-05-AC01** — Given A newer uploaded rule is not effective at the enquiry time; when policy search runs; then exclude it and use the applicable edition or report a gap. Evidence: DEV-05-T01 (runtime evidence in acceptance.md).
- **DEV-05-AC02** — Given Similar text belongs to another product or restricted audience; when retrieval runs; then exclude it before returning content to the agent. Evidence: DEV-05-T02 (runtime evidence in acceptance.md).
- **DEV-05-AC03** — Given Two applicable rules conflict; when a response is drafted; then expose the conflict and request authorized clarification, not an authoritative guess. Evidence: DEV-05-T03 (runtime evidence in acceptance.md).
- **DEV-05-AC04** — Given No applicable policy exists; when the agent proposes a next step; then state the missing basis and route for manual review. Evidence: DEV-05-T04 (runtime evidence in acceptance.md).
- **DEV-05-AC05** — Given Retrieved narrative includes instructions to bypass permissions; when the model reads it; then treat it as data; tool and server permissions stay unchanged. Evidence: DEV-05-T05 (runtime evidence in acceptance.md).

## Runtime increment

[Runtime contract](runtime-contract.md) defines simulated policy ownership, effective-time filtering, conflict handling, API boundaries and RP-01–05 tests. [Implementation evidence](implementation-evidence.md) records executed checks. Shared schemas remain v0.4; this does not claim the Agent is implemented.

## Ready gates

- Fixture authorship, conservative overlap handling and lead/policy-owner clarification route are documented in the runtime contract; owner walkthrough acceptance remains pending.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

[Design](design.md) · [Tasks](tasks.md) · [Acceptance record](acceptance.md) · [Tool contracts](../contracts/agent-tools.md) · [Review increment](../../docs/sprint-01/workflow-increment.md).
