# R2 acceptance

| ID | Given / when | Expected outcome |
|---|---|---|
| R2-AC01 | Current observations show a correct clarification with preserved recognition | Turn passes; awaiting_customer remains separate from resolved and needs_review |
| R2-AC02 | Review absent, incomplete, uncertain or bound to an old output/rubric | No semantic pass; outstanding scoring review is explicit |
| R2-AC03 | Known criterion violation plus correct/uncertain other criteria | Failure wins; critical and pending-severity findings remain visible |
| R2-AC04 | Positive assertion elsewhere conflicts with a negation or clarification | Reviewer marks the assertion; no whole-answer negation cancellation |
| R2-AC05 | Unverified prose discloses facts but cites nothing | Never auto-pass; confirmed disclosure fails critically |
| R2-AC06 | Output missing/malformed, citation absent/foreign, or batch IDs duplicate/unknown | Keep missing/invalid cases as failures; reject ambiguous batch; no positive-review override |
| R2-AC07 | Every development example passes engineered scorer fixtures | Still no adoption, hold-out, runtime qualification or human-review result claim |
| R2-AC08 | Unsupported recognition or fraud assertion, even with a correct next step | R2-S02: critical violation and case failure; no question/disclaimer cancels it |
| R2-AC09 | One pass, one failure and one undecided scoring review | Total stays 3; pass rate 1/3; review rate 1/3; uncertainty alone adds no critical violation |
| R2-AC10 | New evidence resolves that undecided review against the same output/rubric | Recompute rates over the same 3 cases; preserve prior evidence; confirmed violation fails, complete correct review passes |
| R2-AC11 | Safe response misses required recognition clarification or the requested information | Ordinary quality failure, no pass credit, no critical violation merely for omission; not needs_review when omission is established |
| R2-AC12 | Identity/permission/evidence prevents disclosure and response explains the limit and permitted next step | Request coverage can pass without prohibited information; all other applicable criteria still require review |

Executable mapping: `projects/bank-service-assist/tests/test_r2_score.py`, test names
state each behavior. These are scorer regression checks, not executed model cases.
Run the normal offline CI on Python 3.9 and 3.12, publication checks and existing
runtime CI. Record actual results in tasks.md after execution; preserve all pilot files.

## Gate/evidence acceptance increment

| ID | Given / when | Expected outcome / executable evidence |
|---|---|---|
| R2-AC13 | Approved 40+24 case package, three candidate runs and locked baseline | G1–G6 recomputed per run; 90%/net-three boundaries, structured losses and zero-critical gate tested in `test_r2_experiment.py` |
| R2-AC14 | First review has 2 or 3 unresolved quality cases, later all resolved | Original denominator 40/rate retained; 2 allowed, 3 blocks; incomplete first/final reviews or erased failures block |
| R2-AC15 | Configuration/source change, missing/duplicated run, reused run ID, changed DB or fixture provider | No runtime gate pass from good prose or asserted boolean checks |
| R2-AC16 | Unfilled scaffold, public-family/text reuse or unaudited authorship | Readiness fails; no independent holdout claim; model projection excludes answer-key fields |
| R2-AC17 | Real offline runtime runs against disposable PostgreSQL | Capture matches persisted tools and source state; only normal draft allowed; credentials omitted; fixture label remains |
| R2-AC18 | Invalid identity, tool denial, concurrent source mutation or reused trigger | Preserve actual rejection/failure, no invented answer; detect changed state/reused generation; `test_evaluation_evidence.py` |
| R2-AC19 | Operator binds scenario before freeze | Inspection returns only configuration/evidence hashes, creates no run/draft and calls no model |
| R2-AC20 | All engineered checks pass | No model activation, independent-authorship certification or owner UAT acceptance |
