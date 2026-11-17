# Security reporting and demo boundaries

This is a simulated portfolio, not a production banking service. Do not submit real customer data or use real financial actions.

Do not disclose credentials, personal records or exploitable sensitive details in a public issue. If GitHub provides a private security-reporting option for this repository, use it; otherwise contact the repository owner through an available private channel before sending details. No private email address or guaranteed response SLA is published here.

Public demo releases must use synthetic data, keep provider keys server-side, enforce scoped access and preserve manual fallback. Current specification checks do not certify runtime security or regulatory compliance.

## Automated security checks

- **Secret scanning and push protection** are enabled as repository settings.
- **CodeQL** ([workflow](.github/workflows/codeql.yml)) runs the `security-extended` queries for Python, JavaScript/TypeScript and GitHub Actions workflows on pull requests, `main` and weekly.
- **Dependency audit** ([workflow](.github/workflows/dependency-audit.yml)) runs `pip-audit` over every pinned Python requirement file and `npm audit` for both web apps. Shipped browser dependencies fail the check at high severity; build-only tooling is reported and reviewed against the exceptions below.
- **Dependabot version updates** ([configuration](.github/dependabot.yml)) propose weekly pip, npm, GitHub Actions and Docker updates.

These checks find known code patterns and published advisories. They are not a penetration test, threat model or runtime security assessment.

## Accepted dependency exceptions

Reviewed 17 November 2026. Each exception is re-checked when the weekly audit or a Dependabot update changes it.

| Advisory | Where | Decision and reason |
|---|---|---|
| [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) — `picomatch` ≤ 4.0.7 regular-expression denial of service | Vite build tooling in both web apps (development dependency only) | Accepted until a patched release exists. No fixed version is published; `npm audit fix --force` would downgrade Vite rather than fix it. The package is not in the shipped browser bundle and only matches repository-defined build globs. |
| [CVE-2025-71176](https://github.com/advisories/GHSA-6w46-j5rx-g56g) — `pytest` ≤ 9.0.2 shared temporary directory | Python 3.9 compatibility runs of the offline tooling | Accepted while Python 3.9 support is required. The fix (pytest 9.0.3) requires Python 3.10+, so Python 3.10+ installs 9.0.3 and only Python 3.9 keeps 8.4.2; those runs happen on disposable CI runners and developer machines. |
