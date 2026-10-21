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
| S04 | Manual note and reviewed referral: DEV-06/07; provider qualification DEV-09 | Draft/edit/approve, missing-material/contact-gap intake, atomic receipt, replay tests | Planned; typed intake extension still needed |
| S04A | Minimal result and manual feedback: DEV-11, core guards from DEV-12/13 | Finding, accountable feedback, actual outcome, no false closure, manual lead review for exceptions | Planned; advanced continuation automation deferred |
| S05 | Bounded assistance: DEV-08 | Qualified provider, allowlisted tools, cited drafts, manual fallback and model-failure scenarios | Planned; no Agent code yet |
| S05A / S06 | Evaluation, SQL/Tableau evidence, staging/UAT and bank release | Reconciled metrics, executed evaluation, reproducible deployment/recovery and recorded acceptance | Planned |

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

## Next PR-sized work after the foundation

- DEV-03: statement/recognition and query-context correctness.
- DEV-04/05: existing-work and policy evidence, with missing/source-failure paths.
- BA-07/09 + DEV-06/07: typed intake and reviewed persistence, then referral.
- DEV-11: result and manual feedback with minimal deadline/closure guards.
- DEV-09/08: provider qualification and bounded assistant, using tested services.

No bulk runtime rewrite solely to change folder names. Keep each PR tied to its
story, accepted rules, design and executed tests. Re-estimate changed/deferred
work before committing a Sprint; do not reuse the old expanded forecast as a
verified estimate for this narrower slice.
