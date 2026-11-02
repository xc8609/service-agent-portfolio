# Conclusions and improvement plan

**Scenario (simulated):** written for the simulated solid-waste operations lead and
311 contact-centre lead. The conclusions are measured from the public dataset
([baselines](../results/improvement_baselines.json), built by
[`build_improvement_baselines.py`](../scripts/build_improvement_baselines.py) from the
published results). Recommendations, targets and pilot designs are the author's
proposals: none has been adopted or tested, and no benefit has been measured.

## Summary

1. **Most demand comes from collections that went wrong.** 63% of garbage and
   recycling cases (174,086 of 277,951) report a missed pickup, a cart damaged by
   collection crews or City equipment, or a crew-conduct or damage complaint.
   Carts reported damaged by collection crews alone are 84,457 cases (30%), about
   19,000–20,000 in each of the last two January–September periods, with a median
   of 14–20 days to close by year opened. The largest lever on 311 demand is getting the collection
   right the first time, not handling the resulting cases faster.
2. **Summer is the weak point, and not because of more reports.** Missed collections
   closed within seven days in June–August fell from 89.6% (2023) and 88.9% (2024)
   to 59.4% (2025) and 77.2% (2026). Outside summer, 2026 reached 92.9%, so the
   yearly 2026 figure (86.9%) hides a second weak summer. Summer 2025 had the
   fewest missed-collection reports of the four summers (5,104) yet the slowest
   closing. Summer missed collections still open after a week: 614 (2023), 625
   (2024), 2,070 (2025) and 1,466 (2026).
3. **The open queue cannot be used as a backlog.** 58% of the 16,545 open records
   are a year old or more, including 1,704 missed collections. A target set on
   this count would mostly measure unclosed paperwork.
4. **Chasing cannot be measured yet.** Follow-up calls are not recorded on the
   original case (240 of 277,951 cases have a second interaction) and carry no
   department. City-wide, the share of follow-up calls recorded as SLA breached
   rose from 15.1% (2023) to 27.3% (January–September 2026), and summer 2026
   follow-up calls were about two-thirds above summer 2025 (9,091 against 5,460). How much of that comes from garbage
   and recycling is unknown.

"Collection failure" is the author's classification by request-type name
([map](../reference/demand_type_map.csv)); it does not establish fault. It is
conservative: cart-delivery problems and contractor tag disputes are left out.

## Improvement plan

| # | Recommendation | Simulated owner | When | Measure: baseline → proposed target |
|---|---|---|---|---|
| 1 | Prepare missed-collection recovery for summer 2027 | Solid-waste operations lead | Plan by May 2027 | June–August 7-day share: 77.2% (2026) → 89% (2023–24 level) |
| 2 | Clean up open records and agree a closure rule | Records owner | Q1 2027, before recommendation 1 is measured | Missed collections open 90+ days: 1,799 → near zero; open a year or more: 57.6% of open records |
| 3 | Pilot cart-damage prevention on selected routes | Operations lead with the contract manager | 2027 pilot | Crew-damaged cart reports per 1,000 households served, pilot against comparison routes |
| 4 | Record follow-up calls against the original case | Contact-centre lead and 311 system owner | Change request | Follow-up calls linked to a case: not available → 95% or more |
| 5 | Document a turnaround standard per request group | Operations lead and records owner | Q1 2027 | Groups with a published standard: none found → all seven |

**Order.** Recommendation 1 has a fixed deadline and affects residents directly.
Recommendation 2 is cheap and must come first in practice, because the summer
measure is only as reliable as the closure dates. Recommendation 3 addresses the
largest volume but needs internal data and a season of piloting. Recommendation 4
is a system change with lead time; recommendation 5 is a decision that makes "late"
measurable.

### 1. Summer missed-collection recovery

- **Evidence:** conclusion 2. Fewer reports did not mean faster closing in 2025,
  so the cause is more likely capacity or process than demand.
