# Retail visual analysis

Three views answer the business questions using the same reconciled SQL results:

1. **Sales overview:** complete-month sales, comparable January–November results,
   order/value decomposition, cancellation amounts and country contribution.
2. **Customer repeat purchasing:** 90-day and 24-month measures, identified-customer
   coverage and first-observed-purchase cohorts.
3. **Customer priorities:** explicit customer groups, their counts and last-12-month
   sales contributions, with proposed investigation questions.

## Open the portable report

Open [index.html](index.html) in a browser. It reads the three adjacent SVG images,
works offline, and supports mouse and keyboard tab navigation. The SVGs also render
directly in the [project README](../README.md). They are generated analytical charts,
not screenshots of Tableau. Full-size image links allow closer inspection.

For a local HTTP preview, run from the repository root:

```bash
python3 -m http.server 8020 --bind 127.0.0.1 --directory projects/retail-customer-analytics
```

Then open `http://127.0.0.1:8020/dashboard/`.

## Tableau workbook

[retail_customers.twb](retail_customers.twb) is a native workbook **draft** with
four CSV data sources, five worksheets and three dashboards. Keep `dashboard/`
and `results/` beside each other. Connections use relative `../results` paths.
If Tableau asks for a missing file, select the matching CSV from `results/`.
The [data model and metric definitions](../docs/metrics.md) describe each grain.

The workbook provides sales, cohort and segment views. The portable report adds
summary cards and business commentary. No global cross-source filter is claimed.
The workbook's XML, field types and CSV header references were checked; native
Tableau rendering and interaction acceptance remain pending. During the local
attempt the app automation did not reach an inspectable retail workbook, so the
attempt is not recorded as a successful native open.

## Verification — 24 October 2026

- Source rows: **1,067,371** = 22,523 proven overlapping copies + 25,526 partial-final-
  month rows + **1,019,322** rows in the analytical window (before record-class filtering).
- **11 SQL reconciliation checks passed** in [checks.json](../results/checks.json).
- **10 synthetic regression tests passed**, including sheet overlap, same-invoice
  lines, accounting entries, cancellations, missing IDs, cohort blanks and 90-day eligibility.
- All **7 result files reproduced byte-for-byte** on a second SQL run. The repository
  offline suite passed **167 tests** on Python 3.12, including these 10 retail cases.
- All three SVG reports were visually inspected after the overlap correction.
- Portable-report mouse navigation across three views, Home and Right-arrow tab
  navigation were observed in the browser. Business owner review and action
  selection remain the next review step.

Native acceptance checklist: open the workbook against relative CSVs, inspect all
three dashboards, verify sales £19,513,678.427 and group customers 5,826, confirm
future cohort cells are unavailable rather than zero, then record any layout fixes.
