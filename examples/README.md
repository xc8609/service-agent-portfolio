# Adaptation rehearsals

All example bank rows and account aliases here are **synthetic**. No external source
was downloaded. The two shapes demonstrate mapping requirements, not real bank schemas.
Source provenance: authored for this portfolio on 20 October 2026; MIT project terms.

## Transaction source preview

From the repository root, with application dependencies installed:

```bash
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.integrations.transactions \
  --fixture examples/integrations/legacy-export.json --observed-at 2026-10-20T16:00:00Z
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.integrations.transactions \
  --fixture examples/integrations/api-export.json --observed-at 2026-10-20T16:00:00Z
```

Both validate one row; neither writes to the database. `key_scope` declares where the
source guarantees key uniqueness: `source` (the API shape) or `account` (the legacy
entry number). Canonical IDs follow that scope, so equal entry numbers on different
accounts never alias, and a reused source-unique key rejects the batch. A posted row
must carry a booking time no earlier than its event; a pending row must not. The Python function returns
canonical fields for contract testing; the CLI reports only summary information.
Account aliases must be mapped by the institution's authorized integration process,
never inferred by the model. Namespace/source names are stable deployment identifiers.
The observed timestamp is supplied by the trusted connector/batch operator, not the
source payload. No staleness threshold is assumed from a transaction's last-change time.

To onboard a bank, review its read-only SQL view/API contract and map IDs, ownership,
revision semantics, currencies/units, time zones, status enums and lineage. Then implement
and test the ingestion path and freshness policy against the canonical read model.
The API still reads local PostgreSQL; this preview is not a live connector.

## Model profile selection

`providers/profiles.example.json` defaults to `offline-scripted-v1`. All API candidates
have `live_enabled: false` and `qualified: false`, and model IDs are placeholders.
OpenAI Responses, Claude Messages and compatible-chat are distinct protocols; use the
last only after qualifying the actual DeepSeek or internal endpoint's capabilities.

For a native local launch, set `BANK_PROVIDER_CONFIG` to an absolute copy of that file
before starting the API. A credential is referenced by environment variable name;
never put the key in JSON or a browser request. Keep deployment copies outside Git.
The default compose deployment remains offline; a future qualified route needs an
explicit read-only config mount and secret environment injection in a deployment
override. Do not bake credentials into the image.

Selecting a disabled candidate demonstrates `LIVE_NOT_QUALIFIED`, without network
traffic. `qualified: true` is not sufficient on its own: `qualified_fingerprint` must
equal the route fingerprint that the dated qualification report evaluated. Print it
without any network call:

```bash
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.agent.selection --config <copy>
```

The fingerprint covers protocol, model, endpoint allowlist, internal-only routing and
the credential environment *name* (never its value). Changing any of them requires a
new qualification. A qualified route additionally needs reviewed exact HTTPS egress endpoints,
a model/version and budget, credential injection, provider capability/quality tests
and data-handling approval. Configuration flags do not substitute for that evidence.
The owner has deferred real model testing; no live candidate is enabled by this change.

Configuration is loaded at application startup. After restart, model rollback selects the offline profile for new runs. Existing triggers replay
saved outcomes; the UI/manual workflow and business receipts remain authoritative.
[Design and acceptance](../projects/bank-service-assist/specs/contracts/extensibility-change.md).
