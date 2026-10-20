# <STORY-ID>: <business outcome>

Status: Draft | Ready | In progress | Accepted. Actual owner/reviewer: TBD.

## Problem and evidence
Problem ID, target role requirement, relevant owner experience, sources and assumptions; why a simpler solution is/is not sufficient.

## Scope and decisions
User story; in/out of scope; affected personas; actual decision owner; business objective and baseline/target/denominator/data source/review date. Decision and assumption IDs.

## Process and rules
As-is/to-be step; preconditions; main flow; alternative/exception flows; business rule IDs; authority and data classification; state transitions and prohibited transitions.

## Acceptance examples
| AC ID | Given | When | Then | Test/evidence ID | Status |
|---|---|---|---|---|---|
| <ID>-AC1 | Explicit input/state | Action | Observable result and no unintended write | <ID>-T1 | Planned |

Include permission, stale state, invalid input, retry/duplicate, timeout and recovery where relevant.

## Design contract
Link design.md: API schemas/errors, UI states, data/migration, server authorization, tool contract, provider boundary, logs, failure/recovery, ADRs and rejected options.

## Delivery slices
Link tasks.md: vertical slices, role estimates, dependency order, developer tests, independent QA, documentation and deployment. Split slices >5 developer-days. Estimate ranges and assumptions, not uncalibrated points-to-hours conversion.

## Traceability and change
Requirement → rule → story/spec version → PR/implementation → AC → executed test/UAT → release. For changed behavior, link change request and impacted contracts/tests/support docs.

## Acceptance record
Link acceptance.md: command/environment/date/data version, expected/actual, pass/fail/blocked, evidence paths, defects, actual reviewer, release recommendation. No implementation or approval claim from this template.
