# Retail customer and sales analytics delivery plan

Direction confirmed 24 October 2026: pause investment Agent development and build
a data-analysis case aligned with customer management, commerce and payments.
The bank case remains available. This is an independent analytical project under
`projects/retail-customer-analytics/`, with no dependency on either Agent runtime.

[Business case](../../projects/retail-customer-analytics/docs/business-case.md) ·
[Metric definitions](../../projects/retail-customer-analytics/docs/metrics.md)

## Delivery sequence

Estimates are focused person-days for an analyst/developer with BA and reviewer
input, not calendar promises or the owner's weekly capacity. Each increment
ends with a reviewable result. The work can be shared by a small team without
creating additional services.

| Increment | Stories | Effort estimate | Reviewable result | Current status |
|---|---|---:|---|---|
| 1. Trusted data and sales | RA-01, RA-02 | 2–3 person-days | Source manifest, metric definitions, reproducible SQL, reconciled monthly sales and cancellation analysis | Implemented; technical checks passed |
| 2. Customer decisions and presentation | RA-03, RA-04 | 3–4 person-days | Customer and cohort analysis, three visual views, findings, recommendation and acceptance record | Analysis and portable report implemented; native Tableau and owner review pending |

## RA-01 — Establish reliable measures

**Story:** As an analyst, I need documented source and calculation rules so that
the same question produces the same result in SQL and the dashboard.

**Build:** download and record the official source; profile both source sheets;
retain source-row lineage locally; create typed staging data; document complete
months, eligible sales, cancellation records, duplicate handling and customer-ID
coverage. Keep ambiguous adjustments visible in quality counts instead of silently
turning them into purchases.

**Deliverables:** source manifest, data-quality summary, metric dictionary, staging
SQL, reproducible run command and focused calculation tests.

**Acceptance:** A1–A3 below. Depends on source availability.

## RA-02 — Explain sales patterns

**Story:** As a trading manager, I want to see sales, order and cancellation
patterns together so that I can choose a period, product or market to investigate.

**Build:** monthly measures for complete months through November 2011 and
country summaries; separate sales and cancellation values; comparisons with
consistent time coverage. Publish aggregate outputs suitable for visualization.

**Deliverables:** SQL marts, aggregate CSV and a sales view with concise findings.

**Acceptance:** A1, A2 and A6. Depends on RA-01.

## RA-03 — Understand repeat purchasing and customer groups

**Story:** As a customer-development manager, I want to compare repeat purchasing
and customer groups so that I can prioritize a justified follow-up proposal.

**Build:** count distinct eligible orders per identified customer; distinguish a
period repeat-buyer measure from a fixed-window repeat-purchase measure; show
monthly cohorts with observable cells only. Create mutually exclusive recency
and frequency segments from explicit rules at a fixed analysis date. Describe
them as observed behaviour rather than predicted churn or future value.

**Deliverables:** customer/cohort SQL, aggregate summaries, documented segment
rules and a proposed next action for a group supported by actual results.

**Acceptance:** A3–A5. Depends on RA-01.

## RA-04 — Present and verify the analysis

**Story:** As a reviewer, I want three readable views and a short business
explanation so that I can understand the findings and inspect the supporting work.

**Build:** sales overview, repeat/cohort view and customer-segment view; use shared
metric definitions and clear period labels. Prepare Tableau-ready aggregate data,
the report specification, actual chart images and a findings narrative. Validate
native Tableau filters and refresh separately before calling that workbook accepted.

**Deliverables:** visual report, Tableau inputs/specification, concise project
README, findings and dated acceptance evidence.

**Acceptance:** A6 plus the recorded outcomes of A1–A5. Depends on RA-02 and RA-03.

## Acceptance cases

| ID | Check | Expected result |
|---|---|---|
| A1 | Reconcile source, staging and published aggregates | Source-row counts reconcile to the documented retained/excluded groups. Eligible monthly amounts sum to the unfiltered headline amount within the documented currency precision. Repeating the same run produces the same aggregates. |
| A2 | Exercise cancellations and partial months | Cancellation records appear in their own counts and amounts and never increase purchase order frequency. Without a validated link they are not attributed to an original order. December 2011 is excluded from full-month comparisons. |
| A3 | Exercise a valid purchase with no customer ID | It remains in eligible sales totals and in the customer-ID coverage measure, but not in customer counts, repeat-buyer denominators or segments. No placeholder ID combines unknown shoppers. |
| A4 | Exercise cohort maturity and repeated invoice lines | Multiple lines in one invoice count as one purchase order. Future cohort cells are blank/unavailable, not zero. Fixed-window repeat rates include only customers observed for the full window; a customer with two orders qualifies only under the documented interval rule. |
| A5 | Exercise segment boundaries | Every eligible identified customer belongs to exactly one segment. Counts sum to the customer population at the fixed analysis date. Boundary examples match the published recency/frequency rules. |
| A6 | Compare visuals with the SQL output | Headline values and representative chart points match the aggregate files; axes show units, period and population. Published screenshots are legible. Any Tableau filter/refresh checks state their actual tested scope; unavailable data is not shown as a valid zero. |

Technical assessment, 24 October 2026: A1–A5 passed through 10 synthetic regressions
and 11 real-data reconciliations. A6's portable charts and browser navigation were
inspected; native Tableau rendering/interaction and owner business review remain
pending. See [verification](../../projects/retail-customer-analytics/dashboard/README.md).
Passing calculations does not establish a campaign benefit.
