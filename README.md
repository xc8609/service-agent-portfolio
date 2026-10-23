# Service Agent Portfolio

[![Checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)
[![Bank runtime](https://github.com/xc8609/service-agent-portfolio/actions/workflows/bank-runtime.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/bank-runtime.yml)

**A bank service workspace that brings transaction investigation, Agent assistance
and customer follow-up into one workflow.**

A customer asks: **“I bought once — why do I see two credit-card charges?”**
The representative needs transaction details, the right handling procedure and a
clear next step. This project connects those tasks from the first enquiry through
specialist review and customer feedback.

It combines banking product and business-analysis experience with full-stack
engineering: business problem → requirements → story cards → implementation → acceptance.

[Case study](docs/case-study.md) · [Workflow and screenshots](docs/demo.md) ·
[Run locally](#run-the-demo) · [Trello](https://trello.com/b/wtNhuN0q/ai-agent)

## The business workflow

The starting pain is fragmented information: staff move between customer records,
transaction screens, case history and handling procedures. The target is one
workspace that supports the enquiry and keeps each next step owned.

```mermaid
flowchart TD
    A[Customer questions two charges] --> B[Representative checks facts and rules]
    B --> C[Agent organizes evidence and drafts a note]
    C --> D[Representative reviews and submits enquiry]
    D --> E[Specialist investigates and publishes findings]
    E --> F[Customer service delivers approved feedback]
    F --> G{Outstanding work?}
    G -->|Yes| H[Keep open with an owner]
    G -->|No| I[Staff confirm closure]
```

| Stage | Business decision supported |
|---|---|
| Establish customer context | Which account can this representative access, and which purchase does the customer recognize? |
| Compare transactions | What do the amount, currency, dates and status actually establish? |
| Check cases and procedures | Is someone already investigating, and which handling rule applies? |
| Review the Agent draft | Are the facts, missing information and proposed next step supported by the evidence? |
| Hand off to a specialist | What needs investigation, who owns it, and what can be supplied later? |
| Follow up and close | Has the customer received the explanation, and what work still needs completion? |

Read the [five-minute walkthrough](docs/demo.md) directly on GitHub; screenshots
and decision points show the flow without installing the application.

| Investigate the charges | Review the Agent draft | Follow through to resolution |
|---|---|---|
| ![Transaction comparison with currency and posting dates](docs/images/lookup-fixed-manual.png) | ![Customer statement and three-part Agent summary](docs/images/lookup-fixed-handoff.png) | ![Customer feedback and remaining follow-up actions](docs/images/closure-checklist.png) |

## How the Agent fits

The Agent gathers transaction, case and procedure evidence through scoped tools,
keeps source references with its draft, and saves the result for staff review.
Staff can edit, approve or return a draft. Evidence changes trigger a fresh review;
permissions and business actions are enforced by the application.

The design separates **model providers**, **tool contracts** and **business workflow**.
This keeps model integration adaptable while retaining the same review and handoff process.
[Agent and application architecture](docs/architecture.md).

## From BA design to working software

The [case study](docs/case-study.md) explains the current process, target workflow,
responsibilities and intended business value. Process maps, decision rights and
story acceptance criteria connect to implementation and tests through
[38 requirements](docs/backlog/traceability-matrix.md).

The bank core has passed its [delegated workflow assessment](docs/uat/bank-core-closeout.md).
As of 23 October 2026, verification includes **294 API tests, 45 browser tests**,
container smoke and offline Python 3.9/3.12 checks. A lookup rehearsal led to
specific improvements in transaction details and handoff completeness;
[findings and retest](docs/uat/2026-10-22-lookup-gap-retest.md) show that feedback loop.

The companion [complaint analytics case](projects/complaint-analytics/README.md) uses
27,011 public CFPB complaints, SQL and Tableau to explore service operations. Its
frozen routing baseline reached 81.7% team accuracy versus 31.5% for the majority baseline.

## Technology and structure

**React / TypeScript → FastAPI / Python → PostgreSQL**, packaged with Docker Compose
and tested with pytest, Playwright and GitHub Actions.

Transaction-source mapping examples and model-provider adapters sit behind small,
defined interfaces. Provider adapters cover OpenAI Responses, Claude Messages and
compatible-chat protocols. [Adaptation examples](examples/README.md) and
[design decisions](docs/architecture/ADR-004-lightweight-enterprise-adaptation.md)
explain how to extend the project for an institution's data and processes.

```text
docs/case-study.md + demo.md      Project overview and walkthrough
docs/backlog/                    Story cards, Sprint planning and traceability
projects/bank-service-assist/
  docs/                          Business analysis, processes and decisions
  specs/<STORY-ID>/               Requirements, design, tasks and acceptance
  specs/contracts/               Permissions, data model and tool/API contracts
  evaluation/                    Evaluation cases and results
apps/web/                        React workspace and browser tests
services/api/bank_api/
  agent/                         Agent runtime and provider adapters
  integrations/                  Transaction-source mapping
services/api/tests/              API and workflow regression tests
projects/complaint-analytics/    SQL, Tableau and complaint-routing analysis
docs/uat/ + .github/workflows/   Acceptance evidence and CI
```

## Run the demo

Requires Docker Compose:

```bash
python3 scripts/configure_demo.py
docker compose up --build --wait
```

Open **http://127.0.0.1:8000** and follow the [five-minute walkthrough](docs/demo.md).
The local demo uses synthetic bank records, simulated roles and an offline scripted
Agent provider; no model key is needed.
[Mac setup, tests and recovery](services/api/README.md).

## Roadmap

Current focus: present the business workflow, BA decisions and acceptance evidence
directly on GitHub. Public hosting and live-model integration are deferred.
Future extensions include telephone self-service with human handoff and retail clienteling.
[Delivery plan](docs/backlog/current-delivery.md).

[Business analysis](projects/bank-service-assist/docs/README.md) ·
[Detailed design](projects/bank-service-assist/specs/README.md) ·
[Acceptance](docs/uat/bank-core-closeout.md) · [Contributing](CONTRIBUTING.md) ·
[Security](SECURITY.md) · [MIT](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
