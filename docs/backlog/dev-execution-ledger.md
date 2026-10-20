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
| DEV-06 | Reviewed notes, receipts and retries | [PR 5](https://github.com/xc8609/service-agent-portfolio/pull/5); four cloud checks passed |
| DEV-07 | Reviewed specialist referral and typed intake | [PR 6](https://github.com/xc8609/service-agent-portfolio/pull/6); four cloud checks passed; downstream follow-up in DEV-11–13 |
| DEV-11 | Specialist result and owned feedback | [PR 7](https://github.com/xc8609/service-agent-portfolio/pull/7); four cloud checks passed |
| DEV-12 | Contact plans, attempts and closure guards | [PR 8](https://github.com/xc8609/service-agent-portfolio/pull/8); four cloud checks passed |
| DEV-13 | Overdue work, objection/review and complaint | [PR 9](https://github.com/xc8609/service-agent-portfolio/pull/9); four cloud checks passed |
| DEV-09 | Provider boundary and qualification | [PR 10](https://github.com/xc8609/service-agent-portfolio/pull/10); four cloud checks passed; live qualification explicitly deferred |
| DEV-08 | Bounded persisted Agent | [PR 11](https://github.com/xc8609/service-agent-portfolio/pull/11); four cloud checks passed |
| DEV-10 | Evaluation marts and Tableau | [PR 12](https://github.com/xc8609/service-agent-portfolio/pull/12); SQL/CSV checks passed; Desktop open verified; refresh/layout acceptance pending |

Confirmed D-17–25 remain binding. No contact attempt quota reset, automatic closure
of unanswered contact, financial execution or invented customer evidence. Keep
public story cards and execution evidence aligned with actual verified changes.

Owner confirmed on 20 October: complete DEV-09 offline first; live model validation is deferred. No paid model calls are authorized by this execution pass.

## Final integration review

[PR 13](https://github.com/xc8609/service-agent-portfolio/pull/13) corrects DEV-13-AC04:
published findings supersede interim progress tasks/commitments without losing overdue
history. 181 PostgreSQL API tests passed. DEV-10 adds six metric tests to the prior
174-test baseline; the integration regression adds one. The latest local demo runs
these branches on localhost with synthetic data.

Trello DEV-06–13 cards are verified in **Review and acceptance**, with per-story PR
and execution comments. Nothing is marked Done or merged. DEV-10 Tableau native
open is verified after fixing three XML compatibility errors; refresh/layout acceptance remains pending. Live model testing is owner-deferred;
human effort study and owner UAT remain release gates. Voice/retail are later scope.
