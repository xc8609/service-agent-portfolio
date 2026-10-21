# R2 delivery tasks

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
- [ ] Owner adjudicates R2-A01 answer expectations and R2-G01 gate proposal.
- [ ] Preregister approved numerical adoption targets and review-rate ceiling before any freeze.
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
additional completed Sprint or a new cumulative estimate. Pending scoring decisions
block corpus/adoption freeze, not these independent scorer engineering checks.

Batch-review packet check, 21 October 2026: documentation-only increment; public links
passed (407 files / 787 links); the unchanged local offline suite passed 49 tests
with two SQL modules skipped for missing DuckDB. It adds no
model run, automated adoption gate or reviewed answer approval.
