# DEV-01 — Create the application skeleton and deterministic demo environment

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S02 | Release: B0 | Estimate: Dev 3, BA 0.25, QA 0.5 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Create React/TypeScript UI, FastAPI service, PostgreSQL migration setup and health/readiness endpoints.
- [ ] Add isolated synthetic seed/reset command, configuration validation and safe .env.example.
- [ ] Keep Python 3.9 evaluation modules separate from Python 3.12 application dependencies; lock versions after compatibility checks.
- [ ] Implement and record DEV-01-T01: run documented migration and seed commands twice.
- [ ] Implement and record DEV-01-T02: start UI/API/worker and complete manual lookup.
- [ ] Implement and record DEV-01-T03: check liveness and readiness.
- [ ] Implement and record DEV-01-T04: request reset.
- [ ] Implement and record DEV-01-T05: install Python 3.12 application dependencies in separate environment.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.
