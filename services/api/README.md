# Bank lookup runtime

Python 3.12, FastAPI, psycopg and PostgreSQL. Three v0.4 read contracts are implemented for an authorized **inbound representative**. Feedback assignment, agent delegation, commands and worker processing are intentionally unsupported and deny by default. All records and identity assertions are synthetic.

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

The demo persona adapter is separate from model tools. It issues opaque credentials mapped to server-side synthetic principals/contact records; no request body can grant roles, approve transactions or expand customer scope. The three tool paths follow the shared JSON schema registry. Search uses UTC date bounds, exact integer minor units, literal merchant matching and bounded keyset pagination. The UI requests up to 50 results and asks for narrower filters when more are available. Evidence retrieval requires explicit selection (1–10 IDs); a mixed-scope request fails as a whole.

`/health/live` measures process liveness; `/health/ready` checks database, schema and demo marker. A database outage returns sanitized 503 plus a correlation ID; it is never an empty successful search. Wrong database credentials/schema or failed initialization should stop startup readiness; inspect configuration and migration checksums, preserve the volume and forward-fix. This read-only slice introduces no workflow worker or recoverable write effects.

## Traceability and limits

See [slice specification](../../projects/bank-service-assist/docs/sprint-02/implementation/lookup-slice.md) and [execution evidence](../../projects/bank-service-assist/docs/sprint-02/implementation/lookup-evidence.md). This is not production authentication, bank connectivity, UAT or regulatory certification. Policy lookup, case-detail retrieval, note/referral commits, callbacks and agent execution remain future work.

Implementation references: [FastAPI container guidance](https://fastapi.tiangolo.com/deployment/docker/), [psycopg installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), [optional pgserver publisher](https://pypi.org/project/pgserver/). These inform packaging; the domain authority rules come from this project's accepted decisions and specs.
