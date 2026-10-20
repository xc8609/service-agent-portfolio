# S02 lookup slice execution evidence

20 October 2026. Scope: [slice specification](lookup-slice.md). This record distinguishes executed checks from parent-story acceptance. No business savings or bank results measured.

## Local execution

- Python 3.12.14, macOS arm64, actual PostgreSQL 16.2 from optional isolated `pgserver` runner. 30 API/database integration tests passed using the restricted `bank_app` role for requests and a separate admin connection for fixtures/migrations.
- `services/api/local_postgres.py test`: migration repeatability, seed invariance, relational/check constraints, authorized reads, session/proof expiry, role/queue/contact revocation, cross-customer and mixed-ID denials, strict payload validation, literal search, cursor binding, source relationships, ledger/internal-note database privileges, unavailable dependency and guarded reset.
- React/TypeScript type check and Vite production build passed. Three Playwright Chromium journeys passed: explicit selected-transaction evidence, identity change and denial with old-data clearing, and injected source outage with no empty-success display.
- A local HTTP demo runs with actual PostgreSQL and no model credentials. UI fault test injects an HTTP 503 deliberately; separate backend integration uses an unavailable PostgreSQL endpoint.
- Runtime dependencies and direct frontend dependencies were installed and locked. Python 3.9 offline tooling stays separate. PostgreSQL image/base images are digest-pinned; actual cloud runtime/container results will be linked on the PR after execution.

## Acceptance coverage and remaining work

| Story | Implemented evidence | Still pending |
|---|---|---|
| DEV-01 | Migration/seed repeatability, health/readiness, guarded reset, separate 3.12 environment, React manual lookup | Worker and full environment acceptance; owner review |
| DEV-02 | T01–T04 read boundary: context, expired/unverified denial, cross-customer and financial-operation denial | T05 proposal approval expiry; callback and delegated scope |
| DEV-03 | T01/T02 uncertainty, T03 explicit selection and search, T05 unavailable source | T04 corrected statement persistence; T06 full case history/status UI |
| QA-01 | Real PostgreSQL negative authorization tests; frontend fault journey; precise scope record | Full Must-requirement coverage, write/receipt/concurrency/worker tests, mutation gate |
| OPS-01 | Locked dependencies, reproducible build configuration and separate runtime CI | Cloud/container outcome until verified; deployment recovery/UAT/release |

No parent story or Sprint is marked Done. These read endpoints do not prove future write transitions, financial operations, production identity or model behavior. First PR is the review boundary; no merge or cloud deployment is implied.
