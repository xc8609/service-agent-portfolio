# Sprint forecast — S02 revision v0.3

Current execution scope: [core-first delivery](current-delivery.md), updated
20 October under D-26. The dates/capacity below are the retained expanded
forecast, not a fresh estimate of the simplified core. Deferred automation must
be re-estimated before commitment; no completed work is inferred from dates.

BANK-S02-v0.3 · 19 October 2026. Supersedes previous relative weeks/dates for expanded scope. Historical cards and the pre-S02 snapshot preserve prior estimates.

**12 delivery iterations / 24 weeks, plus two unallocated reserve iterations.** Two developers plus explicit BA/QA, not personal-hours scheduling or actual staffing. S02 specification refinement is now in progress by owner request; S01 repository/acceptance work remains open. Future calendar blocks are illustrative.

Capacity: Dev 14 person-days per sprint (7 per developer); BA 7 in S01–02, 3.5 later; QA 5.25. Total effort: {'dev': 104.0, 'ba': 31.5, 'qa': 35.0, 'total': 170.5}.

| Sprint | Weeks / illustrative dates | Goal | Dev / BA / QA | A / B Dev |
|---|---|---|---|---|
| S01 | 1–2; 2026-10-19–2026-11-01 | Business framing and public delivery foundation | 3.5 / 7.0 / 0.5 | 2 / 1.5 |
| S02 | 3–4; 2026-11-02–2026-11-15 | Rules, permissions, data and API foundation | 10.0 / 6.75 / 4.5 | 5.5 / 4.5 |
| S03 | 5–6; 2026-11-16–2026-11-29 | Authorized transaction and policy investigation | 12 / 1.25 / 2.5 | 6 / 6 |
| S04 | 7–8; 2026-11-30–2026-12-13 | Reviewed referral, persistence and provider spike | 13 / 1.25 / 3 | 7 / 6 |
| S04A | 9–10; 2026-12-14–2026-12-27 | Specialist result, callback and exception workflow | 11 / 2.0 / 3 | 5 / 6 |
| S05 | 11–12; 2026-12-28–2027-01-10 | Bounded agent orchestration over durable workflows | 9 / 1 / 2.0 | 5 / 4 |
| S05A | 13–14; 2027-01-11–2027-01-24 | Integrated evaluation, data evidence and staging | 11 / 1.75 / 5.0 | 6 / 5 |
| S06 | 15–16; 2027-01-25–2027-02-07 | Bank UAT, release and reviewer case study | 2.5 / 2.5 / 3.5 | 1.5 / 1 |
| S07 | 17–18; 2027-02-08–2027-02-21 | Voice boundaries and browser channel | 7 / 2.0 / 2.0 | 4 / 3 |
| S08 | 19–20; 2027-02-22–2027-03-07 | Inbound phone and verified human handoff | 9 / 1.0 / 3.5 | 5 / 4 |
| S09 | 21–22; 2027-03-08–2027-03-21 | Retail discovery and manual clienteling | 7 / 2.5 / 1.5 | 4 / 3 |
| S10 | 23–24; 2027-03-22–2027-04-04 | Retail agent and open-source review | 9 / 2.5 / 4.0 | 5 / 4 |
| S11 | 25–26; 2027-04-05–2027-04-18 | Conditional contingency and observed fixes | 0 / 0 / 0 | 0 / 0 |
| S12 | 27–28; 2027-04-19–2027-05-02 | Conditional contingency and observed fixes | 0 / 0 / 0 | 0 / 0 |

## Release forecast

B0 S04A/week 10; B1 S06/week 16; B2 S08/week 20; R1 S10/week 24. Reserve through week 28. [Capacity and dependency rationale](../../projects/bank-service-assist/docs/sprint-02/forecast-impact.md) and [machine-readable forecast](sprint-forecast.json).

Holiday and leave availability are unconfirmed. Reduce actual capacities before commitment, particularly year-end; the illustrative dates are not a holiday-adjusted schedule.

## Detailed sprint cards

# S01 | W1–2 | Business framing and public delivery foundation

BANK-S02-v0.3
Status: In progress; repository/acceptance carryover remains
Weeks 1–2; illustrative 2026-10-19 to 2026-11-01. Not holiday-adjusted or a delivery commitment.

## Goal
Business framing and public delivery foundation

