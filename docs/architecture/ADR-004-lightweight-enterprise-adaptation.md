# ADR-004 — A small business core with explicit adaptation boundaries

20 October 2026 · Owner-directed engineering follow-up to DEV-02/08/09.
Decision: retain one React app, one FastAPI app and one PostgreSQL workflow store.
One institution per deployment is the initial target; multi-tenant hosting is not
implemented. No claim of production bank connectivity or SDK qualification.

## Business reason

The owner's representative-desktop experience identifies repeated customer-information
navigation, restricted access and learning handling rules as the main pain points.
The portfolio demonstrates the ability to turn those needs into roles, process,
exceptions, stories, contracts, implementation and reviewable evidence. Configurable
infrastructure supports that work; it is not the product's primary outcome.

Start with “I bought once, but see two charges.” Assemble authorized source facts,
distinguish the customer's statement from recorded evidence, locate related work
and rules, and draft a next step. Preserve missing-material/contact obligations and
human specialist decisions. Do not build a general bank platform or a refund agent.

## Decisions and implementation boundaries

| Boundary | Implemented now | Adaptation and remaining qualification |
|---|---|---|
| Enterprise transaction data | PostgreSQL canonical read model; offline normalization preview for two explicitly synthetic export formats | A reviewed read-only DB view, export or API adapter must feed that read model. Real connectors, atomic ingestion, version reconciliation and freshness gating are not implemented. Changing BANK_DATABASE_URL is **not** a connector to an arbitrary bank database. |
| Workflow persistence | PostgreSQL migrations, restricted runtime role, transactional audit/receipts/outbox | Keep this store independent of external source schemas. No promise of switching the application's database engine by config. |
| Model API | Server-selected profile; normalized Responses/Messages/compatible-chat adapters; disabled by default; mock HTTP evidence | Exact endpoint, model revision, credential environment reference and qualification are deployment settings. DeepSeek/internal compatibility must be tested against the actual endpoint. |
| Agent runtime | One bounded evidence/draft loop with current scope and version checks | An SDK runtime is a future alternative loop, not another planner wrapped around this loop. Retain the same tool and human-command contracts. |
| Institution process | Versioned policy rows, queue/role data and explicit simulated deadlines | Review rule changes with the business owner; configuration cannot widen permissions or silently reinterpret historical deadlines. Some rules remain code and require a spec/test change. |
| Identity / channels | Local synthetic identity and manual telephone outcome capture | Production SSO/customer verification and telephony are separate adapters and release gates, not enabled by model configuration. |

External source facts should land in a canonical, versioned projection, while all
runtime reads and approval rechecks use a consistent local snapshot. Direct remote
queries inside a business transaction would introduce inconsistent evidence and
unbounded dependency failure; use that approach only after an explicit redesign.
No arbitrary SQL, enterprise credentials or bank connection strings go to the Agent.

## Agent structure and selection

- `agent/runtime.py`: scope rehydration, tool ordering, bounded execution, persistence,
  cited draft validation and replay. Tool schemas remain next to their small workflow.
- `agent/providers.py`: provider-independent calls/replies and vendor wire adapters.
- `agent/selection.py`: one server-owned profile and audit fingerprint; no user/model
  choice of endpoint, no automatic provider failover. Switching applies to new runs;
  existing trigger keys replay their recorded results.
- Existing domain services own deterministic rules, permissions and writes. Business
  tools read or draft; an authenticated human must execute the trusted command.
- `integrations/transactions.py`: standalone offline onboarding validation. This
  utility is not a deployed ingestion service and does not write database records.

Unknown usage remains unknown. Configured `qualified: true` is an operational gate,
not evidence that a model has passed tests; it only takes effect when
`qualified_fingerprint` matches the route's identity fingerprint, so a later model,
endpoint or credential-reference change silently loses qualification rather than
inheriting it. The release owner must retain the dated
qualification report and approved budget; no candidate is qualified in this repo.

## Reference review and deliberate differences

Official sources reviewed 20 October 2026:

- [OpenAI Agents SDK Model/ModelProvider interfaces](https://github.com/openai/openai-agents-python/blob/main/src/agents/models/interface.py)
  separate model lookup and calls from orchestration. We use a small Python protocol
  boundary today; SDK adoption is not claimed.
- [OpenAI tool guardrails and approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
  inform checks at tool execution boundaries. Our server still enforces current
  identity, account scope and evidence versions for every step.
- [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
  supports custom tools via in-process MCP servers. Its `allowed_tools` setting
  pre-approves tools; it does not remove other tools. A future SDK spike must explicitly
  restrict the toolset and deny unused filesystem/shell capabilities, then test denial.
- [Anthropic's effective-agent guidance](https://www.anthropic.com/research/building-effective-agents)
  supports simple composable patterns. Our predictable bank workflow does not yet
  justify a manager/specialist/reviewer network.

OpenAI Agents Python and Claude Agent Python SDK repositories both publish MIT
licenses ([OpenAI](https://github.com/openai/openai-agents-python/blob/main/LICENSE),
[Anthropic](https://github.com/anthropics/claude-agent-sdk-python/blob/main/LICENSE)).
This describes SDK code, not model weights, hosted API access or all bundled runtime
terms. Direct Messages API support is not the same as adopting Claude Agent SDK.

A locally reviewed sibling application also informed the separation of provider,
runtime, tool authority and evidence. No sibling source code, private configuration
or domain data is copied into this public repository. Its research-oriented specialist
orchestration is deliberately not added to this service workflow.

## Success and deployment gates

Compare manual B0 and assisted B1 on the same labelled synthetic cases: time to find
correct evidence, rule applicability, unsupported claims, appropriate escalation,
draft corrections and task completion. Include model latency/cost and human review
work when measuring effort. Results and cost savings are not yet measured. Source
mapping consistency and protocol compatibility are engineering acceptance, not proof
of customer-service benefit.

Production onboarding requires approved field/identity mappings, source ownership and
freshness rules, least-privilege credentials, data handling approval, institution-specific
policies, one qualified model, recovery testing and owner UAT. Deploy the same small
application with separate configuration/secrets; do not turn on multi-tenancy, financial
execution or autonomous calls as a side effect of integration. Roll back a model route
to the offline/manual path without changing recorded business outcomes.

See the [implementation change and acceptance](../../projects/bank-service-assist/specs/contracts/extensibility-change.md)
and [onboarding examples](../../examples/README.md).
