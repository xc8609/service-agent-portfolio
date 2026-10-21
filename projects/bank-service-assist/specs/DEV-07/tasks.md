# DEV-07 task slices

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [x] Draft [intake review refinement](referral-intake-review.md) for one recognized
  purchase and two posted entries; business decisions are recorded below; no implementation acceptance implied.
- [x] Record owner acceptance of RI-01 as D-23.
- [x] Record owner acceptance of RI-02 as D-24.
- [x] Record owner acceptance of RI-03 as D-25.
- [ ] Close [readiness gaps](referral-readiness.md) and assess contract/data/estimate
  impact before implementing intake criteria RI-AC01–17.
- [ ] Close Ready gates and accept technical/data contract.
- [x] Add referral payload and unique operation key, queue ownership and case/work-item versions.
- [x] Build review/edit UI with draft/submitting/queued/failed/unknown states.
- [x] Implement outbox replay and operation reconciliation without duplicate work.
- [x] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [x] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 explicitly splits into 3+4 developer-days. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

## Current implementation update

The [v0.5 runtime contract](runtime-contract.md) supersedes historical initial-intake
implementation gates above. See [executed evidence](implementation-evidence.md).
Post-intake supplementation/contact resolution and owner acceptance remain pending.
