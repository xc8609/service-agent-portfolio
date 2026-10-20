# Data model v0.4

BANK-S02-v0.4 · Current candidate; application implementation and runtime acceptance pending.

Synthetic operational records only. [Structured model](data-model.json) defines fields/keys/checks; [reference DDL](schema-reference.sql) is not applied to PostgreSQL. Cross-record authority and transitions also require service validation.

## staff_principals

External identity reference; no local passwords

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| subject_ref | text | False |  |
| active | boolean | False |  |

Unique: [['subject_ref']].

## service_queues

Accountable specialist/feedback/lead destinations

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| name | text | False |  |
| kind | text | False |  |
| active | boolean | False |  |

Unique: [['name']].

## queue_memberships

Scoped role membership

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| principal_id | uuid | False | staff_principals.id |
| queue_id | uuid | False | service_queues.id |
| role | text | False |  |
| active | boolean | False |  |

Unique: [['principal_id', 'queue_id', 'role']].

## customers

Synthetic customer identity reference only

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| external_ref | text | False |  |
| display_alias | text | False |  |
| data_origin | text | False |  |

Unique: [['external_ref']].
- data_origin is synthetic_demo; real identity/PII absent from public fixtures

## card_accounts

Synthetic masked card context

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| customer_id | uuid | False | customers.id |
| masked_ref | text | False |  |
| product | text | False |  |
| currency | char(3) | False |  |
| version | bigint | False |  |

Unique: [['masked_ref']].

## card_transactions

Read-model snapshot, not a settlement engine

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| account_id | uuid | False | card_accounts.id |
| amount_minor | bigint | False |  |
| currency | char(3) | False |  |
| merchant_description | text | False |  |
| status | text | False |  |
| occurred_at | timestamptz | False |  |
| posted_at | timestamptz | True |  |
| source_ref | text | False |  |
| version | bigint | False |  |

Unique: [].
- Amounts use integer minor units; no floating point money
- Matching merchant/amount does not assert transaction relationship

## transaction_relationships

Evidence-supported relationship only

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| left_transaction_id | uuid | False | card_transactions.id |
| right_transaction_id | uuid | False | card_transactions.id |
| relation | text | False |  |
| evidence_ref | text | False |  |
| version | bigint | False |  |

Unique: [['left_transaction_id', 'right_transaction_id', 'relation']].
- Both transactions must belong to permitted customer/account context

## contacts

Inbound/callback interaction separated from case

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| customer_id | uuid | False | customers.id |
| actor_id | uuid | False | staff_principals.id |
| kind | text | False |  |
| status | text | False |  |
| opened_at | timestamptz | False |  |
| closed_at | timestamptz | True |  |
| version | bigint | False |  |

Unique: [].

## verification_assertions

Trusted current-contact proof, not customer answers

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| contact_id | uuid | False | contacts.id |
| issuer_ref | text | False |  |
| state | text | False |  |
| verified_at | timestamptz | True |  |
| expires_at | timestamptz | True |  |
| scope_json | jsonb | False |  |

Unique: [].
- Only trusted identity adapter writes; no model-provided proof
- Store outcome/reference, not secret answers or identity documents

## cases

Durable unresolved customer concern

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| customer_id | uuid | False | customers.id |
| origin_contact_id | uuid | False | contacts.id |
| owner_queue_id | uuid | False | service_queues.id |
| status | text | False |  |
| concern | text | False |  |
| created_at | timestamptz | False |  |
| closed_at | timestamptz | True |  |
| disposition | text | True |  |
| version | bigint | False |  |

Unique: [].
- Customer on case/contact/accounts must agree
- Open case always has accountable queue; contact ending does not close it

## case_transactions

Selected transaction links

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| transaction_id | uuid | False | card_transactions.id |

Unique: [['case_id', 'transaction_id']].

## work_items

Investigation, feedback, lead review or linked follow-up

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| kind | text | False |  |
| queue_id | uuid | False | service_queues.id |
| assignee_id | uuid | True | staff_principals.id |
| status | text | False |  |
| due_at | timestamptz | True |  |
| original_due_at | timestamptz | True |  |
| calendar_ref | text | False |  |
| source_event_key | text | False |  |
| version | bigint | False |  |
| parent_work_id | uuid | True | work_items.id |

