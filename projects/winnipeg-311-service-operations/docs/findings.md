# Findings

Cases opened January 2023 – September 2026; open records at 31 October 2026 00:00.
Figures are measured from the public 311 dataset unless labelled otherwise.
Results: [summary](../results/summary.json), [monthly mart](../results/monthly_requests.csv),
[turnaround](../results/turnaround_by_year.csv), [open ageing](../results/open_ageing.csv),
[follow-up calls](../results/follow_up_monthly.csv).

## 1. Demand is seasonal and higher in 2026

- 277,951 garbage and recycling cases, about 6,000 a month.
- May–July averages 7,177 cases a month, compared with 5,037 in December–February
  (42% higher). The busiest months were July 2026 (8,417) and June 2026 (8,364).
- January–September volume: 55,182 (2023), 50,434 (2024), 58,210 (2025) and
  62,806 (2026). That is 7.9% above the same months of 2025.

| Group | Share of cases | Jan–Sep 2023 | Jan–Sep 2026 |
|---|---:|---:|---:|
| Cart damaged in collection | 31.3% | 17,633 | 19,819 |
| Missed collection | 28.5% | 17,227 | 16,694 |
| Bulky and special pickup | 18.6% | 9,953 | 10,313 |
| Cart repair or supply | 9.1% | 4,104 | 6,456 |
| Crew conduct or property damage | 6.9% | 2,634 | 5,879 |
| General collection concern | 5.4% | 3,405 | 3,401 |
| Escalated missed collection | 0.4% | 226 | 244 |

Crew-conduct and property-damage reports more than doubled between the two
January–September periods, and cart repair or supply rose 57%. The data cannot say whether that reflects service,
reporting practice or type usage; it is a question for the records owner.

## 2. Turnaround differs by an order of magnitude between request groups

Median days to close, by year opened (blank: not yet determinable under the
[censoring rule](metrics.md#measures)):

| Group | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|
| Missed collection | 2.8 | 2.8 | 3.7 | 2.8 |
| Bulky and special pickup | 8.8 | 8.8 | 9.2 | 8.8 |
| Cart damaged in collection | 17.0 | 14.4 | 15.7 | 20.1 |
| Cart repair or supply | 47.1 | 29.9 | 35.9 | — |

Missed collections closed within seven days fell from 90.9% (2023 and 2024) to 74.1%
in 2025, then rose to 86.9% in 2026. In July and August 2025 only 50.0% and
40.9% closed within seven days. The 2026 recovery is outside summer: June–August
2026 reached 77.2%, against 92.9% in the other months and 89.6% and 88.9% in the
summers of 2023 and 2024. These are elapsed times, not breaches of a standard.

## 3. The open queue is mostly old records

- 16,545 in-scope cases were open at the snapshot; 9,528 (58%) had been open a year
  or more, and only 3,057 were under 30 days old.
- 1,799 missed-collection records and 4,457 bulky or special pickup records had been
  open 90 days or more. A missed pickup is unlikely to remain unresolved for months,
  so these are more likely records that were never closed than outstanding work.
- Assumption to test with the records owner: the open count overstates live work.
  A closure-hygiene review would be needed before open counts are used as a backlog.

## 4. Residents chase through separate follow-up calls

- Only 240 cases (0.09%) have more than one interaction, so repeat contact is not
  recorded on the original case.
- City-wide follow-up calls (all departments) fell from 25,700 in 2023 to 20,764 in
  2025, while the share recorded as SLA breached rose from 15.1% to 25.2%
  (27.3% in January–September 2026).
- Follow-ups cannot be linked to a department or request type, so this does not show
  that garbage or recycling caused the change.

## 5. Intake and data quality

- First contact: voice 66.2%, online form code `VOF` 26.9%, email 6.0%.
- Ward is present on all in-scope 2023 cases but about 70% from 2024.
- Cart repair types were renamed in March 2025; the analysis maps both names.

## 6. Most demand reports a collection that went wrong

174,086 cases (63%) report a missed pickup, a cart damaged by crews or City
equipment, or a crew-conduct or damage complaint (the author's classification by
request-type name, [map](../reference/demand_type_map.csv)). Crew-damaged carts
alone are 84,457 cases. Conclusions and proposed improvements:
[conclusions and improvement plan](02_conclusions_and_improvements.md).

## Questions for the (simulated) stakeholders

1. Which cases count as resolved, and who closes the record after field work?
2. Can follow-up calls carry the original case ID so chasing can be attributed?
3. What are the current internal standards per request type, and how is "SLA
   breached" determined for follow-up calls?
4. What changed in cart-damage and crew-conduct reporting in 2025?

## Not claimed

No result measures crew or contractor performance, staffing needs, cost or savings.
No case is labelled late. The scenario and stakeholders are simulated.
