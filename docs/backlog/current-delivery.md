# Current delivery — finish the bank core first

**27 October 2026:** native Tableau checks completed for both analytics cases: three
retail page screenshots, and the complaint dashboard's shared filters verified after
fixing a broken channel filter and an unshared product filter.

**26 October 2026:** the owner asked to finish and merge investment PR #37, so
INV-04 (cited Agent drafts) is delivered. INV-05 saved briefs, memory and live model
integration remain paused; the retail and complaint cases are unchanged.

**Latest owner direction — 24 October 2026:** pause investment Agent development
and build [Retail Customer & Sales Analysis](../../projects/retail-customer-analytics/README.md).
The selected case uses real transaction records, SQL and visual reporting to explain
sales changes, repeat purchasing and customer-development priorities. Follow the
[RA-01–06 plan](retail-analytics.md). Investment PR #37 remains separate and is not
merged by this change; memory, live model integration and further investment features
are paused. The dated investment direction below is superseded for current priority.

**Retail review complete — 24 October 2026:** the recorded Tableau interaction
checks are complete, and the owner accepted the three-page business findings and
recommendation priorities (A13). The [retail case study](../../projects/retail-customer-analytics/docs/business-case.md)
contains the walkthrough, evidence and accepted priorities. Proposed commercial
interventions have not been executed.

**24 October 2026 direction:** the owner selected an investment Agent as the next
case, with architecture inspiration from ValueFocus rather than a product copy.
Start [Investment Research Brief](../../projects/investment-research/README.md):
real annual-report facts and a deterministic comparison, followed by a manual
research workspace, one Agent and reviewed briefs. The
[two-Sprint plan and INV-01–06 cards](investment-research.md) govern this work.
Bank core remains the completed delegated-assessment baseline; hosting, paid model
API integration, voice and retail stay deferred. Earlier priorities below are dated history.

**Owner confirmation — 24 October:** the investment scenario is financial-report
changes and a research brief. It is an independent Agent application with its own
web/API entry points, tools and build under `projects/investment-research/`, not a
bank-workspace feature. INV-03's independent manual workbench is merged in #36.
INV-04 adds scoped evidence tools and cited draft generation; saved/reviewed brief
versions remain INV-05. [Agent verification](../../projects/investment-research/docs/agent-acceptance.md).

**23 October 2026 status:** the bank core has reached delegated acceptance and local
demo handover. [Completion/evidence matrix](../uat/bank-core-closeout.md) is the current
status, superseding the dated snapshots below. PR #30 is merged as `0799865`; all four
required checks and both post-merge workflows passed. No blocking defect was found
in the assessed offline core. Personal owner sign-off and broader release gates
remain explicit; this does not mark all original Sprint or QA/OPS stories Done.

**Presentation direction — 23 October 2026:** the owner deferred public deployment.
Use GitHub as the review surface: business problem, current/target process, decision
rights, Agent contribution, screenshots and acceptance evidence. The
[case study](../case-study.md) and [workflow walkthrough](../demo.md) are the entry points;
local setup remains available for technical reviewers.

At that stage, next was to collect feedback on this business walkthrough. No hosting resources or model
API integration are planned in the current increment. Do not add further
micro-features absent a concrete defect. Hosting, API, voice and retail remain
future options; the original forecast below is planning history.

## Dated delivery history

20 October 2026 · Owner-directed simplification (D-26). Delivery route updated 22 October 2026.

Build a small, explainable service workflow before expanding its automation.
Keep the existing application initialization and story IDs. Preserve accepted
business rules; avoid further expanding the first increment into a complete
bank operations platform.

## Core demonstration

1. Establish an authorized contact; record the customer's charge enquiry.
2. Query and explicitly select the transaction pair; separate reported statements
   from source facts and show pending/posted differences and uncertainty.
3. Retrieve applicable handling rules and any existing related work.
4. Review an explanation/note; if unresolved, approve a specialist enquiry and
   display its real receipt and accountable queue.
