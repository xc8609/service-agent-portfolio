# DEV-05 task slices

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [x] Author explicitly fictional policy editions and conflicting/expired examples with provenance.
- [x] Implement metadata filtering and section retrieval before model summarization.
- [x] Render cited sections and a manual search fallback; keep customer instructions untrusted.
- [x] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [x] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

Implemented scope and remaining gates: [runtime contract](runtime-contract.md), [executed checks](implementation-evidence.md). AC05 model evaluation remains pending even though deterministic boundaries are tested.
