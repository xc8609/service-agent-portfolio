# Bank lookup runtime

Python 3.12, FastAPI, psycopg and PostgreSQL. Six v0.4 read contracts are implemented for an authorized **inbound representative**. Assigned specialist and feedback commands are implemented through the separate trusted workflow desk. Agent delegation and scheduled continuation remain dependent work. All records and identity assertions are synthetic.

## Run with Docker Compose (from repository root)

```bash
python3 scripts/configure_demo.py
docker compose up --build --wait
python3 scripts/smoke_demo.py
```

Open http://127.0.0.1:8000. Select **Verified inbound representative**, start the contact, search, select transactions, then inspect evidence. The API serves the built React UI on the same origin. No model key is needed. Database ports are not exposed; API binds to host loopback. Never forward this demo to a public interface. `BANK_MODE=production` is rejected; real identity integration is a separate gate.

Generated `.env` has separate random admin/runtime passwords and is ignored by Git. Configuration refuses to overwrite it. Migration/seed/provision runs in the one-shot initializer. The API uses `bank_app`, which cannot modify transaction records or read specialist private notes. Successful reads and denied lookups append sanitized audit metadata; tokens are stored as hashes. No full PAN/CVV is stored or returned.

`docker compose down` stops the stack and preserves its named volume. Do not use volume deletion as routine recovery. For an explicit disposable reset after the one-hour fixture proof expires:

```bash
docker compose run --rm init python -m bank_api.manage reset --target bank_demo_compose
docker compose run --rm init python -m bank_api.manage seed --target bank_demo_compose
```

Reset requires the matching target database, local mode and an existing disposable marker. Never mark a populated foreign database disposable. Repeat normal seed retains IDs, values and original proof expiry; it does not silently renew identity assurance. Demo sessions last 15 minutes. All returned private lookups recheck session, actor, role, contact and assertion scope.

## Optional local path without Docker

Requires Python 3.12 and Node 24.19.0 (exact dependency resolutions in locks):

```bash
python3.12 -m venv .venv-app
.venv-app/bin/python -m pip install -r services/api/requirements.lock -r services/api/requirements-localpg.txt
npm --prefix apps/web ci
npm --prefix apps/web run build
.venv-app/bin/python services/api/local_postgres.py test
.venv-app/bin/python services/api/local_postgres.py serve
```

The optional `pgserver` package launches a separate local PostgreSQL 16.2 instance; it is a development convenience, excluded from the application image. It keeps files in a system temporary directory and stops the server on exit. No existing PostgreSQL installation is touched. Each invocation starts fresh synthetic fixtures. The supported container/CI database is PostgreSQL 17.6; local 16.2 compatibility is separately checked.

To use an existing *isolated disposable test* PostgreSQL, set `BANK_TEST_ADMIN_URL` to a database with a `bank_demo` name, then run:

```bash
PYTHONPATH=services/api .venv-app/bin/python -m pytest -c services/api/pytest.ini services/api/tests -q
.venv-app/bin/ruff check services/api
.venv-app/bin/ruff format --check services/api
```

Tests refuse to substitute SQLite or silently skip database coverage. They reset only the supplied explicitly marked disposable database. Never use shared/application data for test URLs.

With the app running, browser verification is:

```bash
cd apps/web
npx playwright install chromium
npm run test:e2e
```

## Read flow and recovery

The demo persona adapter is separate from model tools. It issues opaque credentials mapped to server-side synthetic principals/contact records; no request body can grant roles, approve transactions or expand customer scope. Canonical tool paths follow the shared JSON schema registry. Search uses UTC date bounds, exact integer minor units, literal merchant matching and bounded keyset pagination. The UI requests up to 50 results and asks for narrower filters when more are available. Evidence retrieval requires explicit selection (1–10 IDs); a mixed-scope request fails as a whole.

`/health/live` measures process liveness; `/health/ready` checks database, schema and demo marker. A database outage returns sanitized 503 plus a correlation ID; it is never an empty successful search. Wrong database credentials/schema or failed initialization should stop startup readiness; inspect configuration and migration checksums, preserve the volume and forward-fix. The DEV-03 report-capture increment adds append-only revisions with atomic audit and replay receipts; there is no workflow worker or referral side effect.

## Traceability and limits

See [slice specification](../../projects/bank-service-assist/docs/sprint-02/implementation/lookup-slice.md) and [execution evidence](../../projects/bank-service-assist/docs/sprint-02/implementation/lookup-evidence.md). This is not production authentication, bank connectivity, UAT or regulatory certification. Scoped inbound case and policy reads are implemented; reviewed inbound note commits are implemented. Reviewed referrals are implemented; callbacks and Agent execution remain future work.

