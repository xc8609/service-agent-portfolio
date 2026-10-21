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
