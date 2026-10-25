# Retail Customer & Sales Analysis

**What is driving sales changes, and which customer groups deserve a closer look?**

This case connects customer-development decisions with real retail transactions,
SQL and visual analysis. It builds on customer-management, commerce and payment
workflows: define the business question → reconcile data → explain the result →
propose a focused follow-up.

The source is UCI Online Retail II, a UK online gift retailer's invoice lines.
The case uses **24 complete months, 38,870 purchase invoices and 5,826 identified
customers** after reconciling overlapping source sheets.

**Stack:** Python · DuckDB SQL · Tableau · pytest · GitHub Actions.

## What the analysis shows

- **Sales +4.0%, invoices −3.7%, average invoice value +8.0%:** January–November
  2011 versus the same months of 2010. The headline increase hides a lower order count.
- **46.9% purchased again within 90 days:** 2,454 of 5,229 customers with a complete
  observation window. The broader two-year repeat-buyer share is 71.9%.
- **591 previously repeat buyers had not purchased for over 90 days:** their
  previous-12-month recorded sales total £650,317. This is a group to investigate,
  not proven lost revenue or a measured win-back opportunity.

[Five-minute business case and review](docs/business-case.md) · [Detailed findings](docs/findings.md) ·
[Metric definitions](docs/metrics.md) · [Stories and acceptance](../../docs/backlog/retail-analytics.md)

**Recommended business sequence:** investigate the continuing-customer order
decline, review lapsed-repeat customers' purchasing cadence, then use product and
market evidence to define the next action. The case study walks through all three
views and connects the findings to proposed business owners and follow-up evidence.

**Business review accepted — 24 October 2026:** the portfolio owner confirmed the
three-page findings and recommendation priorities. [Acceptance record](docs/business-case.md#business-acceptance-record).

## Skills demonstrated, with evidence

| Capability | Implemented work | Inspect the evidence |
|---|---|---|
| Data cleaning | Reconciled 22,523 overlapping rows with `EXCEPT ALL`, preserved source lineage, separated cancellations and reported missing-customer coverage | [Staging SQL](sql/01_staging.sql) · [Overlap check](scripts/build_analysis.py) · [Quality results](results/quality.json) |
| Data modelling | Built invoice-line and invoice facts plus date, product, customer and country dimensions; validated keys and joins without multiplying amounts | [Model and grains](docs/model.md) · [Model SQL](sql/03_model.sql) |
| Analytical SQL | Used fixed observation windows for repeat purchase, a reconciled customer order-change bridge and product contribution/ranking analysis | [Customer marts](sql/02_marts.sql) · [Diagnostics](sql/04_diagnostics.sql) |
| Tableau analysis | Implemented `COUNTD`, `FIXED` LOD/context filters, linked selections, reset and separate page scopes | [Calculation example](docs/metrics.md#tableau-calculation-example) · [Native interaction results](dashboard/README.md#native-interaction-retest--24-october-2026) |

**Verification:** [28 retail tests](tests/), [11 source/metric reconciliations](results/checks.json)
and [18 model/diagnostic reconciliations](results/model_checks.json). Tableau
interaction checks and the owner business review are complete for the recorded scope.

DuckDB owns the dimensional model. Tableau consumes sales-line, customer-snapshot
and cohort exports at their respective grains and recalculates selected-scope
measures using the same definitions. [Client-development design](docs/client-development-design.md).

The diagnostic increment explains the **676-invoice decline** through four
customer groups. Merchandise value grew from **£8.63m to £8.88m** in comparable
January–November periods; the top ten products contribute **8.49%** of current
merchandise value. [Diagnostic results](results/diagnostic_summary.json).

## Three decision views

**Native Tableau workbook — actual Desktop capture, 24 October 2026.**
Trading is shown at its default January–November 2011 scope; the three page tabs
are visible along the bottom.

![Native Tableau Trading page with country/date filters, KPIs, trend and market chart](dashboard/images/tableau-trading-native.png)

| Page | Business question | Interactive analysis |
|---|---|---|
| Trading performance | Why do sales and order volume move differently? | Filter country/date; select a market to focus KPIs and the monthly trend |
| Client development | Which customer groups need review? | Select a group to update customer measures and the cohort heatmap |
| Product preferences | Which products accompany the purchasing pattern? | Filter date/country/group, then select a product; the penetration denominator retains the full filter scope |

For these interactions, follow the [workbook setup](dashboard/README.md) and open
[retail_customers.twb](dashboard/retail_customers.twb). The verified product example
shows **1,757 / 17,407 invoices = 10.1% penetration**, rather than becoming 100%
when one product is selected.

<details>
<summary>Three comparative chart previews — view directly on GitHub</summary>

These Python-generated analytical charts include the fixed comparable-period
order bridge and product changes. The local [HTML preview source](dashboard/index.html)
adds tab navigation; the native Tableau workbook provides data filtering and
linked selections. [Run the local preview](dashboard/README.md#portable-github-preview).

![Sales, order volume and invoice value](dashboard/sales-overview.svg)

| Client development | Product preferences |
|---|---|
| ![Customer groups and cohort purchasing](dashboard/client-development.svg) | ![Product contribution to sales change](dashboard/product-preferences.svg) |

</details>

## Structure and reproduction

```text
docs/             Business case, metric definitions, findings
data/             Source attribution and checksum manifest
sql/              Staging, fact/dimension model and analytical marts
scripts/          Download/extract, analyze, render and build Tableau workbook
results/          Aggregate CSVs, findings inputs and reconciliation checks
dashboard/        Interactive Tableau workbook and portable review previews
tests/            Business-boundary, model and BI contract regressions
```

Python 3.12, from the repository root:

```bash
python3.12 -m venv .venv-retail
.venv-retail/bin/python -m pip install -r projects/retail-customer-analytics/requirements.txt
.venv-retail/bin/python projects/retail-customer-analytics/scripts/prepare_data.py
.venv-retail/bin/python projects/retail-customer-analytics/scripts/build_analysis.py
.venv-retail/bin/python projects/retail-customer-analytics/scripts/render_report.py
.venv-retail/bin/python projects/retail-customer-analytics/scripts/build_tableau.py
.venv-retail/bin/python -m pytest projects/retail-customer-analytics/tests -q
```

The 43.5 MB source download stays local. The pipeline verifies the pinned archive,
checks sheet overlap and reconciles detail to published aggregates. Customer
analysis covers the identified subset, representing 85.9% of recorded sales value.
Amounts are GBP; cancellation entries are shown separately. [Source and terms](data/README.md).