- **Proposal:** review summers 2025 and 2026 with data the public dataset lacks:
  route schedules, crew or contractor availability, vehicle downtime, and how
  missed-collection reports are dispatched and closed. Choose responses from that
  review, for example reserved recovery capacity in June–August or a daily check of
  missed collections older than three days.
- **Measure:** weekly in June–August: missed collections opened, the share closed
  within seven days and the number still open after seven days. Dashboard page 1
  already shows the monthly share for the Missed collection group.
- **Size (illustration, not a forecast):** at the 2023–24 summer rate (10.8% still
  open after a week), summer 2026 would have had 694 rather than 1,466 missed
  collections open past a week, 772 fewer.
- **Risk:** if closing dates record paperwork rather than the pickup, the measure
  can improve without residents noticing. Recommendation 2 addresses this.

### 2. Open-record clean-up and closure rule

- **Evidence:** conclusion 3; 4,457 bulky or special pickups and 1,799 missed
  collections have been open 90 days or more.
- **Proposal:** check a random sample of old open records in each group against
  field records to estimate how many are finished work (sample size to agree with
  the records owner). Agree who closes a case and when, close confirmed cases with
  an audit note, then report each month the cases open past the agreed standard.
- **Measure:** open records by group and age band (dashboard page 2).

### 3. Cart-damage prevention pilot

- **Evidence:** conclusion 1; crew-damaged carts are the largest single request
  family and each one is a case, a replacement and a wait of about two to three weeks.
- **Proposal:** analyse damage reports by route, contractor, cart model and age
  using internal data, then pilot one change, for example a lifting-equipment check
  or a cart-handling refresher, on selected routes with comparison routes.
- **Measure:** crew-damaged cart reports per 1,000 households served per month
  (household counts per route are not public); median days to replace.
- **Size (illustration):** every 10% fewer crew-damaged cart reports is about 1,900
  fewer cases per January–September at the 2026 level (19,123).
- **Assumption to test:** some wear-and-tear may be reported as crew damage.

### 4. Link follow-up calls to the original case

Proposed requirements for a change request:

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-1 | A follow-up call about an existing request is saved against that case | Given a resident gives a case number or service address, when the agent selects the matching case, then the follow-up is saved with the case ID and its request type |
| FR-2 | A follow-up without a findable case still records the department | Given no matching case is found, when the agent saves the call, then it is saved with the department and the reason "case not found" |
| FR-3 | Managers can report follow-ups by original request group | Given linked follow-ups, when the monthly report runs, then it shows follow-ups per 100 cases for each request group |
| FR-4 | The open-data export keeps follow-ups attributable | Given a follow-up row, then the export includes its department and original request type; a case reference only if the privacy review approves |
| NFR-1 | Linking must not slow calls noticeably | The added handling time is measured in UAT against a limit agreed with the contact centre |

### 5. Turnaround standards per request group

Publish a target closing time for each request group and define how "breached" is
set; the "Breached Missed Collection …" types and the follow-up "SLA breached"
flag have no published definition. The dashboard could then report "closed within
standard" instead of descriptive day bands.

## How the dashboard supports the plan

| Need | Where |
|---|---|
| Summer missed-collection monitoring | Page 1, monthly 7-day share; select Missed collection |
| Demand mix and growth | Page 1, cases by month and by request group |
| Closure clean-up progress | Page 2, open records by group and age |
| Chasing baseline until linked data exists | Page 2, city-wide follow-up calls |

To add once the data exists: a collection-failure share, a weekly summer view and
"closed within standard".

## Not recommended

- **A routing model:** the request type already determines the department.
- **Staffing numbers or savings:** the public data has no workload, cost or route data.
- **Ward rankings:** ward is missing on about 30% of cases from 2024.

## What would change these conclusions

- If internal records show summer delays are in closing the record rather than in
  the field, recommendation 1 becomes a records issue rather than a service issue.
- If crew-damage request types are used for all cart replacements, conclusion 1
  overstates collection failures.
