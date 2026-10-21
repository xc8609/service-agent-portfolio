# R2 delivery tasks

- [x] Record confirmed business rules and R2-S01 scoring decision.
- [x] Author ten public synthetic development cases with family and criteria trace.
- [x] Add offline scoring, case accounting, hash-bound review and separate business states.
- [x] Add failure-path regressions including self-certification, disclosure without citations,
  mixed positive/negative prose, duplicate IDs, missing outputs and stale review.
- [x] Record local checks; PR CI is checked separately on the submitted commit.
- [ ] Owner decides R2-S02 critical severity; other grading thresholds remain pending.
- [ ] Independent author/reviewer supplies new hidden families before any hold-out freeze.
- [ ] Execute actual runtime/model runs and evidence-backed human adjudication.

No task here marks parent QA-02 or an entire Sprint Done. The existing model qualification,
owner UAT and benefit-study gates remain separate. This PR is independent of unmerged
PR #23 at code level; it references that decision record rather than copying runtime work.

Executed 21 October 2026: 28 new scorer regression tests passed. The complete local
offline suite had 43 passes and two SQL modules skipped because the application venv
lacks DuckDB. Ruff lint/format, publication links and whitespace checks passed. CI
installs the full offline dependencies for Python 3.9 and 3.12. No actual model output,
human adjudication, database runtime test or benefit study was executed in this slice.

Scheduling: this is part of the proposed S05B QA-02 stage-1 work in PR #23, not an
additional completed Sprint or a new cumulative estimate. Pending scoring decisions
block corpus/adoption freeze, not these independent scorer engineering checks.
