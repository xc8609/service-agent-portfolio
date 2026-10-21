# S02 implementation slice 01: authorized transaction lookup

20 October 2026. Owner requested the first running database/permissions/lookup loop and a PR. This is a bounded implementation of DEV-01, DEV-02, DEV-03, QA-01 and OPS-01, not whole-story acceptance.

## Business and scope decision

An inbound representative needs permitted transaction evidence in one place to investigate an unfamiliar or apparently repeated card charge. Read access never implies refund authority. This slice implements context → search → explicit selection → evidence. It preserves ambiguity and separates source records from a financial determination. Synthetic scenario only; no model key, bank connection or benefit measurement.

Pull forward only DEV-02/03's read path from S03 into S02 to prove the foundation. Remaining S03 scope (case snapshot, statement correction, policy retrieval and write workflows) stays in the forecast. Original estimates remain provisional; no claim that the complete stories fit this slice or are Done.

## Technical walkthrough and decisions

- FastAPI/Python 3.12, psycopg and real PostgreSQL; React/TypeScript investigation screen. Keep legacy Python 3.9 checks independent.
- Versioned SQL migrations execute the v0.4 32-table reference schema plus lookup constraints, disposable-environment marker and hashed demo sessions. Runtime credentials are separate from migration credentials; only selected table reads, session writes and audit inserts are granted.
- Three existing POST contracts are implemented unchanged: get_contact_context, search_transactions and get_transaction_evidence. Validate input and output using the canonical JSON Schemas. Unknown request fields (including actor/role/customer scope) fail closed.
- Local-only synthetic identity adapter issues opaque, expiring sessions for fixed personas. It is not employee identity proofing. Tokens are stored hashed, browser memory only; no CORS wildcard and local allowed-host checks. Refuse public/production mode. Real IdP integration is a release gate.
- Inbound authorization checks active principal, current role, live session, contact ownership/status, fresh assertion and selected account scope on every request. All other roles are denied in this slice, including agent_runtime; later assignment/delegation grants are not approximated.
- Parameterized queries enforce account scope at retrieval. Mixed authorized/unauthorized IDs fail as a whole. Missing and inaccessible resources share the same error shape/status; no partial response leaks.
- Search uses UTC calendar-date bounds, inclusive end date; bounded date span and merchant input, exact minor-unit amount, stable keyset cursor tied to contact/account/filters. Explicit selection is required to inspect evidence. Equal amount/merchant is never a relationship rule.
- Read audit is metadata only (actor, action, outcome, correlation ID); no request body, token or transaction description. Failure to commit audit fails the response. Database failure is not an empty search.
- Demo initialization is explicit; API startup does not migrate/seed. Seed IDs are deterministic and repeat seed changes no records. Reset requires local mode, matching database name and a pre-existing disposable marker. Never erase unmarked data.

## Acceptance mapping

| Case | Story trace | Independent expected outcome |
|---|---|---|
| MIG-01 | DEV-01-T01 | Apply migrations twice, seed twice: versions, IDs and counts unchanged; FK/check constraints reject invalid rows |
| AUTH-01 | DEV-02-T01; QA-01-T02 | Verified assigned representative sees masked card and only permitted transactions |
| AUTH-02 | DEV-02-T02 | Missing/expired session or proof denies private fields |
| AUTH-03 | DEV-02-T03 | Forged scope, other customer, other contact/card, mixed IDs and revoked authority disclose nothing |
| AUTH-04 | DEV-02-T04 | No financial command endpoint; agent/feedback/lead have no implicit inbound grant |
| TX-01 | DEV-03-T01/T02 | Equal posted entries stay unlinked; pending/posted evidence does not promise reversal/refund |
| TX-02 | DEV-03-T03 | Filtered stable pagination, explicit selection and accurate source versions; no automatic proposal |
| FAIL-01 | DEV-01-T03; DEV-03-T05 | Liveness independent; unavailable DB gives safe 503/readiness failure, never empty success |
| RESET-01 | DEV-01-T04 | Wrong target/unmarked database refuses reset without deleting data |
| UI-01 | DEV-01-T01/T02; DEV-03-T03 | No-key browser journey: start demo, context, search, select, evidence; stale data cleared on new identity/failure |
| CI-01 | DEV-01-T05; OPS-01-T02; QA-01-T05 | Separate app/offline environments, real Postgres integration, web types/build/E2E and image smoke checks |

## Remaining acceptance

Worker processing, feedback claims, proposal/command writes, audit/outbox/receipt atomic effects, production identity, policy/agent integration, full case snapshots, UAT and deployment are not included. The API exposes only implemented paths; unsupported future grants deny by default. S01/S02 and parent stories remain in progress. Report actual commands, versions and failure evidence in the PR.