Unique: [['source_event_key']].
- Atomic claim compares expected version and eligible queue membership
- Reassignment revokes former assignee authority; original deadlines retained
- D-19: persist callback window due time and calendar version from first placed-call service date through third service date at 17:00 America/Winnipeg; no fault-based reset; first-callback target remains separately auditable.
- D-20/D-21: investigation, progress callback, specialist re-review and complaint-intake tasks keep independent ownership/status and original-case linkage; new update commitments do not replace the original investigation deadline.
- D-22: lead-review hold requires owner and review date; a new contact plan has a separate approval/limits record and never overwrites original deadline or attempts.

## investigation_results

Versioned findings with approved customer explanation

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| work_item_id | uuid | False | work_items.id |
| author_id | uuid | False | staff_principals.id |
| version | bigint | False |  |
| finding_code | text | False |  |
| evidence_refs | jsonb | False |  |
| approved_customer_explanation | text | False |  |
| published_at | timestamptz | False |  |

Unique: [['case_id', 'version']].
- Immutable published versions; newer result stales dependent proposals

## result_private_notes

Internal-only storage separated from public DTO

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| result_id | uuid | False | investigation_results.id |
| body | text | False |  |

Unique: [['result_id']].
- Excluded from feedback/model retrieval and traces

## required_actions

External action status/evidence; never executes money movement

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| action_kind | text | False |  |
| status | text | False |  |
| external_ref | text | False |  |
| receipt_ref | text | True |  |
| updated_at | timestamptz | False |  |
| version | bigint | False |  |

Unique: [['external_ref']].
- Approval is not completion; financial actions remain external

## callback_attempts

Actual operator-reported attempts, including technical failures

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| work_item_id | uuid | False | work_items.id |
| contact_id | uuid | False | contacts.id |
| actor_id | uuid | False | staff_principals.id |
| occurred_at | timestamptz | False |  |
| service_date | date | False |  |
| dial_state | text | False |  |
| outcome | text | False |  |
| counts_toward_limit | boolean | False |  |
| rule_version | text | False |  |
| operation_key | text | False |  |
| contact_plan_id | uuid | False | contact_plans.id |
| reservation_id | uuid | True | contact_reservations.id |

Unique: [['operation_key']].
- Never delete an actual duplicate call to satisfy a quota; block duplicate planned contact instead
- Count flag derived server-side from reviewed rule, not supplied by model
- D-18: not_placed technical_failure is auditable but does not consume quota or extend original deadlines; placed no_answer consumes one attempt.
- D-22: retain lifetime contact history; any post-exhaustion attempt must reference a distinct lead-approved plan. Plan linkage is mandatory; policy violations stay auditable.

## contact_reservations

Prevent conflicting scheduled contact slots

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| service_date | date | False |  |
| scheduled_at | timestamptz | False |  |
| state | text | False |  |
| version | bigint | False |  |
| contact_plan_id | uuid | False | contact_plans.id |

Unique: [].
- Partial unique active reservation per case/service_date; released reservations do not erase attempts

## customer_objections

Preserved exact statement and review link

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| contact_id | uuid | False | contacts.id |
| statement | text | False |  |
| evidence_refs | jsonb | False |  |
| complaint_requested | boolean | False |  |
| created_at | timestamptz | False |  |

Unique: [].
- Exact statement retained; parallel links live in objection_work_links, not a single overwritten pointer.

## policy_versions

Fictional handling-rule text with applicability and source

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| policy_key | text | False |  |
| version | text | False |  |
| product | text | False |  |
| jurisdiction | text | False |  |
| audience | text | False |  |
| effective_from | timestamptz | False |  |
| effective_to | timestamptz | True |  |
| body | text | False |  |
| source_label | text | False |  |

Unique: [['policy_key', 'version']].
- Effective intervals are explicit; overlapping conflicting rules block authoritative guidance

## service_calendars

Versioned timezone/open windows/fixture holidays

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| calendar_key | text | False |  |
| version | text | False |  |
| timezone | text | False |  |
| open_windows | jsonb | False |  |
| holidays | jsonb | False |  |

