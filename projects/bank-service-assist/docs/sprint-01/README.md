# Sprint 1 bank service discovery

> **Historical discovery snapshot — 19–21 October 2026.** The pending setup and
> implementation statements below describe that stage. For the current project,
> use the [BA evidence guide](../README.md), [delivery status](../../../../docs/backlog/current-delivery.md)
> and [bank-core acceptance record](../../../../docs/uat/bank-core-closeout.md).

Review increment at this snapshot: [v0.2 stories, contracts and scope change](workflow-increment.md). D-09–D-16 record the reviewed transaction/feedback workflow. Eight detailed development specs and three incremental stories are prepared; old 22-example counts describe v0.1 only. See workflow validation for current counts.

Started **19 October 2026** at the owner's request. Forecast end: **1 November 2026**, subject to capacity and review. Status: **In progress — v0.2 workflow stories and tool contracts prepared; implementation pending**. This is actual portfolio work, not a claim of a staffed bank project.

## Business conclusion

The owner selected **finding customer information and handling rules** as the primary pain. The proposed product helps a representative assemble authorized facts and applicable procedure evidence, understand missing/conflicting information, and explain a supported next step. Contact notes are secondary; new follow-up is conditional.

The owner selected credit-card charge identification and apparent duplicate entries for the first job. Standalone existing-case progress enquiry remains a candidate; related-case lookup supports the selected job. Establish a usable manual/search baseline before adding bounded assistance. Do not equate contact closure, complaint resolution and case completion.

## Read the package

| Read order / story | Detailed deliverable | What to review |
|---|---|---|
| BA-01 | [Business background, pain and options](../../specs/BA-01/spec.md) | Problem plausibility, primary/secondary value and non-AI alternatives |
| BA-02 | [Stakeholders and decision rights](../../specs/BA-02/spec.md) | Who proposes, approves, executes and accepts; actual vs simulated feedback |
| BA-03 | [Current process](../../specs/BA-03/spec.md) | Two journeys, logical systems, handoffs, uncertainty and bottleneck hypotheses |
| BA-04 | [Target process](../../specs/BA-04/spec.md) | Manual/assisted paths, 16 draft rules, state distinctions and exception recovery |
| BA-05 | [Requirements and story map](../../specs/BA-05/spec.md) | 22 requirements with acceptance/verification IDs, release scope and deferrals |
| Cross-cutting | [22 acceptance examples](scenarios.md) | Correct next step, prohibited inference and data boundaries |
| Value | [Measurement contract](value-measurement.md) | Lookup/verification effort, quality and conditional cost benefit |
| Evidence | [Source register](evidence-register.md) | Owner statements, external precedents and unverified hypotheses |
| Decisions | [Decision/change log](decision-log.md) | D-01 accepted priority; other decisions and policy change dependency |
| Governance | [SDD agreement](sdd-working-agreement.md) | Ready/Done, traceability, review and release boundaries |
| Repository | [Public export preparation](public-export-plan.md) | One monorepo and portfolio-only export; GitHub URL still pending |
| Verification | [Review report](review-report.md) and [traceability](traceability.md) | Exact checks run vs owner acceptance and unexecuted application tests |

Each BA story has spec.md, design.md, tasks.md and acceptance.md. The requirements/scenario source is [requirements.json](requirements.json). This is a specification candidate; S02 formalizes rule tables, schemas, NFR thresholds and API contracts before code-ready acceptance.

## Actual progress and remaining work

| Item | Actual status | Remaining gate |
|---|---|---|
| BA-01–05 | Drafted; candidate for owner review | Owner reviews detailed scope, process and proposed business threshold |
| GOV-01–03 | Working agreement/roadmap/capacity documents prepared | Owner review; no fake stakeholder/team sign-off |
| GIT-01 | Export/PR preparation drafted | Intended GitHub URL, license/export review and actual repository setup |
| S01 | Started, not completed | Review/changes and remaining repository work; no velocity or hours claimed |
| Application / live models / deployment | Not started by this sprint activity | Follow accepted S02 contracts and later delivery cards |

[Trello board](https://trello.com/b/wtNhuN0q/ai-agent) carries the candidate specs inline on BA cards and progress on governance/S01 cards. Full local artifacts remain canonical until a public GitHub URL exists. No local file path is represented as an internet-accessible document.

## Next review

D-01 and D-09–D-16 record accepted priorities and simulated workflow decisions. Remaining review concerns detailed permissions/data/tool schemas, exception escalation/re-review rules, calendar fixtures and the proposed usefulness threshold. It is not necessary to provide confidential employer data. Corrections become a versioned CR and updated examples; do not treat silence as acceptance.

## Verified v0.2 publication

23 Trello cards saved and checked in the UI (20 updates, three new DEV-11/12/13 cards); 54 cards now registered across the board. See [sync evidence](workflow-trello-sync.json). Specification structure checks pass; all 49 detailed application acceptance examples remain unexecuted.
