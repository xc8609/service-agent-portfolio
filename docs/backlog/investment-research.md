# Investment Research Brief — delivery plan and story cards

24 October 2026 · First increment: a comparable-facts foundation for a research brief.
[Project](../../projects/investment-research/README.md) ·
[Business case](../../projects/investment-research/docs/business-case.md) ·
[Design](../../projects/investment-research/docs/design.md) ·
[Executed evidence](../../projects/investment-research/docs/acceptance.md).

The user selects a company and reporting periods, checks what changed, and produces
an evidence-backed brief for human review. Start with Microsoft FY2025 and FY2024
comparative figures **within the same FY2025 annual report**: revenue, operating
income and operating cash flow. Broader company coverage follows this working example.

The foundation slice contains a reviewed six-fact source pack and original Python
3.9 standard-library validation/calculation CLI. INV-03 connects a standalone manual
workbench and read-only API; INV-04 adds evidence retrieval and a cited draft.
Persistence remains INV-05.
The owner confirmed this research scenario and an independent Agent application on
24 October. Its own UI, API, tools and build run without the bank service or database.
ValueFocus informs architectural boundaries; its code, prompts and private content
are not copied. Acceptance records distinguish implemented slices from full stories.

## Two-Sprint forecast

Relative weeks begin when delivery starts; these are estimates, not fixed dates or
actual staffing. Capacity assumes two developers with **14 available developer
person-days per Sprint**, plus explicit BA and QA support. Developer estimates include
implementation, developer tests and review fixes; QA covers additional workflow testing.

| Sprint | Goal / stories | Dev / BA / QA person-days | Exit evidence |
|---|---|---|---|
| INV-S01 · weeks 1–2 | Sources, comparable calculations and manual workbench; INV-01–03 | 13 / 3.5 / 3 | One research task completed manually with traceable facts and reproducible calculations. |
| INV-S02 · weeks 3–4 | Agent draft, review/export and UAT; INV-04–06 | 10 / 2 / 4 | Same task completed through assistance, human review and saved/exported brief; observed comparison recorded. |

Total: **23 Dev + 5.5 BA + 7 QA person-days**. Unused developer capacity is integration
and correction allowance. Deferred model access can delay Agent-quality acceptance
without blocking the source, calculator, manual workbench or review features.

## INV-01 — Establish the research question and source pack

**Status:** Source pack merged in #35; report selection integrated in INV-03, verification below.
**Dependencies:** None. **Estimate:** Dev 4, BA 1.5, QA 1 person-days · INV-S01.

As an analyst, I want a defined question and a traceable report selection so that
I know which company, periods and evidence my brief represents.

**Deliverables:** research-task fields, source register, six reviewed facts, source-to-field
mapping and retrieval outcome. The 24 October SEC probe returned 403; the issuer report
download succeeded. Record those outcomes separately and retain the usable issuer source.

- **INV-01-AC1:** Each fact identifies its report, metric, reporting period, currency/unit and table/row locator; the source records URL, retrieval date and content hash.
- **INV-01-AC2:** Both selected years come from the same reviewed annual report; the task displays those years rather than implying a live or latest feed.
- **INV-01-AC3:** A failed source request remains a recorded failure. A verified alternative source has its own provenance; no fabricated filing or fact fills the gap.

## INV-02 — Validate comparable facts and calculate changes

**Status:** Calculation foundation merged in #35; API/UI integration delivered with INV-03.
**Dependencies:** INV-01 fact/source contract. **Estimate:** Dev 4, BA 1, QA 1 person-days · INV-S01.

As an analyst, I want reproducible comparisons so that I can verify the numbers
before interpreting business performance.

**Deliverables:** typed fact validation, deterministic year-over-year changes and
operating margins, a runnable CLI, calculation tests and result/source references.
Keep formulas outside the model and reuse them in the later manual and Agent paths.

- **INV-02-AC1:** The reviewed six facts reproduce the expected changes and margins with a stated formula and rounding convention.
- **INV-02-AC2:** A missing metric leaves its affected calculations unavailable while other valid metrics remain usable. Incompatible periods or units reject the pack; a zero/negative denominator produces an explicit unavailable ratio, not a guessed value.
- **INV-02-AC3:** Every calculated result retains its input references, periods and units; API/UI integration preserves the same calculation semantics.

## INV-03 — Complete the research manually in one workbench

