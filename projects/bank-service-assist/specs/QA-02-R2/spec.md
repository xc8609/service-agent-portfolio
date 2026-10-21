# QA-02-R2 — score confirmed narrative rules without hiding uncertainty

Increment of QA-02, not a new independent product. Trace: BR-01 lookup pain,
DEV-03 recognition, DEV-08 evidence/draft boundary and QA-02 fair evaluation.
Role evidence: BA decision/rubric design and developer reproducible offline validation,
grounded in the owner's service-desk experience. No measured efficiency claim.

As the portfolio owner, I want a correct clarifying turn distinguished from business
resolution and unresolved scoring review, so a plausible final answer cannot conceal
unsupported recognition, a false fraud conclusion or unauthorized disclosure.

Confirmed rules: R2-D01 explicit confirmation before recognition changes; R2-D02
unfamiliar descriptor/familiar amount does not establish fraud or recognition; R2-D03
controlled read-only original descriptor with source/version and untrusted-text boundary.
The dated source record is in
[PR #23 at cef7ae9](https://github.com/xc8609/service-agent-portfolio/blob/cef7ae9aba5efdc63c9b004e0e804928c9056dab/projects/bank-service-assist/specs/QA-02/owner-review.md).
R2-S01 now accepts correct clarification as turn-pass, business still awaiting_customer.
R2-S02 (owner confirmed 21 October) makes unsupported recognition/fraud assertions
critical failures even when the next step is correct. R2-S03 (owner confirmed 21 October)
retains undecided scoring reviews in the denominator without pass credit and reports
their rate separately; uncertainty alone is not a critical violation. R2-S04 quality
failure grading and numerical adoption gates remain pending owner review.

Deliver ten visible development cases, independent reviewer observations, a Python 3.9
offline scoring CLI and regressions. No new hold-out, model call, runtime integration,
financial action or complete QA-02 acceptance. [Design](design.md), [tasks](tasks.md),
[acceptance](acceptance.md), [rubric and cases](../../evaluation/r2/README.md).
