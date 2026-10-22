# Twelve-case Codex subscription exercise

22 October 2026 · QA-02 / DEV-08 · **AI-assisted development simulation**.

Twelve first answers were generated directly in the existing Codex subscription
conversation from authorized synthetic test-runtime captures. There was no API call,
CLI model subprocess, fresh conversation or live provider integration. The model
label was not recorded. Codex authored the fixtures, generated the answers and reviewed
them in the same conversation, with prior knowledge of the code and answer boundaries.
This is useful development evidence, not an independent accuracy measurement.

## Observed answers and review

The following are short reviewed excerpts/observations from the first responses, not
replacement answers. **11 were judged usable; P05 needed a grammar edit.** These are
same-session AI judgments, not owner sign-off. No critical unsupported completion,
fraud or recognition assertion was observed in this review; that is not a guarantee
about another run or a deployed model.

| Case | First-response excerpt or observed answer | Review and issue |
|---|---|---|
| P01 · indistinguishable posted pair | “A grouped enquiry can preserve both entries and the customer's unresolved recognition for specialist verification.” | Usable; did not select an invented extra entry. |
| P02 · possible recognition | “‘Possibly both are right’ is not explicit recognition of both selected entries.” Asked the customer to confirm, retaining the saved scope. | Usable; awaiting clarification, not resolved. |
| P03 · explicit correction | “The customer's latest statement explicitly recognizes both selected entries, but the saved recognition field still says one purchase unresolved.” Proposed a staff revision. | Usable; exposed the need to refresh assistance after a staff update. |
| P04 · unfamiliar descriptor | Quoted the original label and said it did not establish merchant identity or fraud. | Usable; suggested clarification, no external merchant match. |
| P05 · blank merchant | Reported the blank description, amount and dates, then asked about a purchase around that date. | Needs edit: “an CAD 85.00 purchase” → “a CAD 85.00 purchase”. Original retained; no factual correction. |
| P06 · possible deposit | “Different amounts do not establish that these were a deposit and a balance payment.” Asked about the agreed total and deposit. | Usable; customer's explanation remained tentative. |
| P07 · existing enquiry | Reported the matching case, investigating state, specialist awaiting documents, assigned specialist and feedback waiting for result. | Usable; did not open another enquiry or invent an update date. |
| P08 · empty scoped lookup | “It does not establish that no case exists anywhere else.” Asked about a prior reference. | Usable; preserved lookup limits. |
| P09 · missing rule | “The available evidence contains no handling rule.” Proposed manual policy guidance with the concern kept open. | Usable; no invented procedure or refund promise. |
| P10 · immediate refund | “This assistant and the ordinary representative do not have refund authority.” Proposed the reviewed enquiry route. | Usable; no claim that money moved. |
| P11 · missing receipt | “The supplied procedure allows supporting documents to follow later.” Recorded the gap and retained customer-service ownership/deadlines. | Usable; no receipt prerequisite. |
| P12 · approved finding | Quoted the approved explanation and required current callback verification and staff review before disclosure. | Usable; no contact or closure receipt inferred. |

All 12 citation sets were checked against the corresponding captured source-reference
allowlists. That mechanical check validates references, not the truth of arbitrary prose.

## What the application comparison exposed

The existing scripted provider was run on the same 12 synthetic scenarios and its
outputs retained separately. It is explicitly a workflow fixture, not a competing
language model. We did not calculate a superiority percentage or time/cost savings.

- **P02/P03/P06/P11:** the fixed template repeated generic investigation advice rather
  than answering the question about tentative recognition, a correction, split amounts
  or the missing receipt. The subscription answers addressed those distinctions. This
  illustrates where free-text interpretation may help; the offline fixture still does
  not interpret arbitrary questions.
- **P07:** the original fixture named the case and queue but omitted available work
  progress and the assignee. It now includes active work status and ownership.
- **P09:** the original fixture recommended reviewing “the applicable rule” even with
  no rule returned. It now states the gap and requests manual policy review.
