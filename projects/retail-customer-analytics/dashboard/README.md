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

The table above originally recorded native render and persisted-filter checks.
The following retest adds actual pointer and keyboard interaction evidence.

### Native interaction retest — 24 October 2026

Evaluator: Codex, delegated technical review, using Tableau 2026.2 and the local
regenerated inputs. No calculation or chart-layout defect was found in the tested
sequence. Owner business acceptance is a separate decision.

| Check | Observed result | Outcome |
|---|---|---|
| Select France in the Markets bar chart | KPIs become £183,330 / 349 / £525.3; the monthly line follows France | Pass |
| Clear the selected market | Original all-country KPIs return | Pass |
| Change Trading end date to 30 June 2011 | £3,972,627 / 8,059 / £492.9; line ends in June and France's market value becomes £79,172 | Pass |
| Select product 22423, then clear | £140,608 / 1,757 / 10.1% and product trend; clear restores £8,878,008 / 17,407 / 100.0% | Pass |
| Select Lapsed repeat, then clear | 591 / £650,317 / 64.3% and filtered cohort matrix; clear restores 5,826 / £8,339,723 / 46.9% and full matrix | Pass |
| Keep France selected in Trading and open other pages | Product scope remains all countries; Client snapshot remains 5,826 customers | Pass |
| Scroll the Markets chart | Countries remain readable; scrolling reaches United Kingdom (£7,640,540), USA and the other lower rows without overlap | Pass |
| Open Trading's Recorded country dropdown and select France | After the automated retest, the owner confirmed that the dropdown opens and France can be selected | Pass — owner confirmation |
| Select Lapsed repeat in Product's customer-group dropdown, then reset to (All) | Owner confirmed £559,280 / 1,521 invoices after selection and £8,878,008 / 17,407 after reset, matching SQL | Pass — owner confirmation |

Owner follow-up, 24 October 2026: the Trading country-control check above is based
on the owner's direct confirmation, not an automated pass. It confirms opening
the dropdown and selecting France; the KPI values above come from the separate
bar-action checks. The customer-group confirmation is recorded below.
Independent code review and 28 retail tests found no model, aggregation or filter-
scope blocker. The workbook was not saved with temporary review selections.

Customer-group follow-up, 24 October 2026: after #39 merged, the Product page
was reopened. Its default KPIs showed £8,878,008 / 17,407 / 100.0%. The control
received focus, but neither pointer nor keyboard interaction exposed its options
through the automation. The owner then performed the selection and reset directly
and confirmed that both sales and invoice counts matched the SQL targets below.

Independent SQL provides these comparison targets for all countries,
1 January–30 November 2011, merchandise only, with no product selected:

| Customer-group selection | Sales (rounded display) | Distinct invoices |
|---|---:|---:|
| Lapsed repeat | £559,280 | 1,521 |
| Reset to (All) | £8,878,008 | 17,407 |

This closes the remaining direct-control check for the recorded A12 scope.
The dropdown evidence is owner-confirmed; the automated popup limitation remains
part of the test history. No workbook or calculation change was needed.

The ignored verification copies can be regenerated with
`python projects/retail-customer-analytics/scripts/build_tableau.py --smoke-variants`.
