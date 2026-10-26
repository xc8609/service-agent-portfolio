# Business Requirements — Complaint Operations & Assisted Routing

*Simulated scenario. Updated after the 21 October 2026 baseline evaluation.*

## 1. Problem statement
In the simulated bank, intake analysts read every complaint and forward it to the
owning product team. A complaint sent to the wrong team is handled late and then
re-forwarded. Public data provide complaint volume but not triage minutes or
misroute rates; any savings estimate must use labelled assumptions.

## 2. Objective
Decide whether a product suggestion, which an analyst accepts or overrides, is accurate
enough to pilot. Automated routing without review is out of scope for the first release.

## 3. Stakeholders (simulated)
| Stakeholder | Interest | Involvement |
|---|---|---|
| Complaints operations lead | Throughput, regulatory timelines | Sponsor |
| Intake analysts | Workload, trust in suggestions | Users; accept/override decisions |
| Product teams (5) | Receive only their own complaints | Downstream recipients |
| Compliance / ombudsman liaison | Timeliness, audit trail | Approver |
| Privacy office | Personal information in complaint text | Reviewer |
| IT / data team | Integration, model hosting, support | Builder |

## 4. Scope
- **In scope:** the seven products and five simulated teams in
  [`sql/03_routing_scope.sql`](../sql/03_routing_scope.sql). Product suggestion from
  complaint text, analyst accept/override, audit record, operational reporting.
- **Out of scope:** credit reporting, debt collection, debt/credit management, student
  loans, issue-level classification (later extension), automatic routing without
  review, and customer responses.
- **Data:** CFPB July 2026 archive as US proxy data. There is one month of data, so
  no seasonality claims.

## 5. User stories
| ID | As a… | I want… | So that… | Acceptance criteria |
|---|---|---|---|---|
| US-1 | intake analyst | a suggested product and team for each complaint with text | I spend less time reading to route | Suggestion and confidence are shown; I can accept or override it; the override records a reason |
| US-2 | operations lead | a report of volume, timeliness and text coverage by team and product | I can staff and spot emerging problems | Totals reconcile with SQL; filters by date, team, product and channel ([dashboard spec](../dashboard/README.md)) |
| US-3 | compliance officer | every suggestion and decision logged with model version | I can audit routing decisions | The log holds complaint ID, suggestion, confidence, final team, analyst and timestamp |
| US-4 | intake analyst | complaints without text, or with a failed model call, to go to manual triage | nothing is lost or delayed | Such complaints are shown as "manual" with no suggestion, never with a guess |

## 6. Success metrics
| Metric | Baseline | Pilot target | How measured |
|---|---|---|---|
| Team-level accuracy (misroute avoidance) | Majority class, TF-IDF | Proposed: ≥ 80% on a fresh hold-out ([evaluation §7](04_ai_pilot_evaluation.md#7-next-steps-for-a-real-pilot)) | Untouched holdout vs. CFPB product mapped to team |
| Product accuracy / macro F1 | Majority class, TF-IDF | Proposed: no product below 0.6 F1 | Same holdout, per-class table |
| Share of complaints above confidence threshold | — | No threshold selected yet ([evaluation §4](04_ai_pilot_evaluation.md#4-confidence-threshold-and-human-review)) | Threshold chosen on validation data, not the holdout |
| Analyst override rate | — | Monitored during the pilot | Audit log (synthetic in demo) |
| Net analyst hours saved / month | — | Estimate only | `estimate_hours_saved()` with labelled assumptions |

Pilot targets were not pre-registered before the first baseline run (2026-10-21);
the [evaluation](04_ai_pilot_evaluation.md) proposes them for the next fresh hold-out.

## 7. Assumptions & constraints
- US CFPB data stands in for a Canadian bank's complaint inbox. Consumer-selected
  product labels are proxy ground truth.
- Only about 24% of in-scope complaints have public text. Complaints without text follow the manual path.
- The product-to-team mapping is a simulated design decision, documented in SQL.
