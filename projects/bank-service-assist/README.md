# Bank Service Assist

A service-desk workspace for **“What is this charge?”** and **“Why are there two
entries?”** It brings customer context, transaction evidence, handling rules and
follow-up into one flow, helping representatives find information and prepare a
clear handoff.

## Working features

- **Customer and transaction lookup:** role-based access, transaction status,
  currency and UTC dates, with the customer's statement recorded separately.
- **Case and rule retrieval:** related enquiries, responsible teams, current progress
  and applicable procedures alongside the selected transactions.
- **Agent assistance:** a source-linked **Facts / To confirm / Next step** summary
  and an editable note draft for staff review.
- **Specialist handoff:** reviewed referrals carry the selected transactions,
  recognition scope and missing-material details into existing or new work.
- **Feedback and closure:** approved explanations, verified callback records,
  follow-up ownership and a checklist showing what remains before closure.

The local demo uses synthetic records and business rules with a scripted offline
Agent provider; no model API key is needed.

## From requirements to working software

The case connects banking service-desk experience to process analysis, story cards,
permissions, acceptance criteria and tested implementation. The core passed its
[delegated acceptance review](../../docs/uat/bank-core-closeout.md), supported by
294 API and 45 browser tests.

**Stack:** React/TypeScript → FastAPI/Python → PostgreSQL, with Docker Compose for
local setup. Source mappings and model-provider interfaces provide extension points
for different institutions.

| Explore | Contents |
|---|---|
| [Five-minute demo](../../docs/demo.md) · [Case study](../../docs/case-study.md) | Scenario, workflow and screenshots |
| [Run and test](../../services/api/README.md) | Local setup, verification and reset instructions |
| [Business analysis](docs/README.md) | Problem, target process, rules and decisions |
| [Stories and Sprints](../../docs/backlog/README.md) · [Specifications](specs/README.md) | Requirements, design, tasks and acceptance criteria |
| [Architecture](../../docs/architecture.md) | Agent tools, commands and integration boundaries |
| [Acceptance evidence](../../docs/uat/bank-core-closeout.md) · [Data sources](data/README.md) | Executed checks and dataset provenance |

Next increments: hosted demo, live-model integration, then voice and retail cases.
