# CR-004 — S02 reforecast

BANK-S02-v0.3 · Planning forecast, not a date commitment or staffed delivery report.

CR-003 added 16 person-days. S02 refinement adds a further 6 person-days: BA-06 +0.5 BA, BA-07 +0.5 BA, DEV-08 +2 Dev/+0.5 QA, QA-01 +0.5 Dev, QA-02 +0.5 QA, OPS-02 +1 Dev/+0.5 QA. Total: **104.0 Dev + 31.5 BA + 35.0 QA = 170.5 person-days** over 42 stories. No prior work is double-counted or called completed.

Insert S04A for continuation and S05A for integration/evaluation/staging, preserving existing IDs. Delivery becomes 12 two-week iterations (24 weeks), plus two unallocated reserve iterations (up to 28 weeks). Bank B1 at week 16, phone B2 at week 20, retail R1 at week 24. Calendar dates are illustrative from the original kickoff; holiday/leave and unresolved acceptance can move them.

Per normal sprint: Dev 14 planned days (20 x 70%), BA 7 for S01–02 then 3.5, QA 5.25. Each developer lane stays at or below 7 planned days. Lane assignments are workload budgets, not a completed resource-level critical-path proof. Same-sprint dependencies must be demonstrated by slices below; otherwise move unfinished work and downstream gates.

## Dependency-sensitive execution slices

- S02: BA-06 decision tables → BA-07 data/ownership → BA-08 limits → BA-09 API baseline → DEV-01 fixture/app foundation → QA-01 contract harness → OPS-01 packaging. Specs can be prepared in parallel, but dependent implementation waits for the accepted boundary. If review is late, carry foundation work; no empty sign-off.
- S03: A completes authorized contact then transaction view; B implements policy retrieval against accepted contracts, then related-case read. No financial writes.
- S04: DEV-06 draft/commit first, then DEV-07 referral. Provider spike runs against deterministic tools in parallel. A 7 / B 6 days leaves little headroom.
- S04A: DEV-11 is split into API/result/event slice (A 2 days) and feedback UI slice (B 2 days) using accepted contracts; integration completes before dependent continuation. Then A leads DEV-12 (3 days), B DEV-13 (4 days). A 5 / B 6. Detailed exception rules must be accepted; otherwise exclude pending branches and reforecast.
- S05: DEV-08 split into runtime/tool execution, durable event/proposal continuation and integration/trace slices; no slice exceeds 5 developer-days. UI/manual affordances can proceed against accepted schemas while runtime work proceeds. A 5 / B 4.
- S05A: A staging/recovery (6 days); B event marts/evaluation runner (5 days), using the prior accepted agent increment. QA load is 5 of 5.25 days, so no unplanned feature additions.
- S06: mainly business UAT, defects/release decision and public demonstration. Low planned Dev load is intentional for evidence and observed fixes, not guaranteed spare capacity for new scope.

An optional third developer can absorb independent provider, QA automation or deployment tasks; no blanket acceleration is claimed. S01 GitHub setup and approvals remain carryover until actually completed. Do not infer a GitHub repository exists from the forecast.
