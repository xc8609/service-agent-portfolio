# Permission matrix v0.4

BANK-S02-v0.4 · Current candidate; application implementation and runtime acceptance pending.

D-17–D-22 are accepted to their stated extent. Below are engineering mappings for review. Default deny; trusted staff scope and customer disclosure verification are separate.

| Action | inbound_representative | specialist | feedback_representative | queue_lead | policy_steward | scheduler | agent_runtime |
|---|---|---|---|---|---|---|---|
| queue.list_summary | own_queue_masked | own_queue_masked | own_queue_masked | managed_queue_masked | deny | deny | delegated_masked |
| work.claim | deny | eligible_specialist_queue | eligible_feedback_queue | assign_managed_queue | deny | deny | deny |
| customer.read_context | verified_active_contact | assigned_case | claimed_feedback_task | managed_case_with_reason | deny | deny | delegated_read_scope |
| transaction.read | verified_active_contact | assigned_case | claimed_feedback_task_minimum | managed_case_with_reason | deny | deny | delegated_read_scope |
| result.read_approved | verified_contact_linked_case | assigned_case | claimed_feedback_task | managed_case_with_reason | deny | deny | delegated_customer_visible |
| result.read_internal | deny | assigned_case | deny | managed_case_with_reason | deny | deny | deny |
| policy.read | staff_audience | staff_audience | staff_audience | staff_audience | steward_scope | deny | delegated_policy_scope |
| referral.submit | verified_active_contact_approve | deny | deny | managed_case_with_reason | deny | deny | deny |
| result.publish | deny | assigned_case | deny | managed_case_with_reason | deny | deny | deny |
| callback.record | deny | deny | claimed_feedback_task | managed_case_with_reason | deny | deny | deny |
| objection.capture | verified_contact_linked_case | assigned_case | claimed_feedback_task | managed_case_with_reason | deny | deny | deny |
| proposal.create | scoped_draft | scoped_draft | claimed_feedback_draft | managed_case_draft | deny | deny | delegated_draft_only |
| proposal.approve | allowed_inbound_action | allowed_specialist_action | allowed_feedback_action | managed_case_with_reason | deny | deny | deny |
| case.close | deny | deny | claimed_feedback_closure_guards | managed_case_closure_guards | deny | deny | deny |
| work.reassign | deny | deny | deny | managed_queue_reasoned | deny | deny | deny |
| deadline.evaluate | deny | deny | deny | deny | deny | service_identity_metadata | deny |
| policy.publish | deny | deny | deny | deny | steward_scope | deny | deny |
| financial.execute | deny | deny | deny | deny | deny | deny | deny |
| commitment.propose | deny | assigned_case | deny | deny | deny | deny | deny |
| commitment.confirm | deny | deny | deny | managed_case_with_reason | deny | deny | deny |
| complaint.register | deny | assigned_case | claimed_feedback_task | managed_case_with_reason | deny | deny | deny |
| contact_continuation.decide | deny | deny | deny | lead_continuation_approval | deny | deny | deny |
| proposal.edit | verified_active_contact | assigned_case | claimed_feedback_task | managed_case_with_reason | deny | deny | deny |

## Predicates

- **verified_active_contact**: Trusted employee session + fresh customer proof + explicitly selected authorized card/account + active contact purpose.
- **claimed_feedback_task**: Employee is current assignee of an active feedback work item; restrict to its case/customer and needed evidence. Caller verification is NOT required to prepare; it IS required to disclose private facts to the customer.
- **managed_case_with_reason**: Lead manages the current queue and supplies an auditable operational purpose; no global access or financial authority.
- **delegated_read_scope**: Agent receives server-issued run scope from initiating staff assignment/contact; event runs receive only customer-visible scoped evidence. It never supplies roles or widens scope.
- **own_queue_masked**: Eligible membership grants summary-only queue listing; details require assignment.
- **disclosure_gate**: Fresh identity assurance belongs to the current callback contact; old inbound verification cannot be reused.
- **lead_continuation_approval**: Responsible lead within managed feedback queue; reason, fresh case/work/proposal versions; explicit bounded contact plan or named hold owner and review date; agent cannot approve.

## Action boundaries

- **queue.list_summary**: Customer alias/card last4, concern category, work age/status; no transaction amounts or findings before claim.
- **work.claim**: Atomic claim on expected work version; one current assignee. D-17 accepted for feedback.
- **customer.read_context**: Staff preparation and customer disclosure are separate authorities.
- **transaction.read**: No all-customer or all-account grant; full PAN/CVV never returned.
- **result.read_approved**: Only approved customer explanation enters feedback generation.
- **result.read_internal**: Internal-only notes excluded from model prompts/traces; steward is not a customer-data role.
- **policy.read**: Product, jurisdiction, audience and effective time filter enforced before return.
- **referral.submit**: Human approval followed by server guards; model only proposes.
- **result.publish**: Publishing specialist findings is not a financial operation; queue-lead override is proposed pending review.
- **callback.record**: Record actual result even if verification failed; completed feedback requires verified disclosure context.
- **objection.capture**: Exact customer statement retained; complaint handling is a separate pending rule.
- **proposal.create**: Draft is not approval; affected source versions attached.
- **proposal.approve**: Action-kind specific validation; broad approve-any is prohibited. D-22: post-exhaustion plan/hold approval is restricted to responsible queue lead; generic feedback/specialist approval grants do not authorize this subtype.
- **case.close**: Accepted normal closure only; lead-review cannot become automatic unresolved closure.
- **work.reassign**: Proposed lead-only control; revokes former assignee scope and invalidates stale approvals.
- **deadline.evaluate**: Scheduler reads only timing/status/ownership metadata, never transcript/body to detect time.
- **policy.publish**: Separate versioned publishing authority; never lets policy text grant data access.
- **financial.execute**: Outside demo; no refund/card-block/dispute-submission endpoint exists.
- **commitment.propose**: Current investigation assignee; server records proposer, future update, immutable history.
- **commitment.confirm**: Responsible investigation lead only; not ordinary staff or agent.
- **complaint.register**: Explicit customer complaint request; designated intake queue; independent of re-review.
- **contact_continuation.decide**: New bounded plan or owned review hold; cannot erase lifetime history.
- **proposal.edit**: Staff edit draft only; kind and customer/case/contact immutable; previous revision audited.

Before claim: masked summaries only. After claim: case-relevant details; no internal notes in feedback/model DTOs. Reassignment revokes old scope. Caller verification must belong to current callback before disclosure. Scheduler metadata privilege never transfers to the model. Runtime API/database enforcement remains unexecuted.
