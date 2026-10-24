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
`processed/`. Public `results/` contains small aggregate tables and verification
results. Original code and documentation use the repository's MIT licence;
source data and derived aggregates retain the CC BY 4.0 attribution.

The source sheets overlap. [Metric definitions](../docs/metrics.md) explain the
verified overlap removal, retained identical rows, missing customer IDs, separate
cancellation records and complete-month window. Source dates are used as recorded;
no timezone or exchange-rate conversion is assumed.

The analytical change is from raw invoice lines to attributed aggregate measures,
cohorts and rule-based segments. These historical UK data support a simulated
customer-development case; they are not observations from a Canadian luxury store.
