# DEV-09 — Qualify model runtime and provider adapters with a bounded spike

BANK-S02-v0.4 · Offline implementation delivered for PR review; live qualification deferred by owner.
Forecast: S04 | Release: B1 | Estimate: Dev 4, BA 0.25, QA 1 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Define normalized text/tool/usage/error/cancel events; keep authorization and persistence in application services.
- [ ] Qualify one OpenAI route and one Claude route when credentials/budget are available. Document DeepSeek/internal compatible endpoint gaps; do not claim untested compatibility.
- [ ] Add fake-provider fixtures for offline CI, endpoint allowlist, server-only credentials and no public fallback in internal-only mode.
- [ ] Implement and record DEV-09-T01: run normalized multi-turn conversation.
- [ ] Implement and record DEV-09-T02: receive tool event.
- [ ] Implement and record DEV-09-T03: handle event.
- [ ] Implement and record DEV-09-T04: attempt fallback/provider request.
- [ ] Implement and record DEV-09-T05: run identical required scenarios.
- [ ] Implement and record DEV-09-T06: prepare request.
- [ ] Implement and record DEV-09-T07: select route for B1.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.

## Offline delivery decision

See [implemented boundary and remaining qualification gates](runtime-contract.md). Live tests are not executed; no public provider is enabled.
