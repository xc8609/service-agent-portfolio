# Bank core clarity — delegated retest

22 October 2026 · Assessor: Codex, delegated by the portfolio owner.
Scope: [CF-01–05](../../projects/bank-service-assist/specs/DEV-08/core-flow-clarity.md).
Synthetic records only; this is not owner sign-off or live-model qualification.

## Automated verification

- Local PostgreSQL 16.2 / Python 3.12: 286 API tests passed.
- Python 3.9 offline suite: 109 passed; two SQL modules skipped because DuckDB
  is not installed in that environment. No real-data SQL rerun is claimed.
- Frontend TypeScript check and production build passed.
- 44 Playwright browser tests passed on a fresh synthetic database, including
  WF-06: delivered feedback → blocked closure → specialist records a synthetic
  external receipt → staff confirms closure → related-case header says closed.
- Ruff, format, workflow/contracts, public-file/link checks and whitespace passed.
  Initial WF-06 authoring runs failed on ambiguous/missing test locators and an
  unawaited search result; the corrected complete suite passed (no retries).
- CI follow-up: two hosted runners stalled downloading Playwright dependencies
  from the Azure Ubuntu mirror after API tests passed. The workflow substitutes
  the [official Ubuntu archive](https://archive.ubuntu.com/ubuntu/) in the runner's
  mirror list and bounds download timeouts/retries. Package signature validation,
  all tests and required checks remain unchanged. Final CI evidence is on the PR.

## Interactive review

Executed in the visible local browser at `127.0.0.1:8000` on a separate fresh
synthetic database, 20:50–20:53 UTC. The seeded case intentionally has both a
pending action and open complaint work; it was left open for inspection.

| Step | Observed result |
|---|---|
| Unverified inbound contact | `AUTH_REQUIRED`; transaction controls stayed unavailable |
| Verified lookup and recognition | Two DEMO STORE CAD 85 posted entries; no recorded relationship; one purchase, entry mapping unresolved |
| Agent draft and human note | Facts / To confirm / Next step displayed; existing enquiry identified without a duplicate-charge conclusion; staff approved note receipt `072631db-6fd9-4c18-85f0-d153e2f66a22` |
| Missing receipt and referral | Linked to DEMO-CASE-001; intake receipt `85a127d1-36d0-48d4-9501-92554bd48c66`; no duplicate investigation |
| Specialist and feedback assignment | Specialist saw the submitted statement/gap. Unclaimed feedback detail was denied; claim enabled preparation |
| Customer disclosure | Approved review alone was insufficient (`AUTH_REQUIRED`); fresh callback identity enabled only the approved explanation, not the private specialist note |
| Actual feedback | Verified delivery receipt `0791fd9c-4b72-4862-b32b-bc4e8ca6b8dd`; work completed, case version 5 |
| Status and closure | Overview/checklist displayed “Feedback delivered · case remains open”. Missing action receipt and open complaint intake were listed with follow-up role/queue; closure stayed disabled even with a reason |
| Updated Agent evidence | Old inbound run failed refresh with `CONFLICT`; a new run used delivered/open status. Feedback run `353ccd4b-8d2c-4ab4-b806-01edcf2c19b2` preserved approved text and advised closure-checklist review, not another callback |

Result: the requested presentation fixes passed the observed scope. The separate
WF-06 browser test verified successful closure after all prerequisites; this
interactive seeded case was not forced closed. No phone call, model API, financial
execution, measured saving or owner acceptance is claimed.
