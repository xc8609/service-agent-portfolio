# Service Agent Portfolio

[![Checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)

**From customer-service problems to working, human-reviewed AI workflows.**

Service Agent Portfolio is a lightweight, open-source application portfolio that
connects **business analysis, specification-driven development and Agent engineering**.
It starts with a simulated banking service desk and demonstrates how requirements,
process decisions and acceptance criteria become working software and test evidence.

## Why this project

Customer-service representatives often need to navigate several screens to find
customer information, work within different access permissions and learn which
handling rules apply. This project brings permitted information, relevant rules and
accountable follow-up into one workflow.

The first case is **“I bought once — why do I see two credit-card charges?”**
The representative inspects transactions and existing cases, records what the
customer recognizes, checks handling rules, and submits a reviewed specialist enquiry
when needed. The Agent helps assemble evidence and draft the next step; authorized
staff retain responsibility for decisions and customer communication.

**The intended value:** less information-search effort, more consistent handling and
clearer handoffs. These are hypotheses to test against the manual workflow; measured
cost savings and production outcomes are not yet claimed.

## What you can explore

- **Business analysis:** problem definition, current/target processes, permissions,
  exceptions, story cards, Sprint planning and traceable acceptance criteria.
- **Working service workflow:** scoped transaction/rule lookup, reviewed notes and
  referrals, specialist findings, manual feedback and contact/exception handling.
- **Agent engineering:** a bounded evidence assistant, server-selected model API
  adapters, persisted runs, source citations and human approval boundaries.
- **Data and delivery evidence:** reconciled SQL exports, a Tableau workbook,
  automated tests, CI and a reproducible local deployment.

**Stack:** React/TypeScript · FastAPI/Python · PostgreSQL · SQL/Tableau · Docker Compose.

**Current status:** implementation is under review in [stacked pull requests](https://github.com/xc8609/service-agent-portfolio/pulls).
The runnable assistant defaults to a scripted offline provider; live models and real
bank integrations are unqualified. All operational records and rules are synthetic.
Tableau opens locally; refresh/layout acceptance and human benefit measurement remain
pending. Voice service and retail clienteling are later releases.

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

One UI, one API and one workflow database keep the application small and understandable.
Institution-specific data integration is designed around a canonical read model;
server-owned profiles separate model APIs from Agent execution.
Permissions, evidence versions and human approval remain in shared business services.
Two source formats and three model protocols have offline test coverage. Real bank
connectors, SDK runtime adoption and live model qualification remain separate work.
[Adaptation examples](examples/README.md) ·
[Decisions, references and limits](docs/architecture/ADR-004-lightweight-enterprise-adaptation.md).

## Open-source references

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) and
[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) inform our
separation of model access, tools and orchestration. This project currently uses its
own small bounded runtime and HTTP protocol adapters; it does not claim to integrate
those SDKs. [Architecture decisions](docs/architecture/ADR-004-lightweight-enterprise-adaptation.md)
explain what we adopted, what remains optional and how a concrete institution's
requirements would change the implementation.

## Delivery

Bank core first: **lookup → rules → reviewed enquiry → specialist finding →
customer feedback**. Agent assistance builds on that manual path. Voice and retail
are later releases. See the [current scope and Sprint sequence](docs/backlog/current-delivery.md).

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [MIT](LICENSE) ·
[Third-party notices](THIRD_PARTY_NOTICES.md). Independent portfolio work; all
operational records and business rules are explicitly simulated.
