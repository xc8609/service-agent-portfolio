# DEV-02/08/09 — Lightweight adaptability follow-up

20 October 2026. Technical implementation for PR review; no new customer policy,
provider enablement or external connection approved by this change.

## Need and stories

Owner experience: banking customer-service desktop, customer lookup and process-rule
use. Target evidence: API/data mapping, access control, requirements traceability and
UAT from the existing R01/R02/R06 role-evidence baseline; this is not a new job survey.

- **DEV-02 extension:** As an integration analyst, I want explicit source-to-target
  mappings and rejection of ambiguous source facts, so another institution can review
  integration requirements without changing the customer-service process.
- **DEV-09 extension:** As a deployment maintainer, I want server-owned model profiles,
  so a qualified API can be changed without replacing business rules or giving clients
  authority to select a data destination.
- **DEV-08 extension:** As a representative, I want the same scope, draft-only behavior
  and manual route regardless of provider, so an API failure does not alter case handling.

## Detailed design / change impact

See [ADR-004](../../../../docs/architecture/ADR-004-lightweight-enterprise-adaptation.md).
No migration, endpoint payload, permission, deadline or human-approval change.
`BANK_PROVIDER_CONFIG` optionally names a server-local JSON file. Default is the
existing offline fixture. Startup rejects malformed selection; an unqualified route
fails its run before transport, with a persisted failure and usable manual workflow.
A live configuration is only used in mock transport tests in this increment.

The selected name and configuration fingerprint are recorded in `agent_runs`.
Credentials are environment references and excluded from repr, model messages and
config fingerprints. Existing run triggers replay saved results after configuration
changes; a new trigger is required for a deliberate new run. No hidden failover.

The source preview maps source-specific identifiers, status enums, currency units,
offset-aware timestamps and approved account aliases. It derives stable namespaced
transaction IDs and preserves source version plus source-update/observation times.
Unsupported statuses, unknown accounts, duplicate keys, floating-point money and
lossy rounding reject the **whole batch**; extra source fields do not propagate.
Preview only: no account provisioning, database mutation or live connection occurs.

Before actual ingestion, specify transactional batch commit and receipt, ownership
cross-checks against identity, duplicate/replay handling, same-version different-value
rejection, monotonic revision rules, deletions/reversals, source outage/freshness
thresholds and post-refresh invalidation of old approval evidence. These are not
proven by a successful preview. Do not use it as a production importer.

## Acceptance and traceability

| ID | Given / when / then | Evidence |
|---|---|---|
| EXT-01 | Two differently named synthetic export/API rows / normalize / same business amount, state and timestamps; IDs stable within source and distinct across sources | `test_source_mapping.py::test_different_source_shapes_preserve_business_meaning_and_namespace` |
| EXT-02 | Bad account, state, precision, revision or timestamp / preview / fail whole batch without inferred facts or database writes | Parameterized negative mapping tests and duplicate/sign test |
| EXT-03 | No config / start / retain offline fixture; malformed route / start / sanitized config failure, no guessed fallback | `test_default_offline_and_strict_server_configuration` |
| EXT-04 | Unqualified candidate / run / zero transport calls, persisted failure and readiness/manual route retained | `test_unqualified_route_records_failure_without_transport_and_manual_path_remains` |
| EXT-05 | Three protocol mock routes / same scoped run / execute evidence/rule tools, produce a cited review draft or fail safely on simulated rate limit | Parameterized `test_server_selected_protocol_uses_same_scoped_runtime_and_persists_route` |
| EXT-06 | Existing trigger / change route and replay / return recorded outcome, never silently make a second provider call | Replay assertion in EXT-04 |
| EXT-07 | Owner reads repository / inspect boundaries / distinguish implemented preview/protocol support from live integration, SDK adoption and demonstrated benefit | README, ADR-004, examples and owner review (pending) |

Implementation tasks: source preview and two fixtures; server profile factory; runtime
wiring and audit label; negative/integration tests; concise architecture documentation;
PR and Trello review evidence. Complete engineering execution evidence is recorded in
the PR and delivery ledger; owner acceptance remains pending.

## Schedule and release impact

A focused follow-up within the current S04/S05 engineering review, not an additional
platform release or a new Sprint marked Done. Planning estimate for a 2–3 developer
team: development 2–3 person-days, BA 0.5, QA 1; work can overlap, but elapsed time is
not obtained by simply dividing by headcount. Estimates are prospective, not a claim
of actual effort. Live model qualification, external connector implementation and
staging/UAT remain separately scheduled gates. Voice and retail scope are unchanged.

## Executed engineering evidence — 20 October 2026

Python 3.12.14 / isolated PostgreSQL 16.2: **203 tests passed**, including 22 new
mapping/profile tests. The three protocol routes each exercise a successful draft
and a simulated rate-limit failure through the application endpoint using mock HTTP.
Five offline data tests, both SDD validators, publication/link checks and Ruff passed.
Both documented mapping CLI examples executed successfully with one validated row
and `database_written: false`. No real provider request or bank connection executed.
Owner review and live qualification remain pending. CI evidence is tracked in the PR.
