# DEV-09 — Qualify model runtime and provider adapters with a bounded spike

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S04 | Release: B1 | Estimate: Dev 4, BA 0.25, QA 1 person-days. Provisional until technical review.

| AC | Test | Expected outcome | Actual evidence | Status |
|---|---|---|---|---|
| DEV-09-AC01 | DEV-09-T01 | same domain tool schemas and server authorization run without vendor credentials | Pending implementation | Not executed |
| DEV-09-AC02 | DEV-09-T02 | buffer until complete, validate schema, execute no partial/invalid call; bounded repair or safe failure | Pending implementation | Not executed |
| DEV-09-AC03 | DEV-09-T03 | return typed terminal status; no duplicate operational effect; missing usage/cost stays unavailable, not zero | Pending implementation | Not executed |
| DEV-09-AC04 | DEV-09-T04 | deny unauthorized egress; never silently switch to a public provider | Pending implementation | Not executed |
| DEV-09-AC05 | DEV-09-T05 | record dated model/provider/config, tool compatibility, actual costs and failures for each; otherwise mark live qualification not executed | Pending implementation | Not executed |
| DEV-09-AC06 | DEV-09-T06 | exclude credentials/contact details/internal-only notes; safe trace preserves references not sensitive payload | Pending implementation | Not executed |
| DEV-09-AC07 | DEV-09-T07 | route remains unqualified; DeepSeek/internal compatibility is not inferred from API similarity | Pending implementation | Not executed |

Record environment, commit, fixture/calendar/provider versions, command, actual result, defects and reviewer. Artifact checks are separate from runtime acceptance.
