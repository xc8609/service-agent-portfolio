# Bank DEV execution ledger

20 October 2026. Owner requested implementation of the designed bank DEV stories
with one reviewable PR per story. Voice and retail remain later releases. PRs are
stacked in dependency order; do not merge a child before its prerequisite. A passing
suite is engineering evidence, not business-owner UAT or production qualification.

| Story | Scope | State / dependency |
|---|---|---|
| DEV-01/02 | Database, scope, inbound reads | PR 1; feedback scope follows DEV-11 |
| DEV-03 | Statement and recognition | PR 2 |
| DEV-04 | Related case progress | PR 3; assigned-feedback extension follows DEV-11 |
| DEV-05 | Scoped handling rules | PR 4 |
| DEV-06 | Reviewed notes, receipts and retries | Implemented; PR preparation |
| DEV-07 | Reviewed specialist referral and typed intake | Next, depends on DEV-06 |
| DEV-11 | Specialist result and owned feedback | After DEV-07 |
| DEV-12 | Contact plans, attempts and closure guards | After DEV-11 |
| DEV-13 | Overdue work, objection/review and complaint | After DEV-11/12 |
| DEV-09 | Provider boundary and qualification | Offline implementation independent; live qualification needs approved credentials/budget |
| DEV-08 | Bounded persisted Agent | After domain tools and DEV-09 |
| DEV-10 | Evaluation marts and Tableau | After event-producing runtime |

Confirmed D-17–25 remain binding. No contact attempt quota reset, automatic closure
of unanswered contact, financial execution or invented customer evidence. Keep
public story cards and execution evidence aligned with actual verified changes.
