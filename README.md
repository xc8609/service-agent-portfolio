# Service Agent Portfolio

[![Portfolio checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)

A specification-driven portfolio connecting business analysis, data analysis and agent engineering. The first case is a **simulated bank representative workspace**: find authorized customer and transaction facts, retrieve applicable handling rules, and move unresolved work through accountable human review.

**Current state: specifications and offline validation tooling.** There is no working banking application, deployed agent, real customer data or measured savings yet. This is independent portfolio work, not a bank-sponsored system.

## Start here

- [Bank case and current S02 specification](projects/bank-service-assist/docs/sprint-02/README.md)
- [Specification handoff and remaining gates](projects/bank-service-assist/docs/sprint-02/spec-completion.md)
- [Business requirements](projects/bank-service-assist/docs/sprint-01/requirements.json) and [decisions](projects/bank-service-assist/docs/sprint-01/decision-log.md)
- [Permissions](projects/bank-service-assist/specs/contracts/permissions.md), [data model](projects/bank-service-assist/specs/contracts/data-model.md), [OpenAPI](projects/bank-service-assist/specs/contracts/openapi.json)
- [Publication evidence and remaining gates](docs/github-publication.md)
- [Sprint plan](docs/backlog/sprints.md) · [Public Trello](https://trello.com/b/wtNhuN0q/ai-agent)

## Business case

The initial job is a credit-card charge enquiry: “What is this charge?” or “Why does it appear twice?” A representative gathers evidence across customer, transaction and policy views. The assistant is intended to reduce lookup effort while preserving access restrictions and supported answers.

The planned workflow keeps ordinary staff read access separate from financial authority. Representatives review drafts; specialists investigate; the feedback queue contacts customers. Timers, permissions, contact limits and approvals belong to deterministic services. Agent text is never proof of execution.

## Delivery sequence

| Release | Scope | State |
|---|---|---|
| B0 | Manual bank investigation, notes, referral and continuation | Specified; application not implemented |
| B1 | Bounded agent, provider qualification, operational SQL/Tableau and evaluation | Specified/planned |
| B2 | Bank voice self-service with verified human handoff | Planned |
| R1 | Separate retail clienteling assistant for reviewed follow-up | Planned |

One repository retains separate business modules. Shared infrastructure is introduced only where implementation warrants it. Banking comes first; voice is its channel extension.

## Run the existing checks

Python 3.9 and 3.12 are CI targets; Python 3.12 is the intended application runtime.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m pytest
python projects/bank-service-assist/scripts/validate_workflow_specs.py
python projects/bank-service-assist/scripts/validate_s02_contracts.py
python scripts/check_publication.py
```

These run local data-parser tests and specification/schema/reference checks. They do **not** validate PostgreSQL execution, an API, a UI, live model behavior or deployment. Calendar fixtures explicitly use the `tzdata==2025.2` rule snapshot, independent of the runner OS. This simulated baseline is not a claim about current civil-time rules; a production calendar requires separate validation. Public dataset download is optional and is not run by CI. See [data provenance](projects/bank-service-assist/data/README.md).

## Proposed implementation

React/TypeScript UI, Python 3.12/FastAPI, PostgreSQL, a durable worker and provider-neutral business tools. Model SDK/provider choices and dependency versions require a qualification spike. The current contracts expose 10 model tools and 12 trusted commands; human approval does not become a model capability.

## Working together

Use a story-linked specification before a feature PR. See [contribution guidance](CONTRIBUTING.md), [development instructions](AGENTS.md), [security guidance](SECURITY.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

Original code and documentation are available under the [MIT License](LICENSE). Third-party data and sources retain their own terms; see [source notices](THIRD_PARTY_NOTICES.md).