Unique: [['calendar_key', 'version']].
- Synthetic holidays are test inputs, not official Canadian holiday claims

## proposals

Editable suggested changes, independent of execution

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | True | cases.id |
| contact_id | uuid | False | contacts.id |
| kind | text | False |  |
| payload | jsonb | False |  |
| source_versions | jsonb | False |  |
| status | text | False |  |
| version | bigint | False |  |
| author_ref | text | False |  |
| rendered_source_hash | text | False |  |

Unique: [].
- Created proposal confers no business authority; approve/commit require trusted actor and fresh source versions

## operations

Idempotent write reconciliation

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| actor_id | uuid | False | staff_principals.id |
| operation_key | text | False |  |
| command | text | False |  |
| request_hash | text | False |  |
| status | text | False |  |
| receipt | jsonb | True |  |
| created_at | timestamptz | False |  |

Unique: [['actor_id', 'command', 'operation_key']].
- Unique actor/command/key plus normalized request hash; authorized replay returns prior receipt before stale version checks.

## audit_events

Append-only safe decision/action evidence

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | True | cases.id |
| actor_ref | text | False |  |
| event_type | text | False |  |
| occurred_at | timestamptz | False |  |
| safe_details | jsonb | False |  |
| operation_id | uuid | True | operations.id |
| aggregate_sequence | bigint | False |  |

Unique: [['case_id', 'aggregate_sequence']].
- No raw card/contact secrets or hidden model reasoning

## outbox_events

Atomic publication with domain write

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| event_key | text | False |  |
| aggregate_ref | text | False |  |
| aggregate_version | bigint | False |  |
| event_type | text | False |  |
| payload | jsonb | False |  |
| status | text | False |  |
| lease_expires_at | timestamptz | True |  |
| attempt_count | integer | False |  |

Unique: [['event_key']].
- At-least-once delivery; consumer effect deduplication required; no exactly-once transport claim

## agent_runs

Short bounded execution over durable case state

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | True | cases.id |
| contact_id | uuid | False | contacts.id |
| scope_snapshot | jsonb | False |  |
| provider_profile | text | False |  |
| trigger_key | text | False |  |
| status | text | False |  |
| started_at | timestamptz | False |  |
| finished_at | timestamptz | True |  |

Unique: [['trigger_key']].
- Expiry/reassignment revalidated on every tool/commit; no multi-day live model loop

## agent_steps

Sanitized tool/proposal trace

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| run_id | uuid | False | agent_runs.id |
| sequence | integer | False |  |
| tool_name | text | False |  |
| source_refs | jsonb | False |  |
| safe_result | jsonb | False |  |
| duration_ms | integer | False |  |

Unique: [['run_id', 'sequence']].
- Store references and outcome summaries; not internal notes, secrets or hidden reasoning

## update_commitments

Specialist proposal and lead-confirmed next-update history

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| work_item_id | uuid | False | work_items.id |
| proposed_by | uuid | False | staff_principals.id |
| proposed_at | timestamptz | False |  |
| proposed_update_at | timestamptz | False |  |
| customer_safe_progress | text | False |  |
| reason | text | False |  |
| status | text | False |  |
| version | bigint | False |  |
| decided_by | uuid | True | staff_principals.id |
| decided_at | timestamptz | True |  |
| decision_reason | text | True |  |
| supersedes_id | uuid | True | update_commitments.id |
| operation_key | text | False |  |

Unique: [].
- Only lead can approve; original investigation deadline remains unchanged; source work version rechecked.
- SQL check: `status IN ('pending_approval','approved','rejected','superseded','missed')`.
- SQL check: `status NOT IN ('approved','rejected','superseded','missed') OR (decided_by IS NOT NULL AND decided_at IS NOT NULL)`.
- SQL check: `proposed_update_at > proposed_at`.

## complaint_intakes

Independent simulated intake; not full complaint adjudication

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| objection_id | uuid | False | customer_objections.id |
| work_item_id | uuid | False | work_items.id |
| queue_id | uuid | False | service_queues.id |
| recorded_by | uuid | False | staff_principals.id |
| recorded_at | timestamptz | False |  |
| status | text | False |  |
| external_receipt_ref | text | True |  |
| acknowledged_at | timestamptz | True |  |
| version | bigint | False |  |

