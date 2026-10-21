# DEV-13 task slices

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [ ] Add deduplicated deadline events and progress-update proposals with original due timestamps.
- [ ] Add objection/re-review linkage and proposal invalidation on new evidence.
- [ ] Build lead review UI; keep detailed exception routing disabled until rules are accepted.
- [ ] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [ ] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

- [ ] Complete next-update proposal/lead approval and progress-message contract without requiring a completed finding.
- [ ] Add independent complaint-intake reference/receipt and one-to-many objection/work linkage; route alongside specialist re-review.
- [ ] Add unauthorized commitment, duplicate event/intake, branch failure and completion-race tests from the contract addendum.

## Current delivery

[Runtime behavior and executed checks](runtime-contract.md) supersede historical implementation-pending wording. Agent drafting and owner UAT remain separate gates.
