# State transitions v0.4

BANK-S02-v0.4 · Business decisions are accepted as referenced; runtime state-machine implementation is pending.

| ID | Entity | From → To | Actor | Guards | Effects / status |
|---|---|---|---|---|---|
| ST-01 | investigation | queued → assigned | specialist | claim permitted queue; expected work version matches | set assignee; keep queue owner; D-12/D-13 |
| ST-02 | investigation | assigned → investigating | specialist | current assignee and scope | append start event; design |
| ST-03 | investigation | investigating → completed | specialist | approved finding and evidence; version fresh | publish result version; enqueue one feedback item; D-13 |
| ST-04 | feedback | queued → assigned | feedback_representative | eligible membership; atomic expected-version claim | grant minimum detail scope; audit claim; D-17 |
| ST-05 | feedback | assigned → retry_scheduled | feedback_representative | actual no-answer; quota/window permit; approved slot | reserve one slot; retain owner; D-16 |
| ST-06 | feedback | retry_scheduled → assigned | feedback_representative | slot due and still permitted; latest result fresh | prepare callback, no fabricated call outcome; design |
| ST-07 | feedback | assigned or retry_scheduled → lead_review | scheduler | three counted attempts or elapsed window | create one review task; retain case open; D-16/D-19; third service date 17:00 deadline accepted |
| ST-08 | feedback | assigned → completed | feedback_representative | actual contact plus trusted fresh identity; approved explanation delivered; result current | record response and any unresolved objection; D-14 |
| ST-09 | case | open or awaiting_feedback → closed | assigned feedback or scoped lead | current authorized result; necessary actions completed or none; verified feedback; no outstanding work; fresh version | audit reason and references; set closed_at; D-14 |
| ST-10 | proposal | draft → stale | system | source/result/assignment scope changed | preserve human edits; prevent commit; design |
| ST-11 | proposal | draft → committed | authorized person via server | explicit approval; fresh versions; allowed action; domain transaction succeeds | business+audit+outbox+receipt atomically; design |
| ST-12 | investigation | investigating → investigating | scheduler | original due time breached and still unfinished | keep due time/owner; deduplicated escalation; progress task; D-14/D-20; original specialist retained; lead confirms specialist-proposed next update; feedback queue communicates |
| ST-13 | case | open or closed → under_review | authorized reviewer | customer objection captured; linked re-review route approved | preserve old finding and disposition; link new work; D-21; separate linked re-review and complaint intake; v0.4 contract authored |
| ST-14 | work_item | assigned → assigned | queue_lead | managed queue; reasoned reassignment; expected version | revoke prior assignee scope; invalidate affected approval; Proposed role detail |
| ST-15 | agent_run | running → awaiting_approval | agent_runtime | typed proposal with citations; bounded run | persist draft; stop run; no operational effect; D-15 |
| ST-16 | agent_run | running → failed | worker | deadline/provider/schema failure | safe error; preserve committed work/manual path; design |
| ST-17 | feedback | lead_review → retry_scheduled | queue_lead | responsible lead; reason; fresh versions; explicit bounded new plan approved | create distinct approved plan and scheduled work; retain prior attempts/deadlines/approvals; never automatic reset; D-22 accepted; v0.4 plan contract authored |
| ST-18 | feedback | lead_review → review_hold | queue_lead | responsible lead; reason; named owner; review date; fresh versions | retain open case and history; create review obligation; no automatic closure; D-22 accepted; v0.4 hold contract authored |
| ST-19 | commitment | none → pending_approval | specialist | current investigation assignee; future proposed time; fresh versions | record customer-safe progress and pending proposal; no approved promise; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-20 | commitment | pending_approval → approved or rejected | queue_lead | responsible investigation lead; current versions; ongoing investigation | record decision; supersede previous active commitment atomically; preserve original due; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-21 | objection | captured → linked_work_created | authorized_staff | exact statement; explicit complaint flag; current case scope | persist specialist re-review and optional independent complaint intake/work/outbox atomically; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-22 | complaint_intake | recorded or delivery_failed → pending_delivery | worker | durable request; configured destination; idempotent key | retain request and enqueue/retry delivery independently of re-review; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-23 | complaint_intake | pending_delivery → acknowledged or delivery_failed | trusted_adapter | validated receipt or recorded delivery failure | record actual receipt/status; never infer acknowledgement from generated text; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-24 | feedback | review_hold → lead_review | scheduler | hold review_at reached and still current | create deduplicated review work for owner; no automatic contact/closure; D-20/D-21/D-22 mapped in v0.4; runtime pending |
| ST-25 | contact_plan | active → exhausted or expired | scheduler | quota reached or deadline elapsed; unresolved feedback | retain plan and attempts; route feedback to lead review; D-20/D-21/D-22 mapped in v0.4; runtime pending |

Forbidden transitions:

- lead_review -> closed solely because calls exhausted
- proposal draft -> financial execution
- agent run succeeded -> case resolved
- callback no_answer -> feedback completed
- stale proposal -> commit without refresh