Unique: [['objection_id'], ['work_item_id']].
- Explicit complaint request creates internal intake immediately; external acknowledgement requires trusted receipt.
- SQL check: `status IN ('recorded','pending_delivery','delivery_failed','acknowledged')`.
- SQL check: `status <> 'acknowledged' OR (external_receipt_ref IS NOT NULL AND acknowledged_at IS NOT NULL)`.

## objection_work_links

Parallel independently owned review/intake work

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| objection_id | uuid | False | customer_objections.id |
| work_item_id | uuid | False | work_items.id |
| kind | text | False |  |
| created_at | timestamptz | False |  |

Unique: [['objection_id', 'kind']].
- Both work items must belong to the objection case; distinct statuses do not automatically close one another.
- SQL check: `kind IN ('specialist_rereview','complaint_intake')`.

## lead_review_decisions

Immutable accountable plan/hold decisions

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| work_item_id | uuid | False | work_items.id |
| exhausted_plan_id | uuid | False | contact_plans.id |
| actor_id | uuid | False | staff_principals.id |
| decided_at | timestamptz | False |  |
| reason | text | False |  |
| kind | text | False |  |
| owner_id | uuid | False | staff_principals.id |
| review_at | timestamptz | True |  |
| operation_key | text | False |  |
| expected_work_version | bigint | False |  |

Unique: [].
- Current responsible lead only; one effective decision per expected work version, enforced atomically with work version increment.
- SQL check: `kind IN ('new_plan','review_hold')`.
- SQL check: `(kind = 'review_hold' AND review_at > decided_at) OR (kind = 'new_plan' AND review_at IS NULL)`.

## contact_plans

Original and separately approved post-exhaustion contact plans

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| case_id | uuid | False | cases.id |
| work_item_id | uuid | False | work_items.id |
| kind | text | False |  |
| status | text | False |  |
| version | bigint | False |  |
| previous_plan_id | uuid | True | contact_plans.id |
| approval_decision_id | uuid | True | lead_review_decisions.id |
| owner_id | uuid | True | staff_principals.id |
| max_attempts | integer | False |  |
| valid_from | timestamptz | True |  |
| valid_until | timestamptz | True |  |
| approved_slots | jsonb | False |  |
| calendar_ref | text | False |  |
| first_placed_at | timestamptz | True |  |
| created_at | timestamptz | False |  |

Unique: [['approval_decision_id']].
- Initial window set atomically on first placed call using D-19. Preserve initial first-callback due on work item. Global case/service-date limit applies across plans.
- SQL check: `kind IN ('initial','lead_approved')`.
- SQL check: `max_attempts > 0`.
- SQL check: `valid_until IS NULL OR valid_until > valid_from`.
- SQL check: `kind <> 'lead_approved' OR (approval_decision_id IS NOT NULL AND previous_plan_id IS NOT NULL AND owner_id IS NOT NULL AND valid_from IS NOT NULL AND valid_until IS NOT NULL)`.
- SQL check: `kind <> 'initial' OR (previous_plan_id IS NULL AND approval_decision_id IS NULL AND max_attempts = 3)`.

## contact_notes

Human-reviewed note content and immutable source provenance

| Field | Type | Nullable | Reference |
|---|---|---|---|
| id | uuid | False | primary key |
| contact_id | uuid | False | contacts.id |
| case_id | uuid | True | cases.id |
| proposal_id | uuid | False | proposals.id |
| reviewed_proposal_version | bigint | False |  |
| body | text | False |  |
| customer_allegations | jsonb | False |  |
| source_versions | jsonb | False |  |
| committed_by | uuid | False | staff_principals.id |
| committed_at | timestamptz | False |  |
| operation_id | uuid | False | operations.id |

Unique: [['proposal_id', 'reviewed_proposal_version'], ['operation_id']].

## Link and history constraints

Service transactions must check same-case/customer linkage for every related record; an FK alone does not enforce this. Cross-plan contact limits use case/service date. Approved plan/commitment supersession is atomic and preserves history. Separate original investigation/first-callback obligations from later plan windows. Identity, audit and model-safe projections remain distinct.