Implementation references: [FastAPI container guidance](https://fastapi.tiangolo.com/deployment/docker/), [psycopg installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), [optional pgserver publisher](https://pypi.org/project/pgserver/). These inform packaging; the domain authority rules come from this project's accepted decisions and specs.

## DEV-03 customer reports

Migration `003_investigation.sql` adds `investigation_revisions`; the runtime role
has SELECT/INSERT only (no UPDATE/DELETE) on this table and still cannot mutate
the ledger. Run the normal initialization/migration and role-provisioning path
when upgrading an existing disposable volume. No data reset is needed for upgrade.
Historical reports require fresh inspection before reuse; failed saves preserve
local edits. Retry unchanged input after an uncertain response, or reload saved
history. A 409 requires reloading history and rechecking evidence. Preserve the
database on failure; forward-fix migrations instead of deleting saved reports.
See the [human capture contract](../../projects/bank-service-assist/specs/DEV-03/investigation-contract.md).

## DEV-04 case progress

Migration `004_case_lookup.sql` adds customer-safe timeline/source-head fields.
Normal migrate/seed/provision upgrades the disposable demo additively; it does not
overwrite report history. `case_fixtures.py` seeds three synthetic cases, including
the two $85 entries linked to DEMO-CASE-001, closed history and another customer.
Fresh fixtures are `bank-cases-synthetic-v2`; transaction source references remain
`synthetic-ledger-v1`. The database itself is not tracked in Git.

After inspecting the pair, review its linked case and refresh to recheck current
ownership. STALE_VERSION means timeline/head disagreement: preserve source data,
use the correlation ID for manual reconciliation and retry after the source is
corrected. Never invent a closed status or create another case to bypass a failed
lookup. On access denial, re-establish authorized context; do not alter role/proof
in the request. No case mutation or outbound feedback permission is enabled.
See [contract and acceptance](../../projects/bank-service-assist/specs/DEV-04/runtime-contract.md).

## DEV-05 simulated handling rules

Migration `005_policy_lookup.sql` adds nullable account jurisdiction, policy
publication state and exact sections. Run normal migrate/seed/provision for
existing disposable volumes; runtime has SELECT only on policies. Existing
accounts retain unknown jurisdiction rather than infer a country from currency:
those accounts show a policy gap. A fresh disposable demo has explicitly authored
CA accounts (`bank-policy-synthetic-v3`). Preserve saved reports when upgrading;
use a new isolated demo for a full fresh fixture set rather than reset useful work.

Select two entries and inspect evidence to see conditions, citation and proposed
next steps. Manual refresh works without an LLM. Gap/conflict: seek service-lead
policy clarification. Evidence changed: reinspect the pair. Access denied:
re-establish authorized context. Outage: keep the concern open through manual
support; do not reuse stale advice or fabricate a policy result.

`policy_lookup.py` implements pair-specific workspace reads and the canonical
`search_policy`/`get_policy_section` tools. Scope/time/audience filtering precedes
content; exact fetch repeats it. Search uses literal text matching, not embeddings.
[Runtime contract](../../projects/bank-service-assist/specs/DEV-05/runtime-contract.md)
and [evidence](../../projects/bank-service-assist/specs/DEV-05/implementation-evidence.md)
record the narrow inbound scope. Contact-start effective time is shown separately
from retrieval time. The current demo is one exact section per edition; production
knowledge ingestion, policy approval and model orchestration remain later work.

## DEV-06 reviewed service notes

Migration `006_reviewed_notes.sql` adds immutable draft revisions and contact-bound
operation receipts. Refresh note sources, edit facts/allegations separately, save a
draft, then explicitly approve. Only a successful commit receipt means the service
record exists. Refresh retains edits and exposes old/current source facts for review.
Unknown responses retain the operation key; retry the same operation. A definitive
validation rejection unlocks editing. History is scoped to the authenticated author
and current verified contact. The runtime cannot update/delete committed notes.
See [executed evidence](../../projects/bank-service-assist/specs/DEV-06/implementation-evidence.md).

## DEV-07 reviewed specialist intake

After saving the customer report for two posted entries, prepare a fresh referral,
review related work, record missing materials/contact readiness, confirm the summary,
save and approve. A linked receipt reuses existing work; queued means not yet
accepted. Migration 007 and normal seed/provision add synthetic route/contact
configuration and immutable intakes. Existing records are preserved. Restart retains
receipts and history. See [v0.5 intake contract](../../projects/bank-service-assist/specs/DEV-07/runtime-contract.md).

## DEV-11 specialist and customer-feedback desk

Open the operations desk using a separate synthetic specialist/feedback persona.
Claim queued work before detail access. Publish a finding, switch to another feedback
representative, claim the shared task, open a new callback context, save/approve the
feedback review, simulate fresh identity verification and retrieve customer disclosure.
Record the actual outcome; feedback completion does not close the case. Never-dialed
faults do not consume attempts. Materials/contact-resolution work retains original
deadlines. Migration 008 grants only needed column updates and private-note INSERT;
private-note SELECT and ledger mutation remain denied.

[Authority, recovery and actual test evidence](../../projects/bank-service-assist/specs/DEV-11/runtime-contract.md).
