# DEV-05 execution evidence

20 October 2026 · Branch `codex/dev-05-handling-rules`, based on DEV-04 PR #3.
Inbound read increment; owner walkthrough acceptance and merge pending.

## Implemented

`policy_lookup.py`, migration 005, synthetic policy fixtures and React handling-rule
panel. Pair-specific human reads plus v0.4 `search_policy` and `get_policy_section`.
Permitted source filtering, citation/conditions/next steps, gaps/conflicts,
authority rechecks and transaction-version binding. See [runtime contract](runtime-contract.md).

## Checks executed locally

- Python 3.12.14 + disposable PostgreSQL 16.2: 105 API tests passed (27 new
  policy cases); existing Starlette/httpx deprecation warning remains.
- TypeScript check and Vite production build passed.
- Ruff check and format passed.
- Extended HTTP smoke passed: transaction evidence, customer-report replay,
  related-case progress, matching policy and exact canonical citation.
- Playwright: 23 browser journeys passed (8 new policy journeys), including delayed
  responses, query/selection/statement/identity invalidation, source markup and failures.
- Offline tests: 5 passed. Workflow and S02 v0.4 contract checks passed (using
  pinned offline jsonschema 4.25.1/tzdata 2025.2); publication/local-link checks passed.
- `git diff --check` passed.

During verification, the effective-time assertion was corrected to compare
instants across PostgreSQL session offsets. An unsupported-status test now uses
the schema's permitted `reversed` value instead of bypassing its check constraint.
Browser regression exposed duplicate sibling component keys between case/rule
panels; unique prefixes fix invalidation. The original case regression is retained. A new browser locator was corrected to
use the textbox accessible name when saved text already exists.

## Limits and next work

No LLM, semantic search, actual policy ingestion/approval, assigned callback role,
refund, referral mutation or independent owner UAT. Literal search and exact read
are real endpoints; the UI uses deterministic pair lookup/manual refresh. Both
rule bodies and operational records are synthetic. Model-safe tool boundaries
are tested; this is not evidence of a model resisting prompt injection.

Existing-volume upgrade preserves account jurisdiction as unknown rather than
inventing it. Use a new isolated synthetic demo for the v3 fixture set. No existing
reports need deleting to apply the migration. Cloud PostgreSQL 17/container
results are recorded on the PR, separately from local evidence.
