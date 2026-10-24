# Design — one researcher, checked evidence, reviewed output

24 October 2026 · Independent investment Agent application. The calculation core
and manual workbench form INV-S01; Agent drafting and saved briefs follow in INV-S02.

## Architecture and ownership

```mermaid
flowchart TD
    UI[React research workspace] --> API[FastAPI research endpoints]
    API --> DATA[Source packages and fact validation]
    API --> RUN[One Research Agent]
    RUN --> TOOLS[Read and calculate tools]
    TOOLS --> DATA
    TOOLS --> CALC[Python Decimal calculations]
    RUN --> DRAFT[Brief with evidence references]
    DRAFT --> UI
    UI --> SAVE[Human review and save]
    SAVE --> DB[(PostgreSQL tasks and brief versions)]
```

- **React/TypeScript:** its own research application under `web/`; company,
  periods, metric comparison, source evidence and brief editor.
- **FastAPI/Python:** its own `research_api.app:create_app` entry point under `api/`,
  served on port 8010. It does not import or start the bank service.
- **Storage:** source packs are read-only files in this increment. Task, research-run
  and brief-version persistence belongs to INV-05, in investment-owned storage;
  neither bank credentials nor bank tables are dependencies.
- **Research core:** `projects/investment-research/src/research_brief/` currently owns
  pure calculation/validation code. Future API tools call this code directly.
- **Runtime:** one Agent owns evidence gathering and the final draft. The application
  supplies tools, budgets, storage and human review. An SDK or provider adapter does
  not own the financial facts or the reviewed document.

The [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk)
is a candidate execution adapter when API integration is scheduled. Keep a small
`ResearchRunner.run(task, tools) → DraftResult` boundary so a different model runtime
can be added without changing facts or review semantics. OpenAI, Claude and compatible
API profiles are future choices; there is no new SDK dependency or paid call now.
Do not promise that changing an endpoint makes different providers equivalent.

Use the portfolio's engineering conventions with this application's own Dockerfile,
web build, dependency files and CI job. The same Git repository organizes the cases;
it does not combine their runtimes. The investment Agent owns its prompts, tools,
research context and outputs. ValueFocus informs these architecture boundaries.

## Architecture choices

| Adopt | Keep out of this release |
|---|---|
| One Agent responsible for the research brief | Separate planner, writer, critic and investor-persona Agents |
| Facts with source, period and unit | Live multi-market pricing and trading calendars |
| Code-owned arithmetic with input references | Model-written formulas or arbitrary expression execution |
| A saved, reviewed brief linked to evidence | Long-term personal memory, broker connections and automatic trades |

The implementation and research prompts are original portfolio work. Architecture
inspiration is applied as design principles, without importing another product's
source code, prompts, user records or configuration.

## Data contract — current calculation input

[Example](../examples/msft-fy2025.json), schema version 1:

| Object | Required meaning |
|---|---|
| `issuer` | Stable company ID, name and SEC CIK for source identification. |
| `source` | ID, title, HTTPS URL, retrieval timestamp and downloaded-content SHA-256. |
| `periods` | Exactly two consecutive complete annual periods, with stable ID and inclusive start/end dates. |
| `facts` | Stable ID, supported metric, period ID, decimal value string, currency, unit/scale, source ID and table/row/year locator. |

Supported metrics: `revenue`, `operating_income`, `operating_cash_flow`. The initial
pack uses USD millions for consolidated Microsoft figures; all facts in a pack
must use the same currency and scale. The FY2024 comparative column is taken from
the FY2025 report, not silently merged with an earlier report edition.

`growth_pct = (current - prior) / prior × 100`; a zero/negative prior value leaves
growth unavailable with a reason. `operating_margin_pct = operating_income / revenue × 100`;
margin change is the current margin minus the prior margin, in **percentage points**.
Keep full Decimal precision until the final two-decimal display. Missing inputs
remain gaps. Reject duplicate facts, invalid references and incompatible periods/units.

Future explanatory passages have `evidence_id`, `source_id`, section locator and
text with an explicit `verbatim` or `analyst_summary` kind. They are source material,
not instructions to the Agent. The current six-number pack contains no explanation
passages, so it cannot establish causes of the financial changes.

## Four Agent tools — INV-04

| Tool | Input | Output |
|---|---|---|
| `list_sources` | Registered issuer ID | Available report IDs, dates, titles and URLs. |
| `read_facts` | Source and period IDs; supported metric IDs | Facts with units, dates and locators; explicit missing items. |
| `compare_periods` | Selected fact IDs | Validated calculations with formula, input IDs and any gaps. |
| `read_passages` | Registered source ID and research query | Relevant passages/section references from the selected report; empty if unavailable. |

The model may choose and repeat reads within a proposed limit of eight tool calls
per run. Tools accept registered IDs, not arbitrary URLs, SQL or Python. An invalid
tool result or exhausted budget leaves a recoverable draft/gap state. No model tool
marks a document reviewed or publishes it.

## Manual workbench — INV-03

The standalone API exposes two read-only routes for the current registered report:

| Route | Result |
|---|---|
| `GET /v1/research/sources` | Report ID, company, title, URL and comparable periods. |
| `GET /v1/research/sources/{id}/comparison` | The original comparison contract: facts, metrics, margins, sources and gaps. |

The source registry owns file paths; the browser sends a report ID. These public
financial facts need no bank session, database or model. Missing individual facts
remain a successful response with gaps; an unreadable/invalid pack returns 503,
and an unregistered report returns 404. Reload revalidates the registered file.

The browser holds the research question, notes and open questions for the current
visit. Failed refreshes preserve these edits. Selection changes clear the old
comparison so it cannot appear under a different report. Persistent reviewed
versions remain INV-05. The page shows the report's actual years and units, exposes
source facts and formulas, and distinguishes unavailable figures from zero.

## Brief contract and application flow — INV-03/05

`ResearchTask`: ID, question, issuer, source snapshot ID, period IDs, selection version.
`DraftResult`: task/selection version, summary, metric comparison references,
explanations with evidence IDs, open questions, runtime identity and completion state.
`BriefVersion`: task, source hash, draft reference, edited content, author/reviewer,
version and review timestamp. Financial values remain bound to fact/calculation IDs.

Planned endpoints are `POST /v1/research/tasks`, `GET /v1/research/tasks/{id}`,
`POST /v1/research/tasks/{id}/runs`, `POST /v1/research/tasks/{id}/briefs` and
`GET /v1/research/briefs/{id}/export`. Use request/response schemas when implemented.
Task states stay small: preparing → draft → reviewed, with needs-review on changed
source selection. A failed Agent run leaves manual editing available. Save uses the
expected selection and brief version to prevent accepting an outdated draft.

There is no scheduler or deployment expansion in this increment. Normal request/run
status is enough; add streaming only if observed task latency warrants it.
