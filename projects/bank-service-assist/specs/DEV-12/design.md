# DEV-12 design

BANK-SDD-v0.2 · Candidate architecture; no runtime implementation.

Model-visible tools: get_case_snapshot, get_contact_attempts, get_service_targets, create_proposal, get_operation_status. Human/system commands and complete schemas are in [shared contracts](../contracts/agent-tools.md).

## Delivery boundary

- Implement versioned calendar calculations and persisted attempts; reserve slots to prevent concurrent duplicates.
- Add queue lead review state and callback constraints with manual fallback.
- Implement server closure preconditions and reasoned rejection with preserved notes.

## Cross-cutting contract

Backend derives identity and scope. Every returned record carries source/version/as-of. Read, draft and committed states are distinct. No UI-only authorization. Human approval rechecks versions, permissions and allowed transition; commit business data, audit and outbox atomically. Reconcile uncertain outcomes using the operation key. Restart does not lose committed state.

UI must distinguish loading, empty, denied, failed, stale and completed. Manual lookup/edit remains available on agent failure. Show actual receipts and customer-visible explanations separately from internal notes. Tool/schema errors are typed and sanitized; safe correlation IDs link events and evaluation.

## Data and integration

Use explicit foreign keys among contact, case, work item, result, attempt and proposal; version changes must invalidate dependent drafts. Record synthetic provenance. API/data contracts are finalized in BA-07/09 before implementation. Integration tests use a real test database and deterministic calendar, not only model mocks.

## Deployment

Ship through existing API/worker/UI release, with migration and fixture updates. Verify permissions, pending-event replay and rollback/restore in staging before acceptance. This story does not provision infrastructure or contact real customers.

## D-18 callback quota semantics

A technical failure with dial_state=not_placed does not consume contact quota. Persist the fault and preserve all original deadlines. A placed unanswered call consumes one contact attempt. The server derives counting from trusted call evidence; the agent cannot override it.

DEV-12-T01 must include paired synthetic fixtures: existing count 1, unchanged due time, then (a) not_placed + technical_failure leaves count 1 and persists fault, (b) placed + no_answer produces count 2. Replay of either operation key must not duplicate its effect. Deadline expiry still sends the case to lead review, never resolved closure. These tests are planned, not executed.

## D-19 deterministic calendar fixtures (planned)

First actually placed callback service date is day 1; the retry window ends at 17:00 America/Winnipeg on the third service date, excluding configured holidays and weekends. At the deadline, unresolved feedback enters lead review even if fewer than three calls occurred; no extension or automatic resolved closure. Before the first placed call, the original first-callback target still applies. Never-placed technical faults do not start or reset this window.

DEV-12-T04 must cover:
- Monday first placed call, no holidays: deadline Wednesday 17:00 local.
- Friday first placed call, Monday configured synthetic holiday: deadline Wednesday 17:00 local.
- First placed call at 16:59 still makes that date day 1; this is not a rolling 24-service-hour timer.
- At deadline minus one second, eligibility still checks quota/date/contact windows; at the exact deadline no new normal retry is authorized and unresolved feedback goes to lead review.
- Two counted calls plus a never-placed fault still expire at the original deadline.
- Only never-placed faults: retain the first-callback target and its overdue evidence; no fabricated first-call date.
- Across a DST change use local calendar dates and 17:00 local, then store the UTC instant; do not add fixed 72-hour durations.

All fixtures use synthetic records and configured calendar data. They are specification examples, not executed runtime tests.

## Accepted lead continuation — D-22

After contact quota or window exhaustion, the responsible lead may approve a reasoned new contact plan or a review hold with a named owner and review date. Preserve all original attempts, deadlines and approval history. Never reset history or mark the case resolved merely because the customer did not answer. Agent suggestions cannot authorize the new plan or hold.

See [continuation addendum](../contracts/continuation-addendum.md). Ordinary retry eligibility remains bounded by D-16/D-19; exceptional contact requires a separate approved plan. Plan quota/window limits must be explicit, never inferred as an automatic fresh three-call allowance.
