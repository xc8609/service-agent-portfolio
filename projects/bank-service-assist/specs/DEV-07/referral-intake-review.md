# DEV-07 refinement — one recognized purchase, two posted entries

Business review completed for RI-01–03; technical refinement pending · 20 October 2026 · `BANK-REFERRAL-REVIEW-01`

This is a detailed child card of DEV-07, not another independently estimated story.
All scenarios, records and policies are simulated. RI-01–03 are owner-accepted as
D-23–D-25; no implementation acceptance, real-bank procedure or compliance is asserted.
Existing accepted decisions D-10–D-22 remain unchanged. New rules below are
proposals until explicitly reviewed. This document does not change v0.4 schemas.

## Story card and business outcome

As an authorized inbound representative, I want to assemble and review a
transaction enquiry with explicit customer statements and evidence gaps, so that
the specialist can begin investigation without asking the customer to repeat
information or treating an allegation as a confirmed duplicate debit.

Owner relevance: customer-service desktops, authorized customer lookup and
processing-rule lookup. Role evidence: existing R01/R02/R06 requirements,
API, access-control and testing evidence; no new hiring research.

Requirements: FR-02/03/06/07/09/10/13/16.
Dependencies: DEV-02 authorized contact; DEV-03 transaction selection and
statement revision; DEV-04 existing work; DEV-05 applicable policy;
DEV-06 versioned notes; DEV-07 human-reviewed submission.
Later feedback remains DEV-11–13.

Hypothesis: a structured enquiry reduces clarification and repeated lookup.
Measure intake preparation time, returned-for-clarification rate and missing
required-information rate against the manual baseline. No target or benefit
is accepted or measured here.

## Walkthrough

1. Customer says: “I bought something once, but I see two charges of CAD 85.”
2. Verify the contact and obtain the permitted card context from trusted services.
3. Ask for approximate purchase date, merchant description, amount/currency and
   which entries concern them. Record the customer's words separately from facts.
4. Retrieve both posted DEMO STORE records. Show immutable IDs, versions, status,
   dates, amount/currency and available relationship evidence. Same merchant and
   amount alone do not establish a duplicate.
5. Clarify: one purchase recognized; one particular entry disputed, or the pair
   cannot be distinguished. Do not infer which row is the legitimate purchase.
6. Check existing work and applicable handling guidance. Ask whether the customer
   already contacted the bank or merchant; “not contacted” is a valid response.
7. Preview a referral: reported concern, observed facts, requested investigation,
   missing evidence, destination and feedback arrangements. Ask the customer to
   confirm the summarized concern; the representative reviews and approves the
   actual proposal version.
8. Revalidate scope, source versions, route and duplicate-work guard on submission.
   Only a committed receipt permits “submitted to queue.” Specialist acceptance
   is a separate event. No refund, chargeback or completion promise is implied.

## Intake minimum — accepted decisions and proposed technical controls

“Required” means available to the trusted submission service, not necessarily
typed by the representative. An explicit unknown is allowed only where stated.
System failures must not be recorded as successful checks.

