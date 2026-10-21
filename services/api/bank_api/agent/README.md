# Bank Agent module boundary

**Design only; no executable Agent implementation yet.** DEV-08/09 own this
module. The current application works without model credentials.

Keep the first implementation inside the existing backend. Add files as their
story is implemented, rather than creating empty SDK/provider packages:

| Planned responsibility | Boundary |
|---|---|
| Orchestration | Bounded sequence of permitted reads and draft creation; stop for missing evidence, failure or human review |
| Tool adapter | Call the same authorized application services as the manual UI, with current trusted contact scope; never bypass them with direct SQL |
| Provider adapter | Translate model/tool requests and responses; qualify one provider first, then add interchangeable implementations with tests |
| Output validation | Typed facts, citations, uncertainty and proposed next action; no prose treated as proof of an operation |
| Evaluation | Synthetic scenario fixtures and deterministic fake-provider tests in the existing test suite; later live-provider results reported separately |

Implemented read contracts: `get_contact_context`, `search_transactions`,
`get_transaction_evidence`. Other model tools, including policy/case retrieval
and proposal persistence, remain planned. Human approval commands are excluded
from the model tool registry. Do not register a planned tool until its domain
service and authorization tests work.

[Detailed Agent design](../../../../projects/bank-service-assist/specs/DEV-08/design.md) ·
[Provider qualification](../../../../projects/bank-service-assist/specs/DEV-09/spec.md) ·
[Architecture](../../../../docs/architecture.md)
