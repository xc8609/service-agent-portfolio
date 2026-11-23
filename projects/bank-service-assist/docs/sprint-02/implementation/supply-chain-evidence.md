# Supply-chain scanning slice — execution evidence

17 November 2026. Parent story: OPS-01 (artifact and release controls), test OPS-01-T02
"dependency lock validation and secret/data-exclusion inspection". This slice adds
automated scanning; it does not complete OPS-01, and it is not a threat model,
penetration test or runtime security assessment.

## Repository baseline before this change (GitHub API, read-only)

| Control | State |
|---|---|
| Secret scanning | Enabled |
| Push protection | Enabled |
| CodeQL | Not configured |
| Dependabot alerts / security updates | Disabled |
| Dependency audit in CI | None |
| Required checks on `main` | Offline checks (Python 3.9, 3.12), Bank API + browser, Bank container smoke |

## Changes

- `.github/workflows/codeql.yml`: CodeQL `security-extended` for Python,
  JavaScript/TypeScript and Actions; pull requests, `main` and weekly. Actions pinned by
  commit SHA, consistent with existing workflows.
- `.github/workflows/dependency-audit.yml`: `pip-audit` 2.10.1 over all nine pinned
  Python requirement files (listed explicitly so included files are covered); `npm audit`
  gate on shipped dependencies (`--omit=dev`, high) for both web apps, with build tooling
  reported as a warning.
- `.github/dependabot.yml`: weekly pip, npm, GitHub Actions and Docker updates; Python 3.9
  tooling ignores major pytest updates.
- Remediation: `opentelemetry-api` 1.45.1 → 1.45.2 in the bank API lock and the
  investment API requirements (GHSA-mf5v-w3w3-f6cg, trace-context ReDoS). `pytest` 9.0.3
  on Python 3.10+ (CVE-2025-71176); Python 3.9 keeps 8.4.2 by environment marker because
  9.0.3 requires Python 3.10+.
- Accepted exceptions recorded in [SECURITY.md](../../../../../SECURITY.md#accepted-dependency-exceptions).

## Local execution — macOS arm64

| Check | Environment | Result |
|---|---|---|
| Initial `pip-audit` (before remediation) | Python 3.9, pip-audit 2.9.0 | 2 advisories: opentelemetry-api 1.45.1; pytest 8.4.2 |
| Initial `npm audit` | Both web apps | 4 high in build tooling (picomatch via Vite); 0 with `--omit=dev` |
| `pip-audit` on all nine files (after) | Python 3.12.14, pip-audit 2.10.1 | No known vulnerabilities |
| Root `pytest` | Python 3.12.14, pytest 9.0.3 | 232 passed |
| Root `pytest` | Python 3.9, pytest 8.4.2 | 232 passed |
| Both SDD validators, publication check | Python 3.9 and 3.12 | Pass (validation timestamps reverted) |
| `build_traceability.py --check` | Python 3.12 | Pass |
| API suite, `services/api/local_postgres.py test` | Python 3.12.14, opentelemetry-api 1.45.2, disposable PostgreSQL | 294 passed |
| Investment research `pytest`, Ruff | Python 3.12.14, opentelemetry-api 1.45.2 | 93 passed; lint and format clean |
| YAML parse of the three new files | PyYAML | Pass |

## Cloud execution — pull request #52, commit `cc72535`

All 12 checks passed on GitHub-hosted `ubuntu-24.04` runners, including the four
existing required checks.

| Workflow | Result |
|---|---|
| [CodeQL](https://github.com/xc8609/service-agent-portfolio/actions/runs/44165813958) | Python 50 rules, JavaScript/TypeScript 103 rules, Actions 23 rules; **0 results** in each analysis |
| [Dependency audit](https://github.com/xc8609/service-agent-portfolio/actions/runs/44165813962) | pip-audit: no known vulnerabilities in all nine files. npm runtime gate: 0 vulnerabilities in both apps. Build tooling: 4 high (picomatch via Vite) reported as a warning, matching the accepted exception |
| [Portfolio checks](https://github.com/xc8609/service-agent-portfolio/actions/runs/44165813511) | Python 3.9 and 3.12 passed |
| [Bank runtime](https://github.com/xc8609/service-agent-portfolio/actions/runs/44165813572) | API + browser and container smoke passed |
| [Investment research](https://github.com/xc8609/service-agent-portfolio/actions/runs/44165813653) | API + browser + container passed |

Zero CodeQL results means no matches for the configured queries; it is not proof that
the code has no vulnerabilities.

## Not done in this slice

- Dependabot alerts and security updates are repository settings and remain disabled
  until the owner enables them.
- The new checks are not added to the required checks on `main` (repository setting).
- Dependabot's pip support for `services/api/requirements.lock` (non-`.txt` name) is
  unverified; `pip-audit` covers that file regardless. *(Resolved 23 November: confirmed
  not covered — see below.)*
- No SBOM, container image scan or signed release artifacts yet.

## Follow-up triage — 23 November 2026

The first Dependabot run after the merge opened 17 pull requests (#53–#69); the first
`main` CodeQL analysis raised one alert.

| Item | Finding | Action |
|---|---|---|
| Actions #56, #58, #59, #60; web group #61; runtime group #63 | CI passed | Applied in this branch (commits cherry-picked with `-x`) |
| Offline group #62, duckdb #64 | Python 3.9 job failed: jsonschema 4.26 and duckdb 2.0 require Python 3.10+/3.11+ | Closed; ignored for the 3.9-compatible tooling |
| tzdata #65, #66 | Contract validator failed: tzdata is pinned to `calendar-fixtures.json` | Closed; ignored; change with the fixture by hand |
| duckdb 2.0 in analytics #67–#69 | Green only because CI does not install analytics dependencies | Closed; completed analytics cases removed from version updates (pip-audit still covers them) |
| Base images #53–#55, #57 (Python 3.12→3.15, Node 24→26) | Runtime version is an architecture decision | Closed; Docker updates limited to patch versions |
| CodeQL `js/regex/missing-regexp-anchor` (high), `projects/investment-research/web/tests/agent.spec.ts` | Unanchored URL regex in a browser test assertion; test code, not shipped | Replaced with a polled substring assertion |
| `services/api/requirements.lock` | Dependabot does not parse this file (#63 updated only the investment API and `requirements-localpg.txt`) | Bank runtime lock aligned by hand to the same versions (fastapi 0.163.0, pydantic 2.14.3 / core 2.50.4, starlette 1.10.0 and others) |

`dependabot.yml` now opens one grouped pull request per ecosystem per week.

Local checks on this branch (macOS arm64): API suite in disposable PostgreSQL 294 passed
(fastapi 0.163.0, `pip check` clean, Ruff clean); root pytest 232 passed on Python 3.9 and
3.12; both validators, publication check and traceability check pass; pip-audit clean on
all nine files; investment research 93 passed and Ruff clean; both web apps build;
investment Playwright suite 11 passed against an API on a spare port.