| ID | Information | Source and validation | Submission rule |
|---|---|---|---|
| M01 | Current authorized contact and permitted card/account | Server-derived actor, contact, verification and scope; masked card in preview | Required; expired/unverified/out-of-scope blocks this submission, preserving permitted draft content for revalidation |
| M02 | Selected transaction pair | Source IDs/versions, amount/currency, status, occurrence and posting dates where available, provenance/as-of | Both distinct authorized IDs required for this scenario; dates/status may not be invented; source-unavailable cannot use stale screen data as current evidence |
| M03 | Original customer statement and current interpretation | Customer quote, contact/time, revision and representative summary | Required; capture one purchase recognized and the concern about an additional entry, without asserting duplicate debit |
| M04 | Recognition mapping | Explicit customer confirmation, not model inference | Specific recognized/queried IDs when distinguishable; otherwise both IDs with unresolved mapping. RI-01 accepted as D-23; `pair_unresolved` remains a proposed schema representation |
| M05 | Clarification responses | Approximate purchase date, purchase count and amount as reported; merchant/bank contact history if asked | Record answered, unknown or declined distinctly; unknown receipt date or absent merchant contact does not itself block review |
| M06 | Checked facts and evidence gaps | Versioned transaction/case/policy references, reported facts separately labelled | Required explicit gap list, possibly empty; “no relationship returned” is not “duplicate confirmed” |
| M07 | Existing-work check | Current authorized case search and coverage; source/time | Completed check required for normal new submission. Active same-issue work is linked; distinct new work requires reviewed reason. An outage triggers manual continuation, not “no existing case” |
| M08 | Requested review and valid destination | “Investigate whether the additional posted entry is a separate valid purchase or requires correction”; trusted routing configuration | Required; no request text grants financial authority. No applicable rule/conflict requires a configured manual-review route, never an invented policy |
| M09 | Feedback arrangement or explicit contact gap | Reference to permitted existing contact method, masked preview; customer preference and availability only if provided | Under D-25, allow submission with a contact gap and customer-service ownership; preserve deadlines and keep undelivered feedback open. Do not require a new phone number in free text or silently change the customer master |
| M10 | Approval and submission controls | Current proposal revision, expected versions, human approver, operation key | Required and enforced server-side. Customer confirmation of the summary is not staff approval or consent to a financial action |

For M09 contact details being unusable is not a rejection reason (D-25).
Technical proposal: persist linked contact-resolution work owned by the configured
customer-service queue, with its responsible lead accountable before individual
claim. Queue/lead mappings and review scheduling must be configured before the
path is released. Missing routing configuration is a system-readiness failure,
not a requirement for the customer to provide a working phone before enquiry.
On such a failure preserve the draft and expose manual escalation, without a
false submission receipt. No customer-master update endpoint is added here.
Contact readiness does not imply authority to disclose details during a later call.

## Evidence that may follow

D-24 accepts initial enquiry with incomplete supporting material when mandatory
intake information is available. The specialist determines what supplementation
is needed; customer service contacts the customer. Neither waiting for evidence
nor receiving it resets or extends processing deadlines. Detailed field/state
representations below still require technical contract review.

| Evidence | Why useful | Proposed treatment when absent |
|---|---|---|
| Receipt, order confirmation or customer screenshot | Supports reported purchase details | Optional at initial enquiry; note unavailable/not requested/declined separately; no upload service is implied |
| Exact purchase time or order number | Helps distinguish matching entries | Approximate or unknown accepted when the source transaction pair is identified |
| Merchant response, cancellation or refund confirmation | Adds evidence about purchase or correction | Record whether contact occurred; do not force merchant contact before opening this simulated enquiry |
| Acquirer/merchant authorization and settlement evidence | Helps specialist establish transaction relationship | Specialist-owned investigation evidence; ordinary staff need not obtain restricted records |
| Supplementary customer account of events | Resolves outstanding questions | Append a revision with source/time, preserving the original statement |
| Preferred callback time | Improves contact planning | Optional; do not promise a time that the service calendar or queue cannot support |

Each material missing item needs an explicit state, follow-up owner, requested
next action and review trigger/date under approved workflow rules. Not every
optional document must be requested. Later evidence must not reset original
submission time or deadlines. Formal dispute/chargeback filing requirements are
outside this initial enquiry and require a separately reviewed policy.

Never request or store PIN, CVV, password or one-time authentication code in notes.
Use authorized references rather than copying full payment credentials.

## Distinct branches

| Condition | Required handling |
|---|---|
| Customer recognizes one purchase but cannot identify the extra row | Paired enquiry with unresolved mapping accepted as D-23; technical contract and implementation pending |
| Customer denies both purchases or changes the selected transactions | Preserve original statement, invalidate affected explanation/proposal, refresh evidence and use the reviewed manual risk route; do not submit the old duplicate-enquiry draft |
| One pending and one posted | Reassess the scenario and applicable rule; do not apply the two-posted-entry conclusion or promise reversal |
| Evidence or policy source fails | Show unavailable and retain safe draft; configured manual continuation, with missing checks explicit |
| Related active case exists | Continue/link it instead of creating duplicate work; new distinct concern needs an explicit reason |
| Customer explicitly requests a complaint | Record the request and use the independently tracked complaint-intake path; do not imply this draft completes complaint intake |
| Customer wants an immediate refund | Explain representative authority; enquiry receipt is not a financial-operation approval |

