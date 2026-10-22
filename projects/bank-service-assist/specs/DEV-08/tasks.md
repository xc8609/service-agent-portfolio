# DEV-08 task slices

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-SDD-v0.2

- [x] Draft story, design and Given/When/Then examples.
- [ ] Close Ready gates and accept technical/data contract.
- [ ] Slice A (3 developer-days): runtime adapter, tool allowlist, bounded execution and deterministic fake-provider tests.
- [ ] Slice B (4 developer-days): durable run/proposal records, streamed evidence UI, resume and failure recovery; evaluate actual integration overhead after contracts.
- [ ] Instrument safe run/tool/operation correlations; normalize provider output and never treat model prose as execution proof.
- [ ] Implement story-specific acceptance tests and fault/recovery coverage.
- [ ] QA walks through normal and adverse paths using versioned synthetic fixtures.
- [ ] Update support notes, migrations and release evidence.
- [ ] Owner reviews demonstrated behavior and records acceptance.

Each implementation slice must be at most five developer-days; DEV-08 now totals 9 developer-days and splits into runtime/tools, durable continuation and UI/integration slices of approximately 3 days each; v0.3 supersedes the older 3+4 estimate. Other listed stories are at most four developer-days before re-estimation. BA/QA estimates are separate. New stories are incremental scope, not hidden inside DEV-07.

## Current offline delivery

See [implemented runtime, executed tests and remaining gates](runtime-contract.md). Historical live-provider/streaming/effort-study acceptance is not marked complete.

## Core context increment — 22 October

[Staff question and scoped transaction context](core-context.md) defines CC-01–09,
implementation boundaries and actual verification evidence for the simplified portfolio.

- [x] Capture 12 authorized synthetic scenario inputs and retain first subscription answers.
- [x] Review answers as disclosed same-session AI assistance; preserve corrections separately.
- [x] Fix read-assistance recognition conditions and reuse workspace policy-state handling.
- [x] Verify active-work/missing-description/feedback reminders and add transition regressions.
- [ ] Owner UAT / live provider qualification remain separate, not inferred from this exercise.