5. Record a role-protected synthetic specialist finding; customer service records
   the manual callback outcome. Undelivered feedback never automatically closes.
6. Add a bounded Agent to assemble evidence and draft through the same workflow;
   retain the manual fallback and measure quality/effort against it.

D-23 allows paired unresolved recognition. D-24 allows supporting material to
follow through specialist-requested/customer-service follow-up. D-25 allows
contact gaps while retaining customer-service ownership, original deadlines and
an open feedback obligation. Preserve these even when follow-up is manual.

## Sprint sequence and reviewable increments

The existing [capacity/calendar forecast](sprints.md) remains indicative. This is
an execution-priority overlay, not a recalculated delivery promise or permission
to mark entire stories complete from a partial slice.

| Existing Sprint | Increment / stories | Exit evidence | Historical status (21 October 2026) |
|---|---|---|---|
| S02 | Initialization, contracts, CI; DEV-01/QA-01/OPS-01 plus DEV-02/03 reads | Runnable demo, authorization failures and CI/PR evidence | Merged (#1–#2); owner UAT pending |
| S03 | Manual investigation: DEV-02/03/04/05 | Statement/selection, current case and policy evidence, stale-query fix, negative permission tests | Merged (#2–#4); owner UAT pending |
| S04 | Reviewed note and referral DEV-06/07; provider boundary DEV-09 | Draft/edit/approve, missing-material/contact-gap intake, atomic receipt, replay tests | Merged (#5, #6, #10, #15); live provider qualification deferred |
| S04A | Result, feedback and exceptions DEV-11/12/13 | Finding, accountable feedback, actual outcome, no false closure, objections, complaint delivery | Merged (#7–#9, #13, #16); owner UAT pending |
| S05 | Bounded assistance DEV-08 | Allowlisted tools, cited drafts, manual fallback and model-failure scenarios | Merged offline (#11); real-model route unqualified |
| S05A / S06 | Evaluation, SQL/Tableau evidence, staging/UAT and bank release | Reconciled metrics, executed evaluation, reproducible deployment/recovery and recorded acceptance | DEV-10 merged (#12, #14); QA-02 pilot executed ([report](../../projects/bank-service-assist/evaluation/README.md)); staging, owner UAT and Tableau refresh acceptance pending |

## Keep out of the first core increment

- Autonomous outbound calls or a new contact-centre/CRM/profile management system.
- Financial execution, automatic duplicate-charge adjudication or refunds.
- Separate automated retry schedules for each possible supplementation/contact issue.
- Multiple live providers, multi-agent orchestration or new infrastructure before
  one bounded Agent and manual fallback have demonstrated value.
- Voice and retail implementation; keep them as later independent releases.

Complex contact follow-up remains an owned manual task/lead review in the first
increment. No new automated calls are created by this simplification. Existing
quota/history/deadline controls must not be bypassed; do not label full DEV-12/13
accepted until their specified automation is implemented and tested. The earlier
question about allocating supplementary calls to plans is deferred with that
scheduler, not an invitation to invent a new quota or block unrelated core work.

## Review and release snapshot — 22 October

All bank DEV increments are merged to `main` with automated evidence in the
[execution ledger](dev-execution-ledger.md). Merged is not owner-accepted. Keep the
original Sprint forecast as planning history, not actual elapsed person-days.

1. [REV-01](review-fixes.md) and [REV-02](uat-corrections.md) merged in #21/#22; the [delegated core retest](../uat/2026-10-21-retest.md) passed its observed scope. Retain the original failed assessment and pending owner sign-off — [UAT pack](../uat/README.md).
2. Tableau refresh/layout acceptance for both workbooks; Desktop open is verified for the bank workbook.
3. QA-02's [12-case subscription exercise](../../projects/bank-service-assist/evaluation/r2/subscription-results-20261022.md) is recorded, with the eight engineering checks mapped to regressions. #25 connected context/questions and fixed recognition/policy gaps; #26 clarified closure and summaries. At `761aeaf`, [CI passed 286 API and 44 browser tests plus container smoke](https://github.com/xc8609/service-agent-portfolio/actions/runs/39859494492). Session answers and scripted runtime evidence remain separate; API use and independent model qualification are deferred.
4. OPS-02 now distinguishes a bounded synthetic public demo (3a) from identity-backed
   staging/recovery (3b); both need explicit hosting/access decisions before deployment.

No automatic phone execution, financial action or bulk architecture rewrite. Voice
and retail remain later releases. Do not equate offline tests with real model quality.

## Presentation and correction history — QA-03 / OPS-03

The [five-minute presentation](../demo.md) and [one-page case study](../case-study.md)
package the existing core for reviewers. Current screenshots and dated CI counts are
linked; historical evaluation records are not rewritten. This is presentation evidence,
not owner acceptance, a recorded video or measured handling time.
PR [#27](https://github.com/xc8609/service-agent-portfolio/pull/27) also corrects a
wall-clock-dependent browser test: a shared test-only clock and one service-close
regression bring the API suite to 287 tests; the browser suite remains 44. The
interactive service-hours rule is unchanged. #27 was reviewed and squash-merged as
`81ae6f1`; all four required checks passed on its reviewed head. Both post-merge main
workflows also passed: [runtime](https://github.com/xc8609/service-agent-portfolio/actions/runs/39867907394)
and [offline](https://github.com/xc8609/service-agent-portfolio/actions/runs/39867907380).

The [four-task rehearsal](../../projects/bank-service-assist/evaluation/effort/results-20261022.md)
now records the actual first answers, navigation, elapsed operator time and omissions.
The prepared workspace used zero page changes versus ten in the simulated source pack,
but required within-page movement and did not establish a speed gain. Case/rule lookup
was complete; transaction display and the scripted handoff each missed two checklist
items. This is a Codex-operated rehearsal, not independent human measurement or model
qualification. QA-03 owner acceptance remains pending.

PR #28 was reviewed and merged as `5943b51` with all four required checks green.
The bounded DEV-02/DEV-08 follow-up now implements
[LG-01–04](../../projects/bank-service-assist/specs/DEV-08/lookup-gap-follow-up.md):
explicit currency/posting dates and a server-owned customer-statement block alongside
the corrected recognition wording. No new service or model route was added.

[Targeted T1/T4 retest](../uat/2026-10-22-lookup-gap-retest.md): 5/5 and 7/7 required
items, with actual screenshots and first preview text. Local verification passed
293 API tests, 45 browser tests and 109 offline tests (two optional SQL modules
skipped). The first comparison remains unchanged; no human speed gain is inferred.
Next: owner walkthrough using the corrected demo. Model API, public hosting, voice
and retail remain separate later decisions.

23 October follow-up: the Agent's specified-entry label now uses the same UTC date
as the transaction table. [Regression and observed retest](../uat/2026-10-23-utc-date-retest.md)
cover a cross-midnight transaction, saved statement, reload and stale-query denial;
294 API and 45 browser tests passed. No additional workflow or model integration.

Done for the presentation slice means: readable entry points, reproducible setup,
actual synthetic screenshots, verified links/counts and passing publication/CI checks.
Keep QA-03 owner UAT and OPS-03 release acceptance separate. Public hosting requires
a host/access decision; API, voice, retail and the larger R2 protocol stay deferred.
Existing Sprint estimates remain planning history; this packaging is not a new platform Sprint.

## Adaptability within the small core

Owner requested lightweight enterprise adaptation on 20 October. The DEV-02/08/09
[follow-up scope](../../projects/bank-service-assist/specs/contracts/extensibility-change.md)
adds source-mapping rehearsal and server-owned model profiles within S04/S05 review.
It does not add another platform service or move voice/retail ahead of bank acceptance.
Real source ingestion, production identity and model qualification remain explicit
future gates after an institution's interfaces and policies are known.
