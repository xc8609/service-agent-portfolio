# Retail customer and sales analytics delivery plan

Direction confirmed 24 October 2026: pause investment Agent development and build
a data-analysis case aligned with customer management, commerce and payments.
The bank case remains available. This is an independent analytical project under
`projects/retail-customer-analytics/`, with no dependency on either Agent runtime.

[Business case](../../projects/retail-customer-analytics/docs/business-case.md) ·
[Metric definitions](../../projects/retail-customer-analytics/docs/metrics.md) ·
[Data model](../../projects/retail-customer-analytics/docs/model.md) ·
[Dashboard design](../../projects/retail-customer-analytics/docs/client-development-design.md)

**Current increment — 24 October 2026:** deepen the real-data case with a compact
fact/dimension model, a customer order-change bridge, product analysis and three
interactive Tableau pages. Preserve the established sales and customer definitions.
Luxury client-development practice informs the business questions and visual
style; the source remains the UCI gift-retail dataset.

## Delivery sequence

Estimates are focused person-days for an analyst/developer with BA and reviewer
input, not calendar promises or the owner's weekly capacity. Each increment
ends with a reviewable result. The work can be shared by a small team without
creating additional services.

| Increment | Stories | Effort estimate | Reviewable result | Current status |
|---|---|---:|---|---|
| 1. Trusted data and sales | RA-01, RA-02 | 2–3 person-days | Source manifest, metric definitions, reproducible SQL, reconciled monthly sales and cancellation analysis | Implemented; technical checks passed |
| 2. Customer decisions and presentation | RA-03, RA-04 | 3–4 person-days | Customer and cohort analysis, three visual views, findings, recommendation and acceptance record | Analysis and portable report implemented; native Tableau and owner review pending |
| 3. Model and interactive diagnosis | RA-05, RA-06 | 3–4 person-days | Fact/dimensions, reconciled customer/product explanations, interactive workbook and updated report | In development; technical and native acceptance recorded separately |

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

## RA-05 — Preserve meaning across analytical grains

**Story:** As an analyst, I want reusable transaction, product, customer and date
structures so that filtering or joining data does not inflate sales or order counts.

**Build:** one invoice-line fact with source-row lineage; date, product, customer
and country dimensions; an invoice summary with one customer per invoice. Retain
original product descriptions, select one deterministic display label per code,
and expose description variants. Separate delivery/service codes for merchandise
analysis while preserving the existing recorded-sales total. Resolve a sole
known customer on an invoice with partially missing IDs; fail on conflicting IDs.

**Deliverables:** SQL model, grain/key diagram, product-quality profile, local
Tableau extracts and focused synthetic/reconciliation tests.

**Acceptance:** A7–A9. Depends on RA-01. Estimated effort: 1–2 person-days.

## RA-06 — Investigate customers and products interactively

**Story:** As a trading and client-development manager, I want to connect sales
changes to customer purchasing and products so that I can choose a specific next
investigation instead of reacting only to headline sales.

**Build:** a comparable January–November order-change bridge for customers present
in both periods, only the current period, only the prior period, and unidentified
orders; product value changes and order penetration; three Tableau pages for
trading performance, client development and product preferences. Make filter scope,
comparison period, currency and customer snapshot visible. Keep merchandise and
recorded-sales totals distinct and support clearing selections.

**Deliverables:** diagnostic SQL and aggregate results, interactive Tableau
workbook, professional visual report, updated findings and dated verification.

**Acceptance:** A10–A13 plus A6. Depends on RA-05. Estimated effort: 2 person-days.

## Acceptance cases

| ID | Check | Expected result |
|---|---|---|
| A1 | Reconcile source, staging and published aggregates | Source-row counts reconcile to the documented retained/excluded groups. Eligible monthly amounts sum to the unfiltered headline amount within the documented currency precision. Repeating the same run produces the same aggregates. |
| A2 | Exercise cancellations and partial months | Cancellation records appear in their own counts and amounts and never increase purchase order frequency. Without a validated link they are not attributed to an original order. December 2011 is excluded from full-month comparisons. |
| A3 | Exercise a valid purchase with no customer ID | It remains in eligible sales totals and in the customer-ID coverage measure, but not in customer counts, repeat-buyer denominators or segments. No placeholder ID combines unknown shoppers. |
| A4 | Exercise cohort maturity and repeated invoice lines | Multiple lines in one invoice count as one purchase order. Future cohort cells are blank/unavailable, not zero. Fixed-window repeat rates include only customers observed for the full window; a customer with two orders qualifies only under the documented interval rule. |
| A5 | Exercise segment boundaries | Every eligible identified customer belongs to exactly one segment. Counts sum to the customer population at the fixed analysis date. Boundary examples match the published recency/frequency rules. |
| A6 | Compare visuals with the SQL output | Headline values and representative chart points match the aggregate files; axes show units, period and population. Published screenshots are legible. Any Tableau filter/refresh checks state their actual tested scope; unavailable data is not shown as a valid zero. |
| A7 | Join each dimension to invoice-line facts | Dimension keys are unique. Fact row count and amount are unchanged after joins; retained repeat rows remain distinct through source lineage. |
| A8 | Resolve an invoice with one known and one missing customer ID, then one with conflicting known IDs, dates or countries | The first invoice has one resolved customer and is counted once. Conflicting attributes fail validation rather than being assigned arbitrarily. An entirely unidentified invoice stays outside identified-customer measures. |
| A9 | Exercise changed product descriptions and service lines | The chosen display description is deterministic, original labels remain traceable, and variant counts are available. Merchandise plus retained service value equals recorded sales; service quantities do not enter merchandise measures. |
| A10 | Reconcile customer order-change components | Both-period change + current-only orders − prior-only orders + unidentified-order change equals the overall comparable-period order change. Same-invoice lines do not increase frequency. |
| A11 | Reconcile product changes and penetration | Product value changes sum to the merchandise value change. Selecting a product does not shrink the penetration denominator to that product's invoices. Product invoice counts are never summed to claim total invoices. |
| A12 | Open and interact with the native Tableau workbook | Open against regenerated local extracts, inspect all three pages, exercise the actual filters/actions and reset, and compare representative filtered values to SQL. Trading selections do not silently recalculate the fixed customer snapshot. Record actual scope and any remaining native limitation. |
| A13 | Complete three business review tasks | Explain the sales/order divergence, inspect the lapsed-repeat group, and identify products contributing to value changes. The reviewer can see the population and evidence behind each finding and propose a next investigation. Record delegated technical review separately from owner business acceptance. |

First-increment technical assessment, 24 October 2026: A1–A5 passed through 10 synthetic regressions
and 11 real-data reconciliations. A6's portable charts and browser navigation were
inspected; native Tableau rendering/interaction and owner business review remain
pending. See [verification](../../projects/retail-customer-analytics/dashboard/README.md).
Passing calculations does not establish a campaign benefit.

RA-05/06 technical increment, 24 October 2026: 28 retail tests and 29 real-data
reconciliations passed. A7–A11 have model/BI regression evidence. All three native
pages and representative persisted filter states were inspected against SQL.
A12 retest passed the three pages' bar selection/clear, date recomputation,
cross-page scope isolation and scrolling market layout. In a follow-up on
24 October 2026, the owner confirmed that Trading's Recorded country dropdown
opens and France can be selected. The Product customer-group dropdown remains
unverified. A13's three evidence-backed findings are documented; owner
business acceptance remains open. See the same
[verification record](../../projects/retail-customer-analytics/dashboard/README.md).
