# Data source

**Dataset:** [City of Winnipeg — 311 Requests (`u7f6-5326`)](https://data.winnipeg.ca/Contact-Centre-311/311-Requests/u7f6-5326),
published by Customer Service & Communications and updated daily.

**Licence and attribution:** Contains information licensed under the
[Open Government Licence – Winnipeg](https://data.winnipeg.ca/open-data-licence).
The portal's licence field names this licence; its API metadata reports the
`OGL_CANADA` identifier. Both values are recorded in the manifest.

**Retrieved:** 1 November 2026, 17:26 UTC, by
[`scripts/extract_requests.py`](../scripts/extract_requests.py). The portal reported its last
row update at 00:12 UTC the same day. [source-manifest.json](source-manifest.json) records
the query, row counts by request type, file checksum and licence fields.

## Extract

| Item | Value |
|---|---|
| Filter | `subject = 'Service Request'`, `reason = 'Water and Waste'`, opened 1 Jan 2023 – 31 Oct 2026 |
| Columns | case and interaction IDs, channel, subject, reason, type, open/close dates, status, neighbourhood, ward |
| Rows | 508,528 (matches the API's count by type) |
| City-wide follow-up calls | 92,724 rows, retrieved as monthly counts only |
| Not retrieved | point geometry (randomized for privacy-sensitive locations) |

The request-level CSV stays in ignored `data/raw/`; the DuckDB file stays in ignored
`data/processed/`. Only aggregate results in [`../results`](../results) are published.
The source has no free-text narrative field.

## Observations that shape the analysis

- **Grain:** rows are interactions. 2,528 Water and Waste cases have more than one row;
  every case attribute agrees across those rows and only interaction ID or channel
  differs. The model counts cases and keeps the interaction count.
- **Snapshot:** the newest records were opened early on 31 October, so the analysis
  snapshot is **31 October 2026 00:00 local time**. Cases opened later are excluded.
- **Status:** in-scope cases are Closed, Open, In-Progress or (four rows) NA.
  Open and In-Progress cases have no closing date. No case closes before it opens.
- **Older open records:** 12,012 Water and Waste service requests opened before 2023
  are still Open in the source (outside this extract's window).
- **Type names change:** cart repair/replacement types gained a `_2025` suffix on
  27 March 2025; both names are mapped to one group in
  [the type map](../reference/request_type_map.csv).
- **Geography:** ward is present on 100% of in-scope 2023 cases and about 70% from 2024.
  Ward is therefore not used for headline comparisons.
- **Follow-up calls** (`Follow Up Call- SLA not breached` and `Follow up- SLA breached`)
  are recorded under Corporate Support Services as separate cases. A sample of 40 did
  not link to any original case, so they are reported city-wide only.

## Reproduce

From the repository root (the extract needs network access; the build does not):

```bash
python3 projects/winnipeg-311-service-operations/scripts/extract_requests.py
python projects/winnipeg-311-service-operations/scripts/build_analysis.py
```

The extract uses only the Python standard library. The build needs DuckDB
([requirements.txt](../requirements.txt)). Because the source updates daily, a new
extract will differ from the recorded snapshot. Compare its manifest before replacing
published results.
