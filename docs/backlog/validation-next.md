# Next validation increments — revised after independent review

21 October 2026. Planning revision, not owner acceptance or executed model evaluation.
Parents: QA-02, QA-03, DEV-08/09, QA-01 and OPS-02. Keep the existing small application.
REV-01/#21 and REV-02/#22 are merged; main `283a33b` passed all four checks.
The [delegated retest](../uat/2026-10-21-retest.md) remains separate from owner sign-off.

## Sequence, estimates and decisions

Person-days below are proposed incremental effort, including implementation/review;
QA is additional system testing. They replace the narrow 2–3 developer-day estimate
for the **whole** first stage; that estimate covers only the replay slice. No real
staffing or elapsed time is claimed. Refine after the first slice, not by adding
these values to the old forecast for the same work.

| Stage | Dev / BA / QA days (total range) | Exit or stop decision | Owner input before dependent work |
|---|---|---|---|
| 1 — runtime replay, independent evaluation design, layered claims, NFR checks | 7 / 1 / 2 (8–14) | Runtime postconditions and guard regressions pass; fresh set/rubric reviewed before freeze; missing review means no qualification claim | Expected outcomes, narrative accuracy target, review-rate ceiling |
| 2 — one real API route | 4 / 0.5 / 2 (5–10) | Exact route passes protocol and frozen quality/critical gates within budget; otherwise narrow/defer model use | Exact provider/model, permitted data handling, spend cap and stop switch |
| 3a — recruiter-facing synthetic demo | 3 / 0.5 / 1 (3–7) | Guest boundary, limits/reset, no real integrations, clear synthetic role simulation and observed public smoke | Host/account, spend cap, isolated vs explicitly shared/reset experience |
| 3b — production-like staging | 5 / 0.25 / 1.5 (5–10.5) | OIDC/role isolation, migration, restore and compatible-image rollback observed; otherwise no staging acceptance | Identity/access design, operator and RPO/RTO |
| 4a — workspace benefit without AI | 1.5 / 1 / 1 (2.5–6) | Paired tasks complete and actual effort/error observations reported; no benefit means revisit integration design | Task equivalence, participants, metrics and consent |
| 4b — incremental model benefit | 1 / 1 / 1 (2–5) | Compare the same workspace with/without qualified Agent; no gain means retain manual/template path | Frozen adoption rule and acceptable error/review burden |

Suggested two-week iteration overlay for the existing simulated 2–3 developer team:
S05B = 1 + preparation/execution of 4a (8.5 dev, 2 BA, 3 QA days);
S05C = 2 + 3a if their independent gates clear (7 dev, 1 BA, 3 QA days);
S06 = 3b + 4b (6 dev, 1.25 BA, 2.5 QA days). Hosting prep can overlap S05B;
API/participant/account waits are not development effort. Keep unready work backlog.
Voice and retail remain later. Two-week slots are forecasts, not delivery promises.

## Stage 1 story slices

### QA-02-R1 — replay actual runtime exchanges

As a reviewer, I need multi-turn responses to traverse the application runtime so
that successful one-shot prose cannot stand in for permitted tools and safe effects.

- Spec/design/tasks/acceptance: [QA-02 package](../../projects/bank-service-assist/specs/QA-02/spec.md).
- Deliver recording/replay provider, bounded normalized format, provenance and full
  request/schema digest, real PostgreSQL postcondition regressions, and use guide.
- Test tool order/arguments, citation allowlist, stale evidence, unauthorized access,
  step/time/cancel boundaries, replay exhaustion/drift and draft-only persistence.
- Current increment: synthetic engineering captures only. A subscription recording
  must be produced one turn at a time from actual runtime-provided tool results.
  Existing single-shot pilot JSON cannot be relabelled as a multi-turn recording.
- No replay score is a live API/latency/cost/model-quality result. No new HTTP route.

### QA-02-R2 — independent corpus and adoption rubric

Keep the original frozen pilot unchanged. Plan 100 distinct scenario families:
60 development / at least 40 held-out, plus 24 separately reported critical cases.
Keep paraphrases and related cases in one family/split. Propose at least 24/40
hold-out families with narrative-only recognition; owner reviews distribution before
freeze. Preserve structured cases to measure when the decision table is sufficient.

Use an independent human author where available; identify author/model assistance
and reviewer for every case. Owner adjudicates expected outcomes; the same model
generating and judging a case is not independent. Until that happens, the set is a
candidate, not a frozen independently validated hold-out. Store answer keys separately
from prompts during runs; publish only after the recorded freeze and evaluation.

