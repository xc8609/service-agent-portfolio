# Private holdout: author, review in batches, then freeze

**Deferred for the portfolio milestone (22 October):** the owner selected a simpler, Codex-managed [portfolio evaluation](portfolio-scope.md). The independent-human and four-packet freeze process below is historical/optional; do not ask the owner to complete it before core delivery.

21 October 2026 · QA-02 / R2-A01 / R2-G01. **Preparation delivered; no new case,
answer approval or freeze has occurred.** [Operating guide](experiment-guide.md) ·
[Accepted gates](adoption-proposal.md) · [Claude handoff](claude-handoff.md).

## Who does what

| Work | Codex | Claude | Human owner / independent reviewer |
|---|---|---|---|
| Business contract, templates, validators, four review packets | Prepare from accepted rules; keep thresholds unchanged | Can inspect structure without hidden cases | No need to re-answer existing rules |
| New causal situations and evidence | Avoid authoring the scored hidden corpus: Codex has developed/tuned this system | Can assist drafting, labelled `model_assisted_candidate`; not independent human authorship | A human independent of system/prompt tuning supplies substantive case facts/intent; disclose prior exposure |
| Wording/formatting of human-authored material | Automate formatting without interpreting hidden answers where possible | May translate/format an already documented human case; preserve before/after and disclose model assistance | Author checks no causal facts or intended answers were introduced/changed |
| Independent answer review and family novelty | Check structural references/exact duplicates; cannot certify semantic independence | Optional critique, not replacement for the required human review | A different human checks evidence, policy applicability, answer boundaries, family novelty and leakage |
| Business acceptance | Assemble decision summary and record actual explicit decisions | List disagreements and alternatives; do not resolve them by inventing a bank rule | Owner accepts four batches, naming exceptions; accepts intent, not exact wording |
| Runtime preparation | Bind sources/configuration, validate setup and hashes; keep keys away from candidate model and tuning | May review setup machinery on development cases | Confirm business facts are faithfully represented; author/reviewer retain private keys |
| Freeze and execution | Execute only after recorded current review, complete readiness and explicit freeze decision | May audit completeness; cannot approve on owner's behalf | Authorize freeze once, for the identified revision; later API spend and adoption are separate |

If you author the cases yourself, a different human must review them independently;
you can still make the final business-owner decision. Alternatively, another person
writes them and you review the answers. Do not enter Claude/Codex as a human reviewer.
You do not need to find a second person merely to review this **workflow preparation**.
That dependency applies before claiming the independently authored, reviewed holdout.

## Two honest lanes, without silently changing the approved gate

**Independent-human lane:** human-written causal situations and expected reasoning,
with a different human reviewer and an exposure audit. Limited AI transcription or
translation is disclosed and compared with the dated original human draft. A fresh
human label is not enough: retain actual authorship evidence and exclude material
substantively generated from model suggestions or exposed/tuned answers.

**Claude-assisted candidate lane:** useful for development, test harness rehearsal
and a separately labelled cross-model exercise. Set `author_kind` to
`model_assisted_candidate`; retain conversation/model/version and who edited it.
Owner acceptance of a model-written key does not transform it into independent human
authorship. The current freeze gate blocks this lane. It can proceed as engineering
work while human authorship is arranged. Changing the evaluation claim/protocol would
need one later explicit batch decision; no threshold or independence rule changes here.

A new chat reduces direct context carryover, but does not establish independence of
model families or authenticated authorship. Do not use the current coding/review chat
that has seen pilot answers to produce a claimed hidden holdout. Do not copy model
outputs into answer keys. This is an evaluation of a scoped synthetic assistant,
not a real-bank population or a regulatory assurance exercise.

## Authoring contract: one record per stable slot

Use the ignored `evaluation/r2/private/` directory. The generator supplies 64 slots
and no substantive examples. An author fills the following in English; dated Chinese
human notes can be retained privately as original authorship evidence.

| Section | Required content |
|---|---|
| Source facts | `source_facts`: transaction states, selected scope, source relationships and existing work actually available; separate assertions from established facts |
| Customer and staff | `customer_statement` in the customer's own intended wording; `staff_request` defines the task; the model-visible `prompt` contains no key/future event |
| Access and knowledge | `authorization_state`, `knowledge_rules` with source/version and applicability; missing facts stay missing |
| Setup | `setup_recipe`: trusted commands/fixture mapping and expected source state; never bypass permissions to force a model call |
| Family | A family ID plus `family_novelty`: how the causal situation materially differs from prior exposure; names, amounts and synonyms alone are not new families |
| Answer key | `answer_intent`, `must_ask`, `must_not_assert`, `next_step`, `citation_rationale`, `allowed_variation`; use an explicit "none, because ..." where applicable |
| Outcome | Expected business state, rubric criterion IDs with severity, permitted/required citations; a correct clarifying turn need not resolve the complaint |
| Provenance | Actual author/kind, independent human reviewer/kind, dated origin/review references, model assistance, exposure evidence; approval starts false |

