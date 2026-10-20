# OPS-01 — Package the application and establish CI release artifacts

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S02 | Release: B0/B1 | Estimate: Dev 2, BA 0, QA 0.5 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Build versioned frontend/API/worker images and Compose configuration with private database networking.
- [ ] Configure CI lint/type/fast tests and isolated integration checks; retain Python 3.9/3.12 pure evaluation coverage.
- [ ] Keep secrets server-side, provide validated .env.example, scan for accidental keys/data and record image/config versions.
- [ ] Implement and record OPS-01-T01: build frontend/API/worker artifacts.
- [ ] Implement and record OPS-01-T02: run pipeline.
- [ ] Implement and record OPS-01-T03: start Compose demo.
- [ ] Implement and record OPS-01-T04: check secret/data exclusions.
- [ ] Implement and record OPS-01-T05: write release evidence.
- [ ] Implement and record OPS-01-T06: follow runbook.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.
