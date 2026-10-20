# DEV-04 — Explain the recorded status and next step of an existing case

BANK-S02-v0.4 · Verified inbound read increment implemented; full story/UAT pending.
Forecast: S03 | Release: B0 | Estimate: Dev 2, BA 0.25, QA 0.5 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [x] Implement scoped case/timeline endpoints and ordered event history. (verified inbound slice)
- [x] Render status source timestamp, pending requirement and ownership; distinguish no case from unavailable data. (verified inbound slice)
- [x] Handle conflicting events explicitly; don't silently pick a convenient narrative. (verified inbound slice)
- [ ] Implement and record DEV-04-T01: open timeline.
- [ ] Implement and record DEV-04-T02: request customer explanation.
- [ ] Implement and record DEV-04-T03: render case history.
- [ ] Implement and record DEV-04-T04: read case.
- [ ] Implement and record DEV-04-T05: read linked work.
- [ ] Implement and record DEV-04-T06: refresh.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.

## Inbound implementation increment — 20 October 2026

[Runtime contract and CK-01–07 scenarios](runtime-contract.md) ·
[Execution evidence and remaining boundaries](implementation-evidence.md).

The current increment supports verified inbound case reads only. Assigned outbound
feedback scope, Agent delegation and referral submission are not implemented.
Existing work produces a review/reuse hint; submission-time atomic duplicate
protection remains a DEV-07 obligation. No case mutation is exposed.
