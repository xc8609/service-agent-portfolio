# Retail visual analysis

Three pages connect a business question to evidence and a follow-up decision.

| Page | Question | Native Tableau interaction |
|---|---|---|
| Trading performance | Is growth coming from more orders or larger invoices? | Country and date filters; select a market to focus the measures and monthly trend. |
| Client development | Which customer groups deserve further investigation? | Select a customer group to update the customer measures and cohort matrix. |
| Product preferences | Which products contribute to performance? | Country, date and customer-group filters; select a product to inspect value, invoices, penetration and trend. |

The warm ivory, charcoal and teal design emphasizes labels, comparisons and
selective colour. It applies a client-development perspective to the UCI retailer;
the source is a UK gift retailer, not a luxury-store dataset.

## Open the Tableau workbook

Run the [project reproduction commands](../README.md#structure-and-reproduction),
then open [retail_customers.twb](retail_customers.twb) in a compatible Tableau
edition. Preserve the project folder structure. If Tableau asks to locate a CSV,
select the file with the same name in the directories below.

| Source | Grain | Location |
|---|---|---|
| Trading / Products (separate filter scopes) | Eligible purchase invoice line | `../data/processed/tableau_sales.csv` |
| Customers | One identified customer at the 1 December 2011 snapshot | `../data/processed/tableau_customers.csv` |
| Cohorts | First-observed month × elapsed month × snapshot group | `../results/cohorts_by_segment.csv` |
| Comparable product changes | One product, January–November 2010 versus 2011 | `../results/product_changes.csv` |

There are five datasource definitions because Trading and Products intentionally
use separate scopes. The customer and transaction exports are generated locally
and excluded from Git. The additional **Comparable product changes** worksheet
has a fixed, all-market comparison; it does not inherit product-page selections.

Trading and Products default to **1 January–30 November 2011**. Client development
uses a fixed **1 December 2011** snapshot. Select a bar again to clear a selection;
restore country/group to `(All)` and the default dates to reset controls.

Key metric rules:

- Count distinct invoices after filtering; do not sum product-level order counts.
- Calculate average invoice value from total value / distinct invoices.
- Product measures exclude delivery and other non-merchandise entries. The
  headline recorded-sales measure retains them, so the two totals differ by design.
- Product selection changes the numerator of order penetration, while its
  denominator remains all merchandise invoices in the date/country/group scope.
- Calculate cohort rates from summed numerators and denominators. Future months
  remain blank. Snapshot groups describe customers at the end of the window.
- The leading-product chart shows 15 products; KPI totals cover the full scope.

[Metric definitions](../docs/metrics.md) · [Fact/dimension model](../docs/model.md).

## Portable GitHub preview

[index.html](index.html) provides three generated chart previews with mouse and
keyboard tab navigation. These are portable analytical SVGs; data filtering and
linked selections are in the native Tableau workbook. The previews include the
comparable-period order bridge and product-change analysis.

```bash
python3 -m http.server 8020 --bind 127.0.0.1 --directory projects/retail-customer-analytics
```

Open `http://127.0.0.1:8020/dashboard/`.

## Verification — 24 October 2026

- **29 reconciliation checks:** 11 existing source/metric checks and 18 new
  model/diagnostic checks. See [checks.json](../results/checks.json) and
  [model_checks.json](../results/model_checks.json).
- **28 retail tests:** cleaning and observation boundaries, invoice attribution,
  dimension integrity, merchandise classification, diagnostic totals and Tableau
  filter/aggregation contracts. Repository offline suite: **185 passed** on Python 3.12.
- The original seven result files remained byte-identical. The expanded result
  exports also reproduced byte-for-byte on a second run.
- The three portable previews were visually inspected; mouse navigation and
  Right-arrow/Home keyboard tab navigation were exercised in the browser.
- Native Tableau 2026.2 opened all three pages. Default KPIs reconciled to SQL;
  unavailable cohort months rendered blank. Independently generated filter-state
  workbooks verified the following displayed values:

| Native state | Measures observed (rounded display) |
|---|---|
| Trading, all countries, January–November 2011 | £9,117,534; 17,483 invoices; £521.5 average |
| Trading, France, same period | £183,330; 349 invoices; £525.3 average |
| Products, all merchandise, same period | £8,878,008; 17,407 invoices |
| Product 22423, same period | £140,608; 1,757 invoices; 10.1% penetration |
| Clients, all identified customers | 5,826; £8,339,723 in the last 12 months; 46.9% eligible 90-day repeat |
| Clients, Lapsed repeat | 591; £650,317 in the last 12 months; 64.3% eligible 90-day repeat |

These are native render and persisted-filter checks, not a completed mouse-action
UAT. The final market-chart layout and the select/clear interaction sequence still
need a manual check; native UI control became unavailable during verification.
Business owner acceptance is not implied.

### Short remaining interaction check

1. In Trading, select France, verify the values above, then clear the selection.
   Change the date range and confirm that the KPIs and both charts agree.
2. In Products, select product **22423**, verify **10.1%** rather than 100%, then
   clear it. Change country/group and confirm the new scope before selecting again.
3. In Clients, select **Lapsed repeat**; verify **591 / £650,317 / 64.3%** and a
   changed cohort matrix. Clear it and return to **5,826 / £8,339,723 / 46.9%**.
4. Confirm that changing Trading's filters does not silently change Products or
   the fixed Client snapshot. Check readable labels at the working window size.

The ignored verification copies can be regenerated with
`python projects/retail-customer-analytics/scripts/build_tableau.py --smoke-variants`.
