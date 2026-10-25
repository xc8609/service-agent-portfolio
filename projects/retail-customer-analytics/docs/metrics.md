# Metrics and source decisions

The unit of observation is an **invoice line**, not an order or a customer.
SQL prepares and reconciles the measures in [staging](../sql/01_staging.sql),
[marts](../sql/02_marts.sql) and customer/product diagnostics. Tableau recalculates
filtered measures using these same definitions. The [model contract](model.md)
owns analytical grains and joins. All amounts remain GBP.

## Source preparation

- Import both source sheets unchanged, preserving sheet name and original row number.
- The first sheet ends on 9 December 2010; the second starts on 1 December 2010.
  An `EXCEPT ALL` comparison confirms all **22,523 overlapping first-sheet rows**
  exist, with matching multiplicities, in the second sheet. Use the first sheet
  before 1 December 2010 and the second from that date. Retain excluded copies in
  staging for reconciliation. Fail the build if this overlap check stops matching.
- Keep the remaining **11,812 exact repeated rows** across the selected source
  history. There is no unique line ID that establishes these are errors. Record
  their monetary sensitivity separately; distinct-invoice frequency does not
  increase because a line repeats.
- Main window: **1 December 2009 through 30 November 2011**. The final 25,526
  December 2011 rows belong to an incomplete month and are outside this window.
  Customer segments use the fixed snapshot **1 December 2011**.
- Classify every raw row once: positive sale, cancellation, invalid required field,
  manual/accounting entry, zero/non-positive price or zero quantity, or sign/cancellation conflict.
  Missing customer IDs do not invalidate a sales record.
- Exclude A-prefix accounting invoices and explicit adjustment/fee codes B, ADJUST,
  ADJUST2, BANK CHARGES, AMAZONFEE, D and CRUK from purchases and cancellations.
  Exclude ambiguous M (Manual) entries too, until their commercial meaning can be
  established. These 1,840 raw rows remain in the quality summary. For example,
  a positive £11,062.06 bad-debt adjustment must not become a customer order.

## Measures

| Measure | Definition |
|---|---|
| Recorded sales | Sum of Quantity × Price for positive-quantity, positive-price non-C records after the manual/accounting exclusions above |
| Purchase invoices | Distinct invoice IDs in those sales records |
| Average invoice value | Recorded sales / purchase invoices |
| Cancellation value | Absolute value of negative-quantity, positive-price C-prefix records after manual/accounting exclusions, separately aggregated by their recorded date |
| Identified customers | Distinct valid numeric customer IDs in sales |
| Customer value coverage | Sales value with a valid customer ID / all recorded sales |
| Customer order coverage | Purchase invoices with a valid customer ID / all purchase invoices |
| Two or more orders in 24 months | Identified customers with at least two distinct purchase invoices / all identified purchasing customers in the main window |
| Repeat within 90 days | Eligible customers whose second distinct invoice occurs within 90 calendar days of their first observed invoice / eligible customers |
| Eligibility for 90-day measure | First observed order date + 90 days is before 1 December 2011; observations include the entire 90th day |
| Monthly cohort purchasing | Customers purchasing in month N / customers whose first observed purchase is in that cohort month |

Two invoices on the same day count as two orders; multiple lines on one invoice
count once. The invoice-level model resolves one known customer across partially
missing source lines before computing customer orders. Conflicting known IDs,
dates or countries on a sales invoice fail validation. Source-ID coverage still
uses the original source fields rather than silently treating inferred IDs as
collected data. A cohort is a **first observed purchase** cohort, not verified acquisition.
Month 0 is 100% by construction. Later cells describe purchasing in that month,
not continuous retention. Unobserved future months are blank; observed months
without repeat buyers are zero. Customer IDs are never replaced with a shared
“unknown customer”.

Recorded sales includes delivery charges such as postage and keeps
source precision (some prices have three decimals). It is not audited revenue,
profit or merchandise-only revenue. Cancellation records have no reliable original
invoice link here, so they are not subtracted to claim completed refunds or an
order return rate. Ratios use summed numerators and denominators.

## Explainable customer groups

Recency is days from the last observed purchase to 1 December 2011. Frequency and
monetary value use the last 12 complete months, 1 December 2010–30 November 2011.
The five rules below partition all identified customers in the 24-month window.
The 90-day cutoff is a transparent case assumption, not an industry standard or
a measured churn boundary.

