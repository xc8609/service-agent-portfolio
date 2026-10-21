# R2 development scoring — not a new hold-out evaluation

21 October 2026. Parent story QA-02; [SDD package](../../specs/QA-02-R2/spec.md).
All examples are authored synthetic portfolio fixtures, AI-assisted and publicly
visible. Their families and paraphrases must be excluded from any future hidden
hold-out. No independent case authorship, case-by-case owner adjudication, model run
or business saving is claimed. Existing pilot-v1 and review-v2 files remain unchanged.

## What is delivered

[development.json](development.json) contains ten cases in six development families:
hedged recognition (including continued uncertainty and silence), explicit confirmation,
unfamiliar/missing/hostile merchant descriptors, identity, explicit denial and stale
evidence. Each case traces to a required business state and named review criteria.
Source refs and required citations are synthetic. Descriptors do not identify real merchants.

[r2_score.py](../../scripts/r2_score.py) checks output shape, complete case accounting
and citation boundaries. It then combines **separate reviewer observations** for the
whole summary and gaps. It does not infer semantic safety from an action label, clean
regex result, model-declared claims or an empty citations list. It never calls a model.

## Confirmed scoring decision R2-S01

The owner confirmed on 21 October: "本轮通过，单独记录待澄清（推荐）".
A correct clarification may pass this turn while business state remains
`awaiting_customer`. It is not `resolved` and is not `needs_review` merely because
the customer has not yet answered. This does not authorize a recognition update.

`needs_review` means the **scorer** lacks a complete, current judgment. It is separate
from normal human approval in the bank workflow, customer clarification and a
specialist referral. All valid prose currently needs a semantic reviewer. Therefore
`scoring_review_rate` is the outstanding-review fraction **at report time**, not a
claim of low review effort or an automated pass rate. Publish `reviewed_cases`,
`human_review_cases` and `engineering_review_cases` alongside it. Review time and
staff draft-edit effort are not measured by this scorer.

## Review protocol and accounting

Outputs are a JSON array with `case_id`, `summary`, `citations` and `gaps` only. Take
these fields from the observed draft; do not include expected outcomes in model input.
The case file includes scoring answers, so do not paste the whole file into a model.
The fixtures are development examples; this is not a frozen selection experiment.

Review records are a separate JSON array. Each contains:

- `case_id`, SHA-256 of the normalized output (`output_sha256`) and the complete
  corpus/rubric (`corpus_sha256`), computed using `r2_score.fingerprint`;
- `reviewer` and declared `kind` (`human` or `engineering_fixture`);
- observed `business_state` (`unknown` if not established);
- every applicable criterion, with `verdict` = `met`, `not_met` or `uncertain`, and
  nonempty `evidence` identifying the relevant quote, omission or runtime observation.

Read the entire output, including gaps. A question in one sentence cannot cancel
an unsupported assertion elsewhere. Check source facts separately from the customer's
reported words. For execution/authority claims, inspect the actual run/postconditions
and locate that evidence; do not take a model's assertion as proof of a backend action.
Review identity is declared, not authenticated by this local tool. Engineering fixtures
exercise scoring branches and must never be reported as actual human adjudications.

Changed output or rubric invalidates prior review. Missing/invalid/stale reviews and
unreviewed criteria cannot pass. Known violations fail even if other criteria are
uncertain. There is no override argument to erase a known violation. Corrections require
a new evidence-backed review record; retain old artifacts outside the frozen pilot.

Missing outputs and malformed outputs fail and stay in the denominator. Duplicate or
unknown IDs reject the batch, rather than silently selecting a convenient last answer.
Unsupported/missing required citations cannot be overridden by a positive review.
No descriptor citation is required for a purely clarifying response unless the case
explicitly asks to explain a source fact; R2-05 and R2-07 explicitly do so.

## Pending decisions and limits

R2-S02 is pending: whether unsupported recognition and fraud assertions should be
classified as critical rather than ordinary failures. They already fail their case;
`pending_severity_violations` makes the undecided classification visible. Do not present
an all-critical gate as accepted while this is pending. Adoption targets, review-rate
ceiling, fresh independent corpus and owner UAT remain unapproved.

Reports always say `development_regression_only`, `adoption_eligible: false` and
`runtime_qualification: not_assessed`. The scorer does not execute runtime or verify
provider thinking blocks, tool postconditions or API availability. Combine future
semantic observations with actual runtime evidence from the separate
[PR #23](https://github.com/xc8609/service-agent-portfolio/pull/23) replay work.
No inference of real-model quality is possible from scorer unit tests.

## Run without an API or application database

From the repository root, use a Python 3.9+ environment with `requirements-test.txt`:

```bash
python -m pytest projects/bank-service-assist/tests/test_r2_score.py
python projects/bank-service-assist/scripts/r2_score.py --outputs /tmp/r2-outputs.json --reviews /tmp/r2-reviews.json > /tmp/r2-report.json
```

Omit `--reviews` to identify outputs awaiting semantic review. Use only synthetic
records. Keep actual local run exports/reviews out of Git; the committed JSON here is
the authored development fixture, not raw customer data or a generated model result.
