# DEV-07 executed evidence

20 October 2026. Initial intake implementation; synthetic records only.

- Python 3.12.14 / PostgreSQL 16.2: **131 API/integration tests passed**, including
  14 additional referral/calendar cases.
- Chromium: **30 browser tests passed**, including four referral journeys.
- TypeScript/Vite build and Ruff passed. Pinned v0.5 schema/meta examples passed.
- CI PostgreSQL 17/container, owner UAT and downstream continuation are distinct
  checks. No model call, bank connection or measured benefit is claimed.

| Acceptance | Evidence |
|---|---|
| AC01 note without case | DEV-06 note tests; no case write in note commit |
| AC02 existing work / distinct reason | link-preserves-deadline and duplicate-reason tests; REF-01 |
| AC03 accountable queued receipt | material/contact-gaps test, current case snapshot and REF-02 |
| AC04 exact replay / one effect | link retry, concurrent draft/key tests and REF-04 |
| AC05 invalid queue / revoked scope / rollback | five changed-context cases, injected outbox failure |
| AC06 no narrative success | draft/receipt UI distinction, REF-01/04 |
| RI-AC01/02/03/04/05/06/08/09/11/12/13 | typed intake, pair/report/source guards, material/contact gap, manual policy basis and stale-query tests |
| RI-AC07/14 | existing DEV-03 risk/selection and minor-unit/date behavior; non-posted/denied-both referral is rejected |
| RI-AC10/15/16/17 | downstream supplementation/contact-resolution/result/overdue integration still pending DEV-11–13 |

Cross-draft concurrent creation creates one enquiry; losing transaction conflicts.
No artificial case or refund is used to hide an unavailable source. Service-hour
calendar test includes a configured holiday; retry-window calendar is reused by
DEV-12. [Runtime design](runtime-contract.md) identifies exact boundaries.
