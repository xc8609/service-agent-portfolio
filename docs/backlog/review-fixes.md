# REV-01 — post-merge review corrections

21 October 2026. Owner authorized these three corrections before bank-core UAT.
This is a defect slice of QA-02, DEV-13 and QA-03, not a new business workflow.
[Trello tracking card](https://trello.com/c/ItGGvliw/57-rev-01-fix-evaluation-false-negatives-and-complaint-receipt-review-gaps).

## Requirements and acceptance

| ID / parent | Reproduction | Required behaviour | Regression evidence |
|---|---|---|---|
| REV-01-AC1 / QA-02 | An unverified answer exposes an amount without citations; or one sentence denies a duplicate and another asserts it | Neither answer may automatically pass. Apply duplicate negation locally. Unverified free text outside the reviewed fact-free response requires review, including text in gaps. Preserve the historical rubric and scores | `test_unverified_free_text_cannot_pass_without_citations`, `test_negation_does_not_cancel_a_separate_positive_duplicate_assertion`, `test_review_rubric_has_separate_reproducible_results_without_old_overrides` |
| REV-01-AC2 / DEV-13, FR-28 | Failure reason is accepted but disappears after delivery retry | Persist outcome, reason/reference, intake version, time, actor and operation key atomically. Retrying a command creates no second receipt; delivery retry/acknowledgement never erases earlier failures. Runtime cannot update/delete receipt rows | `test_receipt_history_survives_retry_and_is_append_only`, `test_complaint_delivery_is_requested_by_worker_and_acknowledged_by_receipt` |
| REV-01-AC3 / DEV-13, NFR-01 | Complaint coordinator clicks Open work and receives 404 | No Open/Claim work control for this queue-only role. Keep acknowledgement/failure controls and server detail denial. Scoped assigned staff can inspect receipt history | `WF-01`, `test_receipt_history_survives_retry_and_is_append_only` |

## Detailed design and change impact

- Evaluation `pilot-v1` remains reproducible with the original frozen cases, outputs,
  expectations and adjudications. `review-v2` is the default for regression scoring,
  writes a separate result file, and does not inherit v1 adjudications. The strict
  unverified-text gate intentionally trades automatic acceptance for review. It is
  not a semantic truth detector or a change to live Agent authorization. Promise
  guard refinement and an independently authored hold-out remain separate QA-02 work.
- Forward migration `013_complaint_receipts.sql` adds `complaint_delivery_receipts`.
  Only SELECT/INSERT are granted to the runtime role. Unique intake/version and
  actor/operation-key constraints complement the existing atomic replay mechanism.
  Old failures cannot be reconstructed and are not fabricated. Apply migrations and
  provision runtime grants before starting the updated application.
- Existing assigned-work authorization protects receipt history; coordinator detail
  privileges do not expand. The UI removes only the inapplicable coordinator controls.
- No financial execution, live provider or external complaint transport is introduced.

## Delivery and UAT

Branch: `codex/qa02-review-fixes`. PR/CI evidence is recorded in the PR and Trello card.
Run API/PostgreSQL tests, browser workflow tests, offline/SQL checks, schema validators,
publication checks, lint and frontend build. A passing build does not accept the stories.

After checks pass, QA-03 starts with U1 (unverified caller), then U2–U4 (authorized
transaction evidence, customer recognition, rules and existing work). Continue through
reviewed enquiry, specialist finding, feedback and complaint exceptions. Record the
owner's answers, commit and fixture version; leave all outcomes pending until observed.

## Executed local checks

21 October 2026: 225 API tests passed on isolated PostgreSQL 16.2, 40 Chromium
browser tests passed on a separate synthetic service, and 20 offline/SQL tests passed.
Ruff, TypeScript/Vite build, workflow/schema validators and publication checks passed.
GitHub checks are attached to the PR. Owner UAT has not been recorded as passed.
