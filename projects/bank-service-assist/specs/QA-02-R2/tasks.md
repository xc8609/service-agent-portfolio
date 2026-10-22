# R2 delivery tasks

**22 October scope update:** the [portfolio plan](../../evaluation/r2/portfolio-scope.md) now governs the next milestone. Existing completed work and tests remain; independent collection/freeze and full qualification requirements below are deferred. Codex performs delegated engineering review, not fabricated human acceptance.

- [x] Record confirmed business rules and R2-S01 scoring decision.
- [x] Author ten public synthetic development cases with family and criteria trace.
- [x] Add offline scoring, case accounting, hash-bound review and separate business states.
- [x] Add failure-path regressions including self-certification, disclosure without citations,
  mixed positive/negative prose, duplicate IDs, missing outputs and stale review.
- [x] Record local checks; PR CI is checked separately on the submitted commit.
- [x] Record owner-confirmed R2-S02 critical severity and both regressions.
- [x] Record owner-confirmed R2-S03 denominator/review-rate treatment and mixed-batch regressions.
- [x] Record R2-S04 quality-failure grading, request coverage and boundary regressions.
- [x] Prepare one batch packet with ten illustrative answers, failure boundaries and candidate gates.
- [x] Owner accepted R2-A01 answer intent and R2-G01 candidate gates on 21 October.
- [x] Record approved numerical targets, review ceiling and three-run requirement as the candidate baseline.
- [ ] Freeze the complete corpus/keys, family split, baselines, configuration and run manifest before execution.
- [ ] Independent author/reviewer supplies new hidden families before any hold-out freeze.
- [ ] Execute actual runtime/model runs and evidence-backed human adjudication.

No task here marks parent QA-02 or an entire Sprint Done. The existing model qualification,
owner UAT and benefit-study gates remain separate. This PR is independent of unmerged
PR #23 at code level; it references that decision record rather than copying runtime work.

Executed 21 October 2026: 34 new scorer regression tests passed. The complete local
offline suite had 49 passes and two SQL modules skipped because the application venv
lacks DuckDB. Ruff lint/format, publication links and whitespace checks passed. CI
installs the full offline dependencies for Python 3.9 and 3.12. No actual model output,
human adjudication, database runtime test or benefit study was executed in this slice.

Scheduling: this is part of the proposed S05B QA-02 stage-1 work in PR #23, not an
additional completed Sprint or a new cumulative estimate. Remaining corpus/provenance and run-readiness work
blocks experiment freeze; confirmed scoring decisions must not be re-asked.

Batch-review packet check, 21 October 2026: documentation-only increment; public links
passed (407 files / 787 links); the unchanged local offline suite passed 49 tests
with two SQL modules skipped for missing DuckDB. It adds no
model run, automated adoption gate or reviewed answer approval.

Owner approval update, 21 October 2026: R2-A01 and R2-G01 are accepted.
The preceding packet commit 4777f8b passed all four CI checks. Approval does not
complete gate automation, independent data authorship, evaluation or UAT.

## Approved gate and runtime-evidence increment — 21 October 2026

- [x] Implement G1–G6 arithmetic for three runs, paired baseline comparison, review
  history, configuration/source binding and rejection of reused/fixture evidence.
- [x] Prepare an ignored private 64-slot manifest and published-exposure inventory;
  implement readiness checks and answer-key-safe field projection.
- [x] Add read-only pre-freeze inspection and actual-runtime/DB evidence capture.
- [x] Add 40 offline gate regressions and 6 PostgreSQL capture regressions; extend
  SDD R2-AC13–20 and the operator guide. No user decision was re-opened.
- [ ] Obtain independently authored hidden cases and owner-reviewed keys; the empty
  scaffold is preparation only, not a completed holdout.
- [ ] Qualify the chosen API route/access/budget, freeze the full experiment, execute
  and adjudicate real model outputs. No live call or model selection was performed.

Executed locally on the final implementation: 89 offline tests passed (including
34 existing R2 scorer + 40 new gate tests); 2 SQL modules skipped for missing DuckDB.
238 API integration tests passed on disposable PostgreSQL 16.2, including 6 new
capture tests. The existing Starlette/httpx deprecation warning remains. Ruff lint
and format, workflow/S02 contract validation, publication links and whitespace checks
passed. GitHub runs PostgreSQL 17, complete offline dependencies on Python 3.9/3.12,
browser and container checks separately on the pushed commit. No UI changed here.

This is one batched increment to open PR #24, still within the S05B stage-1 scope;
PR #23 remains the separate replay/merchant projection increment. Parent QA-02 stays
in Testing. The reports do not authenticate reviewers or certify a live model.

## Private author/reviewer handoff increment — 21 October 2026

- [x] Document human author/reviewer/owner and Codex/Claude responsibilities, with
  a separate disclosed model-assisted candidate lane; preserve accepted rules.
- [x] Supply three Claude handoff prompts without sending messages or hidden data.
- [x] Prepare local ignored 64-slot authoring form, four pending answer-review batches
  (15/15/10/24) and a private review document. No substantive cases or approvals filled.
- [x] Add explicit hash-bound freeze with completeness/readiness checks and exclusive
  file creation; regression acceptance R2-AC21–24.
- [ ] Independent substantive authoring, different human answer reviewer, actual
  owner batch acceptance and exact-revision freeze authorization remain external inputs.

Local checks on this increment: 20 new workflow tests; full offline suite 109 passed,
2 SQL modules skipped (DuckDB absent locally); Ruff lint/format, workflow/S02 contracts,
publication links and whitespace passed. No API/UI code changed and no additional
local runtime run was needed; CI rechecks the submitted head separately. The previous
39e6093 head passed all four checks (94 offline on each Python version, 238 PostgreSQL
API tests, 42 browser tests and container smoke). No model call, data freeze or real
human review occurred. This is another batched increment in PR #24/S05B, not another
completed Sprint or an increase to the published staffing estimate.
