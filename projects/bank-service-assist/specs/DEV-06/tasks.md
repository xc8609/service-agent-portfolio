# DEV-06 — Review, edit and commit a contact note safely

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S04 | Release: B0 | Estimate: Dev 5, BA 0.5, QA 1 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Implement versioned draft and approval endpoints with actor, source versions and operation key.
- [ ] Commit note and audit/outbox event atomically; preserve edits on stale-version conflicts.
- [ ] Build editable note preview with clear unsaved/committed status; deterministic manual template first.
- [ ] Implement and record DEV-06-T01: staff edits and approves current proposal revision.
- [ ] Implement and record DEV-06-T02: approve.
- [ ] Implement and record DEV-06-T03: save both.
- [ ] Implement and record DEV-06-T04: retry.
- [ ] Implement and record DEV-06-T05: retry.
- [ ] Implement and record DEV-06-T06: review/commit.
- [ ] Implement and record DEV-06-T07: submit.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.
