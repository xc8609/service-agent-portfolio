# QA-03 lookup gaps — DEV-02 / DEV-08 follow-up

22 October 2026. Small correction to existing stories; no new service, model route,
financial operation or workflow. Input: [four-task observed report](../../evaluation/effort/results-20261022.md).
Owner authorized fixing the two observed gaps and retesting T1/T4. Owner UAT remains separate.

## Story and acceptance

As a representative reviewing two similar charges, I need complete transaction dates
and the saved customer context beside the draft, so I can review a handoff without
reopening another section or silently losing a material gap.

- **LG-01 / DEV-02:** manual search shows each record's explicit currency code and
  amount, occurrence date and posting date. Date headings specify UTC and offsets
  are converted to UTC before selecting the date. A missing posting date displays
  `Not recorded`; it is not inferred from the occurrence date or status.
- **LG-02 / DEV-08:** the offline summary describes `one_purchase_unresolved` as the
  current reported state and retains the pair for verification. It does not ask staff
  to infer the additional entry. Specific/both/neither recognition remains distinct.
- **LG-03 / DEV-08:** the assistant preview includes the full saved customer statement
  and report revision in a visibly separate customer-reported block. This retains
  missing receipts or other context even when a provider omits them from its prose.
  The statement is not treated as a verified fact or executable instruction.
- **LG-04 / DEV-08:** replay retains the same statement; a report correction makes the
  old run stale, and a fresh run uses the latest report. Notes retain the original in
  `customer_allegations`, separate from the reviewed body. Drafts remain uncommitted;
  financial-claim guards, authorization and human approval are unchanged.

## Small implementation

Use existing authorized `currency`, `occurred_at` and nullable `posted_at` fields in
`apps/web/src/main.tsx`. No API or database change is needed for the table.

The runtime appends a server-owned optional `output.customer_report` from the same
version-checked inbound evidence snapshot. It is not a model tool argument. The UI
renders its statement as escaped React text alongside the three-part draft, labelled
customer-reported. The existing note allegation field already preserves it on save.
This avoids receipt-keyword extraction, quoting customer claims as ledger facts, or
weakening the financial-claim guard. No NLP understanding is claimed for the fixture.
Feedback runs do not gain inbound statement fields. Older persisted runs can omit
this additive field; a fresh run is needed to get the new preview block.

## Verification map

| Acceptance | Regression / retest |
|---|---|
| LG-01 | `lookup.spec.ts` UI-01 actual CAD pair; UI-02 USD/CAD, UTC day rollover and missing posting date (rendering-boundary response variation); delegated T1 |
| LG-02 | `test_agent_handoff.py` unresolved and specified entry; existing both/neither regressions; browser AG-01/AG-02; delegated T4 |
| LG-03 | Default and deliberately terse provider retain exact statement, including a 2,000-character claim/instruction sample; AG-01 renders and loads the allegation separately |
| LG-04 | Report-correction stale run/new revision, durable reload, no committed note and no raw statement in safe trace; existing unauthorized/financial-claim regressions |

Execution results and screenshots: [dated delegated retest](../../../../docs/uat/2026-10-22-lookup-gap-retest.md),
293 API tests, 45 browser tests, T1 5/5 and T4 7/7.
The original comparison remains unchanged. A passed regression does not prove lower
handling time, production readiness, live-model quality or owner acceptance.
