# DEV-09 — Qualify model runtime and provider adapters with a bounded spike

[Current implementation and qualification limits](runtime-contract.md). Historical forecasts are not actual effort; owner UAT remains pending.

BANK-S02-v0.4 · Offline implementation delivered for PR review; live qualification deferred by owner.
Forecast: S04 | Release: B1 | Estimate: Dev 4, BA 0.25, QA 1 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-09-AC01 | DEV-09-T01 | same domain tool schemas and server authorization run without vendor credentials | test_providers: normalized schemas and offline requests | Offline pass |
| DEV-09-AC02 | DEV-09-T02 | buffer until complete, validate schema, execute no partial/invalid call; bounded repair or safe failure | test_providers: buffered partial JSON and strict validation | Offline pass; live stream qualification deferred |
| DEV-09-AC03 | DEV-09-T03 | return typed terminal status; no duplicate operational effect; missing usage/cost stays unavailable, not zero | test_providers + test_agent: typed errors, replay and unknown usage | Offline pass |
| DEV-09-AC04 | DEV-09-T04 | deny unauthorized egress; never silently switch to a public provider | test_providers: endpoint/internal allowlist and no redirect/fallback | Offline pass |
| DEV-09-AC05 | DEV-09-T05 | record dated model/provider/config, tool compatibility, actual costs and failures for each; otherwise mark live qualification not executed | Owner explicitly deferred all real-provider qualification | Not executed: owner deferred |
| DEV-09-AC06 | DEV-09-T06 | exclude credentials/contact details/internal-only notes; safe trace preserves references not sensitive payload | test_providers + test_agent: positive DTO and private-note exclusion | Offline pass |
| DEV-09-AC07 | DEV-09-T07 | route remains unqualified; DeepSeek/internal compatibility is not inferred from API similarity | test_providers: disabled/unqualified route rejected before transport | Automated pass |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.

## Offline delivery decision

See [implemented boundary and remaining qualification gates](runtime-contract.md). Live tests are not executed; no public provider is enabled.