## Agent and trusted-service responsibilities

Agent may retrieve scoped context/transactions/evidence/case/policy, identify
missing fields, propose a concise clarification question and draft the enquiry.
It must distinguish customer allegations, source facts and unresolved inferences.
Every evidence-based assertion needs a retrievable reference; untrusted merchant
text, customer notes and policy text cannot grant privileges.

The representative confirms the concern, edits the draft and approves its exact
version. The server derives identity/scope, validates queue and required fields,
checks versions and duplicate work, and atomically commits case/work/audit/outbox/
receipt. `get_operation_status` reconciles a lost response. Agent failure leaves
the same manual template usable; the model cannot submit via a narrative answer.

Current v0.4 referral payload already has `transaction_ids`, `concern`,
`checked_facts`, `missing_evidence`, `requested_review`, `queue_id` and
`related_case_id`. It does not yet express this complete intake minimum.
Before implementation, review structured statement/revision references,
recognition mapping, clarification states, case-check evidence, follow-up
ownership/contact gap and manual-route basis. Update JSON Schema, OpenAPI,
semantic checks, persistence, fixtures and evaluation together. Do not hide
required workflow controls solely in `concern` text.

## Additional acceptance criteria and planned tests

All cases below are **not executed**. RI-AC02 has accepted business basis D-23;
evidence deferral and unchanged deadlines in RI-AC04/10 have basis D-24;
contact-gap continuation in RI-AC05/15/16/17 has basis D-25. Detailed technical
representations and remaining refinements are proposed. IDs are refinement-local and
do not renumber existing DEV-07-AC01–06. Passing document validation is not UAT.

| ID / test | Given / When | Then |
|---|---|---|
| RI-AC01 / RI-T01 | Two authorized posted entries, customer identifies one recognized and one queried; preview referral | Display that customer-reported mapping, both source records and unresolved relationship; never label duplicate as a verified fact |
| RI-AC02 / RI-T02 | Same pair but customer cannot distinguish rows; draft enquiry | Under accepted D-23, allow paired unresolved mapping; require both IDs and never choose a disputed row automatically |
| RI-AC03 / RI-T03 | Required identity, selected IDs, statement, check evidence, routing or approval data missing; submit | Server rejects with safe field-specific reasons; no case/work/outbox side effect; permitted draft remains editable |
| RI-AC04 / RI-T04 | No receipt, exact time or merchant response, but mandatory minimum available; submit | Under accepted D-24, allow initial enquiry with explicit gaps; specialist requests needed material, customer service contacts the customer; no fabricated attachment, reset or extension of deadlines |
| RI-AC05 / RI-T05 | Bank contact method unusable; prepare referral | Under D-25, allow submission and create accountable customer-service contact-resolution work; never silently add a number, claim callback readiness, reset deadlines or automatically close the case |
| RI-AC06 / RI-T06 | Same issue already has active work, or existing-work lookup fails; submit new enquiry | Link active work/require distinct-work reason; on failed lookup block normal new submission and expose manual continuation, not a “none” result |
| RI-AC07 / RI-T07 | Customer denies both or corrects selected entries; save correction | Preserve earlier statement, invalidate affected draft and require refreshed evidence/reviewed risk path before any new submission |
| RI-AC08 / RI-T08 | Scope, source status, policy version or proposal revision changes after preview; approve | Reject stale/unauthorized submission, preserve permitted edits, display required revalidation and require fresh human approval |
| RI-AC09 / RI-T09 | Approved enquiry commits but response is lost; retry same key/payload | Return original receipt; exactly one case/work and one logical event effect; never assert specialist acceptance |
| RI-AC10 / RI-T10 | New receipt/evidence arrives after submission; append it | Under D-24, preserve original statement, prior evidence, submission time and deadlines both while waiting and when evidence arrives; record specialist requests and customer-service follow-up; expose additions to responsible work |
| RI-AC11 / RI-T11 | Model is unavailable or invents “refund approved/submitted”; render and continue | Manual intake remains usable; no financial approval or submitted state without trusted receipt |
| RI-AC12 / RI-T12 | Operator changes customer, filters or selected transaction pair; continue review | Clear previous-customer sensitive context; bind results to executed filters; flag changed filters and prevent stale selection from feeding a referral until refreshed |
| RI-AC13 / RI-T13 | Applicable policy missing/conflicting; seek next action | Show gap and configured manual-review route with basis; no fabricated citation or unsupported remedy |
| RI-AC14 / RI-T14 | Operator enters 85.00 CAD and customer-local date; query and preview | Use explicit currency/date semantics and correct minor-unit conversion; show the executed search context beside results |
| RI-AC15 / RI-T15 | Investigation result arrives while contact gap is unresolved; process result | Preserve finding and investigation status separately; feedback remains outstanding with customer-service ownership; no delivered flag or automatic case closure |
| RI-AC16 / RI-T16 | Contact gap persists past an original processing deadline; scheduler runs repeatedly | Preserve original due time and overdue history; create deduplicated responsible-lead review work under configured rules; do not stop the clock or invent a successful contact |
| RI-AC17 / RI-T17 | Trusted contact-details update resolves the gap; resume feedback | Use the authorized updated contact reference; retain history/deadlines; require fresh customer verification before disclosure; model text or caller-provided digits alone cannot resolve the gap |