**Status:** Implemented; execution and review recorded in the [workbench acceptance](../../projects/investment-research/docs/workbench-acceptance.md).
**Dependencies:** INV-01–02 contracts; completed calculations for integration.
**Estimate:** Dev 5, BA 1, QA 1 person-days · INV-S01.

As an analyst, I want the question, comparison and evidence together so that I can
prepare a brief without repeatedly rebuilding context across documents.

**Deliverables:** a small research view, facts/comparison table, source links or
excerpts, and editable notes. Use the same React/TypeScript and FastAPI technology
choices in an independent project-local application, with its own startup and CI.

- **INV-03-AC1:** An analyst can select the prepared company/periods, inspect all three metrics and calculations, open the cited evidence and write a manual note.
- **INV-03-AC2:** Loading, missing evidence and source failure remain distinguishable; current edits survive a failed source refresh. Durable saved versions follow in INV-05.
- **INV-03-AC3:** The complete manual task works with model integration disabled, providing the baseline for INV-06.

## INV-04 — Produce a bounded, evidence-backed Agent draft

**Status:** Implemented with an offline scripted provider; [executed acceptance](../../projects/investment-research/docs/agent-acceptance.md).
**Dependencies:** INV-01–03 and the reviewed tool/output contract.
**Estimate:** Dev 4, BA 0.5, QA 1 person-days · INV-S02.

As an analyst, I want assistance that connects the question, calculations and report
evidence so that I spend less effort assembling a reviewable first draft.

**Deliverables:** one research Agent; tools for approved sources, facts, comparisons
and relevant report passages; a provider boundary; a structured brief with changes,
supporting evidence and open questions. Start without multi-agent orchestration.

Implementation: independent Python runtime, four read-only tools, three attributed
report summaries, a strict run API and an explicit draft-to-notes action. The
[INV-04 design](../../projects/investment-research/docs/agent-design.md) records
the provider, citation and stale-context boundaries. Live-model API use remains deferred.

- **INV-04-AC1:** Numeric claims use calculation-tool results and references; company explanations are tied to report evidence and separated from analyst interpretation.
- **INV-04-AC2:** Missing evidence yields a specific open question. Retrieved text cannot change tool permissions, and the Agent cannot approve a brief or execute trades.
- **INV-04-AC3:** A bounded run returns a draft or a clear incomplete result; the manual path remains usable. Recorded/simulated execution and live-model validation have separate evidence labels.

## INV-05 — Review, save and export the research brief

**Status:** Planned. **Dependencies:** INV-03; INV-04 for assisted-draft integration.
**Estimate:** Dev 4, BA 0.5, QA 1 person-days · INV-S02.

As an analyst, I want to correct and save a brief with its evidence so that another
reviewer can understand both the conclusion and its basis.

**Deliverables:** editable brief, explicit draft/reviewed states, saved versions and
Markdown export containing the question, periods, findings, calculations and sources.

- **INV-05-AC1:** Human edits and review are saved with the brief; model output alone never sets the reviewed state.
- **INV-05-AC2:** Changing the selected report or periods marks the existing draft as needing recheck while preserving the prior saved version.
- **INV-05-AC3:** Reload and export retain the reviewed text, selected periods and source references; export does not invent missing evidence.

## INV-06 — Validate the workflow and publish the case

**Status:** Planned. **Dependencies:** INV-01–05 for full workflow acceptance.
**Estimate:** Dev 2, BA 1, QA 2 person-days · INV-S02.

As the portfolio owner, I want observed task results and a concise case study so that
reviewers can assess the business design, data work and Agent contribution.

**Deliverables:** three task scripts, executed outcomes, defect/retest record,
screenshots, brief example and a short GitHub walkthrough.

- **INV-06-AC1:** Run three tasks: compare the reported metrics; explain a change using cited passages; prepare and review a brief with unresolved questions. Check the same required facts and sources in manual and assisted paths.
- **INV-06-AC2:** Exercise missing data, incompatible units/periods and source failure; demonstrate clear recovery without invented figures or lost saved work.
- **INV-06-AC3:** Record numeric/citation correctness, omissions, edits and navigation steps; timing claims require actual observations. Publish the result and remaining work without inferring savings or model quality from fixture-only checks.

Each story closes through its acceptance evidence and review, not from elapsed
Sprint dates. Update this plan when dependencies or scope change; retain bank
acceptance and the deferred voice/retail plans as separate workstreams.