| Group | Rule | Review question |
|---|---|---|
| Active repeat | Recency ≤ 90 days and frequency ≥ 2 | Which products and service needs support this group's repeat purchasing? |
| Recent single-order | Recency ≤ 90 days and frequency = 1 | Is a second purchase expected for this type of customer? |
| Lapsed repeat | Recency > 90 days and frequency ≥ 2 | Is the gap seasonal, wholesale buying cadence, or a service issue? |
| Lapsed single-order | Recency > 90 days and frequency = 1 | Was the purchase a one-off occasion? |
| No orders in last 12 months | Frequency = 0 | Is the historical customer record still relevant? |

Group totals are published; customer-level records stay local. Monetary value
helps compare groups, but is not a customer lifetime-value prediction. Proposed
follow-up is an investigation plan, not an instruction to contact real customers.

## Customer and product diagnostics

Comparisons use **January–November 2011 against January–November 2010**. These are
matched complete months. The four order-bridge components are mutually exclusive:

| Component | Contribution to current minus prior invoices |
|---|---|
| Customers purchasing in both periods | Their current invoices minus their prior invoices |
| Customers purchasing only in the current period | Their current invoices |
| Customers purchasing only in the prior period | Minus their prior invoices |
| Unidentified orders | Current unidentified invoices minus prior unidentified invoices |

Sum all four to the total invoice change. Period membership is observed behaviour,
not an acquisition or churn label. The bridge is an arithmetic explanation; it
does not establish why a customer purchased differently.

| Product measure | Definition |
|---|---|
| Merchandise sales | Eligible recorded sales after separating POST/DOT/C2 delivery, GIFT_0001_* vouchers, S samples and TEST001/TEST002 test items |
| Product value change | Current-period merchandise value minus prior-period merchandise value, per stock code |
| Product purchase invoices | Distinct merchandise invoices containing the product; counts across products are not additive |
| Product order penetration | Product purchase invoices / all merchandise invoices in the same period, market and customer-group scope, before product selection |
| Top 10 product share | Merchandise value of the ten highest-value stock codes / all merchandise value in that scope |
| Group product preferences | Merchandise value and distinct buying invoices by product within a fixed customer group; ranked top 20 per group |

`Service` is the short export label for all retained non-merchandise records in the
mapping above. PADS remains merchandise. The mapping is a documented case decision;
it does not change recorded-sales or cancellation definitions. Merchandise plus
retained non-merchandise value reconciles to recorded sales. Product descriptions
use the deterministic label in the product dimension; amounts remain grouped by
stock code, so a description change does not create another product.

## Visualization scope

| Page | Population and controls | Calculation rule |
|---|---|---|
| Trading performance | Eligible sales lines; default January–November 2011; date and country scope | `SUM(recorded_value)`, distinct invoice count, and their ratio for average invoice value. Country selection applies to that page's linked views |
| Client development | Identified customers at 1 December 2011; customer-group selection | Count one customer per snapshot row. Sum cohort numerators and denominators within a cohort/index; never average group rates. Trading filters do not redefine recency or membership |
| Product preferences | Merchandise lines; visible date/country/customer-group scope and product selection | Date/country/customer-group context defines the full invoice population. Product selection changes the product numerator/detail, while the penetration denominator retains that full population |

## Tableau calculation example

The workbook implements these calculated fields:

```text
scope_invoices = { FIXED : COUNTD([invoice_key]) }
penetration = COUNTD([invoice_key]) / MIN([scope_invoices])
```

Date, country, customer group and merchandise scope are context filters. Product
selection is an ordinary filter, so it changes the numerator without shrinking
the full-scope denominator. At the all-country/all-group January–November 2011
scope, selecting product 22423 displays **1,757 / 17,407 = 10.1%**; clearing the
selection restores the full scope. This was exercised in native Tableau.

The customer page combines customer-snapshot and cohort sources through linked
filter actions. Cohort percentages use summed numerators and denominators, not
an average of group percentages. Separate Trading and Product source definitions
keep their controls from leaking across pages.

[Workbook calculations and actions](../scripts/build_tableau.py) ·
[Filter/denominator regression tests](../tests/test_tableau.py) ·
[Observed native results](../dashboard/README.md#native-interaction-retest--24-october-2026)

The legacy `monthly.csv`, `countries.csv`, `cohorts.csv` and `segments.csv` remain
reconciliation outputs. Local line/customer exports support interactive Tableau
without joining customer snapshots onto sales as additive measures. The
[data model](model.md) describes their grains. The
[verification record](../dashboard/README.md) states which native filter actions
and refresh checks were actually exercised.
