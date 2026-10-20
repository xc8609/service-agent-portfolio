# DEV-12 task slices

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [ ] Implement versioned calendar calculations and persisted attempts; reserve slots to prevent concurrent duplicates.
- [ ] Add queue lead review state and callback constraints with manual fallback.
- [ ] Implement server closure preconditions and reasoned rejection with preserved notes.
- [ ] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [ ] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

- [ ] Implement D-18 server-derived quota and auditable technical faults; add DEV-12-T01 paired fixtures and idempotent replay checks without deadline extension.

- [ ] Implement D-19 versioned three-service-date deadline and DEV-12-T04 boundary/holiday/DST/fault fixtures. Preserve separate first-callback overdue tracking.

- [ ] Implement D-22 typed lead-approved plan/hold with reason, version checks, immutable history, bounded plan limits and review due work. Complete AC03/AC07 permission, replay and stale-approval fixtures.
