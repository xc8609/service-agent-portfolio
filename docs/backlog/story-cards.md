# SDD story cards

Current runtime increment (20 October 2026): DEV-01/02/03, QA-01 and OPS-01 have a bounded read slice in [PR #1](https://github.com/xc8609/service-agent-portfolio/pull/1). [Executed evidence](../../projects/bank-service-assist/docs/sprint-02/implementation/lookup-evidence.md) and [Trello sync](s02-runtime-sync.json) supersede the older not-started wording for this slice only. GIT-01 now has a real PR and verified branch protection. Parent-story acceptance remains open.

Current metadata source: [S02 Sprint forecast](sprint-forecast.json) and trello-cards.json v3. Older sprint/estimate text below is historical where superseded. See [S02 contracts](../../projects/bank-service-assist/docs/sprint-02/README.md).

Current refinement: [bank workflow v0.2](../../projects/bank-service-assist/docs/sprint-01/workflow-increment.md). Detailed selected-story specs supersede older generic wording; new DEV-11/12/13 add explicit scope. No implementation is Done.

Planning baseline: 19 October 2026. S01 started on 19 October; BA-01–05 and GOV-01–03 are review candidates, while GIT-01 bootstrap is published with offline CI passed; contribution/release gates remain. Other stories remain Planned. No application implementation is claimed. Simulated team: two developers, BA/PO and QA; no staffing claim. [Delivery plan](../sdd-portfolio-delivery-plan.md) · [Sprints](sprints.md) · [Trello](https://trello.com/b/wtNhuN0q/ai-agent).

Effort is role-specific person-days, not elapsed duration or a promise. Ranges are judgement-based planning uncertainty, not measured historical velocity. Source: [card data](trello-cards.json).

<a id="gov-01"></a>

## GOV-01 — SDD working agreement, story readiness and traceability

Status: Review candidate — owner acceptance pending
Release: All | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1 person-days most likely (1–1.5 range): Dev 0, BA/PO 1, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: None

## User story
As the portfolio owner, I want each change to start from an agreed specification so that business intent remains traceable through code, tests and release evidence.

## Business value / role evidence
Demonstrate BA requirements lifecycle management and accountable delivery.

## BA analysis and specification
Maintain problem IDs, requirement IDs, rule IDs, story IDs, acceptance IDs and test/evidence links. Distinguish source facts, assumptions, owner decisions and simulated stakeholder decisions.

## Development / delivery tasks
- [ ] Store versioned specs under projects/bank-service-assist/specs/<story-id>/ with spec.md, design.md, tasks.md and acceptance.md.
- [ ] Implement only after the story is Ready: scope, rules, examples, data, dependencies and open decisions reviewed.
- [ ] Every PR references story/spec version, changed requirements and test evidence; update specs before changing accepted behavior.

## Acceptance criteria
- GOV-01-AC1: Given a proposed feature, when it enters development, then its business outcome, acceptance examples, dependencies and decision owner are recorded.
- GOV-01-AC2: Given an approved behavior changes, when implementation changes, then an impact record covers rules, API/data, UI, tests, migration and support.
- GOV-01-AC3: Given a story moves to Done, then executed evidence exists; a generated specification or passing mock alone is insufficient.

## Test and evidence plan
- GOV-01-T1 (planned): Audit one end-to-end requirement→story→spec→implementation→test→release chain.
- GOV-01-T2 (planned): Check that no critical TBD is silently treated as an approved requirement.

## Deliverables
Working agreement, reusable story/spec templates, traceability index, decision/change logs.

## Definition of Done
Owner reviews the working agreement. This is portfolio owner review, not employer approval.

## Boundaries
Workstream columns are planned work, not readiness. Move active work to In progress; one major slice per developer. Done needs executed evidence. Role allocations are simulated; never assign fictional people.

Canonical story: docs/backlog/story-cards.md#gov-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="gov-02"></a>

## GOV-02 — Release roadmap, architecture decisions and scope controls

Status: Review candidate — owner acceptance pending
Release: All | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1.5 person-days most likely (1–2.5 range): Dev 0.5, BA/PO 1, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: GOV-01

## User story
As the owner, I want staged releases with explicit gates so that a complete bank case is delivered before adding voice and retail.

## Business value / role evidence
Show prioritization, option analysis and delivery planning without claiming production readiness.

## BA analysis and specification
Release M0 = reviewed business/spec foundation; B0 = working manual bank workflow; B1 = bounded assistant with comparative evaluation and deployable demo; B2 = real test-phone handoff; R1 = retail clienteling. June 2027 remains a target, not a commitment.

## Development / delivery tasks
- [ ] Proposed stack: React/TypeScript/Vite frontend; Python 3.12/FastAPI/Pydantic backend; PostgreSQL with migrations; Docker Compose; GitHub Actions; DuckDB/SQL and Tableau for evidence.
- [ ] Keep business authorization, policy decisions and persistence independent of the model runtime. Select runtime/provider versions in DEV-09 spike.
- [ ] Use a local deterministic mode and a live-model mode. Start one-host deployment; defer Kubernetes, multi-cloud and fine-tuning.

## Acceptance criteria
- GOV-02-AC1: Given B0, then both selected bank workflows work without an LLM.
- GOV-02-AC2: Given a release request, then its dependencies and evidence gate are satisfied or it remains a candidate.
- GOV-02-AC3: Given scope growth, then priority and effort impacts are recorded before adding a delivery promise.

## Test and evidence plan
- GOV-02-T1 (planned): Review critical path BA→manual flow→assistant→evaluation→deployment.
- GOV-02-T2 (planned): Check later voice/retail work does not bypass bank acceptance.

## Deliverables
Release map, architecture ADR, dependency graph, capacity assumptions and scope-change log.

## Definition of Done
Roadmap reviewed; no future card marked implemented.

## Boundaries
Role-based person-day estimates replace earlier solo-hour sketches. Split slices above five developer-days at refinement; avoid counting unit tests and documentation again in QA effort.

Canonical story: docs/backlog/story-cards.md#gov-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-01"></a>

## BA-01 — Define the service problem, value hypothesis and alternatives

Status: Review candidate — owner acceptance pending
Release: M0 | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1 person-days most likely (1–1.5 range): Dev 0, BA/PO 1, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: GOV-01

## User story
As a service operations sponsor, I want a clear problem statement and measurable value hypothesis so that we can decide whether agent assistance is worth building.

## Business value / role evidence
Connect the owner's call-centre desktop experience to reduced information search and after-contact work.

## BA analysis and specification
Define customer/representative problems, frequency assumptions, affected decisions and evidence gaps. Separate contact, complaint, dispute, case and follow-up. Compare manual process, improved search/templates, workflow automation and a bounded agent.

## Development / delivery tasks
- [ ] Map available event instrumentation to search time, accepted note completion, correction effort and handoff quality.
- [ ] Create an assumptions table with variable, source/status, range, owner and review date.
- [ ] Avoid promising savings from CFPB counts or synthetic outcomes.

## Acceptance criteria
- BA-01-AC1: Given a problem claim, then it is tagged observed, self-reported, external evidence or assumption.
- BA-01-AC2: Given an AI proposal, then a non-AI option is evaluated against the same quality and effort criteria.
- BA-01-AC3: Given a financial projection, then volume, adoption, saved minutes, rework and operating cost remain visible assumptions.

## Test and evidence plan
- BA-01-T1 (planned): Review whether benefits can be measured with available data.
- BA-01-T2 (planned): Reject metrics that merely reward closing contacts or hiding unresolved work.

## Deliverables
One-page business brief, options matrix, benefit hypothesis, assumption and question log.

## Definition of Done
Owner selects initial value hypothesis and records unresolved evidence gaps.

## Boundaries
Two intents: possible duplicate card charge and existing-case status. No actual bank sponsor, approved business case or measured savings is claimed.

Canonical story: docs/backlog/story-cards.md#ba-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-02"></a>

## BA-02 — Stakeholders, personas, decision rights and elicitation plan

Status: Review candidate — owner acceptance pending
Release: M0 | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 0.5 person-days most likely (0.5–1 range): Dev 0, BA/PO 0.5, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-01

## User story
As a BA, I want clear stakeholder responsibilities and elicitation questions so that requirements and approvals have identifiable owners.

## Business value / role evidence
Demonstrate facilitation, stakeholder analysis and governance.

## BA analysis and specification
Define simulated customer, representative, supervisor, specialist, operations owner, security/privacy, QA and engineering roles. Specify who may propose, approve, execute, accept business outcomes and authorize release.

## Development / delivery tasks
- [ ] Translate role decisions into an initial permission matrix for customer data, notes, follow-ups and policy visibility.
- [ ] Prepare interview/workshop agendas and scenario walk-through questions.
- [ ] Record owner review separately from hypothetical stakeholder answers; do not fabricate interviews.

## Acceptance criteria
- BA-02-AC1: Given an operation, then a responsible role and approval boundary are defined.
- BA-02-AC2: Given conflicting stakeholder needs, then the decision owner and rationale are recorded.
- BA-02-AC3: Given an elicitation record, then participant type and evidence status distinguish real feedback from authored simulation.

## Test and evidence plan
- BA-02-T1 (planned): Walk through unauthorized access and disputed approval responsibilities.
- BA-02-T2 (planned): Review coverage of operations, support and customer viewpoints.

## Deliverables
Stakeholder map, personas, RACI/decision matrix, elicitation guide and decision log.

## Definition of Done
Responsibilities reviewed and permission questions assigned; unheld workshops remain planned.

## Boundaries
No real bank stakeholder endorsement or interviews invented.

Canonical story: docs/backlog/story-cards.md#ba-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-03"></a>

## BA-03 — Model the current process and locate service failure points

Status: Review candidate — owner acceptance pending
Release: M0 | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1.5 person-days most likely (1–2.5 range): Dev 0.5, BA/PO 1, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-01, BA-02

## User story
As a BA, I want a current-state service process so that proposed automation addresses identifiable delays and errors.

## Business value / role evidence
Show process analysis grounded in the owner's customer-service system experience.

## BA analysis and specification
Model inbound contact, identity verification, customer/account lookup, clarification, policy lookup, resolution/explanation, notes, escalation and closure. Record systems, handoffs, information needs and known/assumed pain points.

## Development / delivery tasks
- [ ] Produce a BPMN or swimlane source that can be versioned.
- [ ] Define an event dictionary for start/end timestamps and distinguish waiting time from active handling.
- [ ] Document representative research, not a claimed deployed-bank process.

## Acceptance criteria
- BA-03-AC1: Given either bank intent, then the diagram includes entry, roles, decision points, exceptions and outcomes.
- BA-03-AC2: Given a proposed bottleneck, then its evidence status and needed measurement are attached.
- BA-03-AC3: Given an unresolved contact, then the process shows ownership of next work instead of marking it resolved.

## Test and evidence plan
- BA-03-T1 (planned): Walk both intents and identity failure through the diagram.
- BA-03-T2 (planned): Check no elapsed-time KPI is inferred from data without the required timestamps.

## Deliverables
As-is swimlane, pain-point register, event dictionary and measurement gaps.

## Definition of Done
Owner reviews plausibility and records corrections.

## Boundaries
No invented handling-time baseline. Published complaint narratives do not establish call-centre timings.

Canonical story: docs/backlog/story-cards.md#ba-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-04"></a>

## BA-04 — Design the future service journey and exception paths

Status: Review candidate — owner acceptance pending
Release: M0 | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1.5 person-days most likely (1–2.5 range): Dev 0.5, BA/PO 1, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-03

## User story
As a representative, I want assistance embedded in my workflow so that I can verify facts, resolve simple enquiries and retain control over follow-up actions.

## Business value / role evidence
Turn the business problem into an operationally usable service design.

## BA analysis and specification
Map manual and assisted lanes. Define immediate explanation, clarification, specialist review and handoff outcomes. Separate assistant draft, human-edited note, approved proposal and committed record.

## Development / delivery tasks
- [ ] Draw low-fidelity workspace screens: contact/history, facts/policy, draft/next action.
- [ ] Specify loading, no-result, conflicting-record, expired-policy and model-failure states.
- [ ] Define customer correction and interrupted-run behavior before UI implementation.

## Acceptance criteria
- BA-04-AC1: Given no model access, then the representative can complete the manual workflow.
- BA-04-AC2: Given unsupported evidence, then the interface asks for clarification or manual review without inventing a result.
- BA-04-AC3: Given a customer correction, then affected suggestions are invalidated and the new context is visible.

## Test and evidence plan
- BA-04-T1 (planned): Scenario walkthrough: pending/posted, missing case, policy gap and human request.
- BA-04-T2 (planned): Review keyboard order and meaningful error messages on the wireframe.

## Deliverables
To-be process, journey map, annotated wireframes, exception catalogue and service boundary.

## Definition of Done
Owner confirms the first vertical slice and exception handling.

## Boundaries
No automatic refund, credit decision, card cancellation or unrestricted account change.

Canonical story: docs/backlog/story-cards.md#ba-04
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-05"></a>

## BA-05 — Story map, scope baseline and requirement prioritization

Status: Review candidate — owner acceptance pending
Release: M0 | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 0.5 person-days most likely (0.5–1 range): Dev 0, BA/PO 0.5, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-04

## User story
As the product owner, I want a prioritized story map so that each release delivers a usable outcome rather than disconnected technical features.

## Business value / role evidence
Demonstrate backlog refinement and scope negotiation.

## BA analysis and specification
Map activity→user task→story→release. Assign Must/Should/Could with rationale. Connect DEV-02 through DEV-08 to B01–B08 in the existing plan. Keep voice and retail separate release scopes.

## Development / delivery tasks
- [ ] Identify minimum end-to-end manual slice before infrastructure embellishments.
- [ ] Record dependencies and split stories above 16 h into independently verifiable increments before development.
- [ ] Define what is deferred when a dependency, provider or dataset is unavailable.

## Acceptance criteria
- BA-05-AC1: Given each Must story, then a measurable outcome and acceptance owner exist.
- BA-05-AC2: Given an omitted feature, then the consequence and workaround are recorded.
- BA-05-AC3: Given data-download failure, then synthetic labelled scenarios enable manual development without pretending the download succeeded.

## Test and evidence plan
- BA-05-T1 (planned): Check story coverage against both journeys and all critical exceptions.
- BA-05-T2 (planned): Check no infrastructure-only task is represented as a completed user outcome.

## Deliverables
Story map, prioritized scope baseline, dependency register and deferred list.

## Definition of Done
Owner reviews Must scope and sequencing; future estimates remain provisional.

## Boundaries
Preserve existing CFPB analysis; BANKING77 and τ-bench are optional evidence dependencies, not prerequisites for every feature.

Canonical story: docs/backlog/story-cards.md#ba-05
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="ba-06"></a>

## BA-06 — Business rules, decision tables and case state model

Status: Planned — not Ready
Release: M0 | Priority: P0 | Forecast sprint: S02
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 3.5 person-days most likely (2.5–5.5 range): Dev 1, BA/PO 2, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-04, BA-05

## User story
As a representative, I want explicit rules and valid state transitions so that the same evidence leads to consistent handling.

## Business value / role evidence
Demonstrate detailed analysis of banking exceptions and decision logic.

## BA analysis and specification
Version rules BR-01 authorized scope; BR-02 two equal charges do not prove duplication; BR-03 missing facts remain unknown; BR-04 purchase denial changes handling; BR-05 supported current policy; BR-06 approved/fresh writes; BR-07 no duplicate operation; BR-08 unresolved work retains ownership.

## Development / delivery tasks
- [ ] Specify contact and case states separately, with actor, precondition, transition and audit event.
- [ ] Create decision tables for posted/pending charges, unknown/conflicting case, expired policy and failed transfer.
- [ ] Attach synthetic examples and source references; identify invented parameters and unsupported real-bank assumptions.

## Acceptance criteria
- BA-06-AC1: Given the same facts and policy version, then the permitted action set is deterministic.
- BA-06-AC2: Given an invalid transition or stale approval, then no business state changes.
- BA-06-AC3: Given several valid outcomes, then acceptance allows them instead of requiring one exact model wording.

## Test and evidence plan
- BA-06-T1 (planned): Boundary and contradiction review of every decision table.
- BA-06-T2 (planned): Independent negative examples for unauthorized action, missing policy and later purchase denial.

## Deliverables
Business-rule catalogue, state diagrams, decision tables, ten reviewed seed scenarios.

## Definition of Done
Every Must rule has an example, counterexample and responsible decision role.

## Boundaries
Do not copy τ-bench's static recovery-bypass mechanism or treat its fictional rules as Canadian law.

Canonical story: docs/backlog/story-cards.md#ba-06
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ba-07"></a>

## BA-07 — Data contracts, provenance, quality and privacy requirements

Status: Planned — not Ready
Release: M0 | Priority: P0 | Forecast sprint: S02
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 3 person-days most likely (2.5–4.5 range): Dev 1, BA/PO 1.5, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-06

## User story
As a technical BA, I want source-to-target contracts so that every displayed fact has a known meaning, origin and permitted use.

## Business value / role evidence
Connect data analysis to operational APIs and evidence quality.

## BA analysis and specification
Model customer/account/transaction, contact/turn, case/event, policy/version, proposal/approval, audit/outbox. Specify identifiers, null meaning, currency units, timestamps, ownership, lifecycle and retention.

## Development / delivery tasks
- [ ] Create ERD and dictionary; define API examples and invalid payloads.
- [ ] Separate real CFPB, published BANKING77 text, benchmark simulations, authored fixtures and measured application events.
- [ ] Define manifests, schema checks, duplicate grouping and train/test isolation; record downloads only when they actually occur.

## Acceptance criteria
- BA-07-AC1: Given any entity, then primary/foreign keys, data types, source and null semantics are specified.
- BA-07-AC2: Given a synthetic case inspired by public text, then it remains explicitly synthetic and unlinked to a real customer ledger.
- BA-07-AC3: Given logs or public demo data, then raw credentials and private source records are excluded.

## Test and evidence plan
- BA-07-T1 (planned): Reconcile sample account/transaction/case links and chronology.
- BA-07-T2 (planned): Check held-out answers, future events and private fields cannot enter agent-visible inputs.

## Deliverables
ERD, dictionary, source-to-target map, source register, retention/logging rules and fixture contract.

## Definition of Done
Ten seed cases can be represented without ambiguous or fabricated evidence.

## Boundaries
No real bank ledger, call recordings or measured handling-time dataset is currently available.

Canonical story: docs/backlog/story-cards.md#ba-07
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ba-08"></a>

## BA-08 — Nonfunctional requirements and measurable release thresholds

Status: Planned — not Ready
Release: M0 | Priority: P0 | Forecast sprint: S02
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 1.5 person-days most likely (1–2.5 range): Dev 0.5, BA/PO 0.5, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-06, BA-07

## User story
As an operations owner, I want measurable reliability and usability requirements so that release decisions are based on evidence.

## Business value / role evidence
Show technical BA capability beyond functional user stories.

## BA analysis and specification
Define security, access, accessibility, performance, recoverability, observability, retention and cost constraints. Record target, measurement setup, owner and whether proposed or ratified.

## Development / delivery tasks
- [ ] Specify bounded run/tool timeouts, maximum turns, concurrency isolation, cancellation and manual fallback.
- [ ] Define no cross-customer disclosure, no unapproved mutation and idempotent retry as critical requirements.
- [ ] Propose 90% routine scenario success and all critical cases passing for the portfolio suite; freeze before evaluation. Ratify latency/cost budgets through a measured spike rather than inventing production SLAs.

## Acceptance criteria
- BA-08-AC1: Given an NFR, then its metric, workload/environment and pass/fail rule are testable.
- BA-08-AC2: Given a provider timeout, then saved work remains and manual handling is available.
- BA-08-AC3: Given missing cost telemetry, then cost is unknown, not zero.

## Test and evidence plan
- BA-08-T1 (planned): Map every critical NFR to an automated or witnessed test.
- BA-08-T2 (planned): Review finite-test limits and avoid production reliability claims.

## Deliverables
NFR catalogue, threat/abuse cases, workload definition and proposed threshold register.

## Definition of Done
Critical thresholds have tests and owners; unresolved noncritical targets are explicitly tracked.

## Boundaries
A small hosted demo is not high availability or bank compliance certification.

Canonical story: docs/backlog/story-cards.md#ba-08
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ba-09"></a>

## BA-09 — Baseline specifications, API contracts and change impact review

Status: Planned — not Ready
Release: M0 | Priority: P0 | Forecast sprint: S02
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 2.5 person-days most likely (2–4 range): Dev 1, BA/PO 1, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-05, BA-06, BA-07, BA-08

## User story
As a developer and tester, I want implementation-ready specifications so that I can build and verify the same intended behavior.

## Business value / role evidence
Make spec-driven development concrete rather than use SDD as a label.

## BA analysis and specification
For each Ready story record user need, scope/non-goals, process/rules, data/API/UI behavior, exceptions, Given/When/Then criteria and unresolved decisions. Owner review is recorded with version/date.

## Development / delivery tasks
- [ ] Author first specs for DEV-02/03/04/06; include request/response/error examples and optimistic concurrency contract.
- [ ] Link each acceptance ID to a planned test and later evidence path.
- [ ] Create change template: reason, affected requirements, migration, test impact, rollout/rollback, decision and version. An AI-generated draft must be reviewed before baseline.

## Acceptance criteria
- BA-09-AC1: Given a developer receives a Ready story, then mandatory behavior has no unresolved contradiction or hidden TBD.
- BA-09-AC2: Given a spec changes, then its implementation tasks and affected tests are updated together.
- BA-09-AC3: Given UAT evidence, then it identifies the exact specification and application version tested.

## Test and evidence plan
- BA-09-T1 (planned): Three-amigos style owner/engineering/test perspective walkthrough; name actual participants honestly.
- BA-09-T2 (planned): Trace one normal and one exception path end to end before development.

## Deliverables
Baselined first-story specs, OpenAPI draft, traceability matrix and change record template.

## Definition of Done
Owner reviews the first slice; this card plans future specs and does not claim they already exist.

## Boundaries
Specs are versioned in Git; Trello tracks status, summaries, dependencies and evidence links.

Canonical story: docs/backlog/story-cards.md#ba-09
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-01"></a>

## DEV-01 — Create the application skeleton and deterministic demo environment

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0 | Priority: P0 | Forecast sprint: S02
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3.75 person-days most likely (3–6 range): Dev 3, BA/PO 0.25, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-07, BA-08, BA-09

## User story
As a contributor, I want a repeatable local environment so that I can develop and review the manual service workflow without a model key.

## Business value / role evidence
Provide reproducible engineering evidence while keeping domain decisions visible.

## BA analysis and specification
Confirm component responsibilities, demo boundaries and configuration ownership. Reference data/NFR contracts rather than inventing fields in code.

## Development / delivery tasks
- [ ] Create React/TypeScript UI, FastAPI service, PostgreSQL migration setup and health/readiness endpoints.
- [ ] Add isolated synthetic seed/reset command, configuration validation and safe .env.example.
- [ ] Keep Python 3.9 evaluation modules separate from Python 3.12 application dependencies; lock versions after compatibility checks.

## Acceptance criteria
- DEV-01-AC1: Given a clean supported environment, when documented setup runs, then UI/API/database start and a labelled synthetic scenario is available.
- DEV-01-AC2: Given no model key, then manual demo works.
- DEV-01-AC3: Given invalid configuration or unavailable database, then readiness fails clearly without exposing secrets.

## Test and evidence plan
- DEV-01-T1 (planned): Fresh setup smoke test; migration applied to empty database.
- DEV-01-T2 (planned): Reset affects only labelled demo data; production-like configuration refuses destructive reset.

## Deliverables
Runnable skeleton, migrations, seed tooling, environment guide and architecture ADR.

## Definition of Done
A second clean run reproduces setup; evidence identifies versions and limitations.

## Boundaries
No business story marked complete just because services start.

Canonical story: docs/backlog/story-cards.md#dev-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-02"></a>

## DEV-02 — Open an authorized customer contact and inspect account context

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0 | Priority: P0 | Forecast sprint: S03
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3.75 person-days most likely (3–6 range): Dev 3, BA/PO 0.25, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-01, BA-09

## User story
As a representative, I want to open a customer contact within my authorized scope so that I can inspect relevant information without exposing other customers.

## Business value / role evidence
Reflect the owner's customer lookup and call-centre desktop experience.

## BA analysis and specification
Trace B01/BR-01. Specify minimum visible fields, verification status, missing-customer behavior and audit events.

## Development / delivery tasks
- [ ] Implement contact creation/detail and authorized account endpoints using server-derived scope.
- [ ] Build contact header, account selector and clear loading/empty/error states.
- [ ] Separate labelled local fixture identity from hosted OIDC/session integration; never trust prompt-supplied roles or IDs.

## Acceptance criteria
- DEV-02-AC1: Given an authorized session, then only permitted customer/account fields are returned.
- DEV-02-AC2: Given another customer's ID, then access is denied without disclosing whether that account exists.
- DEV-02-AC3: Given refresh/restart, then the saved contact remains with correct ownership.

## Test and evidence plan
- DEV-02-T1 (planned): API object-level authorization across two customers and two roles.
- DEV-02-T2 (planned): UI tests for account selection, denied access and missing records; persistence integration test.

## Deliverables
Endpoints, UI, permission tests, contact schema and requirement/test links.

## Definition of Done
BR-01 tests pass and UI failure states are reviewed.

## Boundaries
No real bank connection or customer authentication claim for fixture mode.

Canonical story: docs/backlog/story-cards.md#dev-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-03"></a>

## DEV-03 — Investigate a possible duplicate charge from transaction evidence

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0 | Priority: P0 | Forecast sprint: S03
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 4 person-days most likely (3–6 range): Dev 3, BA/PO 0.5, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-02, BA-06

## User story
As a representative, I want to compare the customer's selected transactions so that I can clarify a suspected duplicate without assuming two equal amounts prove an error.

## Business value / role evidence
Make the first banking outcome demonstrable and testable.

## BA analysis and specification
Trace B02/BR-02/BR-03/BR-04. Define purchase context, ambiguity, pending/posted meaning and when manual review is needed.

## Development / delivery tasks
- [ ] Implement authorized transaction list/detail with stable IDs, pagination, status, currency and source time.
- [ ] Build side-by-side selection and a structured clarification checklist.
- [ ] Preserve customer allegation separately from ledger facts; support revised purchase-denial context.

## Acceptance criteria
- DEV-03-AC1: Given one pending and one posted record, then the interface distinguishes them without promising a refund or release date.
- DEV-03-AC2: Given several equal-amount records, then the representative must identify the relevant transactions rather than select all.
- DEV-03-AC3: Given a later purchase denial, then the handling path changes and prior duplicate assumptions are visibly superseded.

## Test and evidence plan
- DEV-03-T1 (planned): Decision-table tests for status combinations, different currencies, missing records and changing facts.
- DEV-03-T2 (planned): API/UI test ensuring displayed amounts reconcile to stored minor units.

## Deliverables
Transaction investigation screen, API contracts, decision examples and automated evidence.

## Definition of Done
Normal and exception scenarios complete manually with no LLM.

## Boundaries
No fraud determination, chargeback submission or money movement.

Canonical story: docs/backlog/story-cards.md#dev-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-04"></a>

## DEV-04 — Explain the recorded status and next step of an existing case

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0 | Priority: P0 | Forecast sprint: S03
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 2.75 person-days most likely (2–4.5 range): Dev 2, BA/PO 0.25, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-02, BA-06

## User story
As a representative, I want a trustworthy case timeline so that I can explain current status and outstanding work without inventing progress or dates.

## Business value / role evidence
Support actual follow-up only when an existing case requires it.

## BA analysis and specification
Trace B04/BR-03/BR-08. Define case state, next-action owner, known ETA versus unknown date, and conflict resolution.

## Development / delivery tasks
- [ ] Implement scoped case/timeline endpoints and ordered event history.
- [ ] Render status source timestamp, pending requirement and ownership; distinguish no case from unavailable data.
- [ ] Handle conflicting events explicitly; don't silently pick a convenient narrative.

## Acceptance criteria
- DEV-04-AC1: Given a case awaiting documents, then the recorded request and owner are shown.
- DEV-04-AC2: Given no recorded ETA, then the answer says it is unknown.
- DEV-04-AC3: Given missing/unauthorized case or conflicting records, then a typed response guides manual handling without fabricated closure.

## Test and evidence plan
- DEV-04-T1 (planned): Event ordering and as-of-time tests, unknown/conflicting case fixtures.
- DEV-04-T2 (planned): Cross-customer access and restart persistence tests.

## Deliverables
Case timeline UI/API, state tests and UAT examples.

## Definition of Done
Manual status enquiry succeeds and all exception results are reviewable.

## Boundaries
Merchant refund status is a separate concept and must not be inferred from a bank case label.

Canonical story: docs/backlog/story-cards.md#dev-04
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-05"></a>

## DEV-05 — Retrieve applicable policy with citations and version controls

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0/B1 | Priority: P0 | Forecast sprint: S03
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 5.25 person-days most likely (4–8 range): Dev 4, BA/PO 0.25, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-01, BA-06, BA-07

## User story
As a representative, I want relevant current policy evidence so that my explanation and next action follow the correct rules.

## Business value / role evidence
Improve search while retaining a non-AI baseline.

## BA analysis and specification
Trace B03/BR-05. Specify jurisdiction, product, audience, effective period, version and evidence passage.

## Development / delivery tasks
- [ ] Load a small versioned fictional-bank policy collection with source attribution and authored-rule flags.
- [ ] Implement metadata filtering before keyword/BM25 retrieval; provide policy-detail citations.
- [ ] Add retrieval adapter for later embeddings only if measured need justifies it; restrict the agent to business retrieval tools.

## Acceptance criteria
- DEV-05-AC1: Given a current internal policy, then authorized staff can inspect its exact supporting passage.
- DEV-05-AC2: Given expired/wrong-jurisdiction policy, then it cannot ground an answer.
- DEV-05-AC3: Given no applicable source, then return a policy gap instead of a plausible invented rule.

## Test and evidence plan
- DEV-05-T1 (planned): Known-question retrieval set and metadata exclusion cases.
- DEV-05-T2 (planned): Citation ID/version integrity; customer-facing mode cannot expose internal-only content.

## Deliverables
Policy schema, loader/search/detail service, source register and retrieval baseline.

## Definition of Done
Source support and exclusion tests pass; invented policies remain labelled.

## Boundaries
No general web browsing or unrestricted shell/SQL access for the service agent.

Canonical story: docs/backlog/story-cards.md#dev-05
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-06"></a>

## DEV-06 — Review, edit and commit a contact note safely

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0 | Priority: P0 | Forecast sprint: S04
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 6.5 person-days most likely (5–10 range): Dev 5, BA/PO 0.5, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-02, DEV-03, DEV-04, BA-09

## User story
As a representative, I want to edit and approve a supported note so that the saved service record is accurate and remains under my control.

## Business value / role evidence
Target after-contact documentation effort without reducing record quality.

## BA analysis and specification
Trace B06/BR-06/BR-07. Define draft/edit/approved/committed states and facts versus allegations.

## Development / delivery tasks
- [ ] Implement versioned draft and approval endpoints with actor, source versions and operation key.
- [ ] Commit note and audit/outbox event atomically; preserve edits on stale-version conflicts.
- [ ] Build editable note preview with clear unsaved/committed status; deterministic manual template first.

## Acceptance criteria
- DEV-06-AC1: Given an edited draft, when approved, then exactly the reviewed version is saved with actor/time.
- DEV-06-AC2: Given source data changes after drafting, then commit fails with refresh guidance and edits are preserved.
- DEV-06-AC3: Given the same operation is submitted twice, then one note is stored and both responses identify that result.

## Test and evidence plan
- DEV-06-T1 (planned): Integration tests for duplicate request, concurrent edits and transaction rollback.
- DEV-06-T2 (planned): UI tests for unsaved changes, failed save and retry; no model-only unit test substitutes for persistence.

## Deliverables
Note editor/API, audit schema, concurrency/idempotency tests and traceability.

## Definition of Done
Persisted state and audit evidence match the approved content.

## Boundaries
A drafted statement that work was completed never counts as proof of execution.

Canonical story: docs/backlog/story-cards.md#dev-06
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-07"></a>

## DEV-07 — Create justified follow-up work with ownership and reliable delivery

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B0/B1 | Priority: P0 | Forecast sprint: S04
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 5.5 person-days most likely (4–8.5 range): Dev 4, BA/PO 0.5, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-06, BA-06

## User story
As a representative, I want to create follow-up only when needed so that unresolved work has an owner and resolved enquiries do not generate unnecessary cases.

## Business value / role evidence
Address the owner's concern that many calls resolve immediately.

## BA analysis and specification
Trace B07/BR-07/BR-08. Define follow-up reason, destination, owner, pending facts, requested action and status.

## Development / delivery tasks
- [ ] Add a reviewed follow-up proposal/commit flow and a durable outbox worker.
- [ ] Track pending, delivered, failed and uncertain outcomes separately; retry with operation keys and reconciliation.
- [ ] Provide manual retry/assignment visibility without sending external customer messages in the initial demo.

## Acceptance criteria
- DEV-07-AC1: Given an explanation resolves the enquiry, then no follow-up is required.
- DEV-07-AC2: Given an unresolved approved follow-up, then it has an owner, reason and linked contact.
- DEV-07-AC3: Given worker restart or duplicate delivery, then the business operation is not duplicated; unknown external outcome remains unknown.

## Test and evidence plan
- DEV-07-T1 (planned): Worker crash/reclaim, retry and duplicate-event integration tests.
- DEV-07-T2 (planned): UAT for immediate resolution versus specialist follow-up and failed delivery.

## Deliverables
Follow-up workflow, outbox/worker implementation, failure runbook and tests.

## Definition of Done
Unresolved work remains visible until confirmed handled; queue state is not described as customer resolution.

## Boundaries
Mock recipient delivery is labelled simulated. External integrations need separate acceptance.

Canonical story: docs/backlog/story-cards.md#dev-07
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-08"></a>

## DEV-08 — Add a bounded assistant that proposes evidence-backed next steps

22 October increment: [scoped facts and staff question](../../projects/bank-service-assist/specs/DEV-08/core-context.md), implementing the simplified core demonstration without new orchestration services.


Status: Merged to main (offline bounded runtime) — real-model route unqualified; owner UAT pending
Release: B1 | Priority: P0 | Forecast sprint: S05
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 9.5 person-days most likely (7–14.5 range): Dev 7, BA/PO 1, QA 1.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-03, DEV-04, DEV-05, DEV-06, DEV-07, DEV-09

## User story
As a representative, I want the assistant to gather permitted evidence, ask missing questions and draft a note so that I spend less effort assembling information.

## Business value / role evidence
Deliver the agent use case on top of the same manual workflow.

## BA analysis and specification
Trace B03/B05/B06/B08. Specify supported intents, answer components, clarification triggers, refusal/fallback and human control.

## Development / delivery tasks
- [ ] Implement run state, validated read/proposal tools, turn provenance, bounded tool budget and cancellation.
- [ ] Stream clear progress; distinguish model text, tool facts, proposed action and committed result.
- [ ] Invalidate stale proposals after new facts; preserve manual workflow after model failure; no model-triggered direct commit endpoint.

## Acceptance criteria
- DEV-08-AC1: Given missing transaction context, then the agent asks for clarification before proposing a conclusion.
- DEV-08-AC2: Given prompt injection in customer text, then permissions and allowed tools remain unchanged.
- DEV-08-AC3: Given timeout/cancellation or a later correction, then stale output cannot commit and the representative can continue manually.

## Test and evidence plan
- DEV-08-T1 (planned): Scenario tests for both intents and all ten seeds, including changing intent.
- DEV-08-T2 (planned): Assert tool authorization and final persisted effects independently of generated prose.

## Deliverables
Assistant orchestration/UI, versioned prompts/tool contracts, error traces and story acceptance evidence.

## Definition of Done
Critical behavior passes in deterministic tests before live model evaluation.

## Boundaries
This story does not prove superiority to search/templates; QA-02 and QA-03 decide that.

Canonical story: docs/backlog/story-cards.md#dev-08
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-09"></a>

## DEV-09 — Qualify model runtime and provider adapters with a bounded spike

Status: Merged to main (offline adapters, fingerprint-bound qualification gate) — API qualification deferred (D-27)
Release: B1 | Priority: P0 | Forecast sprint: S04
Role owner: Developer A / backend-platform (simulated team allocation, not actual staffing)
Estimate: 5.25 person-days most likely (4–8 range): Dev 4, BA/PO 0.25, QA 1; confidence low. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-07, BA-08, DEV-01

## User story
As an engineer, I want interchangeable qualified model providers so that business behavior is not tied to one vendor's SDK.

## Business value / role evidence
Demonstrate practical API integration and architectural trade-offs.

## BA analysis and specification
Define portability requirements and data boundary. Compare candidate OpenAI Agents SDK, direct adapters and other runtime options by actual required capabilities; record why one is selected.

## Development / delivery tasks
- [ ] Define normalized text/tool/usage/error/cancel events; keep authorization and persistence in application services.
- [ ] Qualify one OpenAI route and one Claude route when credentials/budget are available. Document DeepSeek/internal compatible endpoint gaps; do not claim untested compatibility.
- [ ] Add fake-provider fixtures for offline CI, endpoint allowlist, server-only credentials and no public fallback in internal-only mode.

## Acceptance criteria
- DEV-09-AC1: Given two qualified live routes, then the same business tool contracts work without changing domain code.
- DEV-09-AC2: Given unsupported schemas or streamed incomplete arguments, then no invalid tool executes.
- DEV-09-AC3: Given missing credentials, then the spike remains pending for live qualification and offline mode remains honest.

## Test and evidence plan
- DEV-09-T1 (planned): Single/dependent tool calls, malformed arguments, rate limit, timeout, cancellation and missing usage.
- DEV-09-T2 (planned): Boundary test for unapproved endpoint/fallback; record model/version/configuration and actual cost.

## Deliverables
ADR, capability matrix, locked dependencies, adapter contract tests and live spike report.

## Definition of Done
At least two live routes qualified for B1 release; untested routes labelled planned.

## Boundaries
No fine-tuning, local model hosting or additional paid deployment required by this spike alone.

Canonical story: docs/backlog/story-cards.md#dev-09
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="dev-10"></a>

## DEV-10 — Build operational event marts and a reconciled Tableau view

Status: Merged to main — automated evidence recorded; owner UAT pending
Release: B1 | Priority: P1 | Forecast sprint: S05
Role owner: Developer B / data, with BA (simulated team allocation, not actual staffing)
Estimate: 4.5 person-days most likely (3.5–7 range): Dev 3, BA/PO 1, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-06, DEV-07, DEV-08, BA-07

## User story
As an operations analyst, I want trustworthy workflow metrics so that I can inspect failures, corrections and handoffs without confusing model output with business results.

## Business value / role evidence
Connect the data analyst portfolio to the same service question.

## BA analysis and specification
Define numerator/denominator, grain, time window and exclusions for proposal acceptance, corrected notes, follow-up, failures, latency and measured handling effort.

## Development / delivery tasks
- [ ] Record run/contact/proposal/action IDs and authoritative timestamps without sensitive payloads.
- [ ] Build SQL marts and aggregate exports for Tableau; retain existing CFPB descriptive analysis separately.
- [ ] Add reconciliation totals and labelled synthetic/live-test segmentation. Report cost unavailable if usage is missing.

## Acceptance criteria
- DEV-10-AC1: Given the same source events, then SQL totals reconcile to exported Tableau data.
- DEV-10-AC2: Given a failed/abandoned run, then it is included in the appropriate denominator.
- DEV-10-AC3: Given no human effort study, then dashboard does not display measured time savings or real-bank ROI.

## Test and evidence plan
- DEV-10-T1 (planned): Fixture totals with duplicates, cancellations and late events.
- DEV-10-T2 (planned): Source-to-mart-to-dashboard reconciliation and metric definition review.

## Deliverables
Metric dictionary, SQL marts, reconciliation report, Tableau workbook and findings note.

## Definition of Done
Reviewed numbers match source events and simulation boundaries are visible.

## Boundaries
Dashboard creation and validation are future work, not completed by this plan.

Canonical story: docs/backlog/story-cards.md#dev-10
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="qa-01"></a>

## QA-01 — Implement layered verification and requirement-to-test coverage

Status: Merged to main — layered API/browser/offline CI in place
Release: B0/B1 | Priority: P0 | Forecast sprint: S02
Role owner: QA with BA/PO (simulated team allocation, not actual staffing)
Estimate: 3 person-days most likely (2.5–4.5 range): Dev 1, BA/PO 0.5, QA 1.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-09, DEV-01

## User story
As a tester, I want independent checks at the appropriate layer so that correct wording cannot hide invalid data access or execution.

## Business value / role evidence
Demonstrate a test strategy connected to business risk.

## BA analysis and specification
Create test IDs linked to each acceptance condition. Distinguish unit, API contract, database integration, UI, security, recovery, evaluation and UAT evidence.

## Development / delivery tasks
- [ ] Use pytest for pure rules/API tests, isolated PostgreSQL integration tests and Playwright for critical UI journeys.
- [ ] Implement fault cases: denied scope, invalid payload, stale version, duplicate request, worker crash, policy gap and provider failure.
- [ ] Make CI run meaningful fast checks on PRs; live-model, full data and deployment checks are separate explicitly triggered suites.

## Acceptance criteria
- QA-01-AC1: Given every Must acceptance condition, then a test method and expected result are linked.
- QA-01-AC2: Given a failing critical rule, then its release gate fails even if other tests pass.
- QA-01-AC3: Given a skipped suite, then the report states it was not executed and why.

## Test and evidence plan
- QA-01-T1 (planned): Verify test fixtures have independently stated expected states, not output copied from the implementation.
- QA-01-T2 (planned): Exercise one deliberately invalid transition to confirm the test catches it.

## Deliverables
Test strategy, traceability matrix, automated suites, defect severity/triage rules and evidence template.

## Definition of Done
Coverage is reviewed by behavior/risk, not only a percentage or test count.

## Boundaries
Passing unit tests does not validate real-data SQL, live providers or cloud deployment.

Canonical story: docs/backlog/story-cards.md#qa-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="qa-02"></a>

## QA-02 — Freeze agent evaluation and compare against simpler baselines

**22 October delivery override:** the owner delegated case decisions to Codex and requested a lightweight portfolio. Follow the [12+8 check plan](../../projects/bank-service-assist/evaluation/r2/portfolio-scope.md); independent holdout, four-packet owner review and the full R2-G01 protocol below are deferred, not passed. Keep historical evidence and implemented controls.

Status: Pilot executed (D-27) — 24 frozen cases, decision table vs three subscription-run models; API qualification and full 100-family evaluation pending — [pilot report](../../projects/bank-service-assist/evaluation/README.md). R2-S01–04 grading rules and [R2-A01/R2-G01 answer intent and candidate gates](../../projects/bank-service-assist/evaluation/r2/owner-review.md) accepted by the owner on 21 October 2026 (PR #24); independent corpus freeze, evaluation and model qualification remain pending.
Release: B1 | Priority: P0 | Forecast sprint: S05
Role owner: QA with BA/PO (simulated team allocation, not actual staffing)
Estimate: 4.5 person-days most likely (3.5–7 range): Dev 2, BA/PO 0.5, QA 2; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: BA-06, BA-08, DEV-08, QA-01

## User story
As a product owner, I want a fair comparison so that I can decide whether a tool-using agent adds value over manual templates and retrieval.

## Business value / role evidence
Show honest model evaluation and solution selection.

## BA analysis and specification
Define correctness as supported facts, valid action, permitted access and actual postconditions. Freeze rubric, thresholds and split before provider/prompt selection.

## Development / delivery tasks
- [x] Implement approved R2 gate arithmetic, local runtime evidence capture and private holdout preparation ([operator guide](../../projects/bank-service-assist/evaluation/r2/experiment-guide.md)); engineering tests do not qualify a model.
- [x] Prepare private authoring, four-batch answer review and explicit freeze workflow with declared human/Claude roles ([handoff](../../projects/bank-service-assist/evaluation/r2/holdout-workflow.md)); substantive independent cases and actual approval remain pending.
- [ ] Plan 100 bank scenario families: 60 development/40 held-out, plus 24 critical cases; group variants and duplicate text before splitting.
- [ ] Compare manual/templates, retrieval and bounded agent with the same information; compare providers after holding architecture constant.
- [ ] Repeat held-out runs three times where budget allows; publish actual denominators, failure types, variance, latency and cost. Keep upstream τ-bench results separate from adapted local UAT.

## Acceptance criteria
- QA-02-AC1: Given held-out cases, then prompts contain neither expected answers nor future user events.
- QA-02-AC2: Given a critical forbidden action, then that run fails regardless of prose or average score.
- QA-02-AC3: Given evaluation findings influence changes, then reused cases become regression evidence and fresh holdout is required for a new selection claim.

## Test and evidence plan
- QA-02-T1 (planned): Audit split leakage, scoring decisions and independent DB postconditions.
- QA-02-T2 (planned): Record all failures and unavailable measurements; no cherry-picked best run.

## Deliverables
Frozen scenario manifest, evaluator/rubric, baseline comparison, error analysis and go/narrow/no-go recommendation.

## Definition of Done
Owner-approved R2-G01 candidate gates are assessed only after complete experiment freeze and execution; limitations and negative results published. Business approval of thresholds alone does not complete QA-02.

## Boundaries
Finite synthetic success is not a real-bank failure rate or a savings measurement.

Canonical story: docs/backlog/story-cards.md#qa-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="qa-03"></a>

## QA-03 — Run business UAT, adoption review and an exploratory effort study

Status: Ready for owner — UAT pack prepared; execution pending
Release: B1 | Priority: P0 | Forecast sprint: S06
Role owner: QA with BA/PO (simulated team allocation, not actual staffing)
Estimate: 3.5 person-days most likely (2.5–5.5 range): Dev 0.5, BA/PO 1, QA 2; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-10, QA-02

## User story
As an operations owner, I want to verify complete working tasks and usability so that a technically passing assistant is useful to representatives.

## Business value / role evidence
Show BA solution evaluation, business acceptance and change readiness.

## BA analysis and specification
Author scripts with role, preconditions, steps, expected evidence, severity and acceptance decision. Cover both intents, manual fallback, corrections and handoff ownership. Record actual reviewers honestly.

## Development / delivery tasks
- [ ] Prepare versioned UAT build, reproducible fixtures and defect log.
- [ ] Where willing participants are available, counterbalance manual/assisted matched tasks and measure time through accepted completion including corrections.
- [ ] Use a small 3–5 participant pilot only to explore usability/protocol; collect feedback and record training/support gaps.

## Acceptance criteria
- QA-03-AC1: Given a UAT scenario, then expected outcome and test data are fixed before execution.
- QA-03-AC2: Given a critical defect, then release is blocked or scope narrowed with an explicit decision.
- QA-03-AC3: Given no independent participants or measured baseline, then publish owner walkthrough and unmeasured savings rather than inventing acceptance.

## Test and evidence plan
- QA-03-T1 (planned): Witness normal, exception and recovery journeys; link screenshots/logs without private data.
- QA-03-T2 (planned): Reconcile effort observations with quality scores; investigate faster but incorrect completion.

## Deliverables
UAT pack/results, defect disposition, adoption/training notes, benefit review and release recommendation.

## Definition of Done
Actual reviewer, build/spec version and decision are recorded; simulated stakeholder approval stays labelled.

## Boundaries
No claim of generalizable productivity uplift from a small convenience sample.

Canonical story: docs/backlog/story-cards.md#qa-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ops-01"></a>

## OPS-01 — Package the application and establish CI release artifacts

Status: Merged to main — container build, CI and local recovery in place
Release: B0/B1 | Priority: P0 | Forecast sprint: S02
Role owner: Developer A / backend-platform (simulated team allocation, not actual staffing)
Estimate: 2.5 person-days most likely (2–4 range): Dev 2, BA/PO 0, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: DEV-01, QA-01

## User story
As a maintainer, I want reproducible build artifacts so that a reviewed change can be tested and deployed consistently.

## Business value / role evidence
Demonstrate engineering completion beyond notebooks.

## BA analysis and specification
Define configuration ownership, environments, release evidence and source/data exclusions.

## Development / delivery tasks
- [ ] Build versioned frontend/API/worker images and Compose configuration with private database networking.
- [ ] Configure CI lint/type/fast tests and isolated integration checks; retain Python 3.9/3.12 pure evaluation coverage.
- [ ] Keep secrets server-side, provide validated .env.example, scan for accidental keys/data and record image/config versions.

## Acceptance criteria
- OPS-01-AC1: Given a clean checkout, then a documented build produces a runnable demo artifact.
- OPS-01-AC2: Given a failed required check, then no release candidate is promoted.
- OPS-01-AC3: Given frontend assets/logs/repository contents, then no provider key or raw bank dataset is exposed.

## Test and evidence plan
- OPS-01-T1 (planned): Clean build and no-key manual startup; configuration error checks.
- OPS-01-T2 (planned): Dependency lock validation and secret/data-exclusion inspection.

## Deliverables
Dockerfiles/Compose, CI workflow, environment guide, versioned build and test artifacts.

## Definition of Done
Local checks and actual cloud CI results are distinguished; only executed CI is claimed.

## Boundaries
No cloud resource purchase or public publication is performed by creating this plan.

Canonical story: docs/backlog/story-cards.md#ops-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ops-02"></a>

## OPS-02 — Deploy staging and verify authentication, migrations and recovery

Status: Planned — not Ready
Release: B1 | Priority: P0 | Forecast sprint: S06
Role owner: Developer A / backend-platform (simulated team allocation, not actual staffing)
Estimate: 6.75 person-days most likely (5–10.5 range): Dev 5, BA/PO 0.25, QA 1.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: OPS-01, DEV-06, DEV-07

## User story
As an operator, I want a recoverable staging environment so that a deployment failure does not lose accepted service records.

## Business value / role evidence
Show practical deployment and support capability.

## BA analysis and specification
Agree hosting budget, data boundary, access model, recovery targets and responsible operator before provisioning. Proposed initial platform is one Linux host; no HA claim.

## Development / delivery tasks
- [ ] Provision only after host/budget decision; deploy TLS reverse proxy, app/worker and private PostgreSQL with standard OIDC/session controls.
- [ ] Apply migrations to a copy, configure encrypted off-host backups and sanitized logs/metrics.
- [ ] Run restore and previous-image rollback drills; document schema backward compatibility and secret handling.

## Acceptance criteria
- OPS-02-AC1: Given an unauthenticated or unauthorized request, then private endpoints are inaccessible.
- OPS-02-AC2: Given a backup restore, then record counts and selected audit chains reconcile.
- OPS-02-AC3: Given rollback, then application/schema compatibility is verified and failed migrations have a documented recovery path.

## Test and evidence plan
- OPS-02-T1 (planned): TLS/auth/session scope, two concurrent customer sessions, readiness and worker restart.
- OPS-02-T2 (planned): Observed backup restore and rollback with timestamps and evidence.

## Deliverables
Staging URL/access instructions, deployment ADR, migration/backup/restore/rollback runbooks and drill report.

## Definition of Done
Actual staging smoke and recovery evidence exists; plans alone do not pass.

## Boundaries
Use synthetic records only; managed PostgreSQL/Supabase is an option after an ADR, not an extra mandatory platform.

Canonical story: docs/backlog/story-cards.md#ops-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="ops-03"></a>

## OPS-03 — Authorize the demo release and establish monitoring/support

Status: Planned — not Ready
Release: B1 | Priority: P0 | Forecast sprint: S06
Role owner: Developer A / backend-platform (simulated team allocation, not actual staffing)
Estimate: 2.5 person-days most likely (2–4 range): Dev 1, BA/PO 0.5, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: OPS-02, QA-02, QA-03

## User story
As the release owner, I want a controlled demo launch and support plan so that reviewers can use it and failures can be diagnosed.

## Business value / role evidence
Demonstrate operational readiness, release management and stakeholder communication.

## BA analysis and specification
Review UAT, critical defects, limitations, cost exposure, demo access and owner decision. Define training quick guide, support triage and known-issue communication.

## Development / delivery tasks
- [ ] Set per-run/global spend limits, rate limits, retention/reset controls and health alerts.
- [ ] Publish versioned release notes and known limitations; validate the chosen access/visibility before activation.
- [ ] Create runbooks for provider outage, failed jobs, database failure, exhausted budget and uncertain writes.

## Acceptance criteria
- OPS-03-AC1: Given unmet critical gates, then release stays a candidate or scope is narrowed.
- OPS-03-AC2: Given model outage/budget exhaustion, then the user sees a clear fallback and accepted records remain available.
- OPS-03-AC3: Given a reported incident, then a correlation ID leads to a redacted trace and recovery instruction.

## Test and evidence plan
- OPS-03-T1 (planned): Post-deployment smoke across both intents, manual fallback and access boundary.
- OPS-03-T2 (planned): Observe a controlled failure and recovery; confirm backup schedule and alert routing.

## Deliverables
Release checklist/decision, hosted demo if activated, runbooks, quick guide and known issues.

## Definition of Done
Owner records the actual release decision and evidence; public access and paid services require their own concrete execution decision.

## Boundaries
No real customers, production banking claim or fabricated uptime history.

Canonical story: docs/backlog/story-cards.md#ops-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="v-01"></a>

## V-01 — Specify the voice journey, customer authority and handoff contract

Status: Planned — not Ready
Release: B2 | Priority: P1 | Forecast sprint: S07
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3 person-days most likely (2.5–4.5 range): Dev 1, BA/PO 1.5, QA 0.5; confidence low. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: OPS-03

## User story
As a caller, I want a clear route from self-service to a person so that I can get help without losing context or being trapped in automation.

## Business value / role evidence
Extend the owner's telephone-enabled representative system experience.

## BA analysis and specification
Define disclosure, consent/recording choices, authentication boundaries, human request, ambiguity, disconnect and unavailable-human outcomes. Reassess customer-facing authority separately from staff assistance.

## Development / delivery tasks
- [ ] Specify states listening, processing, speaking, transferring, queued, connected, failed and ended.
- [ ] Define handoff payload: verified scope, customer intent, supported facts, attempted steps, unresolved questions and consent.
- [ ] Restrict voice tools to supported reads and permitted proposals; no static bypass codes or caller-ID-only authentication.

## Acceptance criteria
- V-01-AC1: Given an explicit human request, then the flow exits automation without repeated persuasion.
- V-01-AC2: Given a queued/failed transfer, then the system never claims a human is connected.
- V-01-AC3: Given no verified scope, then no private account detail is disclosed.

## Test and evidence plan
- V-01-T1 (planned): Walkthrough identity failure, mid-answer correction, no agent available and call drop.
- V-01-T2 (planned): Review recording retention and test-participant consent before collection.

## Deliverables
Voice service blueprint, permission matrix, state machine, handoff schema and voice UAT scripts.

## Definition of Done
Owner reviews channel-specific authority and failure routes before telephony work.

## Boundaries
Use test callers only; no real customer rollout.

Canonical story: docs/backlog/story-cards.md#v-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="v-02"></a>

## V-02 — Build browser voice with interruption and corrected facts

Status: Planned — not Ready
Release: B2 | Priority: P1 | Forecast sprint: S07
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 8 person-days most likely (6–12 range): Dev 6, BA/PO 0.5, QA 1.5; confidence low. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: V-01, DEV-08

## User story
As a test caller, I want to interrupt and correct the assistant so that it follows my current request rather than continue outdated speech.

## Business value / role evidence
Demonstrate voice interaction beyond text-to-speech playback.

## BA analysis and specification
Define meaningful response, critical-value transcription errors and stale output. Proposed timing targets must be measured under documented device/network conditions.

## Development / delivery tasks
- [ ] Integrate chosen STT/TTS or qualified realtime adapter through explicit audio/session events.
- [ ] Cancel stale generation and playback on interruption; route corrected facts through existing invalidation rules.
- [ ] Provide browser-only handoff simulation with an unmistakable simulated state.

## Acceptance criteria
- V-02-AC1: Given an interruption, then stale audio stops and the correction is used for the next proposal.
- V-02-AC2: Given an uncertain amount/name/negation, then clarification occurs before dependent action.
- V-02-AC3: Given speech/provider failure, then a clear fallback remains available.

## Test and evidence plan
- V-02-T1 (planned): 20 scenario families with consented human recordings and labelled TTS variants.
- V-02-T2 (planned): Measure entity/negation accuracy, p50/p95 response latency and interruption delay; do not count filler as a meaningful answer.

## Deliverables
Browser voice demo, audio provenance, timing traces and error analysis.

## Definition of Done
Channel semantics and measured targets reviewed; no telephone-connected claim.

## Boundaries
TTS-only tests cannot establish real caller performance.

Canonical story: docs/backlog/story-cards.md#v-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="v-03"></a>

## V-03 — Connect an inbound test phone call and transfer context to a human

Status: Planned — not Ready
Release: B2 | Priority: P1 | Forecast sprint: S08
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 9 person-days most likely (7–13.5 range): Dev 7, BA/PO 0.5, QA 1.5; confidence low. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: V-02, OPS-02

## User story
As a test caller, I want to reach the AI by phone and then a test representative so that the entire service path can be demonstrated.

## Business value / role evidence
Deliver a concrete end-to-end extension, not a simulated transfer message.

## BA analysis and specification
Confirm provider/number budget, destination test representative, test consent and reachable hours before provisioning. Twilio is a proposed integration, subject to current capability/cost qualification.

## Development / delivery tasks
- [ ] Implement signed webhook validation, session mapping and telephony state reconciliation.
- [ ] Connect voice processing and a controlled transfer endpoint/queue; present the handoff context on the representative desktop.
- [ ] Persist authoritative call IDs/events and distinguish request accepted from recipient connected.

## Acceptance criteria
- V-03-AC1: Given a real inbound test call, then the caller reaches the assistant on the configured number.
- V-03-AC2: Given a human transfer, then a test person actually answers and sees the correct context.
- V-03-AC3: Given a webhook with invalid signature or duplicate event, then it causes no unauthorized or duplicate transition.

## Test and evidence plan
- V-03-T1 (planned): Observed end-to-end call with caller and recipient confirmation.
- V-03-T2 (planned): Signature, replay/duplicate, out-of-order callback and cross-session tests.

## Deliverables
Phone integration, screen-pop contract, actual event trace and witnessed demo.

## Definition of Done
Actual connection evidence exists; no tool success string substitutes for a connected call.

## Boundaries
Actual provisioning/calls incur cost only after the specific budget/destination is established.

Canonical story: docs/backlog/story-cards.md#v-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="v-04"></a>

## V-04 — Validate voice failure handling and release the phone extension

Status: Planned — not Ready
Release: B2 | Priority: P1 | Forecast sprint: S08
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 4.5 person-days most likely (3.5–7 range): Dev 2, BA/PO 0.5, QA 2; confidence low. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: V-03, QA-01

## User story
As an operations owner, I want phone failures tested so that callers receive honest status and support can recover interrupted sessions.

## Business value / role evidence
Show production-minded testing without claiming production scale.

## BA analysis and specification
Define caller messaging and ownership for no available agent, timeout, disconnect, failed speech, repeated transfer and missing context.

## Development / delivery tasks
- [ ] Implement failure transitions and bounded retry/reconciliation.
- [ ] Add voice/telephony costs including abandoned and failed calls, with unknown values explicitly retained.
- [ ] Update support instructions, privacy/retention settings and release evidence.

## Acceptance criteria
- V-04-AC1: Given no human answers, then the caller gets the configured fallback and status remains failed/unconnected.
- V-04-AC2: Given a dropped call or duplicate callback, then the session reaches a coherent state without repeated operations.
- V-04-AC3: Given missing handoff context, then the representative sees the gap rather than invented conversation history.

## Test and evidence plan
- V-04-T1 (planned): Execute 12 transfer/failure cases plus regression on the voice families.
- V-04-T2 (planned): Verify actual receiver connection, correct context, latency and complete call-cost denominators.

## Deliverables
Voice UAT report, failure recordings/events, cost report, release decision and runbook.

## Definition of Done
All critical transfer cases pass on the defined test environment; limitations documented.

## Boundaries
No claims about all accents, population-wide accuracy or real contact-centre savings.

Canonical story: docs/backlog/story-cards.md#v-04
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="r-01"></a>

## R-01 — Discover retail follow-up value and specify eligibility rules

Status: Planned — not Ready
Release: R1 | Priority: P2 | Forecast sprint: S09
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3.5 person-days most likely (2.5–5.5 range): Dev 1, BA/PO 2, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: OPS-03

## User story
As a retail sales associate, I want relevant, permission-aware follow-up tasks so that I can act on a customer's stated need without unnecessary outreach.

## Business value / role evidence
Build on the owner's luxury retail customer/visit/task system experience.

## BA analysis and specification
Define current/to-be journey, stakeholder responsibilities, need capture, inventory trigger, relationship owner, consent/channel, previous outreach and expiry. Confirm product category/store assumptions before detailed implementation.

## Development / delivery tasks
- [ ] Create retail problem/options brief and story map, using manual templates as baseline.
- [ ] Specify decision tables and entity contracts for visit/need, product/variant, store stock, consent, task and outreach outcome.
- [ ] Record gaps in real linked retail data; authored fixtures are not sales-effectiveness evidence.

## Acceptance criteria
- R-01-AC1: Given a follow-up proposal, then a stated need, permitted channel and responsible associate exist.
- R-01-AC2: Given withdrawn permission, stale stock or duplicate trigger, then outreach is blocked or refreshed.
- R-01-AC3: Given no suitable item, then no recommendation is a valid outcome.

## Test and evidence plan
- R-01-T1 (planned): Owner scenario review using prior experience without claiming employer approval.
- R-01-T2 (planned): Walk through no-consent, changed inventory and relationship reassignment cases.

## Deliverables
Retail BA pack, rules, ERD, synthetic fixture contract and refined story specifications.

## Definition of Done
Scope and store/category assumptions reviewed; implementation stories split to <=16 h.

## Boundaries
No automated customer messaging or invented conversion uplift.

Canonical story: docs/backlog/story-cards.md#r-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="r-02"></a>

## R-02 — Implement customer visits, stated needs and manual follow-up tasks

Status: Planned — not Ready
Release: R1 | Priority: P2 | Forecast sprint: S09
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 7.5 person-days most likely (5.5–11.5 range): Dev 6, BA/PO 0.5, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: R-01, DEV-06, DEV-07

## User story
As an associate, I want to record a visit and manage assigned follow-up so that a customer's specific needs are not lost between interactions.

## Business value / role evidence
Deliver a usable manual retail workflow before AI assistance.

## BA analysis and specification
Specify required versus optional customer/need fields, permission provenance, task ownership and completion reasons.

## Development / delivery tasks
- [ ] Add store-scoped retail tables/migrations and authorized APIs.
- [ ] Build visit/need capture, consent status and task queue with edit/approval history.
- [ ] Reuse proven approval/outbox infrastructure only where semantics match; keep retail rules separate.

## Acceptance criteria
- R-02-AC1: Given a visit note, then stated preference is separated from inferred preference.
- R-02-AC2: Given a task reassignment, then its ownership history is recorded.
- R-02-AC3: Given another store/customer scope or revoked consent, then unauthorized access/outreach is rejected.

## Test and evidence plan
- R-02-T1 (planned): CRUD/state/authorization integration tests and manual journey UI test.
- R-02-T2 (planned): Concurrent edit, reassignment and repeat trigger cases.

## Deliverables
Retail manual UI/API, migrations, fixtures, rules tests and acceptance evidence.

## Definition of Done
Manual follow-up works with AI disabled and permissions enforced server-side.

## Boundaries
Synthetic demo records; no external customer messages sent.

Canonical story: docs/backlog/story-cards.md#r-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="r-03"></a>

## R-03 — Propose an inventory-matched follow-up for associate approval

Status: Planned — not Ready
Release: R1 | Priority: P2 | Forecast sprint: S10
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 8 person-days most likely (6–12 range): Dev 6, BA/PO 0.5, QA 1.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: R-02, DEV-09

## User story
As an associate, I want the assistant to match a recorded need to current stock and draft a task so that I can prepare relevant follow-up faster.

## Business value / role evidence
Use AI for interpretation and preparation while deterministic rules enforce eligibility.

## BA analysis and specification
Specify supported needs, acceptable alternatives, factual claims, evidence timestamps and approval authority.

## Development / delivery tasks
- [ ] Extract candidate needs from visit notes with source spans and uncertainty; require review before treating inference as fact.
- [ ] Query store/variant inventory, enforce consent/ownership/freshness, and generate a supported task/message draft.
- [ ] Revalidate inventory and permission at commit; deduplicate repeated events and preserve manual edits.

## Acceptance criteria
- R-03-AC1: Given a matching available variant and valid permission, then a supported draft is proposed for approval.
- R-03-AC2: Given stock/permission changes before commit, then the stale proposal is rejected.
- R-03-AC3: Given no exact match, then any alternative is explicitly labelled and an unsupported promise is prohibited.

## Test and evidence plan
- R-03-T1 (planned): Missing size/variant, stale inventory, withdrawn permission, injection, duplicate and changed-owner cases.
- R-03-T2 (planned): Compare rules/templates and assistant using the same facts.

## Deliverables
Retail assistant, evidence UI, eligibility tests and baseline comparison inputs.

## Definition of Done
No unapproved outreach or invented product claims in critical suite.

## Boundaries
The system prepares tasks; real customer delivery is a separately authorized integration.

Canonical story: docs/backlog/story-cards.md#r-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="r-04"></a>

## R-04 — Evaluate retail usefulness and package the second case

Status: Planned — not Ready
Release: R1 | Priority: P2 | Forecast sprint: S10
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 4.5 person-days most likely (3.5–7 range): Dev 2, BA/PO 1, QA 1.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: R-03, QA-03, OPS-03

## User story
As a retail operations owner, I want an honest assessment of task quality and effort so that I can decide whether assistance is worth piloting.

## Business value / role evidence
Connect retail BA, data and software evidence without claiming synthetic revenue gains.

## BA analysis and specification
Define task quality, associate preparation effort and event funnel separately from causal sales outcomes. Plan 60 families (30 development/30 held-out) plus 24 critical cases, refined before execution.

## Development / delivery tasks
- [ ] Build evaluator and SQL/Tableau funnel: eligible need→draft→approved task→simulated delivery→reply/appointment/purchase events.
- [ ] Compare baseline and assistant, include abstention and all failed/duplicate events.
- [ ] Reuse deployment/recovery checks with retail access/retention rules and publish a separate case study.

## Acceptance criteria
- R-04-AC1: Given simulated outcomes, then every chart and claim identifies them as simulated.
- R-04-AC2: Given the evaluation, then critical permission/stock/duplication cases all pass and routine target is assessed as frozen.
- R-04-AC3: Given no controlled real customer pilot, then conversion uplift and revenue gain remain unmeasured.

## Test and evidence plan
- R-04-T1 (planned): Reconcile funnel counts and event order.
- R-04-T2 (planned): Retail UAT and provider/permission regression; fresh setup smoke.

## Deliverables
Evaluation, UAT, Tableau findings, release notes, demo and BA/developer walkthroughs.

## Definition of Done
Results, limits, own contribution and upstream reuse are documented.

## Boundaries
A sales lift claim requires a real authorized controlled pilot, not this synthetic demo.

Canonical story: docs/backlog/story-cards.md#r-04
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="pkg-01"></a>

## PKG-01 — Publish connected BA, data analyst and developer evidence

Status: Planned — not Ready
Release: B1/R1 | Priority: P1 | Forecast sprint: S06
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 2.5 person-days most likely (2–4 range): Dev 1, BA/PO 1, QA 0.5; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: OPS-03, DEV-10

## User story
As a hiring reviewer, I want a concise evidence trail so that I can assess the owner's business analysis and implementation contribution.

## Business value / role evidence
Support Winnipeg BA/BSA and North American developer applications with one coherent business case.

## BA analysis and specification
Prepare role-specific narratives: business problem/options/requirements/UAT for BA; provenance/SQL/metrics/findings for data analyst; architecture/contracts/tests/deployment for developer.

## Development / delivery tasks
- [ ] Create an English case study and short workflow demo with links to specifications, decisions, code, test evidence and release artifacts.
- [ ] Document upstream libraries/data/benchmark reuse and what the owner designed or implemented.
- [ ] Provide reproducible no-key setup and a technical walkthrough the owner can explain/debug.

## Acceptance criteria
- PKG-01-AC1: Given a reviewer follows one requirement, then they can find implementation and executed acceptance evidence.
- PKG-01-AC2: Given a result claim, then measured versus assumed versus planned status is visible.
- PKG-01-AC3: Given a fresh reviewer, then setup instructions lead to the stated demo without private data or paid keys for manual mode.

## Test and evidence plan
- PKG-01-T1 (planned): Fresh-reader walkthrough and link/claim audit.
- PKG-01-T2 (planned): Verify demo footage matches the released build and includes an exception path.

## Deliverables
BA case study, analytical findings, engineering README, demo script/video and evidence index.

## Definition of Done
Only actual work and verified outcomes are presented; no invented seniority, employer approvals or savings.

## Boundaries
Retail packaging follows R-04; do not wait for retail to publish an accepted bank release.

Canonical story: docs/backlog/story-cards.md#pkg-01
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

<a id="git-01"></a>

## GIT-01 — Public monorepo, contribution workflow and release hygiene

Status: Merged to main — branch protection, linear history and auto branch deletion enabled
Release: All | Priority: P0 | Forecast sprint: S01
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3 person-days most likely (2.5–4.5 range): Dev 2, BA/PO 0.5, QA 0.5; confidence medium. Original full-story estimate retained; bootstrap completion is not a re-estimate.
Dependencies: GOV-01

## User story
As a reviewer or contributor, I want one navigable public repository so that specifications, implementation and evidence can be inspected together.

## Business value / role evidence
Show maintainable open-source engineering and transparent individual contribution.

## BA analysis and specification
Recommend one repository with independent bank and retail modules. The bank voice channel shares bank domain rules but has narrower authority. Split repositories only when independent users, release ownership and stable package contracts justify it.

## Development / delivery tasks
- [x] Initialize the owner-provided public repository with clean, portfolio-only history.
- [x] Review an explicit export allowlist and run publication hygiene/link checks. No raw datasets or personal-workspace history included.
- [x] Add README navigation, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY guidance, issue/PR templates, MIT license and separate third-party notices.
- [x] Run offline tests and specification checks on GitHub Actions with Python 3.9 and 3.12.
- [ ] Exercise a story-linked contribution PR and configure/verify default-branch protection.
- [ ] Execute the application release checklist when working software is ready.

## Acceptance criteria
- GIT-01-AC1: Given a public export, when its files and history are reviewed, then only approved portfolio material and permitted assets are included.
- GIT-01-AC2: Given a PR, then it references its story/spec, checks and change impact; a reviewer can reproduce the reported checks.
- GIT-01-AC3: Given a new contributor, then setup, demo limitations, module boundaries and contribution steps are documented.

## Executed evidence
- Initial clean import: 5be1a8d. Reproducible calendar fix: 4af1798.
- Verified CI for 4af1798: https://github.com/xc8609/service-agent-portfolio/actions/runs/39372023490 — both Python jobs passed.
- Each job: 5 parser tests, workflow-spec checks, contract checks and publication checks.
- Contract checks cover 45 schemas, 91 payload examples, 52 authored boundary examples and 4 calendar examples; this does not execute application authorization, PostgreSQL DDL or UAT.
- A host timezone-data mismatch found by CI was corrected by pinning the simulated fixture rule snapshot; current civil-time rules are not asserted by that snapshot.

## Remaining acceptance
GIT-01-T2's contribution PR rehearsal and branch protection verification remain pending. Do not mark the entire story or S01/S02 Done. No application, model evaluation or deployment has been completed by this publication.

## Deliverables
Repository: https://github.com/xc8609/service-agent-portfolio
Publication evidence: https://github.com/xc8609/service-agent-portfolio/blob/main/docs/github-publication.md
Repository ADR: https://github.com/xc8609/service-agent-portfolio/blob/main/docs/decisions/001-repository-boundaries.md
Canonical story: https://github.com/xc8609/service-agent-portfolio/blob/main/docs/backlog/story-cards.md#git-01

PUBLIC-BOOTSTRAP-v1 | MIT selected by owner | 19 October 2026


<a id="gov-03"></a>

## GOV-03 — Two-week sprint planning, capacity and forecast control

Status: Review candidate — owner acceptance pending
Release: All | Priority: P0 | Forecast sprint: S01
Role owner: BA/PO (simulated team allocation, not actual staffing)
Estimate: 0.5 person-days most likely (0.5–1 range): Dev 0, BA/PO 0.5, QA 0; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: GOV-02

## User story
As the delivery lead, I want a capacity- and dependency-based plan for a small team so that estimates can be challenged and revised.

## Business value / role evidence
Show BA delivery planning, scope negotiation and honest forecasting.

## BA analysis and specification
Simulated staffing: two developers as baseline, optional third developer; BA/PO and QA capacity explicitly separate. No claim these people actually participated. Owner's personal 20+ hours/week is not the team schedule.

## Development / delivery tasks
- [ ] Maintain story-level developer, BA/PO and QA person-day estimates; keep calendar duration separate.
- [ ] Use two-week sprints, 70% planned allocation of available days and a 30% allowance for ceremonies, reviews, routine rework and support. Do not add the same overhead twice.
- [ ] Keep future sprint scope forecast; refine next sprint against readiness, actual throughput, holidays and availability. Split delivery slices larger than five developer-days before starting.
- [ ] Record sprint goal, owners by role, acceptance, dependencies, blockers, demo, retro and carryover decisions. One active major slice per developer; unready work stays backlog.

## Acceptance criteria
- GOV-03-AC1: Given sprint planning, then each included item has an estimate, dependency, owner role and measurable exit condition.
- GOV-03-AC2: Given missing capacity or failed acceptance, then scope/date is reforecast and incomplete work does not become Done.
- GOV-03-AC3: Given the third developer is added, then only independent work is accelerated and a new dependency plan is approved.

## Test and evidence plan
- GOV-03-T1 (planned): Check every story is assigned once and no dependency lands in a later sprint.
- GOV-03-T2 (planned): Reconcile each role's effort against available sprint capacity and show overflow/range risks.

## Deliverables
Sprint roadmap, estimate ledger, review/retro template, risk and assumption register.

## Definition of Done
Planning baseline reviewed; no sprint is claimed started or completed merely because its card exists.

## Boundaries
Relative weeks are authoritative. Example calendar dates are forecasts only and rebase on actual kickoff.

Canonical story: docs/backlog/story-cards.md#gov-03
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.

### GOV-03 three-developer alternative

Candidate: nine sprints / 18 weeks, with bank at week 10, phone at week 14 and retail at week 18. Initial discovery/contract sprints remain unchanged. A03 contains DEV-02/03/04/05/06/09 (21 developer-days), with developer C leading retrieval/provider work. A04 contains DEV-07/08/10 and QA-02 (16 developer-days), then bank release. See the full role-capacity comparison in [the sprint ledger](sprints.md). This is lower confidence; keep the two-developer board baseline unless refinement confirms feasibility.


### Actual Sprint 1 increment — 19 October 2026

Version 0.1 analysis is prepared. The owner selected customer-information and handling-rule lookup as the primary pain. See the [bank SDD package](../../projects/bank-service-assist/docs/sprint-01/README.md) for detailed specs, evidence and decisions. Structural checks passed; owner acceptance and application implementation remain pending. Current Trello list: 10 | Review and acceptance.

<a id="pkg-02"></a>

## PKG-02 — Final open-source reviewer rehearsal and two-case portfolio

Status: Planned — not Ready
Release: R1 | Priority: P1 | Forecast sprint: S10
Role owner: Developer A + B (vertical slice) (simulated team allocation, not actual staffing)
Estimate: 3 person-days most likely (2.5–4.5 range): Dev 1, BA/PO 1, QA 1; confidence medium. Includes implementation, developer tests, review fixes and story documentation. QA = additional independent/system testing, not duplicate unit-test effort.
Dependencies: PKG-01, V-04, R-04

## User story
As a prospective employer, I want to inspect connected business, data and engineering evidence without being misled about delivery status.

## Business value / role evidence
Make BA/BSA and developer evidence accessible from one public entry point.

## BA analysis and specification
Explain why the bank assistant and retail task proposal need bounded reasoning, compare simpler options, and show measured evidence, limitations and owner contribution.

## Development / delivery tasks
- [ ] Create two concise case studies and three audience routes: BA, data analyst, developer.
- [ ] Record bank/voice/retail demos only after their gates pass; link spec, PR, test report and release version.
- [ ] Rehearse fresh setup, issue submission, demo reset and documentation navigation; fix observed blockers.

## Acceptance criteria
- PKG-02-AC1: Given a reviewer, then they can locate the problem, alternatives, rules, implementation, executed tests and limitations for each case.
- PKG-02-AC2: Given any metric, then its dataset, denominator, measurement method and synthetic/real status are explicit.
- PKG-02-AC3: Given a fresh checkout, then documented setup/tests work or documented external prerequisites explain the remaining steps.

## Test and evidence plan
- PKG-02-T1 (planned): Conduct a recorded fresh-reviewer walkthrough or clearly label self-review if no independent person participates.
- PKG-02-T2 (planned): Check public links, license attribution and no fabricated collaboration or production claims.

## Deliverables
Public case-study index, final demos, walkthrough report and contribution guide.

## Definition of Done
Rehearsal results and fixed/remaining issues recorded.

## Boundaries
No invented peer approval, employer endorsement or business ROI.

Canonical story: docs/backlog/story-cards.md#pkg-02
SDD: spec → design → task slices → code/PR → executed tests/UAT → release/support. GitHub: https://github.com/xc8609/service-agent-portfolio; no application implementation/evaluation is claimed by this planning card.


<a id="dev-11"></a>

# DEV-11 — Receive specialist findings and complete a verified customer callback

BANK-SDD-v0.2 · 19 October 2026
Status: Merged to main — automated evidence recorded; owner UAT pending
Forecast: Reforecast pending; after S04 foundation, before B1 acceptance | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 0.5, QA 1 person-days; total 5.5 (4–8), confidence low. Not actual effort.

## User story and value

As a feedback representative, I want approved findings and a callback task, so that I can continue the case without requiring the original representative.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-17, FR-18. Decisions: D-13, D-14. Dependencies: DEV-07, DEV-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Specialist accepts work; use a role-protected synthetic result entry or signed adapter event.
2. Store finding, evidence, approved customer explanation, action status and version separately.
3. Create one feedback task for the shared queue; assign a person when work begins.
4. Draft from approved customer-visible content; person calls, verifies identity and records actual outcome.

## Acceptance criteria

- **DEV-11-AC01** — Given An authorized specialist submits an approved result; when the event is processed twice; then persist one result version and one corresponding feedback task. Evidence: DEV-11-T01 (planned, not executed).
- **DEV-11-AC02** — Given The original representative is unavailable; when another authorized feedback representative claims the task; then provide scoped history and retain clear ownership. Evidence: DEV-11-T02 (planned, not executed).
- **DEV-11-AC03** — Given A result contains internal-only notes and approved explanation; when the agent drafts customer feedback; then use only approved customer-visible content for the explanation. Evidence: DEV-11-T03 (planned, not executed).
- **DEV-11-AC04** — Given A customer answers but identity verification fails; when the callback is recorded; then record verification failure, disclose no transaction detail and do not mark feedback complete. Evidence: DEV-11-T04 (planned, not executed).
- **DEV-11-AC05** — Given The specialist result changes after draft review; when feedback approval is attempted; then reject stale content and preserve edits for refresh. Evidence: DEV-11-T05 (planned, not executed).
- **DEV-11-AC06** — Given A financial action is only approved or pending; when the agent summarizes the result; then do not state funds moved or that the financial issue is resolved. Evidence: DEV-11-T06 (planned, not executed).

## Ready gates

- Result payload and callback outcome codes need schema review; real outbound telephony is excluded.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

Design (repository document) · Tasks (repository document) · Acceptance record (repository document) · Tool contracts (repository document) · Review increment (repository document).

## Implementation and tool design

- Add InvestigationResult and CallbackAttempt tables with versioned evidence and disclosure fields.
- Implement specialist fixture result entry, shared feedback inbox and callback-result form.
- Enforce internal-only exclusions, duplicate-result handling and latest-result checks.
Tools: get_case_snapshot, get_contact_attempts, get_service_targets, create_proposal. Server enforces scope, source versions, idempotency and transitions. Human approval remains required for operational changes.

## Verification and release

All listed test IDs are planned. Include database integration, UI state, permission, stale-data and retry/failure tests. Verify migration, worker restart, manual fallback and restore in staging before Done. No application tests or deployment were run by writing this card.


<a id="dev-12"></a>

# DEV-12 — Retry unanswered callbacks and guard normal closure

BANK-SDD-v0.2 · 19 October 2026
Status: Merged to main — automated evidence recorded; owner UAT pending
Forecast: Reforecast pending; after S04 foundation, before B1 acceptance | Release: B0 manual path / B1 assisted path.
Estimate: Dev 3, BA 0.5, QA 1 person-days; total 4.5 (3.5–7), confidence low. Not actual effort.

## User story and value

As a feedback representative and queue lead, I want bounded retries and evidence-based closure, so that I can avoid abandoned feedback and false resolution.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-18, FR-19. Decisions: D-14, D-16. Dependencies: DEV-11, BA-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Record each actual call attempt with time, verification and outcome.
2. For no answer keep feedback ownership and propose the next allowed contact slot.
3. Allow at most three attempts over three service days, including the first; at most one per service date.
4. On exhaustion or elapsed window send to lead review; do not close automatically.
5. On successful feedback allow human-confirmed closure only when all required work is complete.

## Acceptance criteria

- **DEV-12-AC01** — Given The first actual callback is unanswered; when the retry is planned; then keep awaiting-feedback state and ownership; schedule only within the accepted contact window. Evidence: DEV-12-T01 (planned, not executed).
- **DEV-12-AC02** — Given One attempt is already recorded for a service date; when a concurrent second retry is submitted; then reject the extra attempt plan for that date; actual duplicate call records remain auditable. Evidence: DEV-12-T02 (planned, not executed).
- **DEV-12-AC03** — Given Three attempts have been made or the three-service-day window has elapsed; when the next-step rule is evaluated; then enter unable-to-contact lead review with no resolved closure. Evidence: DEV-12-T03 (planned, not executed).
- **DEV-12-AC04** — Given Friday is the first attempt and Monday is a configured holiday; when a retry window is calculated; then use the versioned calendar and customer contact windows, not elapsed 72 hours. Evidence: DEV-12-T04 (planned, not executed).
- **DEV-12-AC05** — Given Approved findings exist, necessary actions are complete and verified feedback leaves no unresolved work; when an authorized person confirms closure; then persist a closed disposition with references and audit evidence. Evidence: DEV-12-T05 (planned, not executed).
- **DEV-12-AC06** — Given There is an unanswered call, failed verification, pending refund, new objection or unowned work; when closure is requested; then deny closure with the unmet conditions. Evidence: DEV-12-T06 (planned, not executed).
- **DEV-12-AC07** — Given An agent suggests a fourth attempt or immediate closure; when the proposal is validated; then reject unsupported action without losing case history. Evidence: DEV-12-T07 (planned, not executed).

## Ready gates

- Calendar fixture holiday list and exact window boundaries must be frozen; no administrative non-response closure is authorized.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

Design (repository document) · Tasks (repository document) · Acceptance record (repository document) · Tool contracts (repository document) · Review increment (repository document).

## Implementation and tool design

- Implement versioned calendar calculations and persisted attempts; reserve slots to prevent concurrent duplicates.
- Add queue lead review state and callback constraints with manual fallback.
- Implement server closure preconditions and reasoned rejection with preserved notes.
Tools: get_case_snapshot, get_contact_attempts, get_service_targets, create_proposal, get_operation_status. Server enforces scope, source versions, idempotency and transitions. Human approval remains required for operational changes.

## Verification and release

All listed test IDs are planned. Include database integration, UI state, permission, stale-data and retry/failure tests. Verify migration, worker restart, manual fallback and restore in staging before Done. No application tests or deployment were run by writing this card.


<a id="dev-13"></a>

# DEV-13 — Handle overdue investigations and customer objections with linked work

BANK-SDD-v0.2 · 19 October 2026
Status: Merged to main — automated evidence recorded; owner UAT pending
Forecast: Reforecast pending; after S04 foundation, before B1 acceptance | Release: B0 manual path / B1 assisted path.
Estimate: Dev 4, BA 1, QA 1 person-days; total 6 (4.5–9), confidence low. Not actual effort.

## User story and value

As a service lead and representative, I want current evidence and accountable exception continuation, so that I can avoid silent delays and lost customer objections.

Owner relevance: representative desktop, customer-information lookup and processing-rule experience. Role evidence: requirements/API/access/testing/UAT in dated R01/R02/R06 samples; no current vacancy or outcome claim.

## Scope and authority

Requirements: FR-20, FR-21. Decisions: D-14, D-15. Dependencies: DEV-11, BA-06, BA-09.
Synthetic records and policies only. Financial execution, real outbound calls, App messaging and a full specialist adjudication platform are excluded.

## Main flow

1. Scheduler detects overdue work and rechecks latest state.
2. Agent gathers recorded blockers and commitments; drafts escalation and progress update.
3. Keep original deadlines and specialist ownership; a human confirms new commitments.
4. Capture objection verbatim, compare with old evidence and propose clarification, linked re-review or complaint review.
5. Preserve prior findings and any complaint request independently of re-review.

## Acceptance criteria

- **DEV-13-AC01** — Given A routine investigation exceeds the two-service-day target; when the timer event arrives; then retain original due time and ownership and prepare a progress-update task. Evidence: DEV-13-T01 (planned, not executed).
- **DEV-13-AC02** — Given The same overdue event is delivered twice; when the worker handles it; then produce one escalation per case, deadline and escalation level. Evidence: DEV-13-T02 (planned, not executed).
- **DEV-13-AC03** — Given No blocker reason is recorded; when the agent drafts an update; then label the reason unknown; do not invent merchant or bank explanations. Evidence: DEV-13-T03 (planned, not executed).
- **DEV-13-AC04** — Given An investigation completes while an escalation is being approved; when the backend rechecks state; then invalidate the outdated escalation and continue with the current result. Evidence: DEV-13-T04 (planned, not executed).
- **DEV-13-AC05** — Given A customer provides a different transaction or new evidence; when a re-review is approved; then link the new work to the original case and preserve old findings/versions. Evidence: DEV-13-T05 (planned, not executed).
- **DEV-13-AC06** — Given A customer explicitly requests complaint handling while re-review remains open; when the objection is assessed; then preserve a separate complaint-review route without waiting for re-review completion. Evidence: DEV-13-T06 (planned, not executed).
- **DEV-13-AC07** — Given A customer disagrees without new evidence; when the agent proposes next steps; then present a reasoned clarification/review option for human confirmation; no coercion, financial action or automatic closure. Evidence: DEV-13-T07 (planned, not executed).

## Ready gates

- Draft only: escalation recipient/levels, next-update cadence, re-review authority and complaint intake contract require owner review. Core deadline/progress obligations are accepted; these branch details are not.
- Review data/permission contracts, exact fixtures, dependencies and observable results before moving to Ready.
- No Done status until implementation, appropriate tests, owner UAT and required release evidence exist.

## Traceability

Design (repository document) · Tasks (repository document) · Acceptance record (repository document) · Tool contracts (repository document) · Review increment (repository document).

## Implementation and tool design

- Add deduplicated deadline events and progress-update proposals with original due timestamps.
- Add objection/re-review linkage and proposal invalidation on new evidence.
- Build lead review UI; keep detailed exception routing disabled until rules are accepted.
Tools: get_case_snapshot, get_service_targets, get_contact_attempts, search_policy, create_proposal. Server enforces scope, source versions, idempotency and transitions. Human approval remains required for operational changes.

## Verification and release

All listed test IDs are planned. Include database integration, UI state, permission, stale-data and retry/failure tests. Verify migration, worker restart, manual fallback and restore in staging before Done. No application tests or deployment were run by writing this card.
