# Complaint Operations Analytics — Real Public Data

**Business question:** a bank's complaint intake team reads every complaint and forwards
it to a product team. Where are complaints concentrated, how timely are responses, and
is a text-based suggestion accurate enough to help analysts route complaints?

This project uses **real public US complaint data** from the Consumer Financial Protection
Bureau (CFPB) as a stand-in for a bank's inbox. The bank, its five product teams and the
routing process are simulated; the counts and model scores are actual results on the
public data. It complements the synthetic [bank service workflow](../bank-service-assist/README.md).

## Results at a glance

Scope: 27,011 complaints received 1–31 July 2026 for seven bank products, mapped to five
simulated teams ([SQL](sql/03_routing_scope.sql)).

| Finding | Evidence |
|---|---|
| Two products carry most volume | Credit card 8,027 and checking/savings 7,963 = 59.2% |
| High overall timeliness hides product gaps | 98.6% timely overall; prepaid cards 7.9% not timely vs 0.5% for credit cards |
| Mortgage drives non-timely responses | 118 of 391 "No" flags (30.2%) |
| Most complaints have no public text | 23.7% have a narrative, similar for every product (22.5–25.4%) |
| A simple text model suggests the right team 4 times in 5 | 81.7% team accuracy on a hold-out of 1,903 vs 31.5% majority baseline |
| Unattended routing is not justified | Only 24% of cases clear 0.5 confidence (94.4% accurate there) |
| One product needs taxonomy work | Prepaid-card recall 0.32; confused with checking, cards and transfers |

**Status:** analysis and routing baseline complete. The Tableau workbook is a
draft: both pages render with reconciled totals, but filter checks and screenshots
are still pending (see [Limits](#limits)).

**Recommendation:** pilot *assisted* routing (suggest, analyst confirms) with a manual
path for complaints without text; do not automate routing. Details:
[findings](dashboard/findings.md) · [model evaluation](docs/04_ai_pilot_evaluation.md) ·
[risk and governance](docs/05_risk_governance.md).

## Business analysis and data work

| Artifact | Content |
|---|---|
| [Business requirements](docs/01_business_requirements.md) | Problem, stakeholders, scope, user stories, success metrics |
| [Data model](docs/02_data_model.md) | Load → staging → routing scope → mart / evaluation |
| [Data-quality report](docs/03_data_quality_report.md) | Profiling of all 672,036 archive records |
| [Dashboard specification](dashboard/README.md) | Grain, measures and the Tableau workbook |
| [Verification](dashboard/verification.md) | SQL-to-CSV reconciliation and what is still unaccepted |
| [Results](results/) | Aggregate CSV, reconciliation checks, model metrics — no text, IDs or ZIP codes |

## Data source and terms

CFPB Consumer Complaint Database, official July 2026 historical archive, downloaded
2026-09-28 and pinned by SHA-256 ([provenance](data/source-manifest.json), [notes](data/README.md)).
The raw archive is **not** included. CFPB publishes the data for use and analysis;
narratives are consumer-authored and remain local. These are US records, not Canadian
customer observations, and not verified findings about any company.

## Reproduce

Python 3.12, from the repository root:

```bash
python3.12 -m venv .venv-analytics
.venv-analytics/bin/python -m pip install -r projects/complaint-analytics/requirements.txt
.venv-analytics/bin/python projects/complaint-analytics/scripts/download_archive.py
.venv-analytics/bin/python projects/complaint-analytics/scripts/profile_data.py
.venv-analytics/bin/python projects/complaint-analytics/scripts/export_tableau.py
.venv-analytics/bin/python projects/complaint-analytics/scripts/evaluate_baselines.py
```

Downloads are verified against the recorded checksum. Generated files go to the
git-ignored `data/processed/`; the published `results/` are copies of the aggregate
outputs. Unit and SQL tests run in the repository's offline CI.

## Limits

No classifier is deployed, no analyst used the suggestion and no time saving is measured.
The Tableau workbook's two pages were inspected locally; filter interaction testing and
the relative data path (`../results`) are not yet verified in Tableau Desktop. The model is
scored against consumer-selected product labels; manually annotating the 70-row
discovery sample is an optional pre-pilot step outside this case. No LLM was evaluated.
