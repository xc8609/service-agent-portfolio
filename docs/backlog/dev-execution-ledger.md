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
and execution comments. At that time nothing was marked Done or merged (all PRs were merged on 21 October; see below). DEV-10 Tableau native
open is verified after fixing three XML compatibility errors; refresh/layout acceptance remains pending. Live model testing is owner-deferred;
human effort study and owner UAT remain release gates. Voice/retail are later scope.

## Lightweight adaptation follow-up

[PR 14](https://github.com/xc8609/service-agent-portfolio/pull/14) repairs the actual
Tableau Desktop XML load errors. Desktop opened the workbook; refresh and layout
acceptance remain partial.

[PR 15](https://github.com/xc8609/service-agent-portfolio/pull/15) adds server-owned model selection/audit fingerprints and two
synthetic source-mapping previews. See [change scope and EXT-01–07 acceptance](../../projects/bank-service-assist/specs/contracts/extensibility-change.md).
204 local PostgreSQL/API tests passed, including 23 mapping/profile cases; five
offline tests, SDD/publication checks and Ruff passed. No real bank connector,
provider qualification, production identity or SDK runtime adoption is claimed.
The review follows S04/S05; the original Sprint forecast is not actual effort.

Trello comments verified on DEV-02, DEV-08, DEV-09, DEV-10 and S04 for these
follow-ups; original story specifications remain versioned planning history. No
card marked Done. PR 14 has four passing cloud checks. PR 15 CI tracks its latest
head; local evidence is 204 tests including the precision-boundary regression.

## Independent review follow-up — 20 October 2026

An independent code review found five workflow/evidence defects and several
adaptation gaps. Each fix is committed in the PR that introduced the behaviour and
merged forward through the stack; no applied migration was edited.

| PR | Correction |
|---|---|
| [8](https://github.com/xc8609/service-agent-portfolio/pull/8) | A closed case accepts no new result; a material answer (received, unavailable, declined) ends the customer-service task and returns the specialist from `awaiting_documents`; a finding supersedes open requests, so a refusal no longer blocks closure |
| [12](https://github.com/xc8609/service-agent-portfolio/pull/12) | `reject_proposal` makes declining a draft a recorded human decision; acceptance is reported separately for Agent and staff drafts, so it is no longer 100% by construction |
| [13](https://github.com/xc8609/service-agent-portfolio/pull/13) | One escalation per case and deadline; a verified inbound caller can dispute a published finding, reopening a closed case with history retained (forward migration 012) |
| [15](https://github.com/xc8609/service-agent-portfolio/pull/15) | Qualification bound to the route fingerprint (credential reference included); health reports the selected route; source-key scope and booking-time checks; README walkthrough of the full flow |

Local evidence on the integrated head: 214 PostgreSQL 16.2 API tests and 35 Chromium
browser tests passed (against a disposable database), plus offline tests, both SDD
validators, publication checks, Ruff and the TypeScript/Vite build. Owner UAT, live
model qualification and Tableau refresh acceptance remain pending.

## Post-merge state — 21 October 2026

PRs 1–15 are squash-merged to `main` in dependency order (one linear commit per
story). [PR 16](https://github.com/xc8609/service-agent-portfolio/pull/16) completes the
closure path: complaint delivery (ST-22/23) and synthetic external action receipts.
Requirements baseline v0.3 adds D-23–D-28 rules, review-derived behaviour and EXT
requirements; every requirement now lists the tests that verify it in the
[traceability matrix](traceability-matrix.md), checked offline in CI. Owner UAT is
prepared in the [UAT pack](../uat/README.md) and has not been executed.

