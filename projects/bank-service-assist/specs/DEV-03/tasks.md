# DEV-03 task slices

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [x] Create deterministic synthetic ledger and statement-view fixtures including unlinked equal amounts.
- [x] Implement filtered/paginated search and a selected-record comparison UI.
- [ ] Invalidate affected proposals after transaction selection or customer correction changes.
- [ ] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [ ] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

## Current implementation slice — 20 October 2026

[Lookup execution evidence](../../docs/sprint-02/implementation/lookup-evidence.md). Only the explicitly mapped read-path cases have executed evidence. The historical contract/forecast above remains the full-story scope; no owner UAT, worker, write-effect or model acceptance is implied.

## Manual statement and recognition increment — 20 October 2026

[Detailed runtime contract and SI-01–06 acceptance scenarios](investigation-contract.md)
cover customer statement revisions, explicit recognition including D-23 unresolved
pairs, and immediate invalidation after query/selection/statement changes.
See [execution evidence](implementation-evidence.md) for tested scope and limits.

- [x] Implement strict scoped human save/read endpoints and append-only report revisions.
- [x] Implement explicit pair recognition and immediate UI evidence invalidation.
- [x] Exercise new API/database and browser scenarios, including lost responses and delayed reads.
- [ ] Implement future proposal invalidation/commit binding with DEV-06/07.
- [ ] Complete existing-case status/details in DEV-04 and owner UAT.
