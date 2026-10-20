# DEV-09 — Qualify model runtime and provider adapters with a bounded spike

BANK-S02-v0.4 · Offline implementation delivered for PR review; live qualification deferred by owner.
Forecast: S04 | Release: B1 | Estimate: Dev 4, BA 0.25, QA 1 person-days. Provisional until technical review.

## Business purpose and scope

As an engineer, I want interchangeable qualified model providers so that business behavior is not tied to one vendor's SDK.

Value: Demonstrate practical API integration and architectural trade-offs. Owner relevance: customer-service desktop, banking product/BA and prior frontend experience. Target-role evidence: repository R01/R02/R06 requirements/API/testing/enterprise delivery samples; no new vacancy or proficiency claim.

No fine-tuning, local model hosting or additional paid deployment required by this spike alone. All operational scenarios and records are synthetic.

Requirements: FR-14. Dependencies: BA-07, BA-08, DEV-01.

## Delivery flow

1. Define normalized text/tool/usage/error/cancel events; keep authorization and persistence in application services.
2. Qualify one OpenAI route and one Claude route when credentials/budget are available. Document DeepSeek/internal compatible endpoint gaps; do not claim untested compatibility.
3. Add fake-provider fixtures for offline CI, endpoint allowlist, server-only credentials and no public fallback in internal-only mode.

## Acceptance criteria

- **DEV-09-AC01** — Given Offline fake provider and fixed tool response fixtures; when run normalized multi-turn conversation; then same domain tool schemas and server authorization run without vendor credentials. Evidence: DEV-09-T01, planned/not executed.
- **DEV-09-AC02** — Given Streaming provider emits partial/invalid tool arguments; when receive tool event; then buffer until complete, validate schema, execute no partial/invalid call; bounded repair or safe failure. Evidence: DEV-09-T02, planned/not executed.
- **DEV-09-AC03** — Given Rate limit, timeout, cancellation or missing usage; when handle event; then return typed terminal status; no duplicate operational effect; missing usage/cost stays unavailable, not zero. Evidence: DEV-09-T03, planned/not executed.
- **DEV-09-AC04** — Given Internal-only profile or unapproved endpoint; when attempt fallback/provider request; then deny unauthorized egress; never silently switch to a public provider. Evidence: DEV-09-T04, planned/not executed.
- **DEV-09-AC05** — Given Eligible OpenAI and Claude credentials/budget available; when run identical required scenarios; then record dated model/provider/config, tool compatibility, actual costs and failures for each; otherwise mark live qualification not executed. Evidence: DEV-09-T05, planned/not executed.
- **DEV-09-AC06** — Given Provider input contains customer/internal data outside allowed DTO; when prepare request; then exclude credentials/contact details/internal-only notes; safe trace preserves references not sensitive payload. Evidence: DEV-09-T06, planned/not executed.
- **DEV-09-AC07** — Given A live route lacks a required capability; when select route for B1; then route remains unqualified; DeepSeek/internal compatibility is not inferred from API similarity. Evidence: DEV-09-T07, planned/not executed.

## Ready and Done boundaries

Ready requires versioned technical contract/fixtures, validated dependencies and a story walkthrough. Business rules D-17–D-22 are accepted; proposed business-benefit targets and model budgets are not silently approved. Platform stories can proceed against explicitly frozen draft contracts; dependent workflow acceptance requires those contracts implemented. Done requires the listed tests and review evidence, not merely this document.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) · [Current contracts](../contracts/interface-notes.md)

## Offline delivery decision

See [implemented boundary and remaining qualification gates](runtime-contract.md). Live tests are not executed; no public provider is enabled.
