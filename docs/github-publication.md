# Public repository bootstrap

Published 19 October 2026 (America/Winnipeg; CI timestamps use UTC).

Repository: [github.com/xc8609/service-agent-portfolio](https://github.com/xc8609/service-agent-portfolio). License: [MIT](../LICENSE), selected by the owner. [Third-party notices](../THIRD_PARTY_NOTICES.md) apply separately.

## Published scope

Clean Git history starting at `5be1a8d`, with the bank specifications, authored synthetic contract fixtures, detailed story packages, sprint forecast, data tooling and offline CI. The source allowlist is in [publication manifest](publication-manifest.json). Personal workspace history, private job-search documents, English lessons, raw datasets, local databases and credentials are excluded. Author email uses GitHub's noreply address.

The initial import contains 24 four-file story packages, 10 model tools and 12 trusted commands. The planned bank workflow, voice extension and retail module do not become implemented merely by being published.

## Executed checks

[GitHub Actions run for `4af1798`](https://github.com/xc8609/service-agent-portfolio/actions/runs/39372023490) completed successfully for Python 3.9 and 3.12 on clean GitHub runners. Each job installed declared dependencies and ran 5 parser tests, workflow-spec validation, contract validation and publication checks. Contract checks cover 45 schemas, 91 payload examples, 52 authored boundary examples and 4 calendar specification examples. Initial publication checks covered 290 relative links; subsequent documentation can increase that count.

The initial CI exposed inconsistent system timezone data across runners. The fix loads `tzdata==2025.2` explicitly for simulated calendar fixtures. This versioned snapshot supports reproducible specification checks; it is not validation of current civil-time rules. A production calendar needs separate review and change control.

## Evidence limits and remaining gates

These checks do not execute PostgreSQL DDL, application API authorization, a user interface, live models, UAT or deployment. BANKING77 download remains pending. A secret-pattern check is not a security audit.

GIT-01 remains in progress until its contribution PR rehearsal and default-branch protection are verified. Future application releases use the [release checklist](release-checklist.md). S01 and S02 are not automatically accepted by this bootstrap.

Current specs/code in this repository are canonical. Trello is the planning mirror. Earlier imported sprint/update payloads are dated historical records and may contain superseded repository-pending wording; do not replay them wholesale. Use current story data and current GitHub links for future synchronization.

Trello GIT-01 and S02 descriptions were updated with repository links and CI evidence and verified in the rendered UI; [sync record](backlog/publication-trello-sync.json). Neither card was marked complete.
