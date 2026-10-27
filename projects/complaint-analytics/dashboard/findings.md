# Complaint operations — initial findings and decisions

Analysis date: 2026-09-28. Scope: 27,011 published US CFPB complaints received
1–31 July 2026, within the seven-product simulated routing scope. Snapshot
downloaded 2026-09-28. These are descriptive findings, not causal claims,
Canadian-market estimates, stakeholder approvals or measured AI outcomes.

Evidence: `data/processed/tableau/complaint_daily.csv`, reconciled to the local
DuckDB source by `scripts/export_tableau.py`. Each row is an aggregate; volume
is the sum of `complaint_count`, not the CSV row count. Tableau screenshot
inspection corroborated both pages' unfiltered headline indicators. Update,
27 October 2026: native filter checks passed after two workbook fixes
([verification](verification.md#native-filter-retest--27-october-2026)).

## Findings and proposed operational responses

| Finding | Evidence | Proposed response in the simulated case | Limitation / validation needed |
|---|---|---|---|
| Two products dominate volume | Credit card 8,027; checking/savings 7,963; combined 15,990 (59.2%) | Prioritize discovery of their issues and analyst workflow; retain all seven products in evaluation | No customer/account denominator: counts cannot rank product risk or service quality |
| High overall timeliness masks product differences | Overall 26,620 Yes / 27,011 known = 98.6%; prepaid has 42 No / 530 = 7.9% No, versus 42 / 8,027 = 0.5% for credit cards | Investigate both rates and counts; avoid prioritizing purely by complaint volume | Timely response is not resolution or satisfaction; observations do not establish causes |
| Mortgage contributes a large share of non-timely flags | 118 No / 3,066 = 3.8%; 118 / 391 = 30.2% of all No flags | Include mortgage response handling in discovery and exception analysis | Need workflow timestamps and case review to explain delays |
| Public narratives cover a minority | 6,409 / 27,011 = 23.7%; 20,602 have no public narrative | Evaluate text routing on eligible records; design an explicit missing-text fallback | Public-text absence does not mean the institution lacks a submitted description; published text is a selective sample |
| Text coverage is limited across all seven products | Product coverage ranges from 22.5% to 25.4% | Report results and coverage by product; avoid extrapolating performance to records without public text | No verified manual labels or model performance yet |
| Account management is the most frequent issue in this scope | “Managing an account”: 4,580 (17.0%) | Review representative complaints to refine requirements and exception paths | Consumer-selected taxonomy is a proxy; frequency does not establish severity |

The `company_response` category “Untimely response” has 231 complaints, while
`timely_response = No` totals 391. They are different source fields and must not
be substituted for one another. Timeliness uses the dedicated Yes/No/unknown
counts; the response-type chart retains the response categories.

## Product-level reconciliation

| Product | Complaints | Public narratives | Coverage | Timely No | No / known |
|---|---:|---:|---:|---:|---:|
| Credit card | 8,027 | 1,822 | 22.7% | 42 | 0.5% |
| Checking / savings | 7,963 | 2,025 | 25.4% | 46 | 0.6% |
| Transfers / digital wallet | 3,474 | 781 | 22.5% | 42 | 1.2% |
| Mortgage | 3,066 | 728 | 23.7% | 118 | 3.8% |
| Vehicle loan / lease | 2,158 | 509 | 23.6% | 37 | 1.7% |
| Personal / payday / title loan | 1,793 | 410 | 22.9% | 64 | 3.6% |
| Prepaid card | 530 | 134 | 25.3% | 42 | 7.9% |

There are no unknown timeliness flags in this snapshot. The workbook formula
still excludes unknowns from the known-response denominator for future refreshes.
Rates above use summed counts, rounded to one decimal.

## BA recommendation and next evidence gate

Proceed with an **assisted-routing evaluation**, not an automated-routing rollout.
In the simulated future process, an analyst confirms or overrides a suggested
team. Missing-text records and model failures take an explicit fallback path.
This is a proposed process design, not a demonstrated operational result.

Before recommending a model: review the 70-row discovery sample; document label
ambiguity and team-mapping assumptions; fix the evaluation split before tuning;
compare majority and TF-IDF baselines, adding an LLM only if justified. Evaluate
both product classification and simulated-team errors. Define handling-time and
misroute-cost assumptions before estimating savings; measure them in a future
pilot rather than presenting calculated savings as observed benefits.

Update, 21 October 2026: the split, majority and TF-IDF baselines and the error
analysis are complete ([evaluation](../docs/04_ai_pilot_evaluation.md)). Reviewing
the 70-row discovery sample is now an optional step before a real pilot, not a
prerequisite for this case's recommendation.

Portfolio connection: banking product and consulting BA experience inform the
problem framing, exception handling and metric definitions. Reviewable evidence
is the SQL-to-CSV reconciliation, native Tableau workbook, recorded limitations,
and this recommendation. Model/application delivery remains a separate gate.
