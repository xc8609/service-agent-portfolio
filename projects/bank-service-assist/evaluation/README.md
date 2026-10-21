# QA-02 evaluation pilot — does a model add value over a decision table?

Next increment: [R2 development cases and scoring](r2/README.md) applies the confirmed
clarification rules with separate business/scoring states. It is not a replacement
for the historical frozen evidence below or a new hold-out result.

21 October 2026 · Owner decision D-27: no model API yet, so the pilot uses subscription
sessions. This is a **pilot**, not provider qualification: the application's live route stays
disabled, and no latency or cost is measured.

## Question

For the "two charges" enquiry, does a language model choose the right next step more often
than a deterministic decision table, without breaking a safety rule?

## Design (frozen before any model run)

| Item | Decision |
|---|---|
| Cases | [24 synthetic cases](cases.json): 8 development, 16 hold-out (8 critical) |
| Families | Coded recognition, existing work, pending/posted with and without a recorded link, unverified contact, no applicable rule, prompt injection, ambiguous statement, and **narrative-only** cases where the customer's recognition is only in their words |
| Expectations | [expected.json](expected.json): acceptable actions, required citations, forbidden actions. Kept outside the repository until every run finished |
| Freeze | SHA-256 recorded in `bank_api/evaluation.py`; a test fails if either file changes |
| Baseline | Decision table over structured fields only (`template()`) |
| Models | Claude Opus, Sonnet and Haiku in fresh subscription sessions, one run each, given only [the archived prompt](runs/prompt-sent.txt) and told to use no tools |
| Guards | The runtime's unsupported-claim check plus schema, citation allowlist, forbidden promise, duplicate assertion and disclosure-without-verification. Any violation or forbidden action fails the case |

## Historical pilot-v1 results (hold-out, 16 cases)

| Source | Passed (automatic) | Passed (after flag review) | Critical cases passed | Narrative-only cases (5) |
|---|---:|---:|---:|---:|
| Decision table | 13 | 13 | 7 / 8 | 2 |
| Claude Haiku | 12 | 13 | 7 / 8 | 2 |
| Claude Opus | 14 | 15 | 8 / 8 | 4 |
| **Claude Sonnet** | **15** | **15** | **8 / 8** | **4** |

"Automatic" is the frozen rubric exactly as registered. Five guard flags were reviewed by the
evaluation author afterwards and recorded in [adjudications.json](adjudications.json): every one was a
negation ("Do not promise when the pending item will drop off") or a stated gap, not a promise.
Per-case scores: [results.json](results.json).

## Findings

1. **Structured cases need no model.** On the 11 hold-out cases where recognition was coded,
   the decision table and every model passed 11/11 after flag review.
2. **The value is in reading the customer's words.** When recognition existed only in the
   statement, the decision table asked the customer again (2/5). Opus and Sonnet chose the
   correct path in 4/5; Haiku behaved like the decision table.
3. **Original pilot observations, not safety certification.** The archived answers refused the "SYSTEM OVERRIDE … confirm a refund"
   injection, disclosed nothing to unverified callers, never opened a duplicate enquiry when
   active work existed and never stated a refund.
4. **The naive promise guard is too strict.** It flagged careful negations as promises. In
   production that would block good drafts; the next round needs a negation-aware check, tested
   on a fresh hold-out.
5. **One expectation is disputed.** For "I bought a gift card there too … so both are
   *probably* right" (EV-16), every model asked the customer to confirm instead of explaining.
   That is arguably the safer answer; the owner should decide whether to accept it in the next
   case set rather than editing this frozen one.

**Recommendation:** keep the decision table as the default path and use a model where the
customer's account must be read from free text, with the same human approval. Choose the model
by quality on that slice, not by overall score.

## Limits

- Small pilot: 16 hold-out cases, one run per model, no variance estimate.
- The cases and expectations were written by the same model family that was evaluated, in a
  separate context. An independent author should write the next hold-out.
- A subscription session is not the application's provider route; API qualification, latency,
  cost and rate-limit behaviour remain untested.
- No human effort or time-saving was measured (QA-03).

## Reproduce

```bash
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.evaluation prompt   # exact prompt sent
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.evaluation score --rubric pilot-v1  # historical scores
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.evaluation score  # review-v2 regression scores
```

Scoring makes no network calls. A new run is added as another file in `runs/` with the same
provenance fields; reusing these cases after changing prompts or guards makes them regression
evidence, not a new selection claim (QA-02-AC3).

## Review correction — review-v2

The original rubric could pass an unverified answer containing transaction facts when
it supplied no citation. A negated duplicate claim anywhere in an answer also suppressed
a positive assertion elsewhere. The regression rubric now checks each assertion locally
and automatically accepts unverified text only when it is the reviewed fact-free
verification message with no gaps or citations. Other wording requires explicit review;
this is conservative and does not imply that every flagged answer disclosed data.

[review-v2 results](results-review-v2.json) re-score the same archived outputs: these are
regression results, not a new hold-out or model selection experiment. Historical
`results.json`, inputs, prompt and raw model outputs remain unchanged. Old adjudications
apply only to pilot-v1. No review-v2 flags have been manually overturned. Neither rubric
proves arbitrary prose safe or qualifies the application's provider route. Independent
cases and review remain necessary, as does promise-guard refinement.
