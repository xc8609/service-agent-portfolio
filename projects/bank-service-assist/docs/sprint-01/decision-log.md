# Decisions, assumptions and change impact

Version 0.1 · 19 October 2026. Actual portfolio owner decisions are distinguished from authored recommendations.

## Decision register

| ID | Decision / rationale | Status and authority | Impact |
|---|---|---|---|
| D-01 | Primary pain is finding customer information and handling rules | **Accepted by owner**, explicit answer 19 October 2026 | Prioritize evidence workflow and lookup/verification time; notes secondary, follow-up conditional |
| D-02 | Keep duplicate-charge and existing-case enquiry as first two jobs | Partially superseded by D-10: transaction enquiry selected first; existing-case enquiry remains proposed | No new financial service action added; detailed branches remain under review |
| D-03 | Compare guided search/templates and bounded assistance on same facts | Proposed design recommendation | Agent value must exceed simpler alternative; B0 required |
| D-04 | Proposed 15% lookup-time improvement with preserved quality | Proposed numeric business gate, owner review pending | Freeze before study, do not treat as forecast/result |
| D-05 | Keep complaint review independent from operational follow-up | Proposed simulated safety/semantic design | New explicit FR-11, scenario SC-13 and UI state; S02 must finalize policy boundary |
| D-06 | Git specs canonical; Trello planning/review mirror; public portfolio only | Owner previously authorized public GitHub/Trello; workflow details for review | No private job workspace/history export |
| D-07 | Two developers as normal-team baseline, optional third; BA/QA explicit | Owner requested normal 2–3 developer estimate; allocation details remain planning assumptions | S01 has actually started as portfolio work, no real team staffing claimed |
| D-08 | Current specification version 0.1 is review candidate, not implementation baseline | Author workflow state | Unresolved critical S02 policy/auth/schema/NFR decisions prevent calling code-ready |
| D-09 | Owner confirms page-by-page information collection, access restrictions requiring control, and knowledge-base learning effort (E-09) | Owner-reported problem clarification, 19 October 2026; not approval of the target design | Refine AS-04/05 and P-01a/b/e; compare authorized evidence collection and contextual guidance with simpler search. Exact permission matrix, first jobs and benefit magnitude remain open |
| D-10 | Start the walkthrough with credit-card statement/transaction enquiries: identify a charge and investigate why it appears twice | Owner-selected initial business focus, 19 October 2026 | Elaborate UC-01 across information lookup, access control and applicable handling rules. No implied approval of fees/interest calculation, payment execution, refunds or the full target workflow |
| D-11 | Ordinary representatives may read transaction details/status within authorized customer scope; refunds and similar privileged actions require separately authorized personnel | Owner-approved simulated permission boundary, 19 October 2026; not a claim about a former employer | Read permission does not imply action authority. Agent inherits no additional authority. First release retains its exclusion of financial execution; specialist authority, approval conditions and handoff channel still require design |
| D-12 | Default to asynchronous specialist review and later customer feedback; reserve live transfer for exceptions; prioritize high-volume cases | Owner-approved design direction, 19 October 2026; actual volume ranking unknown | Design the routine path first; do not assume referrals dominate initial-contact explanations. Communication ownership accepted in D-13; normal targets/channel/closure in D-14; retry exhaustion in D-16 |
| D-13 | Specialists own investigation; the shared customer-service feedback queue owns customer communication, without requiring the original representative | Owner-approved responsibility split, 19 October 2026 | Channel, service targets and closure conditions subsequently accepted in D-14; Trello mirrored; current review history in S02 sync records |
| D-14 | Human callback first; App messages later. Accept the simulated normal service calendar, time targets and closure conditions in BA-04 | Owner accepted on 19 October 2026 | One service day for acceptance, two from submission for investigation, one after approved result for first callback attempt; progress update by investigation deadline if unfinished. Holiday fixtures still need definition. Exception rules remain proposed |
| D-15 | Demonstrate an agent-connected end-to-end workflow, agent value, architecture and business-system design | Owner clarified portfolio emphasis on 19 October 2026 | Evidence gathering, tool use, durable continuation and reviewed action proposals must be demonstrable; permission, timing and transition controls remain deterministic. No mandate for full bank operations or real financial execution |
| D-16 | At most three callback attempts in three service days, then responsible-person review; no automatic closure | Owner accepted on 19 October 2026 | Includes first attempt and at most one per service date from the reviewed proposal; precise calendar boundary and technical-failure fixtures need S02 review |
| D-17 | Feedback staff see masked queue summaries before claim and necessary case details after claim; verify customer again before disclosure | Explicit owner answer during S02 review, 19 October 2026 | Separate staff preparation scope from caller verification; atomic claim and reassignment tests required |

