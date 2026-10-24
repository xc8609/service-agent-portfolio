# Business analysis — investment research brief

24 October 2026 · Design baseline for INV-01–06.

## User, problem and intended value

**User:** an analyst preparing a company update for review. **Trigger:** a new
annual report, or a question about changes between two reporting periods.
**Decision supported:** what changed, what evidence explains it and which research
questions deserve follow-up.

The assumed current work involves opening a report, copying figures into a sheet,
checking dates/units, calculating changes, reading management commentary and
assembling a brief. The pain hypothesis is repeated preparation and verification,
with opportunities to lose sources or confuse reporting periods.

This is an authored research scenario. The owner's banking product and BA
experience informs the requirements and delivery approach; investment-research
employment and observed analyst productivity are not claimed.

| Current work | Target workflow | Intended benefit |
|---|---|---|
| Locate report and relevant tables. | Select a registered source and two explicit annual periods. | Reuse a checked source package. |
| Copy numbers and calculate changes. | Show normalized facts with reproducible formulas and input references. | Reduce transcription and arithmetic rework. |
| Read commentary and assemble an explanation. | Agent retrieves relevant evidence and drafts changes, explanations and open questions. | Reduce preparation effort while retaining evidence. |
| Recheck the draft and circulate it. | Analyst edits, reviews and saves a version with its sources. | A reviewable, repeatable research result. |

## First research question

> For Microsoft FY2025 versus FY2024, did revenue growth translate into operating
> profit and cash flow? What do the report and calculations establish, and what
> further evidence would be needed to explain the changes?

The three measures are **revenue, operating income and operating cash flow**.
Compare their levels and year-on-year changes; calculate operating margin and its
change in percentage points. A cash-flow movement alone does not explain its cause.
The brief distinguishes reported facts, calculated results, management explanations
and the analyst's interpretation.

## BA decisions and alternatives

| ID | Design choice | Rationale / acceptance link |
|---|---|---|
| I-D01 | Start with two annual periods from one issuer report. | A small comparable scope; the report's comparative values stay together. INV-01/02. |
| I-D02 | Preserve company, dates, currency, scale and source for every fact. | A number is useful only with its meaning and provenance. INV-01/02. |
| I-D03 | Calculate in Python; use the Agent for evidence selection and synthesis. | Separate reproducible arithmetic from language interpretation. INV-02/04. |
| I-D04 | Support the same brief manually. | Compare assistance against a useful workspace, including review effort. INV-03/06. |
| I-D05 | A reviewer saves the final version; changes to source selection require renewed review. | Make research ownership and evidence changes visible. INV-05. |

A spreadsheet and manual report are the baseline. A structured workspace already
improves reuse and calculation consistency. Add one Agent to answer variable
research questions and connect explanations to evidence; a multi-agent committee
adds no necessary capability to this first release.

These are implementation choices for this portfolio increment, not decisions made
by an external investment team. User-facing product scope remains adjustable.

## Roles and completion

The analyst selects the question/sources, checks explanations, edits and saves the
brief. The application preserves source facts, formulas and versions. The Agent
may retrieve and draft; it cannot change source facts or mark its own brief reviewed.
The first release can use one person for authoring and review; no approval hierarchy.

An enquiry is complete when the brief contains the selected periods, the three
metric comparisons, source references, a supported interpretation and open questions.
Missing evidence may be a valid recorded result; unsupported explanations are not.

## Value measurement and portfolio evidence

Use three tasks: operating update; cash-flow follow-up; incomplete-evidence update.
For manual and assisted paths record numeric/citation correctness, missing required
items, edits before acceptance and lookup/checking actions. Record elapsed time
when an actual walkthrough occurs; do not pre-assign a saving percentage.

For BA/BSA reviewers this case demonstrates options analysis, data mapping,
testable requirements and acceptance. For developer reviewers it demonstrates
typed tools, deterministic calculations, model boundaries, persistence and tests.
[Story cards and acceptance criteria](../../../docs/backlog/investment-research.md)
connect those capabilities to delivery.
