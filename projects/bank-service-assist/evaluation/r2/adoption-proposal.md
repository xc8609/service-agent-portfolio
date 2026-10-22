# R2 evaluation and advancement gates — owner-approved candidate baseline

**Deferred qualification protocol (22 October):** these previously accepted gates remain unchanged but are not prerequisites for the current [portfolio milestone](portfolio-scope.md). The smaller exercise does not qualify as passing this protocol.

21 October 2026 · **R2-G01 accepted by the owner on 21 October 2026; corpus/run manifest not frozen and evaluation not executed.**
[Answer packet](owner-review.md) · [QA-02 story](../../../../docs/backlog/story-cards.md#qa-02).
These numbers are owner-approved portfolio experiment choices, not industry standards or
claimed bank risk tolerances. Approval permits evaluation planning, not API spend,
public exposure, automatic actions or a qualified production release.

## Decision to be supported

Does a bounded, staff-reviewed Agent add narrative understanding over a simpler
baseline without losing correctness or access controls? Passing can support a
**controlled synthetic pilot recommendation**, subject to real-runtime/provider
qualification and owner UAT. It cannot by itself authorize production or establish
cost savings. The existing manual/decision-table workflow remains usable regardless.

## One preregistered evaluation design

- Keep QA-02's 100-family plan: 60 development / 40 held-out scenario families,
  plus 24 separately reported critical cases. This document does not claim those
  cases exist. The present ten visible cases cover only six development families.
- In the 40 held-out quality cases, use one primary case per family: **30 narrative,
  10 structured**. This increases narrative coverage from the earlier minimum 24/40
  proposal while preserving the structured comparison. Record the reason before freeze.
- The 24 critical challenge cases have distinct case IDs from the quality set and
  cover identity, scope/authority, unsupported conclusions, stale evidence and source
  injection. Family overlap within held-out material is declared, not counted as
  independent evidence. Never put a related development variant in held-out material.
- Inventory exposure to the original pilot, all public R2 examples, prompts and
  prior tuning. Exclude their families/paraphrases from fresh hold-out selection.
  Broad capability coverage is not proof of a new scenario family: an independent
  reviewer must justify materially distinct causal situations. Renaming a public
  family does not restore independence. If genuinely fresh coverage cannot be built,
  report development regression evidence and defer a new hold-out claim.
- Use independent human authorship/review where available, with provenance and
  model assistance declared. The owner reviews expected outcomes. An Agent-written
  candidate or owner-approved public example is not an independently hidden test.
- Freeze prompts, answer keys, split/family manifest, rubric, runtime/tool schemas,
  model route fingerprint, baseline configuration, run count and gates before runs.
  Keep answer keys and future customer events outside model-visible prompts.

## Approved candidate gates (all must pass)

| Gate | Preregistered calculation / limit | Failure consequence |
|---|---|---|
| G1 · critical correctness | All 24 challenge cases pass; zero confirmed critical violations anywhere in the 64-case run | No advancement; retain manual/template mode and investigate |
| G2 · useful answers | At least 36/40 quality cases pass (90%); narrative at least 27/30 (90%) | Improve on development evidence; do not claim adoption |
| G3 · incremental narrative value | At least 3 additional narrative passes out of 30 (10 percentage points) against the baseline locked after development comparison; count paired wins minus losses | Prefer simpler baseline or narrow the use case |
| G4 · preserve structured capability | Agent passes at least as many of the 10 structured cases as the locked baseline; report every paired regression | No broad advancement; investigate regressions before any narrower proposal |
| G5 · scoring uncertainty | After complete first-pass review: at most 2/40 quality cases need scoring review (5%); before final decision: resolve all outstanding judgments across 64 cases | Hold decision while unresolved; report first-pass rate even after resolution |
| G6 · runtime and provenance | Actual tools/permission checks, citation boundaries, evidence freshness and DB postconditions pass; configuration and artifact hashes match the evaluated run | Semantic text scores cannot qualify the runtime or changed route |

Important distinctions:

- Missing/invalid outputs fail and stay in their declared denominator. A scorer-uncertain
  answer stays in the denominator with no pass credit (R2-S03). No favourable filtering.
- A quality failure in a critical challenge case blocks G1, but is not relabelled as a
  critical *violation*. Report both challenge pass counts and violation counts.
- G5 is outstanding **scoring** uncertainty after every case has been reviewed. All
  valid prose currently requires semantic review. It is not a claim of 5% human labour,
  automated approval or a low customer/specialist referral rate. Missing reviews are
  incomplete execution, not evidence that the model is uncertain.
- Review-rate resolution must use new evidence, not pressure a reviewer to mark pass.
  Preserve first-pass and final review artifacts. If the review ceiling is exceeded,
  fixing the rubric after seeing held-out outputs requires a new selection experiment;
  it cannot retrospectively make this gate pass.
- G3 is a descriptive pilot hurdle, not statistical significance or proven ROI. A
  count advantage cannot compensate for any critical failure. Publish denominators,
  paired wins/losses and family-level limitations rather than a standalone average.

## Fair comparison and repeated runs

Evaluate manual/templates or decision table, retrieval baseline and bounded Agent
with identical available facts, permissions and retrieval corpus. Do not give one
system the hidden expected recognition or future customer response. Select and lock
the stronger simpler baseline on development evidence, with its tie-break specified,
before looking at hold-out outputs. The same owner-reviewed rubric applies to all.
Evaluate manual operator effort separately from deterministic template output.

Require **three actual independent model generations per frozen case**, no prompt or
provider changes between runs, no best-of-three selection. Apply G1–G6 to each run,
and publish all runs plus aggregate counts and ranges. This is 192 Agent outputs
(64 x 3) per candidate route, not 192 independent scenario families. Deterministic
baselines may run once if their repeatability is verified; identify reused baseline
results instead of claiming extra independent observations.

If budget or access allows only one generation, label it exploratory; do not silently
relax the repeated-run gate. The first candidate is one provider/route, not a vendor
competition. Subsequent tuning makes exposed cases regression data; a new selection
claim requires fresh hold-out evidence. Synthetic replay validates engineering, not
three independent model generations or live API latency.

## Qualification and business evidence remain separate

No real API calls are authorized by this gate approval. Provider/protocol compatibility,
retention controls, synthetic projection, request/token/spend ceilings and kill switch
must be selected and verified for the exact route before API qualification. Those
operational limits remain unapproved, so passing text gates cannot enable a route.
Keep code/provider/prompt/schema/corpus/rubric fingerprints in the eventual report.

Measure actual runtime latency, failure counts and model cost when available; never
substitute replay speed or a subscription run for API cost. Preregister the route's
latency/budget limits before claiming it qualified. Keep NFR/accessibility and deployment
acceptance separate. This packet neither implements nor certifies those capabilities.

Run the workspace-without-AI benefit study separately (BR-01). Only after qualification,
compare the same workspace with/without the Agent using paired, counterbalanced tasks.
Record lookup/handling time, errors, draft edits and review effort. Small samples support
descriptive results, not generalized savings. No positive model gate is a savings result.

## Execution checklist and accountable evidence

| Order | Work and owner role (simulated allocation) | Evidence / exit |
|---|---|---|
| 1 · completed business decision | BA prepared answer packet and gates; project owner accepted R2-A01 and R2-G01 on 21 October | Answer intent and entire candidate-gate package approved; technical execution and model qualification remain pending |
| 2 · before freeze | Independent author and BA/QA construct provenance/family inventory and fresh cases; owner adjudicates keys | 60/40 family inventory, 24 critical cases, exposure audit and split hashes; stop if independence unsubstantiated |
| 3 · execution readiness | Developer/QA connects outputs from real runtime to the rubric; locks baselines/configuration; confirms access and budget | Real trace and postcondition capture plus route/run manifest; no model activation from this document |
| 4 · evaluate once frozen | Execute every scheduled run, retain failures, record reviewer observations with output/corpus hashes | First-pass and final reports, paired baseline comparison, gates reported individually |
| 5 · decide | Owner reviews go / narrow / no-go recommendation and remaining qualification/UAT gaps | Explicit decision; default remains manual/template mode |

This is the remaining R2 work inside the proposed S05B stage-1 increment in
[PR #23's plan](https://github.com/xc8609/service-agent-portfolio/blob/cef7ae9aba5efdc63c9b004e0e804928c9056dab/docs/backlog/validation-next.md),
not another completed Sprint or additional staffing claim. Review/data/access waits
are dependencies. Reconcile effort and dates when author/reviewer availability and
route are known; do not silently add a second full estimate to the existing plan.

The current `r2_score.py` remains a development scorer: `adoption_eligible: false`.
The reviewed increment adds `r2_experiment.py` for these three-run calculations and
`bank_api.agent.evaluation_evidence` for actual runtime/DB capture. See the
[experiment guide](experiment-guide.md) for contracts, commands and limits. Neither
local hashes nor declared reviews authenticate provenance. Independent data, actual
API execution, adjudication and qualification remain pending; no gate result is
claimed from the engineered regression tests.
