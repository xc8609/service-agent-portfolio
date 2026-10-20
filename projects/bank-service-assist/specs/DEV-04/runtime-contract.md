# DEV-04 inbound case lookup increment

20 October 2026. Synthetic B0 workflow, following DEV-03. This implements verified
inbound reads only; assigned outbound feedback authority remains a separate gate.

## Scope and contract

`POST /v1/workspace/get_related_cases` accepts the same strict contact_id and
1–10 unique transaction_ids input as get_transaction_evidence. All selected IDs
must be in the fresh verified account scope. It returns `cases`, `as_of`, and
`review_state` (`review_existing_work` or `no_linked_case_found`). Each entry has
case reference/concern, matched IDs, full/partial selection coverage, an advisory
reuse hint, status source time, queue name, current work owners/status/due dates,
and the canonical get_case_snapshot data. No-case is a successful empty result;
denied, unavailable and inconsistent state are errors, never an empty success.

`POST /v1/agent-tools/get_case_snapshot` implements the existing v0.4 read contract
using the same domain projection. Input expected_work_version must be null in
this inbound-only increment: there is no assigned feedback work context. Backend
rechecks active principal/membership, owned open contact, fresh verification,
case customer and every case-linked account before disclosing any details.
Foreign and missing IDs return the same 404; a mixed unauthorized selection
returns no partial data. Feedback/Agent personas remain denied.

## Recorded progress, not inferred progress

Cases have a public demo reference, concern code, status source timestamp and
current timeline sequence. New customer-safe timeline events are separate from
private audit records. Sort by aggregate sequence and show occurrence and recording
times independently. Latest sequence/version/status must agree with the case;
missing/gapped or conflicting events return STALE_VERSION (409). Do not replace
current status using the newest ingestion timestamp or a late occurrence.

Read linked specialist, feedback, re-review and complaint tasks independently.
Show assigned staff or explicitly Unassigned, plus accountable queue; retain the
original due date alongside any current due date. Inactive owners/queues are
labelled, not silently reassigned. Pending required actions appear as evidence
gaps. Only published customer explanations and decided customer-safe commitments
are projected; pending/rejected commitments, reasons and private notes are omitted.
No approved update means unknown; an update commitment is not a completion date.
A closed case is not evidence of merchant refund execution. Re-review completion
never closes a separate complaint task.

## Duplicate-enquiry review

Both selected entries covered by an active duplicate-charge enquiry produce a
potential-existing-enquiry hint: inspect and continue that case through the
existing service process. Partial overlap, different/unknown concern and closed
work require manual review; do not silently reuse, reopen or block a legitimate
new concern. This slice performs no case creation or case mutation. It exposes
and highlights existing work before referral design, not a financial verdict.

There is no submission button yet. DEV-07 MUST recheck case/transaction scope,
versions and same-concern work atomically when submission is implemented. A
no-case read is never a reusable authorization to submit. Failed/conflicting
lookups leave the duplicate check incomplete. Do not claim write-time duplicate
prevention is already implemented.

## UI and freshness

Inspecting selected transactions automatically retrieves their linked cases.
Refresh rechecks current ownership/progress. Filter, selection, statement or
contact changes remove the case view. Late responses cannot restore old details.
On refresh failure remove details, label the last successful lookup time as stale,
and show unavailable/conflict or denial; never present old detail as current.
Safe errors retain the correlation ID. Customer report capture remains distinct
from creating a specialist enquiry.

## Acceptance mapping

- CK-01 / AC01: same pair, awaiting documents, task owner and original due date;
  verified inbound analogue only (assigned feedback permission still pending).
- CK-02 / AC02: approved vs pending commitments, unknown completion, no private text.
- CK-03 / AC03: stable timeline order, dual timestamps, conflicting head rejected.
- CK-04 / AC04: foreign/missing/mixed scope, revoked proof/role/contact, changed
  owner on refresh; unclaimed feedback denied (assigned feedback not implemented).
- CK-05 / AC05: separate re-review and complaint work, distinct owners/statuses.
- CK-06 / AC06: unavailable/conflict vs empty, stale-view clearing and delayed reads.
- CK-07: same-pair, partial, different-concern, closed and no-case hints; no case
  created and no mutation or private result access granted to bank_app.
