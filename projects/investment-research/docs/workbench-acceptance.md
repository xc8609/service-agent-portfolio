# Independent research workbench — INV-03 acceptance

24 October 2026 · Executed by Codex as delegated technical/workflow verification.
The owner confirmed the financial-report-change scenario and independent Agent
boundary. This record covers the manual workbench, before Agent drafting.

## Workflow observed

The independent API served its own built frontend at `http://127.0.0.1:8010`.
No bank process, bank session, database or model call was needed by this application.

1. Selected Microsoft Annual Report 2025; the page showed FY2024 and FY2025 with
   their full July–June periods.
2. Loaded the three metrics in USD millions. Revenue growth was 14.93%, operating
   income growth 17.45%, and operating cash flow growth 14.86%. Operating margin
   changed from 44.64% to 45.62%, a 0.98 percentage-point increase.
3. Inspected the calculation explanation, six source values, table/row/year
   locators, report URL and retrieval date.
4. Entered a note describing those observed changes and follow-up questions about
   their business causes. The figures and the analyst's interpretation remained
   visually separate. No cause was generated from the numeric pack alone.

![Observed independent workbench comparison and source evidence](images/workbench-comparison.png)

## Acceptance-to-evidence map

| Criterion | Executed evidence |
|---|---|
| INV-01-AC1/2 | Source selection and real comparison API preserve company, dates, units, fact locators and source hash. Browser shows actual years, source link and locators. |
| INV-01-AC3 | The original retrieval record is unchanged. API tests exercise unreadable/malformed packs, and browser tests verify recovery from a source-list failure. Refresh means re-read the registered local pack, not download a newer filing. |
| INV-02-AC1/3 | API response equals the original Python comparison contract; browser checks the three growth figures and margin change. Source facts and formulas are visible. |
| INV-02-AC2 | Core tests cover incompatible periods/units and denominator handling. API and browser tests preserve valid metrics while a missing fact remains unavailable. |
| INV-03-AC1 | The observed manual task and successful browser scenario cover selection, metrics, evidence and editable notes. |
| INV-03-AC2 | Browser regressions cover failed refresh retaining the question/notes, source-list retry, and a delayed response arriving after a source change. Old results cannot replace the newly selected report. |
| INV-03-AC3 | This app runs independently with no model, bank dependency or persistence service. The manual task forms the baseline for later Agent comparison. |

## Checks executed

- **54 Python tests passed:** 43 calculation cases plus 11 independent API cases.
- **5 browser tests passed** against the built application and real local API.
  Error, partial-data and delayed-response scenarios use explicit response fixtures;
  the success scenario uses the actual registered Microsoft source pack.
- TypeScript/Vite build, Ruff checks and API formatting passed.
- A separate read-only review confirmed the application boundary, source references,
  selection handling and note preservation; no blocking defect was found.

From the project directory:

```bash
python -m pytest
npm --prefix web run build
# Start the independent API on 8010 before this command:
npm --prefix web run test:e2e
```

The new [CI workflow](../../../.github/workflows/investment-research.yml) runs the
same tests and builds/smoke-tests the standalone container. CI completion is recorded
on the corresponding PR; this local record does not claim a local Docker run.

## Next increment

The manual workflow is implemented and technically verified. Notes live in the
current page; there is no saved/reviewed brief yet. INV-04 adds report passages,
investment-owned tools and one research Agent. INV-05 adds persistence/review/export.
INV-06 compares the manual and assisted tasks; no productivity gain is inferred
from this initial walkthrough.