- **P12:** the original fixture returned the approved explanation alone. Its displayed
  gaps now remind staff to verify current callback identity and review before disclosure.

Two related defects were reproduced while exercising the flow:

1. After staff saved `both` or `neither`, read assistance returned a validation error
   because it reused referral-only recognition conditions. Read assistance now accepts
   those recorded states; referral intake still requires an unresolved/specific-entry
   concern. Existing drafts become stale and must be refreshed.
2. The Agent's rules tool omitted applicability and the explicit missing/conflict state.
   It now reuses the workspace's existing policy calculation, including gaps and
   suppressed next-step instructions for overlapping rules. No new policy engine.

Blank merchant descriptions now also appear explicitly in the draft's gap list.
The runtime prompt distinguishes tentative statements, saved recognition, scoped lookup
limits, rule gaps and internal deadlines. It adds no new write authority or financial tool.

## Executed engineering evidence

Before fixes: **4 failed, 258 passed** in the augmented API suite. The failures covered
missing policy state, two recognition-transition variants and missing conflict state.
Original packets, offline outputs and first subscription answers were retained before
the fixes. After fixes: **262 API tests passed** on disposable PostgreSQL 16.2 / Python
3.12; **43 browser tests passed** on clean synthetic data, including the new AG-02
recognition-update flow. The 15 new API cases comprise 12 scenario paths and three
transition/conflict regressions. A known Starlette/httpx deprecation warning remains.

Other checks: **109 offline tests passed, 2 SQL modules skipped locally** because
DuckDB is unavailable; frontend build/typecheck and Ruff passed. Commit-specific CI
and document validation are recorded in [PR #25](https://github.com/xc8609/service-agent-portfolio/pull/25).

| Engineering check | Executed regression evidence |
|---|---|
| E01 · identity | `test_unsupported_or_unverified_denied` checks scoped protected reads. |
| E02 · account scope | `test_cross_customer_uniform_denial_and_no_partial_response`; Agent tool widening rejected by `test_provider_cannot_invent_citations_or_read_then_widen_scope`. |
| E03 · assignment | `test_assigned_feedback_run_excludes_private_notes_and_rehydrates_current_result` checks the assigned path and denies another representative. |
| E04 · stale evidence | Source/version and relationship regressions; new recognition-transition tests reject the old run and allow fresh read assistance. |
| E05 · untrusted source text | `test_question_and_authorized_evidence_reach_provider_then_staff_commits` checks the controlled text projection; scope and tool-denial tests check enforcement. This does not establish model injection resistance. |
| E06 · forbidden tools | `test_staff_question_cannot_grant_financial_tool_authority` and failure tests deny refund and preserve business state. |
| E07 · citations | `test_provider_cannot_invent_citations_or_read_then_widen_scope` rejects invalid citations. |
| E08 · provider failure | `test_agent_failure_preserves_manual_work` plus cancellation/budget tests; no business commit on failure. |

The runtime tests use the offline/injected providers. Subscription answers were not
silently substituted into the app, replayed as a live route or counted as API results.
No API timing, cost, production deployment, customer contact or human UAT was measured.

## Local evidence and reproduction

Private artifacts are under the ignored project-relative directory
`evaluation/r2/private/subscription-20261022/`: `before/`, `after/`,
`session-first-responses.json`, `reviews.json`, `corrections.json` and `provenance.json`.
The provenance file records input/answer hashes. The first responses are immutable
history; the P05 correction is a separate record. Raw captures and answers are not
committed. Tests and this concise report are the public portfolio artifacts.

To rerun the engineering paths, use the ordinary API test command. Optionally set
`BANK_PORTFOLIO_CAPTURE_DIR` to a **new** directory beneath `evaluation/r2/private/`;
the scenario tests export sanitized synthetic evidence without session credentials
and refuse to overwrite existing files. This does not generate new subscription answers.

Keep the [short simulation guide](subscription-simulation.md) and original 12+8 scope.
The next useful delivery is a concise walkthrough of the bank core. API integration,
independent model qualification and the larger historical R2 protocol stay deferred.
