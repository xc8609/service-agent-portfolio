# Service Agent Portfolio

[![Checks](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/portfolio-checks.yml)
[![Bank runtime](https://github.com/xc8609/service-agent-portfolio/actions/workflows/bank-runtime.yml/badge.svg)](https://github.com/xc8609/service-agent-portfolio/actions/workflows/bank-runtime.yml)

**Turn a customer-service problem into requirements, a working workflow and reviewable Agent assistance.**

The first case: **“I bought once — why do I see two credit-card charges?”**
Representatives need to find customer information across screens, work within access
restrictions and learn the right handling procedure. This project brings permitted
transactions, existing cases, rules and accountable follow-up into one workspace.

**Start here:** [one-page case study](docs/case-study.md) ·
[five-minute demo script and screenshots](docs/demo.md) ·
[run locally](#run-the-demo) · [Trello](https://trello.com/b/wtNhuN0q/ai-agent)

## What the portfolio demonstrates

| Business need | BA design | Working software |
|---|---|---|
| Find information without losing context | Current/target process, role matrix, source evidence | Authorized transaction, case and rule lookup |
| Handle an uncertain complaint consistently | Customer statement vs source fact; paired unresolved enquiry; missing-material ownership | Reviewed intake, linked existing work, specialist handoff |
| Give staff useful assistance | Facts / To confirm / Next step; explicit human decision rights | Bounded read/draft tools, cited editable notes, stale-evidence checks |
| Keep follow-up accountable | Approved customer wording, fresh verification, closure conditions | Specialist findings, manual callback records, visible closure blockers |

**Intended value:** less search effort, fewer avoidable handoff omissions and more
consistent handling. Measured savings and production outcomes are not yet claimed.
The [four-task rehearsal](projects/bank-service-assist/evaluation/effort/results-20261022.md)
found fewer page changes, but missing transaction fields and handoff details;
it does not establish a time saving. The [targeted retest](docs/uat/2026-10-22-lookup-gap-retest.md)
now verifies complete transaction fields and preserved customer context.

| Inspect the evidence | Review the Agent draft | Keep unfinished work visible |
|---|---|---|
| ![Two posted transactions; equal amounts do not establish a duplicate](docs/images/lookup-fixed-manual.png) | ![Offline Agent separates facts, uncertainty and next step; draft awaits staff review](docs/images/lookup-fixed-handoff.png) | ![Feedback delivered, case still open, with explicit closure blockers](docs/images/closure-checklist.png) |

Actual synthetic app captures; [rules view and capture notes](docs/demo.md#screenshots-and-provenance).

## What runs today

- **Bank workflow:** lookup → rules → reviewed enquiry → specialist finding → verified
  customer feedback. Existing-case checks and human-confirmed closure are implemented.
- **Agent runtime:** authorized evidence, allowlisted read/draft tools, bounded runs,
  citations and manual fallback. **The app uses a scripted offline provider.** It does
  not interpret arbitrary questions; live model APIs are deferred.
- **Model exploration:** [12 Codex subscription scenarios](projects/bank-service-assist/evaluation/r2/subscription-results-20261022.md)
  record actual answers and corrections separately from application execution.
  Cases and review are AI-assisted, not an independent benchmark.
- **Data analysis:** [complaint operations analytics](projects/complaint-analytics/README.md)
  uses 27,011 public CFPB complaints, SQL and Tableau; its frozen routing baseline
  reached 81.7% team accuracy vs 31.5% majority. These public complaints are separate
  from the bank app's synthetic operational records.

**Verification suite — 23 October 2026:** **294 API tests and 45 browser tests**, plus
container smoke and offline Python 3.9/3.12 checks. [Dated regression and retest evidence](docs/uat/2026-10-23-utc-date-retest.md).
The disposable browser-test server and workflow tests share a fixed clock; the
interactive demo retains real service hours, covered by an out-of-hours regression.
[38 requirements trace to tests](docs/backlog/traceability-matrix.md).
Owner UAT, human effort measurement, Tableau refresh acceptance and public deployment
remain separate gates. Historical reports retain their original counts and limitations.

## Repository map

```text
docs/case-study.md + demo.md      Reviewer introduction and five-minute presentation
docs/backlog/                    Story cards, Sprint forecast and current scope
projects/bank-service-assist/
  docs/                          BA discovery, processes, rules and decisions
  specs/<STORY-ID>/               Requirements, design, tasks and acceptance
  specs/contracts/               Permissions, data model and tool/API contracts
  evaluation/                    Model exercises, results and limitations
apps/web/                        React/TypeScript workspace and browser tests
services/api/bank_api/
  agent/                         Bounded runtime and provider adapters
  integrations/                  Source-mapping validation
services/api/tests/              PostgreSQL-backed API regressions
projects/complaint-analytics/    Public-data SQL, Tableau and routing evidence
docs/uat/ + .github/workflows/   Acceptance records and CI
```

## Run the demo

Requires Docker Compose. No model key is needed:

```bash
python3 scripts/configure_demo.py
docker compose up --build --wait
```

Open **http://127.0.0.1:8000** and follow the [demo preparation and walkthrough](docs/demo.md).
Keep this synthetic demo on localhost; its persona selector is a local identity
simulation. [Mac setup without Docker, tests and recovery](services/api/README.md).

## Architecture and extension points

**React/TypeScript → FastAPI/Python → PostgreSQL**, packaged with Docker Compose.
The Agent runs inside the API. Trusted commands enforce permissions, evidence versions,
human approval, receipts and audit history.

Institution-specific sources map into a canonical read model; server-owned profiles
select the model protocol. Two source formats and three model protocols have offline
tests. Real bank ingestion and live route qualification remain future integration work.
[Architecture](docs/architecture.md) · [Adaptation examples](examples/README.md).

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) and
[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) are design
references, not claimed dependencies. [ADR-004](docs/architecture/ADR-004-lightweight-enterprise-adaptation.md)
explains the small custom runtime and what can change for an actual institution.

## Next delivery

Use the corrected demo for owner review. The targeted T1/T4 retest now covers all
required items; human effort measurement remains unproven. Keep the next step small:
a human walkthrough and feedback on clarity. A hosted synthetic demo can follow an
explicit hosting decision. API integration, voice and retail stay later.
[Current delivery and Sprint context](docs/backlog/current-delivery.md).

[Business analysis](projects/bank-service-assist/docs/README.md) ·
[Detailed design](projects/bank-service-assist/specs/README.md) ·
[UAT](docs/uat/README.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) ·
[MIT](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md).

Independent portfolio work. Bank operational records and business rules are simulated;
public analytics data has its own provenance and terms.
