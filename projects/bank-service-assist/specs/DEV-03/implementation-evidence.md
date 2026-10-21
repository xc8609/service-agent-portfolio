# DEV-03 statement and recognition execution evidence

20 October 2026 · Synthetic local portfolio workflow; implementation review,
not owner UAT or a production acceptance. Built on the foundation PR #1.

[Implementation PR #2](https://github.com/xc8609/service-agent-portfolio/pull/2)
uses a stacked base until #1 is merged. [Trello synchronization](trello-sync.json)
records verified updates to DEV-03 and S03; neither was marked Done.

## Implemented increment

- Human-only scoped report read/save, append-only statement revisions with original
  text, explicit recognition and selected source versions; migration 003.
- D-23 unresolved pair retains both IDs without assigning an invented disputed ID.
- Query/selection/statement edits invalidate active evidence and recognition;
  delayed responses cannot restore an earlier context. Saved history remains
  labelled historical, and must not be reused as live evidence.
- Backend verification/account scope, optimistic concurrency, retry receipts,
  audit atomicity and least-privilege append-only grants. No ledger mutation.
- Denial of both purchases shows a manual risk-review prompt, not an automated
  fraud decision or created case.

## Executed checks

| Check | Actual result |
|---|---|
| `python services/api/local_postgres.py test` in application environment | 56 passed on Python 3.12.14 / PostgreSQL 16.2; one existing Starlette/httpx deprecation warning |
| `npm --prefix apps/web run test:e2e` | 9 passed: 6 new capture/invalidation journeys and 3 existing lookup journeys |
| `npm --prefix apps/web run build` | TypeScript and Vite production build passed |
| Ruff check and format check for `services/api` | Passed |
| Root `python -m pytest -q` | 5 passed and 2 subtests passed; separate offline checks |

The first browser run failed four select locators (not application requests);
role/name locators corrected them. A later repeat on the retained demo database
also exposed duplicate test-text locators; each history test now uses its own
synthetic statement. All nine passed after correction. Source records are
`bank-lookup-synthetic-v1`; no external banking data or live LLM is involved.

API coverage includes SI-01–06: persisted correction/reload; recognition modes;
malformed pair and injected authority rejection; cross-customer and role denial;
expired/revoked authorization; stale source/revision conflict; competing writes;
identical replay and changed-key conflict; immutable history permissions; atomic
rollback when audit cannot be inserted; UUID normalization. Browser tests cover
statement correction/manual-risk prompt, unresolved/specified recognition,
filter/selection invalidation, delayed search/inspection responses, lost-save
response retry, and identity isolation. Tests live in `test_investigation.py`
and `investigation.spec.ts` under the repository test directories.

## Remaining acceptance

DEV-03-AC04 has evidence for the manual capture slice only. There are no generated
proposals yet, so future proposal invalidation/approval requires DEV-06/07 tests.
DEV-03-AC06 existing-case detail/status remains pending DEV-04. Handling-rule
retrieval, referral, specialist result/feedback, Agent, owner UAT and deployed
production identity remain unimplemented. The story/Sprint is not Done.

Database upgrade is additive; run migrations and runtime-role provisioning.
Preserve existing volumes and forward-fix rather than resetting data for recovery.
Container smoke now checks persisted capture and replay as well as lookup; cloud
PostgreSQL 17 and container results are reported in the PR checks, separately from
local PostgreSQL 16.2 evidence above.

Cloud run [39488694094](https://github.com/xc8609/service-agent-portfolio/actions/runs/39488694094)
passed PostgreSQL 17 API/browser tests but failed container startup. The image
allowlist/COPY missed the new runtime schema. Both packaging entries were added;
see PR checks for the current commit's subsequent container result.

## Merge-pass recognition regression

[DEV-03/08 UI state correction](../DEV-08/ui-state-regression.md) records the
reproduced post-inspection recognition reset, evidence-bound fix, and SI-07
persistence test. This supplements the historical execution record above.
