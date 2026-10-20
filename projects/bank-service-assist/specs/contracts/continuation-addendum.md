# Continuation contract completion v0.4

BANK-S02-v0.4 · D-20/D-21/D-22 are business-accepted. Their structured contracts are now authored; implementation and runtime acceptance are pending.

| Previously identified gap | Current contract | Data / authority | Planned tests |
|---|---|---|---|
| Next-update proposal and confirmation | propose_next_update / confirm_next_update | update_commitments; assigned specialist proposes, responsible investigation lead confirms | DEV-13-T01/02/04 |
| Progress before completed finding | create_proposal progress_update variant | work version and optional approved commitment; no unsupported date promise | DEV-13-T03/04 |
| Parallel re-review and complaint intake | capture_customer_objection plus idempotent register_complaint_intake | objection_work_links + complaint_intakes; distinct queue work; external acknowledgement requires receipt | DEV-13-T05/06/07 |
| Exceptional contact or hold | decide_contact_continuation with new_plan/review_hold alternatives | contact_plans + lead_review_decisions; responsible feedback lead only, mandatory reason and current versions | DEV-12-T03/07 |
| Per-plan versus lifetime contact history | mandatory contact_plan_id on attempts/reservations | original plan retained, new plan explicitly bounded, global per-date limit preserved | DEV-12-T01/02/04/07 |
| Human note revisions | edit_proposal and note proposal subtype | contact_notes, reviewed revision and source hash, audit history | DEV-06-T01–07 |

## Domain transaction requirements

- Unknown blocker or unapproved date stays unknown. A new update commitment never replaces an original investigation deadline. One approved current commitment per work item; supersession preserves prior approval and overdue evidence.
- Objection and requested branch work persist atomically. Complaint intake must not wait for specialist findings. Downstream delivery can fail independently; status remains pending/failed, not acknowledged. One intake per objection, with safe replay.
- Contact plan creation/hold and lead decision are atomic. Owner must be eligible for the feedback queue; future window and all slots must lie within configured service/contact windows. A new plan is not an automatic three-call reset. Held review creates an obligation for named owner at review_at, never contact authorization or resolved closure.
- Actual late/duplicate call facts are retained, even if they violate a policy. Scheduling denies unauthorized calls; record ingestion must not conceal what happened. Unknown plan linkage goes through authorized reconciliation rather than inventing a plan.
- Same-case/customer checks span all foreign keys. Database foreign keys alone do not authorize reads or approvals. Concurrent result/assignment changes invalidate pending approvals. Caller-supplied identities or verification flags are not trusted.

## Readiness and test boundary

[JSON schemas](agent-tools.json), [HTTP](openapi.json), [role matrix](permissions.json), [structured model](data-model.json) and [DDL](schema-reference.sql) now contain the continuation definitions. [Schema boundary fixtures](continuation-schema-cases.json) check payload shapes and prohibited fields; planned runtime cases remain in DEV-12/13 and the delivery test manifest. SQL has not been applied. No API, worker, UI or live provider has passed by writing these files.

Additional escalation levels, fixed progress cadence and unavailable-lead substitutions are not implied. Configure eligible lead/intake queues before release; unknown configuration fails visibly. Numeric benefit/model budgets and provider qualification remain separate gates.
