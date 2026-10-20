# BA-05 Requirements, story map and priority

Current elaboration: [workflow increment](../../docs/sprint-01/workflow-increment.md) adds FR-16–FR-22 and SC-23–SC-29. Requirements total is now 29; detailed workflow coverage is supplemental, not an implementation result.

Version 0.1 · 19 October 2026 · **Draft scope baseline for review**. The owner's primary pain is lookup; notes/follow-up support that service. Requirements below are proposed behavior, not implemented capabilities. [Decision log](../../docs/sprint-01/decision-log.md) · [Machine-readable register](../../docs/sprint-01/requirements.json).

## Activity to release map

| Activity | User task | Requirement | Story / capability | Release |
|---|---|---|---|---|
| Establish context | Open permitted customer/account/contact | FR-01 | DEV-02 / B01 | B0 |
| Understand concern | Select transactions, clarify reported facts | FR-02/03 | DEV-03 / B02 | B0 |
| Inspect previous work | Find current case and next step | FR-04 | DEV-04 / B04 | B0 |
| Find rule | Search applicable version and read evidence | FR-05/15 | DEV-05 / B03 | B0 |
| Explain | Review a supported answer and missing questions | FR-06/07/14 | DEV-08/09 / B05 | B1 |
| Record | Edit/approve truthful contact note | FR-08/11/13 | DEV-06 / B06 | B0 |
| Continue only when needed | Link existing work or assign next action | FR-09/10/11 | DEV-07 / B07 | B0 |
| Recover and evaluate | Manual fallback, instrumentation and quality/time comparison | FR-12, NFRs, DATA-01, MEAS-01 | DEV-10, QA-01/02/03, OPS / B08 | B0 → B1 |

B01–B08 are historical capability IDs in the architecture plan; DEV IDs are current delivery cards. Bank voice is B2; retail is R1. Do not mix their scope into bank acceptance.

## Requirement register

Every requirement has a portfolio-owner acceptance decision, drafted Given/When/Then condition, implementation story and planned verification ID. BA-06–09 must refine rules, full API/data schemas, performance workload and thresholds before dependent implementation. All rows are Draft.

### BR-01 business · Must · B1

Reduce active customer-information and applicable-rule lookup effort while preserving supported-answer quality.

Rationale: Primary owner-selected value; O-01/O-02. Source: E-02; rule: RULE-16; delivery: DEV-10, QA-03.

**BANK-AC-01:** Given Representative completes the same scenario with manual and assisted tools; when time and correctness are evaluated; then report paired active lookup plus verification time, completion outcome and errors without fabricating savings.

Planned verification: BANK-T-01. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-01 functional · Must · B0

Establish contact context from an authorized session before private customer/account/case lookup.

Rationale: Prevent unauthorized disclosure. Source: E-01; rule: RULE-01; delivery: DEV-02.

**BANK-AC-02:** Given a requested account is outside session scope; when a representative or agent requests it; then deny without exposing the other customer's existence or details.

Planned verification: BANK-T-02. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-02 functional · Must · B0

Let the representative clarify merchant, amount/currency/date or case reference and distinguish reported from verified facts.

Rationale: Lookup must identify the intended record. Source: E-02; rule: RULE-02; delivery: DEV-03, DEV-04.

**BANK-AC-03:** Given multiple transactions match incomplete wording; when a candidate record is suggested; then require selection/clarification and retain fact provenance.

Planned verification: BANK-T-03. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-03 functional · Must · B0

Display scoped transaction status, timestamp and evidence version without treating equal amounts as a confirmed duplicate.

Rationale: Support the duplicate-charge job. Source: E-04; rule: RULE-02; delivery: DEV-03.

**BANK-AC-04:** Given one matching entry is pending and another posted; when facts are displayed or summarized; then show both states and uncertainty without promising reversal/refund.

Planned verification: BANK-T-04. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-04 functional · Must · B0

Retrieve permitted case history, current status, owner and documented next action as of the enquiry.

Rationale: Support status enquiries without invented promises. Source: E-02; rule: RULE-04; delivery: DEV-04.

**BANK-AC-05:** Given a case has no recorded completion date; when the representative asks when it will finish; then state unknown ETA and the recorded next step.

Planned verification: BANK-T-05. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-05 functional · Must · B0

Search policy by product, jurisdiction, audience and effective interval; show policy ID/version/section.

Rationale: Return applicable evidence, not merely similar text. Source: E-03; rule: RULE-05; delivery: DEV-05.

**BANK-AC-06:** Given a candidate document belongs to the wrong product/audience/date; when search runs; then exclude it from authoritative evidence and expose any resulting gap.

Planned verification: BANK-T-06. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-06 functional · Must · B1

Present supported answer/proposed next step, supporting fact/policy references and unresolved questions separately.

Rationale: Make assistant output inspectable. Source: E-02; rule: RULE-05; delivery: DEV-08.