Pre-register overall/narrative accuracy, all-critical-case gate, supported citations,
unsupported financial/duplicate claims, draft edits and manual-review rate. Existing
90% routine / all-critical proposal is not silently accepted; narrative target and
review ceiling need owner decisions. Report review-required outputs separately from
passes and violations: review rate = review-required / all eligible outputs, with
counts; missing runs and invalid outputs remain in their declared failure denominator.
Freeze before selection; tune on development only; budget permitting, three runs.

### QA-02-G1 — layered claims, not regex expansion

Version the normalized draft contract to carry explicit factual claims, cited
evidence, unresolved gaps and commitments separately. Deterministic code rejects
unsupported or unauthorized fields; prose/structured disagreement goes to review.
Model-declared structure is not proof and must never suppress a conflicting prose
assertion. Retain conservative regex checks as backstop, plus paired negation and
positive-assertion regressions and recorded human review. Sample safe-looking passes
as well as flagged outputs; report false positives/negatives and review workload.
Do not claim this slice is implemented by QA-02-R1.

### QA-01-NFR — accessibility and measured latency

Add axe checks for initial lookup, draft/edit, errors/stale state and assigned-work
views. Retain manual keyboard/focus/state-announcement review; automated scans alone
do not prove WCAG conformance. NFR-03's zero serious/critical automated violations
is a proposed gate. For NFR-02 measure scoped reads/commands on the synthetic dataset:
pre-register sample counts, warm-up, concurrency and host/database versions; publish
p50/p95/error counts. Existing proposed read p95 <= 1 s / command <= 2 s thresholds
need confirmation. Replay wall time is application overhead, never live model latency.

## API qualification corrections

- OpenAI reasoning continuation and Claude thinking/signature blocks need faithful
  provider-specific preservation in the wire adapter. The normalized replay format
  does not test that. Do not export opaque thinking blocks as business evidence.
- OpenAI strict-schema support is model-dependent: current docs specifically list
  `minLength`/`maxLength` among additional **fine-tuned** model restrictions. The
  page does not establish `uniqueItems` support. Run a contract probe against the
  selected model, retain full server-side validation, and document any wire-schema
  projection; do not delete domain validation to make an API call work.
- `store: false` is not Zero Data Retention. Confirm account/endpoint retention
  controls and eligibility; OpenAI ZDR requires prior approval. If ZDR is a mandatory
  owner gate and unavailable, stop that route; do not claim a setting enabled it.
- Only synthetic, positively projected data. Route fingerprint plus code, prompt,
  schema, evaluator and corpus hashes identify the evaluated configuration. Set request,
  token and spend caps and a tested disable switch. No automatic vendor fallback.

Official sources checked 21 October 2026:
[OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling),
[schema subset](https://developers.openai.com/api/docs/guides/structured-outputs),
[OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data),
[Claude thinking/tool continuation](https://platform.claude.com/docs/en/build-with-claude/thinking).

## Public demo versus staging

3a may deliberately simulate staff roles with fully synthetic data. Prefer per-visitor
isolated datasets and server-scoped guest sessions. An explicitly shared demo is an
alternative requiring clear disclosure and contention/reset handling. Either design
needs rate/resource limits, expired-session handling, secret-free logs, scheduled reset
with visible timing, and disabled bank/phone/paid-model integrations by default.
Labelling alone does not isolate concurrent users. This requires a reviewed demo mode;
the current local-only mode is not exposed unchanged. No banking identity claim.

3b replaces role simulation with real authentication and server-owned authorization.
Use expand/contract migrations: add compatible structures first, keep old image
read/write paths working during rollout, and remove structures only after old code
is retired. Test the exact previous image against the migrated schema. If incompatible,
use a rehearsed restore/roll-forward procedure; do not promise destructive down-migration
as rollback. Reconcile receipts, contact histories and audit chains after restore.

## Benefit study and acceptance

4a tests BR-01 now: a deliberately fragmented **simulated** multi-screen baseline
versus the integrated workspace, without model assistance. Match source information,
task difficulty and permissions. Use equivalent paired task variants; counterbalance
AB/BA order and record training, carryover, failures and assistance. Pre-register
lookup time, total completion time, navigation count, errors and handoff completeness.
Small samples support descriptive within-participant results only, not significance
or generalized bank savings. 4b applies the same design to workspace vs workspace+Agent
after qualification; report correction/review cost as well as speed.

Owner UAT signature stays blank until the owner actually reviews and signs. Delegated
assessment, technical tests, business rule approval and benefit-study participation
are separate records. Next business review asks for the R2 outcome matrix and adoption
thresholds; it does not repeat accepted D-17–D-25 workflow decisions.
