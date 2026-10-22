# QA-02-R1 task slices

- [x] Version bounded normalized recording format; explicit synthetic provenance.
- [x] Record actual request hashes and normalized replies through Provider wrapper.
- [x] Replay only matching messages/schema; reject drift, exhaustion and unused suffix.
- [x] Exercise real runtime with isolated PostgreSQL; check no committed business writes.
- [x] Record executed local checks; link the review PR from the QA-02 Trello card.
- [ ] Capture a genuine multi-turn subscription session with operator evidence (later;
  no such recording exists in this slice).

R2 corpus/owner adjudication, G1 layered claims/review metrics, axe/latency checks,
4a benefit study, live wire qualification and deployment remain separate planned
slices in the [stage plan](../../../../docs/backlog/validation-next.md). Do not mark
the parent QA-02 or stage 1 Done from this implementation.

## Executed checks — 21 October 2026

- Full API suite: 246 passed on Python 3.12 / isolated PostgreSQL 16.2, including
  14 new replay test instances. These are synthetic engineering regressions.
- Offline suite: 20 passed. Ruff lint and format checks passed.
- Workflow and S02 contract validators, publication/link checks and diff whitespace
  checks passed. PR CI separately verifies PostgreSQL 17, browser and container paths.
- No live model calls, genuine subscription recordings, accessibility audit, measured
  latency study or participant benefit study were performed for this slice.