## Delivery and review tasks

- [x] Inspect DEV-03/05/06/07 and v0.4 referral schema; draft this review card.
- [x] Owner accepted RI-01 paired ambiguity as D-23 on 20 October 2026.
- [x] Owner accepted RI-02 evidence deferral as D-24 on 20 October 2026.
- [x] Owner accepted RI-03 contact gaps as D-25 on 20 October 2026.
- [ ] Confirm normal/manual queue mappings, recognition states and risk-route ownership.
- [ ] Separate implemented read-slice checks from full workflow acceptance wording.
- [ ] Refine contracts/migration and versioned synthetic fixtures; assess estimate impact.
- [ ] Implement manual form and deterministic guards before Agent drafting.
- [ ] Implement atomic reviewed submission, receipt reconciliation and later evidence updates.
- [ ] Execute API/PostgreSQL tests for authority, stale versions and idempotency;
      browser journeys for mandatory/optional evidence, corrections and source failure.
- [ ] Run owner walkthrough and record actual acceptance separately from this draft.

Forecast stays within parent S04 for review purposes only. Existing DEV-07 effort
is not validated by this refinement. Attribute statement/query work to DEV-03,
case lookup to DEV-04, rules to DEV-05 and notes to DEV-06; estimate incremental
referral work before commitment, avoiding double-counting or silently enlarging
the existing four-developer-day implementation slice.

## Completed owner review — implementation acceptance separate

| Item | Proposal | Status |
|---|---|---|
| RI-01 | Allow a paired enquiry when one purchase is recognized but the two records cannot be distinguished | Accepted by owner, 20 October 2026; D-23; implementation/test acceptance pending |
| RI-02 | Allow initial enquiry with incomplete supporting material; record gaps; specialist requests supplementation and customer service contacts the customer; do not reset or extend deadlines | Accepted by owner, 20 October 2026; D-24; implementation/test acceptance pending |
| RI-03 | Allow enquiry submission with unusable contact details; customer service owns contact resolution; preserve deadlines and never automatically close undelivered feedback | Accepted by owner, 20 October 2026; D-25; implementation/test acceptance pending |

See [development-readiness review](referral-readiness.md) for remaining contracts,
fixtures and dependency gates. Trello synchronization is recorded separately with
actual saved/read-back evidence; no card is Done solely because rules are accepted.
