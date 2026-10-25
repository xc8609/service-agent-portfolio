# Source and provenance

**Chen, D. (2012). Online Retail II. UCI Machine Learning Repository.**
[Dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) ·
[DOI](https://doi.org/10.24432/C5CG6D) ·
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Downloaded **24 October 2026** from the official UCI archive. The actual download
time, two file checksums, source headers and per-sheet row counts are recorded in
[source-manifest.json](source-manifest.json). The archive contains a workbook with
1,067,371 rows across two sheets. Source records cover a UK online gift retailer,
including many wholesale customers, from 1 December 2009 to 9 December 2011.

The workbook and derived row-level CSV/database stay in ignored `raw/` and
`processed/`. Public `results/` contains aggregate tables and verification results.
Original code and documentation use the repository's MIT licence;
source data and derived aggregates retain the CC BY 4.0 attribution.

## Local preparation and Tableau inputs

The build preserves source sheet/row lineage, creates the
[fact/dimension model](../docs/model.md), and exports two local Tableau inputs:

| File | Grain and current size | Purpose |
|---|---|---|
| `processed/lines.csv` | One raw workbook row, with source sheet/row | Reproducible DuckDB ingestion |
| `processed/retail.duckdb` | Staging, facts, dimensions and marts | SQL calculations and reconciliation |
| `processed/tableau_sales.csv` | 993,608 eligible sales lines | Date/country/product filtering with distinct invoice counts |
| `processed/tableau_customers.csv` | 5,826 identified purchasing customers | Fixed customer snapshot, groups and eligible repeat measures |

Regenerate these files with the [project commands](../README.md#structure-and-reproduction)
before opening the workbook. It reads the local extracts through relative paths;
the extracts are not embedded in the public workbook.

## Published analytical outputs

The original monthly, country, cohort and segment aggregates retain their existing
definitions. The extension adds:

- `order_bridge.csv`: four mutually exclusive customer components of the comparable
  period's invoice change.
- `product_changes.csv`: merchandise stock-code value changes, distinct product
  invoice counts and penetration for January–November 2010/2011.
- `product_preferences.csv`: the top 20 merchandise products per customer group,
  using the snapshot's last-12-month window.
- `cohorts_by_segment.csv`: cohort month × month index × customer group, preserving
  future blanks and the counts needed for weighted rates.
- `diagnostic_summary.json` and `model_checks.json`: model counts, product-quality
  profile and reconciliation evidence.

The product dimension has 5,130 codes across selected in-window source records;
4,737 occur in eligible sales. Similarly, the customer dimension includes 5,914
source IDs, while customer purchasing analysis covers 5,826. These different
populations reflect their stated grains rather than a discrepancy.

The source sheets overlap. [Metric definitions](../docs/metrics.md) explain the
verified overlap removal, retained identical rows, missing customer IDs, separate
cancellation records and complete-month window. Source dates are used as recorded;
no timezone or exchange-rate conversion is assumed.

The analytical change is from raw invoice lines to attributed aggregate measures,
cohorts and rule-based segments. These historical UK data support a simulated
customer-development case; they are not observations from a Canadian luxury store.
