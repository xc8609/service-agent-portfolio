# Lookup value and evaluation contract

Version 0.1 · 19 October 2026 · Proposed protocol, not executed results. Primary pain D-01 is owner-selected; numeric thresholds remain proposed for review before evaluation.

## Measures and precise meaning

| ID | Measure and denominator | Start / end or calculation | Use and limitation |
|---|---|---|---|
| KPI-01 | Active evidence-search and verification time per task | First lookup begins → representative confirms a supported answer or justified manual referral; active interaction periods only | Primary measure. Record pauses/system wait separately; do not call this total call handling time |
| KPI-02 | Supported outcome rate across all assigned tasks | Correct facts + applicable rule + permitted next step / all tasks, including failures and abstentions | Abstention is correct only where reference requires it; failing tasks remain in denominator |
| KPI-03 | Wrong-policy rate among tasks needing policy | Incorrect product/jurisdiction/audience/effective version / tasks needing policy | Correct citation format alone is insufficient |
| KPI-04 | Critical violation count / defined critical checks | Unauthorized disclosure/write, fabricated financial action, ignored correction, false ownership/execution | Zero observed critical violations required for release candidate; finite test set does not prove zero production risk |
| KPI-05 | Time to accepted contact completion | Task begins → accepted note and any justified next action saved | Secondary; includes reading, correction and retry. Exposes time merely shifted into verification |
| KPI-06 | Material note correction and omission rates | Corrected material claims / reviewed claims; omitted required facts / required facts | Count semantic errors, not harmless stylistic edits |
| KPI-07 | Unnecessary follow-up and duplicate-effect rates | Unneeded tasks / tasks where oracle requires no new work; extra effects / repeated-operation tests | More tasks is not a success metric |
| KPI-08 | Cost and latency per run and accepted task | Actual provider usage + dated price; elapsed response/tool duration; report p50/p95 with sample size | Missing usage = unknown, not zero. Don't price hypothetical runs as measured spend |
| KPI-09 | Lookup navigation effort | Search actions / task; distinct allowed source views / task | Secondary mechanism metric; fewer clicks is not sufficient if accuracy worsens |

The prototype does not yet have a credible real first-contact resolution, repeat-call, satisfaction or payroll measure. Those require an authorized operational pilot with definitions and longitudinal observations.

## Study arms and reference quality

Compare (A) manual source lookup in the demo, (B) unified search/guided steps/templates and (C) bounded assistance with the same available facts/rules. The existing real bank process is unknown; demo arm A is an authored comparator, not a measured production baseline. A1/A2 may share a deterministic workflow implementation but remain explicit in the option analysis.

Independent expected facts, applicable rule IDs, required clarification and permitted end states are authored before model outputs. A fluent answer with a wrong source fails. Search rankings may differ; access rights and available evidence must not. No future conversation events or evaluator-only answers enter runtime context.

## Human effort protocol

Proposed small formative study: six volunteer participants, 12 scored tasks each plus separate practice tasks; report experience level and whether they are actually banking representatives. If only the owner participates, label an N=1 self-test and avoid population claims.

Counterbalance condition order. Use matched scenario families with different facts; the same participant should not solve an identical record set twice. Distribute families across conditions/participants, prevent training/test family overlap, and document accessibility/language differences. Freeze cases and quality rubric before testing. The public SC examples are development material, not a blind holdout.

Capture lookup_start, source_open, policy_open, clarification_requested, evidence_review_start/end, answer_accepted_or_referred, draft_edit and commit_result with synthetic IDs and safe timestamps. System waiting and inactivity are identified by the task protocol and observer/self-timing log, not guessed from silent browser intervals.

Report all task outcomes, completion and failure counts. Present completion-time comparisons alongside quality and noncompletion; do not remove failed tasks to manufacture speed improvement. Use paired/matched summaries and uncertainty appropriate to the small sample. Record learning effects and deviations.

## Decision gates to freeze

- Proposed usefulness gate: median active lookup + verification time at least 15% lower than guided search/templates on matched tasks.
- Supported outcome quality must not deteriorate; all defined critical checks must pass. The existing agent plan's proposed ≥90% routine gate remains a separate technical gate, not evidence of business value.
- If review/correction offsets lookup savings, or wrong-policy/critical errors occur, do not claim a successful business pilot. Improve the design, retain the simpler baseline or defer AI for that branch.
- No firm latency/accessibility/recovery numeric target is invented here; BA-08 defines workload and measurable targets before implementation. Current proposed business threshold is D-04, still pending owner review.

## Value worksheet without invented inputs

| Variable | Meaning | Current status |
|---|---|---|
| V | Monthly eligible contacts for the two supported intents | Unknown |
| a | Proportion actually using assistance | Unknown |
| delta_m | Manual minus assisted minutes through accepted completion, including review/corrections | Unknown |
| R | Additional downstream rework hours not already included above | Unknown |
| C | Actually avoidable loaded labour cost/hour, if any | Unknown |
| M/H/O/T | Model, hosting, maintenance/operations and training/evaluation cost | Unknown |

Net capacity-hours = V × a × delta_m / 60 − R.
Potential avoided cost = net capacity-hours × C only when that spend can actually be avoided.
Net monetary benefit = avoided cost − M − H − O − T, with period and one-time/recurring costs stated.

Do not subtract same-contact corrections twice. Do not convert freed capacity into headcount or cash savings without an operating decision. Maintain low/base/high input scenarios only after their provenance is recorded.
