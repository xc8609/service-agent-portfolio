# Specification-driven delivery plan

Current baseline: [S02 v0.4](../projects/bank-service-assist/docs/sprint-02/README.md), [story registry](backlog/trello-cards.json) and [Sprint forecast](backlog/sprints.md). Earlier estimates in archived artifacts are superseded by this baseline.

## Scope and sequence

B0 establishes the manual bank workflow; B1 adds bounded assistance and evaluation; B2 adds voice self-service/human handoff; R1 is a separate retail clienteling case. The first enquiry is charge identification/apparent duplication. Staff search authorized facts and handling rules, review drafts and refer unresolved cases to specialists. Feedback and exception work retain accountable owners and auditable deadlines.

## Engineering

Proposed UI: React/TypeScript. API: Python 3.12/FastAPI. Persistence: PostgreSQL, migrations and transactional outbox. Worker resumes durable work with current scope. Model tools are provider-neutral and never confer human approval rights. Candidate model runtimes/providers are qualified in DEV-09; untested compatible endpoints stay unqualified. SQL/Tableau reporting uses authoritative workflow events and labelled data provenance.

## SDD and evidence

Requirements and decisions trace to four-file story packages, schema contracts and planned acceptance tests. CI currently verifies only offline data-parser/specification checks. Runtime database, UI, live-provider and deployment evidence must be produced during implementation. Compare a manual baseline against assistance; no measured savings are claimed.

## Forecast

Two-developer planning baseline with explicit BA/QA capacity, not actual staffing. Current ledger: 12 delivery iterations/24 weeks plus two reserve iterations; 170.5 estimated person-days. Illustrative dates are not commitments and must be adjusted to execution conditions. Existing runtime scope is not completed merely because specs are authored.

## Public repository

[GitHub](https://github.com/xc8609/service-agent-portfolio) is the versioned source; [Trello](https://trello.com/b/wtNhuN0q/ai-agent) is its planning mirror. Keep datasets, secrets and personal workspace material out. [Contribution workflow](../CONTRIBUTING.md) and [data plan](agent-data-validation-plan.md) define boundaries.