Broad coverage should include evidence versus customer assertions, recognition
uncertainty, policy applicability, existing work, allowed next steps and trust/scope
boundaries. These are coverage themes, **not a claim of novel scenario families**.
The reviewer compares causal families with the public pilot and R2 after independent
writing. If 40 fresh quality families cannot be justified within this narrow business
scope, report that limitation; do not pad the count or rename exposed variants.

Critical challenges must distinguish semantic robustness from deterministic negative
security tests. A denied request that never reaches the model is useful engineering
evidence, but cannot be counted as one of the required independent model answers.
Use only executable, permitted contexts for the 64 model-scored cases. Keep negative
precondition tests separately; do not expose protected data to manufacture a result.

## Four packets, one consolidated owner response

| Batch | IDs / size | Review emphasis |
|---|---|---|
| A | narrative-01–15 / 15 | Evidence, uncertainty, necessary clarification and permitted next step |
| B | narrative-16–30 / 15 | Remaining independent narrative families; same review dimensions |
| C | structured-01–10 / 10 | Explicit facts, scope and baseline-equivalent correctness |
| D | critical-01–24 / 24 | Every safety boundary and expected behaviour; no sampling-away of failures |

The owner can answer once: **"A/B/C/D accepted except [IDs + reason]; freeze not yet
authorized."** Or identify whole batches needing changes. The example is a response
format, not recorded approval. Every case must be readable and reviewed; batching is
not blanket acceptance of unseen keys. Code/configuration hashes are checked by the
operator rather than read out one at a time to the owner.

Codex consolidates exceptions into one change list: ID, disputed fact/intent, proposed
resolution, affected family/criterion/setup and whether it creates a new business
rule. Established rules stay closed. Escalate only genuine new ambiguity, an actual
scope conflict or a proposed protocol change. Return changed items plus a short impact
summary in the next batch. Don't repeatedly send 64 individual questions.

Before freeze the recorded review must bind the exact final manifest. Editing facts,
keys, rubric or runtime binding makes that review stale. Preserve earlier packets;
carry forward unchanged decisions only by an explicit consolidated final revision
confirmation, not by silently substituting hashes. Freeze is a separate one-time
owner decision identifying that final revision, after technical dependencies are ready.

## File workflow and commands

From repository root, Python 3.9+ with test dependencies:

```bash
python projects/bank-service-assist/scripts/r2_holdout.py prepare --out projects/bank-service-assist/evaluation/r2/private/authoring-v1.json
# The author and independent reviewer complete the private file, retaining dated origins.
python projects/bank-service-assist/scripts/r2_holdout.py review --manifest projects/bank-service-assist/evaluation/r2/private/authoring-v1.json --out projects/bank-service-assist/evaluation/r2/private/answer-review-v1.json --markdown projects/bank-service-assist/evaluation/r2/private/owner-packet-v1.md
```

The packet contains source/answer data as literal JSON under each case heading. It
is for private human review, never candidate model input. `answer-review-v1.json`
starts with blank identity/time, four pending decisions and `freeze_authorized: false`.
Record `reviewer_kind: human`, the actual owner name, timestamp, batch decisions and
rationale only from actual review. Put unresolved `{case_id, reason}` items in the
batch's `exceptions`. No exception may remain at freeze.

After author/reviewer provenance, owner-reviewed keys, 60/40 family allocation,
exposure audit, baseline selection and runtime/configuration bindings are complete,
obtain explicit freeze authorization for the exact manifest and record it. Then:

```bash
python projects/bank-service-assist/scripts/r2_holdout.py freeze --manifest projects/bank-service-assist/evaluation/r2/private/authoring-v1.json --review projects/bank-service-assist/evaluation/r2/private/answer-review-v1.json --out projects/bank-service-assist/evaluation/r2/private/frozen-v1.json
python projects/bank-service-assist/scripts/r2_experiment.py check --manifest projects/bank-service-assist/evaluation/r2/private/frozen-v1.json
```

Freeze returns a new file with source-manifest/review hashes and a timestamp, then
runs the existing readiness checks. It rejects model authorship/review, incomplete
keys, stale decisions, changed membership, pending/excepted batches, missing locks
and exposed families. Files are exclusively created; an existing file is not
overwritten. This is accidental-overwrite protection, not immutable storage or
cryptographic authentication. Privileged operators can still falsify local files;
actual authorship and review evidence must be audited.

Once evaluated, do not repair a case/key after seeing model results and continue
calling it untouched holdout. Retain the historical report, document invalidations
and create a separately identified experiment. If a developer must inspect a hidden
case to debug/tune the system, record that exposure and retire the affected family
from future selection claims. The exact model-visible inputs and keys remain out of
GitHub/Trello; public updates contain workflow, aggregate status and evidence hashes.

## Ready for the next handoff

Codex has prepared the schema, tools, instructions and testable gates. No new answer
approval is requested now. The next external inputs are **substantive human-authored
cases and a different human reviewer**, or explicitly labelled Claude-assisted
candidates for rehearsal. The owner later receives four populated packets together,
then one final freeze-readiness summary. API route/budget and actual model execution
remain separate dependencies; they are not authorized by this preparation.
