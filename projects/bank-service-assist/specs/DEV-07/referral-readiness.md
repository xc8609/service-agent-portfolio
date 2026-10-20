# Referral readiness after D-23–D-25

20 October 2026 · Specification review, not executed runtime acceptance.

RI-01–03 are accepted simulated business decisions. Do not ask the owner to
approve them again. Implementation remains bounded to the separate inbound
read slice; referral, supplementation and contact-resolution writes are absent.

## Inspected baseline and gaps

| Gate | Evidence in current repository | Work before dependent implementation | Owner / trace |
|---|---|---|---|
| Typed intake | v0.4 referral payload has transaction IDs, concern, checked facts, missing-evidence strings, review request, queue and related case | Add recognition mapping and statement revision references; distinguish unknown/declined/not-requested; validate selected IDs, customer scope and source versions | BA-07/09, DEV-03/07; RI-AC01–04 |
| Durable supplemental evidence | Missing-evidence strings and evidence references do not define a request/response lifecycle | Versioned specialist request, customer-service task, response/evidence references and append-only history; retain deadlines | BA-07/09, DEV-07/11; RI-AC04/10 |
| Contact gap | Work items support queue/assignee/parent links; no complete contact-resolution contract | Configured customer-service ownership, reason/status, contact reference, review obligation and trusted resolution evidence; no ordinary-staff customer-master write | BA-06/07/09, DEV-07/11; RI-AC05/15–17 |
| Independent progress | Investigation results and feedback work exist in reference model; state transitions enforce verified feedback before closure | Show investigation result while feedback is blocked; scheduler must preserve due times, escalate deduplicated overdue work and avoid false closure | DEV-11/12/13; RI-AC15–17 |
| Existing-work and policy evidence | Running UI returns related IDs but lacks case-detail/policy lookup | Implement DEV-04/05; define same-concern check and configured manual/risk route; source failure is not absence | BA-06, DEV-03/04/05/07; RI-AC06/07/13 |
| Human-reviewed write | v0.4 proposal/approval/receipt design exists; runtime serves reads only | Recheck current authorization/versions and route; commit case, work, audit, outbox and receipt atomically; reconcile lost responses | DEV-06/07, QA-01; RI-AC08/09/11 |
| UI baseline | Live review found changed filters leave prior results/evidence visible; cents and UTC input remain technical | Bind selected evidence to executed query, clear customer context on switch, add explicit currency and business-date semantics | DEV-03; RI-AC12/14 |
| Test evidence | Current evidence covers read paths, not these writes | Versioned fixtures plus real-PostgreSQL write/denial/concurrency/restart tests and browser journeys; owner UAT last | QA-01, OPS-01; RI-T01–17 |
| Forecast | DEV-07 remains provisionally S04 / four developer-days, no new estimate validated | Allocate work to existing dependencies; re-estimate incremental supplementation/contact-resolution changes before commitment, split work exceeding five developer-days | BA-09; do not claim unchanged cost is verified |

## Proposed technical representation

Names below are design candidates, not accepted JSON Schema fields. Refine schema,
OpenAPI, reference model, migrations, permissions and seed fixtures in one change.

- Recognition: `specific_entries` or `pair_unresolved`, original statement/revision
  reference, selected IDs and recognized/queried ID sets. Explicit mapping must
  be disjoint and contained in selected authorized IDs. Unresolved mapping must
  not smuggle a model-chosen disputed ID. This slice requires two distinct IDs.
- Supplementation: case and originating work references, requesting specialist,
  versioned question/evidence need, customer-service queue/assignee, state,
  requested/received timestamps and evidence references. Preserve original due
  dates; a request is not an attachment receipt and no upload service is implied.
- Contact resolution: case/parent work, trusted contact reference or explicit
  unusable state, customer-service queue, responsible lead, claim/review fields,
  resolution source and version. Raw phone numbers do not belong in model traces.
