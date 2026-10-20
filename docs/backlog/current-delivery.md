# Current delivery — finish the bank core first

20 October 2026 · Owner-directed simplification (D-26).

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

| Existing Sprint | Increment / stories | Exit evidence | Current status |
|---|---|---|---|
| S02 | Initialization, contracts, CI; DEV-01/QA-01/OPS-01 plus pulled-forward DEV-02/03 reads | Runnable demo, authorization failures and CI/PR evidence | Read slice under PR review; intake rules accepted |
| S03 | Finish manual investigation: DEV-02/03/04/05 | Statement/selection, current case and policy evidence, stale-query fix, negative permission tests | DEV-03/04 and DEV-05 inbound rule reads under PR review; full workflow and owner acceptance pending |
| S04 | Manual note and reviewed referral: DEV-06/07; provider qualification DEV-09 | Draft/edit/approve, missing-material/contact-gap intake, atomic receipt, replay tests | DEV-06/07 implemented in PRs 5/6; DEV-09 offline adapters in PR 10; live qualification deferred by owner |
| S04A | Minimal result and manual feedback: DEV-11, core guards from DEV-12/13 | Finding, accountable feedback, actual outcome, no false closure, manual lead review for exceptions | DEV-11/12/13 implemented in PRs 7/8/9; local worker, manual callbacks; owner UAT pending |
| S05 | Bounded assistance: DEV-08 | Qualified provider, allowlisted tools, cited drafts, manual fallback and model-failure scenarios | DEV-08 offline runtime in PR 11; live model validation deferred |
| S05A / S06 | Evaluation, SQL/Tableau evidence, staging/UAT and bank release | Reconciled metrics, executed evaluation, reproducible deployment/recovery and recorded acceptance | DEV-10 export/workbook candidate; Desktop open verified; refresh/layout, human study and staging/UAT pending |

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

## Current review and release gates

All bank DEV offline increments now have implementation/evidence in the
[execution ledger](dev-execution-ledger.md); review stacked PRs in dependency order.
They are not merged or owner-accepted. Keep the original Sprint forecast as planning
history, not actual elapsed person-days or completed Sprint acceptance.

1. Review manual workflow and exceptions together with the owner.
2. Complete Tableau refresh/layout acceptance; Desktop open is verified.
3. Qualify one real provider when the owner resumes that explicitly deferred work.
4. Run the B0/B1 effort/quality evaluation and staging recovery/UAT before release.

No automatic phone execution, financial action or bulk architecture rewrite. Voice
and retail remain later releases. Do not equate offline tests with real model quality.

## Adaptability within the small core

Owner requested lightweight enterprise adaptation on 20 October. The DEV-02/08/09
[follow-up scope](../../projects/bank-service-assist/specs/contracts/extensibility-change.md)
adds source-mapping rehearsal and server-owned model profiles within S04/S05 review.
It does not add another platform service or move voice/retail ahead of bank acceptance.
Real source ingestion, production identity and model qualification remain explicit
future gates after an institution's interfaces and policies are known.
