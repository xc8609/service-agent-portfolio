# Model and metric definitions

## Model

| Table | Grain | Built in |
|---|---|---|
| `staged` | One source row (interaction); nothing dropped | [01_staging.sql](../sql/01_staging.sql) |
| `case_rollup` | One `case_id`; interaction count and attribute checks | [02_cases.sql](../sql/02_cases.sql) |
| `fact_case` | One in-scope case opened 1 Jan 2023 – snapshot | [02_cases.sql](../sql/02_cases.sql) |
| `monthly_requests` | Open month × request type (additive counts) | [03_marts.sql](../sql/03_marts.sql) |
| `turnaround_by_year`, `turnaround_by_type` | Open year × group (or type) | [03_marts.sql](../sql/03_marts.sql) |
| `open_ageing` | Request type × age band at the snapshot | [03_marts.sql](../sql/03_marts.sql) |
| `follow_up_monthly` | Month (city-wide follow-up calls) | [03_marts.sql](../sql/03_marts.sql) |

The build stops if a case's type, open date, close date or status differs between its
rows, if a case closes before it opens, or if required keys are missing.

## Scope

63 request types are mapped to seven analysis groups in
[`reference/request_type_map.csv`](../reference/request_type_map.csv). The map
excludes water, sewer, utility billing, transfers, information requests, depots,
landfill, dead-animal pickup and illegal dumping (an online-form type that starts
in March 2025).

| Group | What it contains |
|---|---|
| Missed collection | Missed garbage, recycling, yard waste and special pickups, including same-day misses |
| Escalated missed collection | Types named "Breached Missed Collection …"; definitions are not published |
| Bulky and special pickup | Bulky, large appliance, surplus waste and ozone-depleting-substance requests |
| Cart damaged in collection | Carts damaged by crews, City equipment or third parties |
| Cart repair or supply | Repair/replacement, new or extra carts, delivery problems |
| Crew conduct or property damage | Operator standards, damage or theft by crews, cart tagging, staff complaints |
| General collection concern | General solid-waste concerns, loose garbage, City collection requests |

## Measures

| Measure | Definition |
|---|---|
| Cases | Distinct `case_id` values opened in the month |
| Interactions | Source rows for those cases; repeat-contact cases have more than one |
| Days to close | `closed_date − open_date` in calendar days, for cases closed before the snapshot |
| Closed within N days | Cases with days to close ≤ N (N = 1, 3, 7, 14, 30); divide by cases for a share |
| Open at snapshot | No close date, or a close date after 31 Oct 2026 00:00 |
| Age | Snapshot time − open time, for open cases; grouped into five bands |
| Median and P90 | Discrete quantiles of days to close, with open cases ranked last |
| Follow-up calls | City-wide `Follow Up Call- SLA not breached` + `Follow up- SLA breached` rows |

**Censoring rule.** A cohort's quantile is reported only when it is below the age of
its youngest open case. Otherwise a case still open could close later and change the
answer, so the value is left blank ("not yet determinable"). For example, the 90th
percentile is blank when more than 10% of a cohort is still open.

**Thresholds.** 1, 3, 7, 14 and 30 days are descriptive bands, not City service
standards. No current public standard per request type was found.

## Calendar

Months and years use the open date in the source's local time. The monthly window
ends with September 2026, the last complete month before the snapshot, so every
monthly cohort is at least 30 days old.
