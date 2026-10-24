# Foundation acceptance — 24 October 2026

Scope: INV-01 source-pack slice and INV-02 calculation slice. The first research
workspace and Agent run are not implemented by this increment.

## Source verification

Downloaded the issuer's annual-report HTML, recorded its retrieval timestamp and
SHA-256, and checked its annual headers, units and six selected values. A local HTML
table check also found all three named rows with their FY2025/FY2024 values.
[Source record](../data/README.md) and [reviewed pack](../examples/msft-fy2025.json).

The SEC Company Concept probe returned 403. The successful issuer download is a
separate, documented source; no SEC API extraction is claimed.

## Observed CLI result

Run from the repository root:

```bash
PYTHONPATH=projects/investment-research/src python3 -m research_brief \
  projects/investment-research/examples/msft-fy2025.json
```

| Measure | FY2024 | FY2025 | Computed change |
|---|---:|---:|---:|
| Revenue, USD millions | 245,122 | 281,724 | +14.93% |
| Operating income, USD millions | 109,433 | 128,528 | +17.45% |
| Operating cash flow, USD millions | 118,548 | 136,162 | +14.86% |
| Operating margin | 44.64% | 45.62% | +0.98 percentage points |

The CLI exited successfully with no data gaps. Output retains the source record,
each original fact and the input IDs for each calculation. Growth uses unrounded
inputs and two-decimal HALF_UP output; the report's displayed growth percentages
are rounded to whole numbers. These are calculations, not model answers or savings.

## Requirement-to-test evidence

| Criterion | Evidence / current outcome |
|---|---|
| INV-01-AC1 | Source, dates, units and table locators recorded in the real pack; reference validation covered by tests. |
| INV-01-AC2 | Both annual columns checked against the same report; on-screen task selection is still pending. |
| INV-01-AC3 | SEC failure and successful issuer retrieval separately recorded; automatic refresh/failure UI is pending. |
| INV-02-AC1 | Real example regression and synthetic arithmetic/rounding cases cover the calculation outputs above. |
| INV-02-AC2 | Tests cover missing facts, zero/negative denominators, duplicates and incompatible periods/currency/scale. |
| INV-02-AC3 | CLI retains source and input fact references; API/UI integration is pending. |

**43 targeted tests passed in local Python 3.12 and Python 3.9.6 virtual environments.** Test code is
[here](../tests/test_comparison.py); the root pytest configuration includes this
suite in both existing offline CI jobs. No network or model credentials are needed.
The complete local offline suite passed **152 tests**, with two optional SQL modules
skipped because DuckDB was absent. Ruff, publication/link checks, bank traceability
and `git diff --check` also passed. A separate review confirmed the six source values,
hash and the foundation's limited implementation scope.

## Next acceptance increment

INV-03 adds a manual research workspace showing the selected report/periods,
comparison table, source links and editable brief. INV-04 then adds a single Agent
and explanatory passages; INV-05 saves/reviews/exports; INV-06 records the three
end-to-end tasks. This acceptance covers the foundation only and does not close
either full Sprint. [Delivery plan](../../../docs/backlog/investment-research.md).