## Scope and role estimates
- GOV-01: Dev 0, BA 1, QA 0 person-days.
- GOV-02: Dev 0.5, BA 1, QA 0 person-days.
- BA-01: Dev 0, BA 1, QA 0 person-days.
- BA-02: Dev 0, BA 0.5, QA 0 person-days.
- BA-03: Dev 0.5, BA 1, QA 0 person-days.
- BA-04: Dev 0.5, BA 1, QA 0 person-days.
- BA-05: Dev 0, BA 0.5, QA 0 person-days.
- GIT-01: Dev 2, BA 0.5, QA 0.5 person-days.
- GOV-03: Dev 0, BA 0.5, QA 0 person-days.
Totals: {'dev': 3.5, 'ba': 7.0, 'qa': 0.5}. Capacity: {'dev': 14, 'ba': 7, 'qa': 5.25}. Developer allocation A 2, B 1.5.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S02 | W3–4 | Rules, permissions, data and API foundation

BANK-S02-v0.3
Status: Specification refinement in progress; implementation not started
Weeks 3–4; illustrative 2026-11-02 to 2026-11-15. Not holiday-adjusted or a delivery commitment.

## Goal
Rules, permissions, data and API foundation

## Scope and role estimates
- BA-06: Dev 1, BA 2.5, QA 0.5 person-days.
- BA-07: Dev 1, BA 2.0, QA 0.5 person-days.
- BA-08: Dev 0.5, BA 0.5, QA 0.5 person-days.
- BA-09: Dev 1, BA 1, QA 0.5 person-days.
- DEV-01: Dev 3, BA 0.25, QA 0.5 person-days.
- QA-01: Dev 1.5, BA 0.5, QA 1.5 person-days.
- OPS-01: Dev 2, BA 0, QA 0.5 person-days.
Totals: {'dev': 10.0, 'ba': 6.75, 'qa': 4.5}. Capacity: {'dev': 14, 'ba': 7, 'qa': 5.25}. Developer allocation A 5.5, B 4.5.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S03 | W5–6 | Authorized transaction and policy investigation

BANK-S02-v0.3
Status: Forecast
Weeks 5–6; illustrative 2026-11-16 to 2026-11-29. Not holiday-adjusted or a delivery commitment.

## Goal
Authorized transaction and policy investigation

## Scope and role estimates
- DEV-02: Dev 3, BA 0.25, QA 0.5 person-days.
- DEV-03: Dev 3, BA 0.5, QA 0.5 person-days.
- DEV-04: Dev 2, BA 0.25, QA 0.5 person-days.
- DEV-05: Dev 4, BA 0.25, QA 1 person-days.
Totals: {'dev': 12, 'ba': 1.25, 'qa': 2.5}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 6, B 6.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S04 | W7–8 | Reviewed referral, persistence and provider spike

BANK-S02-v0.3
Status: Forecast
Weeks 7–8; illustrative 2026-11-30 to 2026-12-13. Not holiday-adjusted or a delivery commitment.

## Goal
Reviewed referral, persistence and provider spike

## Scope and role estimates
- DEV-06: Dev 5, BA 0.5, QA 1 person-days.
- DEV-07: Dev 4, BA 0.5, QA 1 person-days.
- DEV-09: Dev 4, BA 0.25, QA 1 person-days.
Totals: {'dev': 13, 'ba': 1.25, 'qa': 3}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 7, B 6.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S04A | W9–10 | Specialist result, callback and exception workflow

BANK-S02-v0.3
Status: Forecast
Weeks 9–10; illustrative 2026-12-14 to 2026-12-27. Not holiday-adjusted or a delivery commitment.

## Goal
Specialist result, callback and exception workflow

## Scope and role estimates
- DEV-11: Dev 4, BA 0.5, QA 1 person-days.
- DEV-12: Dev 3, BA 0.5, QA 1 person-days.
- DEV-13: Dev 4, BA 1, QA 1 person-days.
Totals: {'dev': 11, 'ba': 2.0, 'qa': 3}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 5, B 6.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S05 | W11–12 | Bounded agent orchestration over durable workflows

BANK-S02-v0.3
Status: Forecast
Weeks 11–12; illustrative 2026-12-28 to 2027-01-10. Not holiday-adjusted or a delivery commitment.

## Goal
Bounded agent orchestration over durable workflows