**BANK-AC-07:** Given a material fact or applicable rule is absent; when the assistant responds; then ask for clarification or manual review rather than fabricate the missing evidence.

Planned verification: BANK-T-07. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-07 functional · Must · B1

Invalidate affected proposals when a customer correction or source version changes.

Rationale: Prevent stale advice and writes. Source: E-02; rule: RULE-11; delivery: DEV-06, DEV-08.

**BANK-AC-08:** Given purchase recognition changes after a draft; when a new turn is recorded; then mark conflicting advice stale and use the manual risk path.

Planned verification: BANK-T-08. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-08 functional · Must · B0

Allow the representative to edit and approve a contact note; distinguish draft, approved and persisted states.

Rationale: Capture a truthful secondary service record. Source: E-01; rule: RULE-09; delivery: DEV-06.

**BANK-AC-09:** Given a representative edits the draft; when they explicitly approve the current version; then save only after current permission/version checks and return actual receipt.

Planned verification: BANK-T-09. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-09 functional · Must · B0

Create follow-up only for explicit unresolved work; link existing tasks before creating new ones.

Rationale: Avoid artificial case volume and duplicate work. Source: E-02; rule: RULE-06; delivery: DEV-07.

**BANK-AC-10:** Given the enquiry is answered and no additional action exists; when the contact is concluded; then save the contact without creating a new operational case/task.

Planned verification: BANK-T-10. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-10 functional · Must · B0

Require a valid owner/queue, reason, next step and review time for follow-up; report actual state.

Rationale: Do not orphan unresolved work. Source: E-01; rule: RULE-08; delivery: DEV-07.

**BANK-AC-11:** Given no valid receiving owner/queue is available; when follow-up is proposed; then do not label it assigned; preserve work and surface the supervisor exception.

Planned verification: BANK-T-11. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-11 functional · Must · B0

Keep complaint-signal review independent of contact closure and new-task need.

Rationale: Do not lose dissatisfaction while simplifying workflow. Source: E-02; rule: RULE-07; delivery: DEV-06, DEV-07.

**BANK-AC-12:** Given a customer expresses dissatisfaction but the factual enquiry is answered; when the representative concludes the contact; then preserve complaint-review signal/reference according to simulated policy without forcing an unrelated operational task.

Planned verification: BANK-T-12. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-12 functional · Must · B1

Provide the same manual lookup/edit workflow when model assistance fails or is disabled.

Rationale: Maintain service continuity and a fair baseline. Source: E-01; rule: RULE-12; delivery: DEV-01, DEV-08.

**BANK-AC-13:** Given a provider times out or returns malformed output; when the run stops within bounds; then retain the manual workflow and existing saved work.

Planned verification: BANK-T-13. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-13 functional · Must · B0

Revalidate authorization and source/proposal versions on every approved write; make retries idempotent.

Rationale: Prevent repeated or stale business effects. Source: E-01; rule: RULE-10; delivery: DEV-06, DEV-07.

**BANK-AC-14:** Given the same approved operation is retried; when the server receives it again; then return a consistent result with one domain effect and auditable attempts.

Planned verification: BANK-T-14. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-14 functional · Must · B1

Use scoped allowlisted tools and bounded turns/time; customer narratives cannot grant authority.

Rationale: Keep model reasoning outside authorization decisions. Source: E-02; rule: RULE-13; delivery: DEV-08, DEV-09.

**BANK-AC-15:** Given customer content requests ignoring permissions; when the assistant processes it; then treat it as data and reject forbidden tool effects.

Planned verification: BANK-T-15. Actual result: not executed. Acceptance owner: portfolio owner.

### FR-15 functional · Must · B0

Select effective policy by explicit contact as-of time and retain that policy version in evidence.

Rationale: Handle changing procedure editions transparently. Source: E-05; rule: RULE-15; delivery: DEV-05, DEV-08.

**BANK-AC-16:** Given a later edition is uploaded but not yet effective; when the earlier-as-of contact is handled; then do not use the future edition as current guidance.

Planned verification: BANK-T-16. Actual result: not executed. Acceptance owner: portfolio owner.

### NFR-01 nonfunctional · Must · B0

Protect private fields in responses, errors, logs and traces; role and customer scope are server-enforced.

Rationale: Access control extends beyond the user interface. Source: E-01; rule: RULE-01; delivery: DEV-02, DEV-08, OPS-02.

**BANK-AC-17:** Given an unauthorized read/write or error occurs; when responses and logs are inspected; then no private cross-customer fields or secrets appear.

Planned verification: BANK-T-17. Actual result: not executed. Acceptance owner: portfolio owner.

### NFR-02 nonfunctional · Must · B1

Bound latency and failure handling; preserve saved state and support reconciliation after an unknown write outcome.

