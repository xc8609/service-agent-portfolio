# QA-01 — Implement layered verification and requirement-to-test coverage

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 1.5, BA 0.5, QA 1.5 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Use pytest for pure rules/API tests, isolated PostgreSQL integration tests and Playwright for critical UI journeys.
- [ ] Implement fault cases: denied scope, invalid payload, stale version, duplicate request, worker crash, policy gap and provider failure.
- [ ] Make CI run meaningful fast checks on PRs; live-model, full data and deployment checks are separate explicitly triggered suites.
- [ ] Implement and record QA-01-T01: build coverage manifest.
- [ ] Implement and record QA-01-T02: run authorization integration suite.
- [ ] Implement and record QA-01-T03: run real test-Postgres transaction suite.
- [ ] Implement and record QA-01-T04: execute suite.
- [ ] Implement and record QA-01-T05: publish test report.
- [ ] Implement and record QA-01-T06: evaluate release gate.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.
