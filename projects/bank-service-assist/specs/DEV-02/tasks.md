# DEV-02 task slices

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [ ] Persist Contact and server-owned ScopeSnapshot; never accept a model-supplied role.
- [x] Implement scoped context API plus loading/expired/denied states in the workspace.
- [ ] Add access tests for representative, specialist and feedback roles; sanitize errors and traces.
- [ ] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [ ] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.
