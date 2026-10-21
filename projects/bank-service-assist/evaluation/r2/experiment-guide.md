# R2 experiment preparation and runtime evidence

21 October 2026 · QA-02 / R2-G01. Engineering implementation; **no independent
hold-out or live-model result exists in this increment**. The accepted rules remain
unchanged. [Gates](adoption-proposal.md) · [SDD](../../specs/QA-02-R2/spec.md).

## Delivery and boundaries

`r2_experiment.py` checks readiness, scores three complete runs against a locked
baseline, and computes G1–G6. It uses the existing reviewer-bound scorer; it is not
a semantic judge. `bank_api.agent.evaluation_evidence` invokes the actual bounded
runtime, reads `agent_runs`/`agent_steps`, and compares database state before/after.
No new service, HTTP endpoint, database privilege or automatic bank action is added.

A successful gate report still says `adoption_eligible: false` and
`runtime_qualification: not_granted`. Hashes detect inconsistent artifacts; they do
not authenticate a human, prove independence, or prevent an operator fabricating a
whole bundle. Review provenance and source logs remain subject to accountable audit.
Offline/injected providers and injected transports are `engineering_fixture`, never
live-model evidence. No API has been called by this work.

## Prepare the hidden collection

Use Python 3.9+ with `requirements-test.txt` from the repository root:

```bash
mkdir -p projects/bank-service-assist/evaluation/r2/private
python projects/bank-service-assist/scripts/r2_experiment.py prepare > projects/bank-service-assist/evaluation/r2/private/manifest-draft.json
python projects/bank-service-assist/scripts/r2_experiment.py exposures > projects/bank-service-assist/evaluation/r2/private/exposure-inventory.json
python projects/bank-service-assist/scripts/r2_experiment.py check --manifest projects/bank-service-assist/evaluation/r2/private/manifest-draft.json
```

The last command **must exit 2** on the empty draft. It creates 30 narrative, 10
structured and 24 critical slots, not 64 independent authored cases. The directory
is ignored by Git. Keep manifests, keys, raw outputs, reviews and requests there;
publish only an explicitly reviewed aggregate report after execution. `prepare`
prints to stdout; choose a new filename rather than overwrite authored material.

The independent author and reviewer must:

1. Inventory all 60 development families and prior exposure. The tool always includes
   every family from the public pilot (including its former holdout) and R2 examples,
   and fingerprints their current sources. Normalized exact text/family matches fail;
   paraphrase/causal-family overlap still requires human audit, not just renamed IDs.
2. Supply 40 materially distinct quality families and 24 separately identified
   critical cases. Declare critical-family overlap. Each case needs a prompt, rubric
   criteria (including safety), expected business state, allowed/required citations,
   runtime evidence hash and author/reviewer provenance. The prompt is a planning
   stimulus: put the corresponding customer statement/request into the authorized
   synthetic scenario via the normal commands. The runtime still uses its own system
   prompt and evidence tools; this CLI does not paste answer keys into model input.
3. Record independent human author and a different reviewer, model assistance (write
   `none` when none), an independence evidence reference, and owner approval of each
   answer. The accepted ten development answers are not approval of these new keys.
4. Audit prompts for hidden answers and future events. `prompts --manifest ...`
   exports only `case_id` and `prompt`, but cannot detect answer leakage deliberately
   embedded inside the prompt text. `corpus --manifest ...` exports the scoring key;
   it must remain private and is **not model input**.
5. Select the baseline using development evidence; record configuration hash and
   selection/tie-break evidence. Bind actual source state using `--inspect-only`
   below, which does not generate an answer. Record actual owner approval and a
   timezone-aware freeze time only when the entire package is ready. Never fill
   identity/provenance fields merely to get a green checker.

The manifest is readiness-gated: no gate scoring against an unfrozen/incomplete
manifest, duplicate cases/prompts/quality families, public-source drift or incomplete
provenance. The current ten development cases cover six families; the remaining
60-family inventory and independent authored holdout are still work to do.

## Capture application execution

Python 3.12 and API dependencies are required only for capture. Use a dedicated,
quiescent synthetic `bank_demo*` PostgreSQL database with the repository's disposable
marker. Application connection uses `bank_app`; the separate trusted observer uses
an administrative test connection to hash state, never to execute model tools.
Observer and application must identify the same database. No production DB is allowed.

Provide `BANK_DATABASE_URL`, `BANK_TEST_ADMIN_URL` and `BANK_EVAL_AUTHORIZATION`
through the local environment, never a public file or command-line literal. The
request JSON uses the normal `/v1/assistant/run` contract: contact/case/work-item
scope, selected transaction IDs and a fresh `trigger_key`. Establish identity,
selection, statement and recognition through normal application commands first.

