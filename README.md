# Service Agent Portfolio

[![Checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)

A **simulated bank service workspace** for investigating credit-card charges:
find authorized transactions, retrieve handling rules, and prepare a human-reviewed
specialist enquiry. It connects business analysis, specification-driven delivery
and agent engineering.

**Works today:** React + FastAPI + PostgreSQL, authorized transaction search and
evidence review, versioned customer statements and explicit pair recognition with
synthetic records. Related-case lookup shows progress, owners and duplicate-enquiry
review hints. Applicable simulated handling rules show conditions, exact citations
and next steps, with explicit conflict/gap handling. Changed queries invalidate old
evidence and guidance. Editable service notes require human approval and return a durable
receipt, with source-version checks and safe retries. Reviewed specialist enquiries
link existing work or create justified queued work, preserving material/contact gaps.
Specialists can publish findings and customer service can claim work, review feedback
and record a newly verified synthetic callback. **Next:** continuation controls and
bounded Agent assistance. No live bank connection, implemented Agent or measured savings.

## Repository map

```text
apps/web/                         React/TypeScript workspace + browser tests
services/api/                     FastAPI, PostgreSQL migrations + API tests
  bank_api/agent/                 Agent module boundary (design only today)
projects/bank-service-assist/
  docs/                          Business analysis, decisions + Sprint evidence
  specs/<STORY-ID>/               spec, design, tasks, acceptance
  specs/contracts/               Permissions, data model, tool/API schemas
  data/                          Source/terms notes; datasets excluded from Git
  scripts/                       Offline data/specification checks
docs/backlog/                     Story catalogue, Sprint forecast + current scope
docs/decisions/                   Repository/architecture decisions
.github/workflows/               Offline, API/browser and container CI
```

[Business analysis](projects/bank-service-assist/docs/README.md) ·
[Stories & current delivery](docs/backlog/README.md) ·
[Detailed design](projects/bank-service-assist/specs/README.md) ·
[Architecture & Agent boundary](docs/architecture.md) ·
[Trello](https://trello.com/b/wtNhuN0q/ai-agent)

## Run the manual demo

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

## Delivery

Bank core first: **lookup → rules → reviewed enquiry → specialist finding →
customer feedback**. Agent assistance builds on that manual path. Voice and retail
are later releases. See the [current scope and Sprint sequence](docs/backlog/current-delivery.md).

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [MIT](LICENSE) ·
[Third-party notices](THIRD_PARTY_NOTICES.md). Independent portfolio work; all
operational records and business rules are explicitly simulated.
