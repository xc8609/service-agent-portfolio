# Agent tool and trusted command registry

BANK-S02-v0.4 · Current candidate; application implementation and runtime acceptance pending.

Only the model-tool allowlist is available to the agent. UI/human commands are not model tools. [JSON Schemas](agent-tools.json) and [OpenAPI](openapi.json) are canonical; domain effects require server permissions and transitions.

| Interface | Exposure | Purpose / authority |
|---|---|---|
| get_contact_context | agent | Get trusted contact context and allowed actions. |
| search_transactions | agent | Find scoped candidates; do not infer intent or a duplicate. |
| get_transaction_evidence | agent | Inspect selected entries, verified relationships and related work. |
| get_case_snapshot | agent | Read versioned current business state and approved disclosure. Return only authorized customer-safe timeline, approved commitments and linked task metadata; exclude pending/rejected commitment details from feedback/model contexts. |
| search_policy | agent | Search applicable and permitted policy metadata. |
| get_policy_section | agent | Fetch exact permitted section for a citation. |
| get_contact_attempts | agent | Read persisted actual callback attempts and allowed windows. |
| get_service_targets | agent | Read deterministic due times, calendar and retry eligibility. |
| create_proposal | agent | Persist an editable draft only; no operational mutation or communication. |
| get_operation_status | agent | Reconcile a permitted earlier write before retry. |
| accept_specialist_work | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| claim_feedback_task | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| record_specialist_result | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| record_callback_attempt | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| capture_customer_objection | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| approve_and_commit_proposal | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| evaluate_due_work | never_model_callable | Authenticate trusted actor; verify current role, assignment, customer consistency, permitted state transition and versions within transaction. |
| propose_next_update | never_model_callable | Assigned specialist only; ongoing investigation; timestamp is future and in service calendar. Server derives proposer. Does not authorize disclosure or replace due time. |
| confirm_next_update | never_model_callable | Responsible lead of investigation queue only; pending current commitment and ongoing investigation. Preserve original due time; do not approve a past update time. |
| register_complaint_intake | never_model_callable | Current assigned feedback staff, current specialist or responsible lead; objection explicitly requested complaint. Queue comes from trusted configuration; intake unique per objection. Never wait for re-review. Only trusted adapter may acknowledge external receipt. |
| decide_contact_continuation | never_model_callable | Responsible feedback-queue lead only; exhaustion/expiry and lead_review state; explicit limits, future dates and eligible owner. New plan must retain per-service-date limit and permitted contact windows. Cannot mutate old plan or auto-close. |
| edit_proposal | never_model_callable | Authorized staff for this case/contact only; draft/stale proposal only. Cannot change proposal kind, customer, contact or case linkage. Preserve previous revision in audit. Replacement sources revalidated; no approval/commit. |

## Semantic guards

- Customer proof must be issued by trusted identity adapter and current callback contact; no body verification_result can assert success.
- A connected_verified outcome requires dial_state=connected and a valid trusted verification assertion; otherwise reject.
- First callback target is an attempt, not completed feedback. Store genuine duplicate call facts even if policy violation; scheduling prevents additional allowed calls.
- Three-day retry exhaustion never invokes automatic resolution. Accepted D-18: A technical failure with dial_state=not_placed does not consume contact quota. Persist the fault and preserve all original deadlines. A placed unanswered call consumes one contact attempt. The server derives counting from trusted call evidence; the agent cannot override it.
- Refund approval or pending required actions blocks normal closure; no financial execution endpoint.
- Actor+command+operation_key must match request_hash for a replay; authorization rechecked before returning receipt.
- Expected case and work versions are required by semantic validation for every existing-case proposal commit; nullable only for a genuinely new referral.
- Failed staff authorization/assignment prevents detailed data retrieval even if the customer was previously verified.
- Accepted D-19: First actually placed callback service date is day 1; the retry window ends at 17:00 America/Winnipeg on the third service date, excluding configured holidays and weekends. At the deadline, unresolved feedback enters lead review even if fewer than three calls occurred; no extension or automatic resolved closure. Before the first placed call, the original first-callback target still applies. Never-placed technical faults do not start or reset this window.
- Accepted D-20: Overdue investigation retains its original specialist and original deadline. Notify the responsible lead and create customer progress work in the feedback queue. The specialist proposes the next update time; the responsible lead confirms it. Preserve original overdue history. The agent may gather evidence, remind and draft, but cannot commit a completion date.
- Accepted D-21: Feedback staff preserve the customer statement and new evidence, and route disputed findings to specialist re-review. An explicit complaint request creates an independent complaint-intake record without waiting for re-review. Both tracks link to the original case and keep independent ownership/status. Objection or silence never implies resolved closure.
- Accepted D-22: After contact quota or window exhaustion, the responsible lead may approve a reasoned new contact plan or a review hold with a named owner and review date. Preserve all original attempts, deadlines and approval history. Never reset history or mark the case resolved merely because the customer did not answer. Agent suggestions cannot authorize the new plan or hold. Only decide_contact_continuation can approve the exceptional plan/hold; ordinary retry proposals cannot.
- v0.4: create_proposal note/progress_update is draft-only; edit_proposal is staff-only; generic approve_and_commit_proposal cannot approve commitments or exceptional contact plans.
- register_complaint_intake creates a durable independent intake/queue work record with unique objection link; no fabricated external acknowledgement. capture_customer_objection commits re-review and explicit complaint-intake work/outbox atomically; reconciliation command is idempotent.
- Contact continuation approval requires unique eligible owner, ordered future window, slots within that window and configured service calendar; at most one placed call per case/service date across ALL plans. Attempt quotas are server-derived. Unknown dial outcomes stay pending reconciliation, never silently not_placed.
- Idempotent replay: authenticate/authorize, then find matching actor/command/key and hash before stale-version rejection for a new effect. Return authorized prior receipt for identical replay; changed payload conflicts. Fresh commits then validate versions/transition and atomically persist business/audit/outbox.
- Commitment and contact-plan approval creates exactly one effective version per work item. Reject stale concurrent decisions. Held review creates one review task at due time; does not authorize automatic contact or closure.
- For progress_update commit, validate current source/work and approved commitment if supplied. Customer-visible future-date commitments must exactly match approved server data; human review cannot turn a generated date into approved evidence.
- Note commit uses contact_notes plus reviewed proposal revision and source versions; factual actions require receipts, while customer allegations remain explicitly labelled. Same operation returns same note.
- Timers use server clock; as_of is a scheduler-only testable input bounded by runtime configuration, never a model-supplied current time.
