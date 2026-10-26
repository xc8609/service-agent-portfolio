# Investment research data

## Actual source and retrieval

The first source is the issuer's [Microsoft Annual Report 2025](https://www.microsoft.com/investor/reports/ar25/index.html).
Its consolidated Income Statements and Cash Flows Statements contain both annual
periods used in the example. These are real public reported figures, not synthetic
bank records or model estimates.

- Downloaded **24 October 2026, 17:35:11 UTC**; 601,259 bytes of HTML.
- SHA-256: `564154a15ac28c0f7f72f304ae26b74c29cfca9f3eafe8d59595776769d621ca`.
- Raw HTML and retrieval manifest are local under `data/raw/`, excluded from Git.
- [Reviewed example pack](../examples/msft-fy2025.json) contains only six numeric
  facts, their source metadata and exact table/row/year locators. The figures were
  manually curated and checked against the publisher tables; no automated extraction
  or SEC ingestion is claimed.

| Canonical metric | Report locator | FY2024 | FY2025 |
|---|---|---:|---:|
| `revenue` | Income Statements / Total revenue | 245,122 | 281,724 |
| `operating_income` | Income Statements / Operating income | 109,433 | 128,528 |
| `operating_cash_flow` | Cash Flows Statements / Net cash from operations | 118,548 | 136,162 |

All values are **USD millions**. FY2024 is 1 July 2023–30 June 2024; FY2025 is
1 July 2024–30 June 2025. Both columns are from the same FY2025 report edition.
This is a reproducible historical example, not a latest-data service.

## Explanatory evidence — INV-04

[Reviewed commentary pack](../examples/msft-fy2025-passages.json) contains three
short original paraphrases, labelled `analyst_summary`, with the same report ID
and SHA-256 as the numeric pack. Checked on 24 October against both the downloaded
HTML and the publisher's report:

| Evidence | Report section | Research use |
|---|---|---|
| Revenue drivers | Discussion & Analysis / Summary Results of Operations / FY2025 compared with FY2024 | Company-reported revenue-growth context. |
| Operating-income context | Same section / operating expenses and operating income | Profit and spending context; does not quantify the cause of the margin change. |
| Cash-flow drivers | Discussion & Analysis / Liquidity and Capital Resources / Cash Flows | Company-reported explanation of operating cash generation. |

These are 69 words of attributed paraphrase, not verbatim report passages. The
Agent retrieves this small registered evidence set by topic; it does not search
the entire internet or infer a quantified causal explanation from six figures.

## Structured-source feasibility

The [SEC data API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
provides submission metadata and standard-taxonomy XBRL facts without an API key.
An actual Company Concept request on 24 October returned HTTP 403 in this environment.
No SEC data were downloaded or silently substituted. The issuer report is the
documented source for this increment. Retry structured integration as a separate
source-adapter task, following [SEC developer access guidance](https://www.sec.gov/about/developer-resources).

## Verification and reuse

Check the company, annual headers, unit, row labels and six amounts against the
source before accepting a new pack. The program then checks dates, references,
uniqueness, currency and scale before calculating. Tests use authored synthetic
values for missing/invalid scenarios; they do not alter the real example.

Public access does not transfer the publisher's rights. The repository MIT license
covers original code and documentation; Microsoft retains its report content.
Link the source and retain attribution. The full report and publisher's narrative
are not redistributed; only the six facts and short original commentary summaries
are included. Generated calculation outputs remain local under `data/processed/`.
