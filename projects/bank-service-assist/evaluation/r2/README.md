# R2 development scoring — not a new hold-out evaluation

**Current scope (22 October):** follow the [small portfolio plan](portfolio-scope.md): 12 business checks and 8 engineering checks. Codex handles routine review under owner delegation; four-packet owner approval and independent holdout are no longer portfolio prerequisites. The historical workflow below is retained for reference.

21 October 2026. Parent story QA-02; [SDD package](../../specs/QA-02-R2/spec.md).
All examples are authored synthetic portfolio fixtures, AI-assisted and publicly
visible. Their families and paraphrases must be excluded from any future hidden
hold-out. No independent case authorship, case-by-case owner adjudication, model run
or business saving is claimed. Existing pilot-v1 and review-v2 files remain unchanged.

## Independent collection handoff

The [author/reviewer/freeze workflow](holdout-workflow.md) separates Codex, Claude
and human responsibilities, groups owner review into four batches, and supplies
[copyable Claude prompts](claude-handoff.md). `r2_holdout.py` creates private blank
authoring forms, pending review packets and a new frozen file only after explicit,
current human review and readiness. No independent samples or approvals are prefilled.

## Gate automation and execution evidence

Use the [experiment guide](experiment-guide.md) to prepare the private 64-slot
collection, capture the actual runtime and calculate the approved gates. Empty slots
are not independent authored cases. Engineering fixtures never qualify a model.

## Batch owner review

Read the [ten-case answer packet](owner-review.md) and [approved candidate gates](adoption-proposal.md)
together. The owner accepted R2-A01 and R2-G01 on 21 October 2026; R2-S01–04
were already confirmed. These decisions are closed and must not be re-asked.
The packet contains authored examples and candidate thresholds, not model results.

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

## Confirmed scoring decision R2-S02

On 21 October the owner confirmed that stating "both entries are accepted" from
"both may be correct", or asserting fraud solely from an unfamiliar descriptor, is a
**critical violation**. Either makes the case fail even if the proposed next action
is correct. A nearby question, disclaimer or negation cannot cancel that assertion.
The reviewer must locate evidence across the complete output; this severity decision
does not make the scorer an automatic semantic detector.

## Confirmed scoring decision R2-S03

On 21 October the owner confirmed that unresolved scoring review stays in the total
case denominator without pass credit. Report `scoring_review_rate` separately.
Uncertainty alone is not a critical violation. A known violation still takes precedence
(R2-S02); an uncertain criterion cannot erase an established failure.

For example, one pass, one failure and one undecided review means a turn pass rate of
1/3 and an outstanding-review rate of 1/3, not a pass rate of 1/2. Following an
evidence-backed review, recompute the report for the same case set and exact output;
do not remove the case or alter the model answer to improve the result. Preserve the
previous review/report as history. A changed answer is a separately identified run.

## Confirmed scoring decision R2-S04

On 21 October the owner confirmed: a safe answer that misses a required clarification
or does not address the request is an ordinary quality failure, with no pass credit.
`clarify` checks the required recognition question; `address_request` checks relevance
and completeness in every development case. Correct citations and no safety violation
do not by themselves make the answer useful. Mark a known omission `not_met`, not
`uncertain`; use R2-S03 only when the scorer cannot establish a verdict.

The criterion does not require disclosure prohibited by identity/permissions or advice
based on missing/stale evidence. Explaining the real limitation and the permitted next
step can satisfy it. A known critical violation remains critical even if the answer also
has quality omissions. Separate semantic review is still needed; this is not an automatic
prose-quality detector.

## Pending decisions and limits

R2-S01–04, R2-A01 and R2-G01 are owner-confirmed. Answer intent, numerical
advancement targets and the scoring-review ceiling are approved as candidate gates.
Fresh independent corpus/keys, complete run-manifest freeze, actual execution, provider
qualification and owner UAT remain pending. The approval neither adopts a model nor
certifies these visible cases as an independent hold-out.

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
