# Service Agent Portfolio development instructions

Read README.md and docs/backlog/current-delivery.md first; use projects/bank-service-assist/docs/sprint-02/README.md for dated evidence. Current tool contract version: v0.5 (initial-intake extension); continuation reference baseline v0.4; requirements baseline v0.3. RB-01–RB-06 are accepted as D-17–D-22; do not repeatedly ask for those decisions. RI-01–03 are accepted as D-23–D-25; D-26 prioritizes a small core with manual continuation before advanced automation. D-27/D-28 (21 October): subscription-run model evaluation without an API; publish analytics results, never raw source data. Numeric business targets and model budgets remain proposed.

- English public artifacts; conversational language follows the owner.
- All bank/retail operational records and rules are explicitly simulated. Never invent measured benefits, a bank sponsor, executed tests or deployment.
- Connect business requirements, rules, story IDs, implementation and UAT evidence.
- Model tools are read/draft only. Trusted commands enforce identity, scope, versions, deterministic transitions and idempotency.
- Keep raw/generated data, private material, secrets and local databases out of Git. Never import an entire personal workspace or its Git history.
- `main` contains the merged bank core: inbound lookup, rules, reviewed notes/referrals, specialist results, verified feedback, contact continuation, exceptions/complaint delivery and a bounded offline Agent; plus real-data complaint analytics. Owner UAT, API model qualification and staging remain separate gates; do not mark whole stories accepted from merged code.
- Start implementation with DEV-01/QA-01/OPS-01, then the B0 manual baseline. Preserve independent later voice and retail scope.
- Use codex/<story-id>-<topic> branches and a reviewable PR. No force pushes to main.
- Pure offline tooling remains Python 3.9 compatible; application runtime is planned for Python 3.12. Pin actual application dependencies after compatibility checks.

Checks from root: python -m pytest; python projects/bank-service-assist/scripts/validate_workflow_specs.py; python projects/bank-service-assist/scripts/validate_s02_contracts.py; python scripts/check_publication.py. State precisely which checks ran and which require future implementation or external services.

Structure: docs/backlog owns story catalogue and scheduling; project docs own BA
evidence and decisions; specs/<ID> owns requirement/design/tasks/acceptance;
services/api and apps/web own runtime code. The Agent module now contains a bounded offline runtime and provider adapters; live providers remain disabled/unqualified. Preserve existing links and stable story IDs; do not create
additional services or placeholder provider implementations solely for structure.
