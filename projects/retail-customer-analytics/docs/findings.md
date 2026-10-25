# Findings and proposed business actions

Analysis: 24 October 2026. Historical window: 1 December 2009–30 November 2011.
The business review is simulated; figures below are calculated from the real source.
[Definitions](metrics.md) · [Headline results](../results/summary.json) ·
[Customer/product diagnostics](../results/diagnostic_summary.json).

| Finding | Evidence | Proposed next step |
|---|---|---|
| A modest sales increase masks fewer orders | Jan–Nov sales: £8,765,001 in 2010, £9,117,534 in 2011 (+4.0%). Invoices: 18,159 → 17,483 (−3.7%). Average invoice: £482.68 → £521.51 (+8.0%). | Investigate product mix, purchase frequency and wholesale buying patterns before treating higher sales as broader customer growth. |
| Repeat purchasing depends on the observation window | 4,186 / 5,826 customers purchased on multiple invoices in the two-year window (71.9%). Within an equally observable 90-day window, 2,454 / 5,229 repeated (46.9%). | Use a fixed window when comparing customer cohorts. Do not compare a recent customer with someone observed for two years. |
| Repeat buyers with a longer purchase gap deserve review | At 1 December 2011, 591 customers had at least two orders in the previous 12 months but none in the last 90 days. Their recorded 12-month sales: £650,317. | Review a business-approved sample to distinguish seasonal or wholesale cadence from service problems before designing a re-engagement experiment. |
| Identified-customer results do not cover all sales | Identified customer IDs cover 85.9% of sales value and 92.5% of purchase invoices. | Track identification coverage alongside customer measures; investigate why IDs are absent before generalizing. |

## Where the 676 fewer orders came from

The comparable January–November periods contain 18,159 invoices in 2010 and
17,483 in 2011. The [customer bridge](../results/order_bridge.csv) reconciles the
change exactly:

| Observed customer component | Prior invoices | Current invoices | Change |
|---|---:|---:|---:|
| 2,596 customers purchasing in both periods | 13,498 | 12,451 | −1,047 |
| 1,572 customers purchasing only in the current period | 0 | 3,832 | +3,832 |
| 1,532 customers purchasing only in the prior period | 3,261 | 0 | −3,261 |
| Unidentified orders | 1,400 | 1,200 | −200 |
| **All orders** | **18,159** | **17,483** | **−676** |

The current-only group contributes more invoices than the prior-only group did,
but lower frequency among customers present in both periods more than offsets
that difference. Start the next business review with those continuing customers:
compare purchasing cadence, order size and products. Period membership describes
what was observed; it does not establish a customer's acquisition or departure.

## Product changes make the review more specific

Merchandise sales increased from **£8,628,418 to £8,878,008 (+2.9%)** in the same
January–November comparison. The ten highest-value products contribute **8.49%**
of current merchandise value, so the analysis should also retain the wider
assortment. [Product comparisons](../results/product_changes.csv).

| Example | Comparable-period evidence | Review question |
|---|---|---|
| PARTY BUNTING · 47566 | Value £48,299 → £97,378; invoices containing it 960 → 1,609 | Which customer groups and purchasing patterns accompany its broader order presence? |
| WHITE HANGING HEART T-LIGHT HOLDER · 85123A | Value £137,681 → £92,852; invoices containing it 2,895 → 1,967 | Is its lower order presence concentrated in particular customer groups or markets? |
| PICNIC BASKET WICKER SMALL · 22502, within lapsed repeat buyers | Last-12-month value £41,276 from 35 customers and 45 invoices; 6.41% of that group's merchandise value | Is this buying pattern linked to a seasonal or wholesale occasion? |

The first two rows use January–November comparisons. The third uses the customer
snapshot's **December 2010–November 2011** window. Its group-level product evidence
is in [product preferences](../results/product_preferences.csv). Product invoice
counts overlap when an order contains several products; do not add these rows to
explain total order loss.

Recorded sales retains eligible non-merchandise entries. Across the full 24-month
window, **£19,085,461.19 merchandise + £428,217.24 non-merchandise =
£19,513,678.43 recorded sales** (rounded to the penny). Keeping both definitions visible makes a product
analysis reconcile with the trading overview.

## A data-quality decision that changes the report

The source contains two overlapping annual sheets. Every one of the 22,523
first-sheet rows dated 1–9 December 2010 also occurs in the second sheet, including
its multiplicity. Excluding these proven copies removes £438,852.65 of positive
invoice value from a naive concatenation before the accounting exclusions. It also prevents duplicated cancellation
amounts. Raw records are retained in staging, with explicit selection flags.

After that correction, 11,812 exact repeated rows remain across source history.
They cannot be reliably classified as errors without a line ID, so the main report
retains them. In the selected window, potential repeated positive value is
£56,090.47 (about 0.29%). A sensitivity calculation that removes exact repeats
changes Jan–Nov growth from **4.02% to 4.14%**; the direction and fewer-orders finding
remain unchanged. [Quality evidence](../results/quality.json).

## Proposed experiment, after business review

First investigate the order-frequency decline among customers buying in both
comparable periods. For customer-development planning, review the 591-customer
lapsed-repeat group as a separate, actionable investigation population; it is not
assumed to explain the full order decline. A retail team
would confirm account type, expected ordering cadence, recent service issues and
permitted contact channels. If an outreach experiment is then appropriate, define
eligible customers, a comparison group, contact costs, a fixed follow-up window and
repeat-order measures before starting. This dataset contains neither that outreach
nor its outcomes, so the portfolio makes no claim of improved sales or recovered value.

The practical BA contribution is to turn an ambiguous request to “improve customer
retention” into agreed measures, a reviewable group definition and a testable next
step. The engineering evidence makes that recommendation repeatable: source
lineage, explicit analytical grains, reconciled customer/product contributions and
the same definitions in SQL and the workbook.
