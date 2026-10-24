# Metrics and source decisions

The unit of observation is an **invoice line**, not an order or a customer.
SQL owns the calculations: [staging](../sql/01_staging.sql) and
[marts](../sql/02_marts.sql). All amounts remain GBP.

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
count once. A cohort is a **first observed purchase** cohort, not verified acquisition.
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

## Tableau data model

Four independent aggregates avoid joining facts with incompatible grains:

| File | One row per | Use |
|---|---|---|
| `monthly.csv` | Complete month | Sales, purchase invoices and cancellation totals |
| `countries.csv` | Country over the main window | Recorded sales contribution |
| `cohorts.csv` | First-observed month × month index | Purchasing heatmap; includes explicit future blanks |
| `segments.csv` | Customer group at the snapshot | Customer counts and last-12-month recorded sales |

These files are not joined in the workbook. The first release has three navigation
pages; it does not promise a global country/date filter that recalculates cohorts
or recency. Such interactive cohort analysis would need a customer/order-level
semantic model and another acceptance pass.
