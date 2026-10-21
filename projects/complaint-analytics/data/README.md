# Data source and downloaded snapshot

Downloaded: **2026-09-28, 16:30 UTC**. Publisher: US Consumer Financial Protection Bureau.

- [Official historical archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/)
- [Selected July 2026 ZIP](https://files.consumerfinance.gov/f/documents/CCDB_Export_20_July_2026.zip)
- [Machine-readable provenance and original schema](source-manifest.json)
- [Actual profiling results](../docs/03_data_quality_report.md)

The complete selected archive contains **672,036 records** received July 1–31,
2026, including **10,002 nonblank narratives** (1.49%). The compressed file is
16,958,404 bytes; the CSV is 216,250,982 bytes. This is one monthly archive,
not the complete CFPB complaint database. No source rows were discarded on loading.

## Terms and interpretation

The [CFPB data page](https://www.consumerfinance.gov/data-research/consumer-complaints/)
states published complaint data is available to use, analyze and build on.
Its [legal notices](https://www.consumerfinance.gov/privacy/website-privacy-policy/)
distinguish CFPB-created public-domain content from third-party copyrighted material.
Attribute CFPB, keep raw narratives local, and use labelled synthetic public demo
examples. Do not describe all consumer-authored material as public domain.

These are real US complaint records, not Canadian customer observations or verified
findings against companies. Consumer-selected product labels are proxy targets.
Public text availability varies sharply across products and must not be treated as
representative sampling. The reason for missing text is not established by this file.

## Schema and compatibility

The inspected CSV contains 16 columns (listed in the manifest), including narrative,
product/issue, company, received/sent dates and response fields. It has no consumer
consent column. Staging now supports this exact source; other snapshots need a new
schema check. Blank text is distinguished from present text and malformed dates/IDs
are counted. No final-resolution date or internal routing history is available.

CFPB's [release notes](https://cfpb.github.io/api/ccdb/release-notes.html) record the
September 2026 removal of narratives from the current database. The downloader now
uses the selected historical archive and verifies its SHA-256 instead of downloading
the latest multi-GB export. A changed archive fails verification for investigation.

## Business discovery selection

The simulated intake scope covers seven bank-relevant products mapped to five
simulated teams in `sql/03_routing_scope.sql`. Credit reporting, debt collection,
debt/credit management and student loans are out of scope. Filtering the scope to
nonblank text yields **6,409** records. This is an explicit scope choice, not an
assertion about all bank complaints. Some in-scope sub-products (e.g. payday loans,
virtual currency) are not typical Canadian bank offerings; product labels are kept whole.

A reproducible review file selects 10 records per product by hashed complaint ID.
Its 70 rows have blank annotation columns. They are **not yet reviewed**, and must
not later be treated as an untouched evaluation set. Fourteen excess rows share
normalized text within the scope; duplicate handling precedes any model split.

## Local files (excluded from Git)

| Path | Contents |
|---|---|
| `raw/CCDB_Export_20_July_2026.zip` | Original complete downloaded archive |
| `raw/CCDB_Export_20_July_2026.csv` | Original extracted CSV |
| `raw/source-manifest.json` | Download provenance; metadata-only copy tracked above |
| `processed/cfpb.duckdb` | Raw/staging, routing scope and banking discovery tables |
| `processed/banking_discovery.parquet` | 6,409 scoped records with text, plus routing team |
| `processed/discovery_review.csv` | Local 70-row discovery worksheet containing real text |
| `processed/product_summary.csv` | Product counts and narrative coverage |
| `processed/profile.json` | Full profiling summary and provenance |

The Tableau exporter additionally creates `processed/tableau/complaint_daily.csv`
with 5,228 aggregate rows representing all 27,011 complaints in the routing scope,
including records without text. Counts are reconciled against staging and
recorded in `processed/tableau_export_checks.json`. No narratives or IDs are exported.
See the [Tableau guide](../dashboard/README.md).

Reproduction commands are in the [project README](../README.md).
