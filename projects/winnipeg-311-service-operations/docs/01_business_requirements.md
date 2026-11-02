# Business requirements

**Scenario (simulated):** the City of Winnipeg's 311 contact centre and its Water and
Waste department review residential garbage and recycling service requests.
The stakeholders and the review are simulated; the City has not commissioned this work.
All figures come from the public 311 dataset ([source](../data/README.md)).

## Problem statement

Garbage and recycling requests are a large, seasonal part of 311 demand. The
simulated operations lead wants to know which requests drive volume, how long each
kind takes to close, and whether the open queue reflects live work. The contact-centre
lead wants to understand how much residents chase existing requests.

## Stakeholders (simulated)

| Role | Interest |
|---|---|
| Solid-waste operations lead | Volume by request type and season; turnaround; records still open |
| 311 contact-centre lead | Channel mix; follow-up calls and the share recorded as breached |
| Data/records owner | Closure practice, type changes, field completeness |

## User stories

- **US-1** As the operations lead, I want monthly cases by request group and type,
  so that I can see which requests drive demand and when it peaks.
- **US-2** As the operations lead, I want closing time by group, type and year, so
  that I can see which requests take longest and whether that is changing.
- **US-3** As the operations lead, I want open cases by age at a fixed snapshot,
  so that I can separate recent work from records that may never have been closed.
- **US-4** As the contact-centre lead, I want city-wide follow-up calls and the
  share recorded as breached, so that I can size chasing demand.
- **US-5** As the records owner, I want the data limits stated beside each measure,
  so that nobody reads elapsed time as a missed standard.
- **US-6** As the operations lead, I want conclusions with proposed improvements,
  baselines and targets, so that I can decide what to change before summer 2027
  ([plan](02_conclusions_and_improvements.md)).

## Acceptance criteria

1. Counts are cases, not rows; repeat interactions collapse to one case
   (tested in [`tests/test_service_model.py`](../tests/test_service_model.py)).
2. Monthly figures cover cases opened January 2023 – September 2026; open-case ageing
   uses a 31 October 2026 snapshot.
3. Extract rows reconcile to the API's counts by type; the case mart reconciles to the
   case table ([checks](../results/checks.json)).
4. A turnaround quantile is shown only when cases still open cannot change it.
5. No result calls a case late or in breach of a standard; no current public standard
   per request type was found.
6. Follow-up calls are reported city-wide and never attributed to a request type.
7. Each recommendation names a measured baseline; targets and sizes are labelled as
   proposals or illustrations, not forecasts or results.

## Out of scope

Contractor or crew performance, staffing, cost or savings estimates, ward
comparisons as headlines, routing or classification models, and forecasting.
