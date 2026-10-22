# Delegated retest — transaction display and customer context

22 October 2026 · QA-03 / DEV-02 / DEV-08 · implementation `86ec657`.
Assessor/operator: Codex, delegated by the owner. **Owner sign-off remains pending.**

[PR #28](https://github.com/xc8609/service-agent-portfolio/pull/28) was reviewed and
merged as `5943b51` after all four required checks passed. This follow-up implements
[LG-01–04](../../projects/bank-service-assist/specs/DEV-08/lookup-gap-follow-up.md).
The [original four-task report](../../projects/bank-service-assist/evaluation/effort/results-20261022.md)
is preserved unchanged; this is a targeted completeness retest, not a new timing study.

## Actual browser walkthrough

Fresh disposable local PostgreSQL 16.2, Python 3.12, built React application and real
demo clock. No API model; scripted offline provider. Verified synthetic inbound
contact, DEMO-4242, both DEMO STORE CAD 85 posted records, saved report revision 1.
The statement matches the original task: “I bought once, but I see two charges for
CAD 85. I cannot tell which entry is extra. I do not have the receipt.”

| Check | Observed result | Disposition |
|---|---|---|
| T1, original five required items | Both records show CAD 85.00, posted, occurred 2026-10-18 and posted 2026-10-19 under UTC headings. Evidence says no relationship recorded and similarity is not proof of duplication. | 5/5, previously 3/5 |
| T4, original seven required items | Same preview includes one purchase, unresolved entry mapping, unavailable receipt, two posted CAD 85 records, no duplicate finding, existing investigation/queue and an uncommitted draft. No manual addition needed. | 7/7, previously 5/7 |
| Reload and review | Durable run reload keeps report v1 and its text. Loading the saved note shows the exact original in Customer allegations, separately from the reviewed body. | Passed; no approval clicked |
| Changed query | Clearing the merchant filter removes the old Agent preview and disables note approval. | Passed |
| Missing posting date | Unfiltered lookup shows pending DEMO NORTH CAFE and reversed DEMO PARKING with `Not recorded`; it does not invent an entry date. | Passed |

Actual run: `bc7835c8-5e56-4784-a144-defc4e19f6d9`; uncommitted draft:
`61390177-e77d-4974-be9d-fc39cb6ee800`. Transaction versions 1; related case version 2.
The operator used the UI to save the report and run/reload the assistant. There was
no note commit, new enquiry, callback or financial execution. Two exact-label browser
locator attempts did not match; fresh accessibility observations and semantic role
locators completed the same preparation. No time comparison is made.

T4's score covers the **whole visible preview**, including the new server-supplied
customer-reported block. The receipt is preserved verbatim, not inferred by NLP or
inserted into ledger facts. This does not establish model comprehension or quality.

| Complete manual transaction fields | Customer context beside the three-part draft |
|---|---|
| ![CAD and occurrence/posting dates](../images/lookup-fixed-manual.png) | ![Saved customer statement and unresolved mapping](../images/lookup-fixed-handoff.png) |

## Actual first preview text

> Customer-reported · report v1
>
> I bought once, but I see two charges for CAD 85. I cannot tell which entry is extra. I do not have the receipt.
>
> Customer statement, not a verified outcome. Retain reported material gaps for customer-service follow-up; review before committing.
>
> Facts
> Two posted entries were retrieved: DEMO STORE — CAD 85.00, occurred 2026-10-18T07:00:00-05:00, posted 2026-10-19T07:00:00-05:00 (source version 1); DEMO STORE — CAD 85.00, occurred 2026-10-18T07:00:00-05:00, posted 2026-10-19T07:00:00-05:00 (source version 1). No source relationship is recorded. Existing enquiry DEMO-CASE-001: investigating. complaint intake: in progress; Demo complaint Casey in Demo complaint review. customer feedback: waiting for result; unassigned in Demo customer feedback. specialist investigation: awaiting documents; Demo specialist Alex in Demo card investigations. The saved customer report recognizes one purchase, but which entry is additional remains unresolved; this is a customer statement, not an adjudicated outcome.
>
> To confirm
> Similar entries do not establish a duplicate; confirm the purchase context and any recorded relationship. Keep both entries grouped for verification; do not infer which entry is disputed. No financial execution is confirmed.
>
> Next step
> Follow up with Demo card investigations on the existing enquiry rather than submit a duplicate.


UI also displayed `awaiting_human`, usage unavailable and the uncommitted draft ID.

## Regression evidence

- **293 API tests passed** on disposable local PostgreSQL 16.2, including six new
  handoff cases: default/terse providers, exact full-length allegations, durable reload,
  no committed note, report correction invalidation and specified-entry recognition.
- **45 browser tests passed** on a separate disposable server with the repository's
  fixed browser clock: existing AG-01/AG-02 expanded; new UI-02 checks USD/CAD, UTC
  day rollover and nullable posting date at the response-rendering boundary. The
  manual walkthrough above uses actual unmodified demo responses and a real clock.
- **109 offline tests passed**, two optional SQL modules skipped locally (DuckDB
  unavailable). Frontend build/typecheck, Ruff/format, workflow/contract validators,
  publication/link checks and whitespace checks passed. CI results are linked by PR.

The observed gaps are closed in this candidate. Existing-case, rule, permission and
human-review paths remain covered by the full suite. This record does not establish
human time savings, live-model qualification, owner UAT or deployment acceptance.
