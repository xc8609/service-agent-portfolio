# REV-02 — bank-core acceptance corrections

Owner-authorized correction of [UAT-01–03](../uat/2026-10-21-delegated-assessment.md).
Branch `codex/uat-bank-handoff-fixes`; depends on REV-01 / PR #21. No new business
scope, financial action, provider route or permission role is introduced.

## Stories, design and acceptance

| Defect / parent | Acceptance criterion | Implementation / regression |
|---|---|---|
| UAT-01 / DEV-04, DEV-13, NFR-01 | Publishing a finding must not promote pending progress into customer-safe evidence. Previously approved historical progress remains identifiable | Migration 014 separates `approved_by`/`approved_at` from supersession decisions. Only lead approval sets them; inbound and Agent case snapshots require both. API transition/replay tests and WF-05 |
| UAT-02 / DEV-07, DEV-11, FR-16, FR-23–25 | An assigned worker can see each submitted statement revision, recognition scope, selected pair, requested review, clarification answers, material/contact gaps and ownership without another-system lookup | `IntakeSummary`, distinct source IDs/versions/amounts/dates in assigned transaction table. API new/linked multi-revision handoff tests; WF-04 checks readable content and denied access before claim |
| UAT-03 / DEV-04, DEV-07 | Guidance distinguishes lookup from explicit reviewed submission and agrees with section 6 | Updated RelatedCases wording; WF-05 |

## Migration and support

Run standard migrations, then provision runtime grants, before starting schema 014.
Legacy `approved` and `missed` rows with decision actor/time preserve their approval
provenance. Historical `superseded` rows are ambiguous: retain them internally, but
do not manufacture approval or expose them as customer-safe history. An institution
may reconcile them from independent approval evidence in a separately reviewed migration.
Generic `decided_at` remains insufficient because publishing a finding also sets it.

No historical statement is overwritten. Intake submissions show their original
timestamp/revision and are explicitly labelled customer-reported. Later contact
resolution and material answers remain separate records. Existing assigned-work
server authorization protects the additional rendered fields; the coordinator gets
no new detail privilege. No raw contact information is added to the summary.

## Validation and retest

Run full API/PostgreSQL regression, browser tests, offline/SQL checks, validators,
lint and frontend build; require all four PR checks. Then rerun the bank-core UAT
on a fresh worker-enabled synthetic demo. Record the commit and evidence separately
from the original failed assessment. No automatic main merge or production release.

## Executed checks — 21 October 2026

Local PostgreSQL 16.2 / Python 3.12: 232 API tests passed, including seven added
parameterized regression cases. Chromium: 42 browser tests passed in the fresh,
worker-free CI-equivalent fixture. The first worker-enabled run passed 41/42;
CK-01's fixed-seed locator matched an additional overdue callback created by the
worker. No assertion was weakened: rerunning with CI's setup passed all 42.
Twenty offline/SQL tests, Ruff, frontend build, spec/schema validators, publication
hygiene and whitespace checks passed. Cloud CI and interactive retest follow the PR.

[Trello REV-02](https://trello.com/c/hqWMOquN/58-rev-02-fix-approval-lifecycle-and-specialist-intake-handoff).

## Post-CI retest

All four PR checks passed on application commit `9b61430`. The subsequent
[delegated core-flow retest](../uat/2026-10-21-retest.md) passed UAT-01–03 and the
observed query-to-verified-feedback path. Remaining manual coverage and the
conservative wording guard limitation are recorded explicitly. PR remains open.