```bash
PYTHONPATH=services/api python -m bank_api.agent.evaluation_evidence --request /tmp/r2-request.json --case-id narrative-01 --inspect-only
PYTHONPATH=services/api python -m bank_api.agent.evaluation_evidence --request /tmp/r2-request.json --case-id narrative-01 > /tmp/r2-runtime.json
```

The second command runs the real runtime with the offline provider by default and
creates only its normal draft. It does not qualify G6's live-generation requirement.
Only after separate access/budget/protocol approval, a selected, qualified
`BANK_PROVIDER_CONFIG` and explicit `--allow-live` can invoke a configured API.
Use the same selected route during pre-freeze inspection and subsequent capture.
Existing route fingerprint and activation controls remain in force; this harness
neither bypasses them nor grants qualification. Provider protocol/thinking-block
compatibility and per-route budget/retention validation remain separate work.

Capture exports normalized actual draft fields, run ID, code/tool/route fingerprint,
source hash, timestamps, tool names, before/after hashes and checks. It exports no
credentials, raw database rows or tool conversations. Draft prose is still sensitive
to its inputs: **synthetic records only**, private output location.

Postconditions compare all public business tables. Audit/run/step bookkeeping is
excluded; existing proposals, revisions and operations must stay unchanged, and
new rows must belong only to this run's draft. Concurrent changes conservatively
fail evidence; use isolated case databases/snapshots, not a shared browser demo.
Reusing an idempotency key yields `fresh_run: false`; it is not another generation.
The final scope check uses the persisted run finish time and preserves original
runtime errors if reauthorization subsequently fails.

A denial before generation or failed runtime is exported as its actual status/error
with no invented answer. It receives no answer-pass credit and cannot satisfy the
approved three-generation gate. Negative authorization tests remain engineering
security evidence. Before freezing, ensure each model challenge has a permitted
scoped execution path; do not turn precondition denials into fake model answers or
silently weaken G6. The current ten public fixtures are not automatically replayable
requests: independent scenario setup and source/citation mapping are required.

## Bundle contract and scoring

`evaluate --manifest ... --bundle ...` accepts:

- `manifest_sha256`: `r2_score.fingerprint` of the complete frozen manifest.
- `baseline`: `configuration_sha256` matching `baseline_sha256`, nonempty
  `repeatability_evidence`, normalized `outputs` and complete `reviews` using the
  [review format](README.md#review-protocol-and-accounting).
- `runs`: exactly iterations 1, 2 and 3, each containing the capture artifacts in
  `evidence`, separate `first_reviews` / `final_reviews`, and timezone-aware
  `first_reviewed_at` / `final_reviewed_at`. Reviewer output hashes bind actual drafts;
  `corpus_sha256` is the fingerprint of `corpus_for(manifest)` (the `corpus` export).

Every applicable criterion requires an explicit first-pass observation, including
`uncertain` where appropriate. Preserve this first complete review even after a
later adjudication. Both stages require declared human review; final review must
resolve every criterion. Review timestamps cannot precede execution. A later review
cannot silently remove an earlier confirmed failure: investigate corrections and
retain a separately audited experiment record rather than edit history to pass.

```bash
python projects/bank-service-assist/scripts/r2_experiment.py evaluate --manifest /tmp/r2-frozen-manifest.json --bundle /tmp/r2-bundle.json > /tmp/r2-gates.json
```

Exit 0 means all arithmetic/evidence gates pass, **not model activation**; exit 2
means an assessed gate failed. Malformed contracts raise an error/nonzero exit.
Missing outputs remain in denominators; duplicate/unknown IDs reject the bundle.
Reports expose per-run counts, paired narrative wins/losses, structured regressions,
first-review rate and actual runtime-check counts. Three repeats must have distinct
run IDs, matching source/configuration hashes and executions after freeze. No best
run selection or averaged-away critical failure.

## Remaining release dependencies

Independent authorship and key review → baseline/configuration lock → exact-route
API compatibility and budget approval → corpus freeze → all scheduled executions
and human reviews → gate report → owner decision. Existing merchant descriptor
projection/replay work is in [PR #23](https://github.com/xc8609/service-agent-portfolio/pull/23);
this capture module uses the existing runtime and is independently reviewable.
No whole QA-02/Sprint completion, owner UAT sign-off, API result, deployment or
measured time/cost benefit is asserted by the engineering tests.