Rationale: Define observable degradation rather than false success. Source: E-01; rule: RULE-12; delivery: DEV-06, DEV-08, BA-08.

**BANK-AC-18:** Given the network drops after commit; when the operation is queried/retried; then reconcile known state by operation ID before any new business effect.

Planned verification: BANK-T-18. Actual result: not executed. Acceptance owner: portfolio owner.

### NFR-03 nonfunctional · Must · B0

Maintain accessible keyboard use and explicit loading/error/stale/saved states in core journeys.

Rationale: Representative can understand and control service. Source: E-01; rule: RULE-14; delivery: DEV-02, DEV-06, QA-01.

**BANK-AC-19:** Given the representative uses keyboard navigation; when they inspect evidence and edit/save a note; then all required controls are reachable with visible focus and state feedback.

Planned verification: BANK-T-19. Actual result: not executed. Acceptance owner: portfolio owner.

### DATA-01 data · Must · B0

Keep public complaint analysis separate from authored operational fixtures and evaluator-only answers.

Rationale: Prevent fabricated real-world findings or test leakage. Source: E-06; rule: RULE-16; delivery: BA-07, DEV-01, QA-02.

**BANK-AC-20:** Given a fixture or evaluation export is prepared; when provenance and model-visible fields are checked; then label source/synthetic status and keep future facts/gold answers out of runtime input.

Planned verification: BANK-T-20. Actual result: not executed. Acceptance owner: portfolio owner.

### MEAS-01 measurement · Must · B1

Record safe correlation IDs, lookup/review/acceptance events, quality scores and known/unknown model usage.

Rationale: Make usefulness/cost inspectable. Source: E-02; rule: RULE-16; delivery: DEV-10, QA-02, QA-03.

**BANK-AC-21:** Given a run has missing usage telemetry; when the report is calculated; then report unknown cost separately rather than treating it as zero.

Planned verification: BANK-T-21. Actual result: not executed. Acceptance owner: portfolio owner.

### OR-01 operational · Must · B1

Support documented setup, access checks, backup restore, rollback and manual-service fallback before public demo release.

Rationale: An operable product is stronger evidence than a hosted screen. Source: E-07; rule: RULE-12; delivery: OPS-01, OPS-02, OPS-03.

**BANK-AC-22:** Given a release candidate is proposed; when deployment readiness is reviewed; then executed recovery/access evidence or explicit blocked results determine release status.

Planned verification: BANK-T-22. Actual result: not executed. Acceptance owner: portfolio owner.

## Priority and deliberate omissions

Must means necessary for the stated B0/B1 outcome or a safe, truthful demonstration; it does not mean every possible banking function. Scope can be reduced by dropping an entire optional journey/release through a change request, not by removing authorization or honest-state controls.

| Priority | Capability / reason | Consequence or workaround |
|---|---|---|
| Should after Must | Search history/filter convenience and saved non-sensitive query patterns | Manual repeat search remains possible |
| Could after B1 evidence | Semantic/hybrid retrieval if full-text results show a measurable gap | Use full-text and structured filters first |
| Could after B1 evidence | Feedback-based ranking and additional service intents | Do not expand before source rules and evaluation exist |
| Won't in B1 | Actual telephone access/transfer | Use text replay; real phone acceptance is B2 |
| Won't in B1 | Customer self-service account tools | Employee authority only; narrower customer scope in B2 |
| Won't in B1 | Refunds, chargebacks, card blocking, credit decisions | Authorized external manual process |
| Won't in B1 | Complete complaint administration / regulatory reporting | Preserve complaint signal and documented manual boundary; do not advertise end-to-end compliance |
| Won't in B1 | Multi-cloud, Kubernetes, fine-tuning, universal autonomous agent | One operable demo and qualified provider boundary |

## First vertical slice and sequence

Slice VS-01: authorized contact → two candidate transactions → applicable simulated policy → representative explanation → edited saved note. No actual money movement or mandatory task. VS-02 adds existing-case lookup and conditional owned follow-up. VS-03 adds assistance to the same workspace, then compares it to manual/templates/search.

BA-01–05 provide discovery evidence in S01. S02 closes decision tables, coherent fixtures, schemas/NFRs/API contracts. S03–04 implement manual slices and provider qualification. S05–06 evaluate assistance and release only with evidence. A failed BANKING77 download does not block synthetic fixture development and is not relabelled successful.

## Requirements change example

CR-001 records the owner's lookup-first clarification, its effect on measures and demos, and no increase in card scope/effort at this stage. CR-002 records future policy-edition review; it does not approve future guidance as current. New requirements must carry problem/evidence/rule/story/acceptance links and an estimate impact before entering a sprint.

BA-05-AC1: all Must rows have measurable behavior and acceptance ownership. AC2: deferred features have consequence/workaround. AC3: independent synthetic scope preserves the failed-download distinction. Review of Must scope and sequencing remains pending.
