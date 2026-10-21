# S02 lookup slice execution evidence

20 October 2026. Scope: [slice specification](lookup-slice.md). This record distinguishes executed checks from parent-story acceptance. No business savings or bank results measured.

## Local execution

- Python 3.12.14, macOS arm64, actual PostgreSQL 16.2 from optional isolated `pgserver` runner. 30 API/database integration tests passed using the restricted `bank_app` role for requests and a separate admin connection for fixtures/migrations.
- `services/api/local_postgres.py test`: migration repeatability, seed invariance, relational/check constraints, authorized reads, session/proof expiry, role/queue/contact revocation, cross-customer and mixed-ID denials, strict payload validation, literal search, cursor binding, source relationships, ledger/internal-note database privileges, unavailable dependency and guarded reset.
- React/TypeScript type check and Vite production build passed. Three Playwright Chromium journeys passed: explicit selected-transaction evidence, identity change and denial with old-data clearing, and injected source outage with no empty-success display.
- A local HTTP demo runs with actual PostgreSQL and no model credentials. UI fault test injects an HTTP 503 deliberately; separate backend integration uses an unavailable PostgreSQL endpoint.
- Runtime dependencies and direct frontend dependencies were installed and locked. Python 3.9 offline tooling stays separate. PostgreSQL image/base images are digest-pinned; cloud runtime/container execution is recorded below.

## Acceptance coverage and remaining work

| Story | Implemented evidence | Still pending |
|---|---|---|
| DEV-01 | Migration/seed repeatability, health/readiness, guarded reset, separate 3.12 environment, React manual lookup | Worker and full environment acceptance; owner review |
| DEV-02 | T01–T04 read boundary: context, expired/unverified denial, cross-customer and financial-operation denial | T05 proposal approval expiry; callback and delegated scope |
| DEV-03 | T01/T02 uncertainty, T03 explicit selection and search, T05 unavailable source | T04 corrected statement persistence; T06 full case history/status UI |
| QA-01 | Real PostgreSQL negative authorization tests; frontend fault journey; precise scope record | Full Must-requirement coverage, write/receipt/concurrency/worker tests, mutation gate |
| OPS-01 | Locked dependencies, reproducible build configuration and separate runtime CI | Worker artifact, deployment recovery/UAT/release |

No parent story or Sprint is marked Done. These read endpoints do not prove future write transitions, financial operations, production identity or model behavior. First PR is the review boundary; no merge or cloud deployment is implied.

## Cloud execution and repository controls

PR: [S02 authorized lookup #1](https://github.com/xc8609/service-agent-portfolio/pull/1). Implementation commit: `d133f1e`.

- [Runtime workflow](https://github.com/xc8609/service-agent-portfolio/actions/runs/39454531846): API/PostgreSQL/browser job and container job both passed. Actual cloud database: PostgreSQL 17.6 (Debian 17.6-2.pgdg12+1), x86_64. Container HTTP smoke exercised readiness, scoped context, filtered search and selected evidence without a model key.
- [Offline workflow](https://github.com/xc8609/service-agent-portfolio/actions/runs/39454531652): Python 3.9 and 3.12 both passed.
- Container image ID for that run: `sha256:0db76bc048f9740faa51e56b56473e5d662dc37e45ccfe29c0ee6592c56777f7`. Build-only artifact; no registry push or cloud deployment.
- [Main protection snapshot](../../../../../docs/github-branch-protection.json) read back on 20 October: PR required; four checks restricted to the GitHub Actions app; branch freshness and resolved conversations required; administrators included; force push/deletion disallowed; linear history. Additional required human approvals: zero for the solo portfolio. No independent reviewer or acceptance is invented.
- Defect found during post-build local verification: static UI serving returned 405 for unsupported POST APIs. Explicit `/v1/` fallback restored uniform safe 404 and the full 30-test suite passed again.

All seven relevant Trello cards were saved and read back with `BANK-S02-RUNTIME-v1`; [sync record](../../../../../docs/backlog/s02-runtime-sync.json). Original card specifications were preserved under an explicitly historical section. S02 and parent stories remain in progress. Latest PR-head checks should be inspected before merge; no automatic merge is requested.