- Display separate `investigation`, `contact_resolution` and `feedback` progress.
  Do not introduce a single ambiguous “completed” status that closes all three.
- Proposed commit boundary: new enquiry and required contact-resolution work
  are durable in the same business transaction. A missing queue configuration
  fails safely; retry cannot create a case without its required follow-up work.
- Trusted contact-profile update is a simulated external adapter/reference in
  this release, not a new production identity/profile system. Resolving a contact
  gap does not itself count as a call attempt or satisfy customer verification.

## Deterministic fixture and verification plan

| Fixture | Expected evidence | Planned test |
|---|---|---|
| Two posted CAD 85 entries, one recognized purchase, unresolved mapping | Both IDs; no invented duplicate label | RI-T02 |
| Same pair, no receipt; specialist later requests and receives evidence through customer service | Request/response history and unchanged original deadlines | RI-T04/10 |
| Unusable contact details at submission, valid service queues | Enquiry and contact-resolution work; separate owners/status | RI-T05 |
| Finding arrives before contact resolution | Investigation complete; feedback outstanding; case remains open | RI-T15 |
| Gap crosses original due date, repeated scheduler delivery | Original due retained, one logical escalation, no closure | RI-T16 |
| Trusted contact update then callback preparation | New permitted reference, retained history, fresh verification before disclosure | RI-T17 |
| Scope revoked, mixed-customer IDs, stale policy/transaction/proposal, invalid queue | No unauthorized/partial domain writes; safe draft recovery | RI-T03/08 |
| Submission response lost, worker restart, duplicate event | Original receipt and exactly one logical effect per event/key | RI-T09 |
| Customer changes account or search filters, or now denies both transactions | Old advice/selection invalidated; no accidental referral from stale evidence | RI-T07/12 |

Planned only. PostgreSQL API tests, browser tests, source/worker fault injection,
container recovery and owner UAT must generate new evidence; existing read-path
CI cannot stand in for this coverage. No application tests are added in this
specification-only update.

## Deferred automation boundary — not a blocker for the manual core

The existing D-16/D-19 callback plan and D-22 exceptional continuation rules are
accepted. The new supplementation/contact-resolution flow creates earlier
customer-service work. Clarify whether these earlier actual outbound calls
share the same three-attempt plan as final-result feedback or have a separately
approved bounded plan. Do not assume unlimited extra calls, reset the existing
plan, invent attempts when no call was placed, or implement a new allowance.
Under D-26 and the [current delivery scope](../../../../docs/backlog/current-delivery.md),
use owned manual follow-up/lead review in the first increment. Schema/read/UI and
reviewed referral work can proceed. Resolve this boundary before adding the
dependent call scheduler; do not add automatic outbound calls or grant extra
attempts. Technical draft-save failures are not contact attempts.

Other queue aliases, field names, constraints, atomic writes and test fixtures
are engineering/configuration work; they do not require repeating the three
accepted business decisions. Numeric escalation/review schedules beyond the
existing accepted deadlines must be explicitly configured/reviewed, not invented.

## Development order

1. Repair query-context UX; persist versioned customer statement/recognition and
   establish current case/policy evidence (DEV-03/04/05).
2. Refine typed intake, supplementation and contact-resolution contracts, queue
   configuration, synthetic fixtures and migration design (BA-06/07/09).
3. Build manual preview/approval, atomic referral and receipt reconciliation
   (DEV-06/07); make missing-material/contact-gap scenarios executable without AI.
4. Implement supplementation and contact-resolution continuation, deadline/closure
   guards and failure recovery (DEV-11/12/13); resolve the call-plan boundary first.
5. Add bounded Agent drafting using the same reviewed commands and evidence;
   compare effort/quality against manual baseline (DEV-08/09, later evaluation).

No Sprint or story is Done. Accepted business rules, completed technical design,
implemented behavior and executed acceptance remain separate states.