| D-18 | Never-placed calls caused by technical failure do not consume contact quota; record the fault and do not extend deadlines. Placed unanswered calls count once | Explicit owner answer during S02 review, 19 October 2026 | Backend-derived quota, auditable fault, unchanged first-callback/window deadlines; exact boundary subsequently accepted in D-19 |

| D-19 | First actually placed callback date is day 1; third service date at 17:00 America/Winnipeg is the deadline, excluding configured holidays. Expiry leads to review even below three calls; original first-callback target remains before first placed call | Explicit owner answer, 19 October 2026 | SR-13; DEV-12-AC04/T04; calendar dates rather than rolling 24 service hours; no automatic closure or fault-based extension |

| D-20 | Overdue investigation retains its original specialist and original deadline. Notify the responsible lead and create customer progress work in the feedback queue. The specialist proposes the next update time; the responsible lead confirms it. Preserve original overdue history. The agent may gather evidence, remind and draft, but cannot commit a completion date. | Explicit owner answer, 19 October 2026 | DEV-13-AC01–04; approval/data contract completion remains a Ready gate |
| D-21 | Feedback staff preserve the customer statement and new evidence, and route disputed findings to specialist re-review. An explicit complaint request creates an independent complaint-intake record without waiting for re-review. Both tracks link to the original case and keep independent ownership/status. Objection or silence never implies resolved closure. | Explicit owner answer, 19 October 2026 | DEV-13-AC05–07; independent intake/linkage contract remains a Ready gate; no full complaint-management platform |

| D-22 | After contact quota or window exhaustion, the responsible lead may approve a reasoned new contact plan or a review hold with a named owner and review date. Preserve all original attempts, deadlines and approval history. Never reset history or mark the case resolved merely because the customer did not answer. Agent suggestions cannot authorize the new plan or hold. | Explicit owner answer, 19 October 2026 | DEV-12-AC03/07; separate approved plan/history and hold review controls required before Ready |

## Assumptions and evidence gaps

### D-23 — Paired enquiry when transaction recognition is ambiguous

Owner explicitly accepted RI-01 on 20 October 2026: when a customer recognizes
one purchase but cannot distinguish the two matching statement entries, allow
both entries to be submitted together for specialist review. Record one purchase
recognized and unresolved transaction mapping. Neither staff nor the agent may
arbitrarily select an entry as the duplicate or infer entitlement to a refund.
This is a simulated business rule, not implementation acceptance.

Trace: [DEV-07 intake refinement](../../specs/DEV-07/referral-intake-review.md),
M04 and RI-AC02/RI-T02. RI-02 was subsequently accepted as D-24 below;
RI-03 was subsequently accepted as D-25 below. Contracts, implementation and tests are pending.

### D-24 — Initial enquiry with incomplete supporting material

Owner explicitly accepted RI-02 on 20 October 2026: allow initial specialist
enquiry when supporting material is incomplete, provided the mandatory intake
minimum is available. Record evidence gaps. The specialist determines whether
additional material is needed and requests it; customer service contacts the
customer to obtain it. Preserve original submission time and processing
deadlines; missing or later-supplied material does not reset or extend them.
This does not waive identity, transaction-scope or submission controls, establish
a new financial-dispute procedure, or accept implementation.

Trace: [DEV-07 intake refinement](../../specs/DEV-07/referral-intake-review.md),
RI-AC04/RI-T04 and RI-AC10/RI-T10. Contact gaps (RI-03) were subsequently accepted as D-25.

### D-25 — Continue investigation when customer contact details are unusable

Owner explicitly accepted RI-03 on 20 October 2026: allow specialist enquiry
submission while customer service owns resolution of the contact-details gap.
Retain original processing deadlines; an undelivered result must not automatically
close the case. Investigation and customer-feedback progress remain distinct.
The reviewed design does not grant ordinary staff or agents authority to silently
replace verified contact details or treat a caller-provided number as verified.

Trace: [DEV-07 intake refinement](../../specs/DEV-07/referral-intake-review.md),
RI-AC05/15/16/17 and corresponding planned tests; DEV-11/12 continuation.
RI-01–03 business review is complete. Typed contracts, queue configuration,
implementation and runtime acceptance remain pending; no new SLA is invented.

### D-26 — Keep the core small and the repository navigable

Owner requested on 20 October 2026: avoid unnecessary complexity, preserve the
core workflow, maintain clear project structure and a concise README, and publish
work through a PR. [Current delivery](../../../../docs/backlog/current-delivery.md)
records implementation prioritization: manual investigation/referral/result/
feedback first, then bounded assistance. Advanced continuation automation, voice
and retail remain later scope. D-23–D-25 and existing access/deadline/closure rules
are retained; no new contact allowance, benefit result or implementation approval
is inferred. Forecasts require re-estimation before commitment.

### D-27 — Evaluate with a subscription model until an API route is enabled

