# Service Agent Portfolio

[![Checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)

A **simulated bank service workspace** for “Why was I charged twice?”
Representatives need to find customer information across screens, respect access
limits and locate the right handling rule. This portfolio turns those pain points
into **business analysis → specifications → working software → test evidence**.
The Agent assembles permitted evidence and drafts a next step for human review.
Business benefit is a hypothesis to evaluate, not a claimed saving.

**Works today:** scoped transaction/rule lookup, reviewed notes and specialist
referrals, specialist findings, verified manual feedback, bounded contact plans,
overdue/objection handling, and a persisted offline evidence assistant. React +
FastAPI + PostgreSQL; all operational records are synthetic. Live models remain
disabled and unqualified. SQL exports reconcile with source records; Tableau Desktop opens the workbook; refresh/layout acceptance and human benefit
measurement remain pending.

## Repository map

```text
apps/web/                         React/TypeScript workspace + browser tests
services/api/                     FastAPI, PostgreSQL migrations + API tests
  bank_api/agent/                 Bounded runtime, provider adapters + server selection
  bank_api/integrations/          Offline source-mapping validation
projects/bank-service-assist/
  docs/                          Business analysis, decisions + Sprint evidence
  specs/<STORY-ID>/               spec, design, tasks, acceptance
  specs/contracts/               Permissions, data model, tool/API schemas
  data/                          Source/terms notes; datasets excluded from Git
  scripts/                       Offline data/specification checks
  sql/ + dashboard/              Operational marts + Tableau workbook candidate
docs/backlog/                     Story catalogue, Sprint forecast + current scope
docs/decisions/ + architecture/   Repository decisions + architecture ADRs
examples/                        Synthetic source mappings + disabled model profiles
.github/workflows/               Offline, API/browser and container CI
```

[Business analysis](projects/bank-service-assist/docs/README.md) ·
[Stories & current delivery](docs/backlog/README.md) ·
[Detailed design](projects/bank-service-assist/specs/README.md) ·
[Architecture & Agent boundary](docs/architecture.md) ·
[Trello](https://trello.com/b/wtNhuN0q/ai-agent)

## Run the demo

Requires Docker Compose. From the repository root:

```bash
python3 scripts/configure_demo.py
docker compose up --build --wait
```

Open **http://127.0.0.1:8000**. Start a verified demo contact, search `DEMO STORE`,
select both entries and inspect evidence. No model key is needed. Keep this
synthetic demo on localhost; it is not production authentication.

[Mac setup without Docker, tests and recovery](services/api/README.md) ·
[Executed evidence and limits](projects/bank-service-assist/docs/sprint-02/implementation/lookup-evidence.md)

## Adapt without rebuilding the business process

One UI, one API and one workflow database. Institution-specific data maps into a
canonical read model; server-owned profiles separate model APIs from Agent execution.
Permissions, evidence versions and human approval remain in shared business services.
Two source formats and three model protocols have offline test coverage. Real bank
connectors, SDK runtime adoption and live model qualification remain separate work.
[Adaptation examples](examples/README.md) ·
[Decisions, references and limits](docs/architecture/ADR-004-lightweight-enterprise-adaptation.md).

## Delivery

Bank core first: **lookup → rules → reviewed enquiry → specialist finding →
customer feedback**. Agent assistance builds on that manual path. Voice and retail
are later releases. See the [current scope and Sprint sequence](docs/backlog/current-delivery.md).

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [MIT](LICENSE) ·
[Third-party notices](THIRD_PARTY_NOTICES.md). Independent portfolio work; all
operational records and business rules are explicitly simulated.