## Scope and role estimates
- DEV-08: Dev 9, BA 1, QA 2.0 person-days.
Totals: {'dev': 9, 'ba': 1, 'qa': 2.0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 5, B 4.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S05A | W13–14 | Integrated evaluation, data evidence and staging

BANK-S02-v0.3
Status: Forecast
Weeks 13–14; illustrative 2027-01-11 to 2027-01-24. Not holiday-adjusted or a delivery commitment.

## Goal
Integrated evaluation, data evidence and staging

## Scope and role estimates
- DEV-10: Dev 3, BA 1, QA 0.5 person-days.
- QA-02: Dev 2, BA 0.5, QA 2.5 person-days.
- OPS-02: Dev 6, BA 0.25, QA 2.0 person-days.
Totals: {'dev': 11, 'ba': 1.75, 'qa': 5.0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 6, B 5.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S06 | W15–16 | Bank UAT, release and reviewer case study

BANK-S02-v0.3
Status: Forecast
Weeks 15–16; illustrative 2027-01-25 to 2027-02-07. Not holiday-adjusted or a delivery commitment.

## Goal
Bank UAT, release and reviewer case study

## Scope and role estimates
- QA-03: Dev 0.5, BA 1, QA 2 person-days.
- OPS-03: Dev 1, BA 0.5, QA 1 person-days.
- PKG-01: Dev 1, BA 1, QA 0.5 person-days.
Totals: {'dev': 2.5, 'ba': 2.5, 'qa': 3.5}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 1.5, B 1.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S07 | W17–18 | Voice boundaries and browser channel

BANK-S02-v0.3
Status: Forecast
Weeks 17–18; illustrative 2027-02-08 to 2027-02-21. Not holiday-adjusted or a delivery commitment.

## Goal
Voice boundaries and browser channel

## Scope and role estimates
- V-01: Dev 1, BA 1.5, QA 0.5 person-days.
- V-02: Dev 6, BA 0.5, QA 1.5 person-days.
Totals: {'dev': 7, 'ba': 2.0, 'qa': 2.0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 4, B 3.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S08 | W19–20 | Inbound phone and verified human handoff

BANK-S02-v0.3
Status: Forecast
Weeks 19–20; illustrative 2027-02-22 to 2027-03-07. Not holiday-adjusted or a delivery commitment.

## Goal
Inbound phone and verified human handoff

## Scope and role estimates
- V-03: Dev 7, BA 0.5, QA 1.5 person-days.
- V-04: Dev 2, BA 0.5, QA 2 person-days.
Totals: {'dev': 9, 'ba': 1.0, 'qa': 3.5}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 5, B 4.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S09 | W21–22 | Retail discovery and manual clienteling

BANK-S02-v0.3
Status: Forecast
Weeks 21–22; illustrative 2027-03-08 to 2027-03-21. Not holiday-adjusted or a delivery commitment.

## Goal
Retail discovery and manual clienteling

## Scope and role estimates
- R-01: Dev 1, BA 2, QA 0.5 person-days.
- R-02: Dev 6, BA 0.5, QA 1 person-days.
Totals: {'dev': 7, 'ba': 2.5, 'qa': 1.5}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 4, B 3.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S10 | W23–24 | Retail agent and open-source review

BANK-S02-v0.3
Status: Forecast
Weeks 23–24; illustrative 2027-03-22 to 2027-04-04. Not holiday-adjusted or a delivery commitment.

## Goal
Retail agent and open-source review

## Scope and role estimates
- R-03: Dev 6, BA 0.5, QA 1.5 person-days.
- R-04: Dev 2, BA 1, QA 1.5 person-days.
- PKG-02: Dev 1, BA 1, QA 1 person-days.
Totals: {'dev': 9, 'ba': 2.5, 'qa': 4.0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 5, B 4.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S11 | W25–26 | Conditional contingency and observed fixes

BANK-S02-v0.3
Status: Forecast
Weeks 25–26; illustrative 2027-04-05 to 2027-04-18. Not holiday-adjusted or a delivery commitment.

## Goal
Conditional contingency and observed fixes

## Scope and role estimates

Totals: {'dev': 0, 'ba': 0, 'qa': 0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 0, B 0.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.


# S12 | W27–28 | Conditional contingency and observed fixes

BANK-S02-v0.3
Status: Forecast
Weeks 27–28; illustrative 2027-04-19 to 2027-05-02. Not holiday-adjusted or a delivery commitment.

## Goal
Conditional contingency and observed fixes

## Scope and role estimates

Totals: {'dev': 0, 'ba': 0, 'qa': 0}. Capacity: {'dev': 14, 'ba': 3.5, 'qa': 5.25}. Developer allocation A 0, B 0.

## Dependencies and gates
Upstream specification/implementation acceptance precedes dependent work. Same-sprint handoffs are sequential; use accepted contracts for independent UI/platform work. No story is Done from document creation. S02 requires current permission matrix, data ownership, schema/examples and unresolved rule decisions before Ready. S04A requires DEV-11 result/feedback integration before retry/exception slices. S05 requires manual continuation plus qualified provider boundaries; S05A performs integration/evaluation/staging. S06/B1 requires executed UAT and recovery evidence.

## Carryover and limits
S01 repo/export approval remains open; S02 contract work began early, not a claim of completed S01. No real financial execution/outbound callback/App messages in bank core. If capacity, holidays or business review block acceptance, carry work explicitly and move dependent releases. Reserve is unallocated, never used to hide unfinished work.