Owner directed on 21 October 2026: no paid model API for now; use the existing
subscription for model evaluation. A subscription session can produce recorded
outputs for frozen synthetic cases; they are replayed offline through the same
citation, claim and schema guards. This is a pilot, not provider qualification: the
application's live route stays disabled and no latency/cost claim is made.

### D-28 — Publish analysis results, cite rather than copy source data

Owner directed on 21 October 2026: the public repository includes analysis results
(aggregates, metrics, findings, SQL and workbooks) from public datasets, while raw
source files stay local and are cited with provenance, checksum and terms. Release
versions may follow delivered value rather than the original Sprint numbering.

| ID | Assumption / gap | Validation / owner role | Consequence if false |
|---|---|---|---|
| A-01 | Lookup consumes material avoidable effort | EL-02 observation/task study; owner/service lead | Prefer better navigation/templates or stop AI investment |
| A-02 | Source data and policies can be accessed reliably with explicit scope | BA-07 contracts; engineering/access owner | Scope down to available evidence; no invented integration |
| A-03 | Applicable policy metadata can distinguish date/product/audience | Policy inventory; steward role | Need curation before retrieval claims |
| A-04 | Simulated conditions resemble useful representative decisions | Owner walkthrough and later external domain review | Revise fixtures/branches before evaluation |
| A-05 | Two intents offer enough depth for first release | Owner scope review, error analysis | Change breadth through CR, not hidden additions |
| A-06 | Volunteers or owner role-play can establish formative effort observations | QA-03 participant plan | Report self-test only; no real-bank efficiency inference |
| A-07 | Proposed role capacity and calendar remain available | Sprint planning at actual kickoff | Reforecast, particularly year-end and phone integration |
| A-08 | Formal complaint process is external and must be represented honestly | BA-06/07 define flag, reference and manual handoff | Do not market complete complaint management or compliance |


## CR-001 Lookup-first prioritization

Trigger: E-02, actual owner answer on 19 October.
Before: primary value discussed as combined lookup and documentation assistance.
After: lookup/customer context/applicable rule is primary; note/follow-up remains supporting workflow.
Affected: BA-01 value hypothesis, BA-03 AS-04/05, BA-04 TO-02–04, BA-05 BR-01/FR-02–06/MEAS-01, KPI-01/02/03/05, future DEV-03/04/05/08/10 and QA-03 demonstration priorities.
Scope/estimate: no story added or removed; current estimate preserved provisionally. Re-estimate if data/source integration grows.
Decision: priority accepted by owner. Detailed numerical target and complete specification remain proposed. No implementation changed.

## CR-002 Policy effective-date dependency

Trigger: E-05 official page revision dated 23 June 2026 with effective date 23 June 2027, observed 19 October 2026.
Impact: POLICY metadata, RULE-15/FR-15, SC-17, BA-06 policy review and BA-07 effective-date fields; regression examples across date boundaries.
Decision: **recorded for investigation**, not approval to apply the future guideline now. Use fictional versioned policies for the demo. Verify applicable current/legal context with authoritative sources and competent organizational review before real use.
Release impact: no new regulatory subsystem; no blanket Canadian-bank compliance claim.

## Concrete owner review package

Review progress: D-09 established the three problem dimensions; D-10 selects transaction identification and apparent duplicate charges; D-11 accepts ordinary-representative read access versus privileged financial actions; D-12 selects default asynchronous review and later feedback; D-13 assigns communication to the shared customer-service feedback queue. Existing-case enquiry remains a candidate second job. Restricted access is a constraint to preserve, not permission for an assistant to bypass it. Proposed field masking, role-specific guidance and handoff behavior require further review. These clarifications and D-14–D-16 are mirrored in Trello; see workflow-trello-sync.json for 23 saved and verified cards.

1. Confirm/adjust two initial jobs and assumed as-is steps (D-02, A-04).
2. Review evidence layout and no-new-task vs complaint-signal distinction (D-05).
3. Accept or revise proposed usefulness threshold and comparison protocol (D-04).
4. Confirm who can approve the public-demo scope/release; real bank roles remain simulated.

These are review items, not a request to stop drafting. Work that does not rely on acceptance continues; later implementation must close critical decisions.


## CR-003 Reviewed workflow elaboration

See [workflow increment](workflow-increment.md): eight detailed development specifications, three new cards and an explicit +16 person-day scope estimate. D-09–D-16 distinguish owner input from draft exception rules. Trello publication verification is recorded in workflow-trello-sync.json after synchronization. No implementation is accepted by this change.

## CR-004 S02 contracts and reforecast

Owner requested S02 refinement on 19 October 2026; S01 repository/acceptance work remains open. See [S02 index](../sprint-02/README.md), current business review and capacity forecast. No dependent implementation is accepted merely because contracts exist.
