# Bank workflow specification increment v0.2

BANK-SDD-v0.2 · 19 October 2026 · S01 refinement and S02 contract preparation.

## Accepted business baseline

D-09: page-by-page lookup, permission constraints and knowledge learning effort are owner-reported pains. D-10: first job is charge identification and apparent duplicates. D-11: scoped read access for ordinary staff; privileged financial actions remain external. D-12/13: asynchronous specialist investigation, shared customer-service feedback queue; live transfer is exceptional. D-14: human callback, simulated service targets and normal closure. D-16: at most three attempts over three service days, then lead review without automatic closure. D-15: demonstrate tool use, durable continuation, business controls and actual agent value.

App messages, real outbound calls, actual refunds and full bank adjudication are outside this increment. The highest-volume intent is not established by evidence. Existing-case enquiry remains a proposed second job; reading related case history is needed for the selected first job.

## Detailed stories

| Story | Outcome | Requirements | Dependency / forecast |
|---|---|---|---|
| [DEV-02](../../specs/DEV-02/spec.md) | Open an authorized contact and assemble permitted customer context | FR-01, NFR-01 | DEV-01, BA-07, BA-09; S03 |
| [DEV-03](../../specs/DEV-03/spec.md) | Identify a card charge and investigate apparent duplicate entries | FR-02, FR-03, FR-06, FR-07 | DEV-02, BA-07; S03 |
| [DEV-05](../../specs/DEV-05/spec.md) | Retrieve applicable handling rules with verifiable citations | FR-05, FR-06, FR-15 | BA-06, BA-07, DEV-02; S03 |
| [DEV-07](../../specs/DEV-07/spec.md) | Submit a reviewed specialist enquiry with accountable ownership | FR-09, FR-10, FR-13, FR-16 | DEV-03, DEV-05, DEV-06, BA-09; S04 |
| [DEV-11](../../specs/DEV-11/spec.md) | Receive specialist findings and complete a verified customer callback | FR-17, FR-18 | DEV-07, DEV-06, BA-09; Reforecast pending; after S04 foundation, before B1 acceptance |
| [DEV-12](../../specs/DEV-12/spec.md) | Retry unanswered callbacks and guard normal closure | FR-18, FR-19 | DEV-11, BA-06, BA-09; Reforecast pending; after S04 foundation, before B1 acceptance |
| [DEV-13](../../specs/DEV-13/spec.md) | Handle overdue investigations and customer objections with linked work | FR-20, FR-21 | DEV-11, BA-06, BA-09; Reforecast pending; after S04 foundation, before B1 acceptance |
| [DEV-08](../../specs/DEV-08/spec.md) | Run a bounded evidence agent across persisted workflow stages | FR-06, FR-07, FR-12, FR-14, FR-22 | DEV-07, DEV-09, DEV-11, DEV-12, BA-09; S05 |

Every story has spec.md, design.md, tasks.md and acceptance.md. All application test results are Not executed. Canonical structured index: [workflow-stories.json](workflow-stories.json). Shared [tool contracts](../../specs/contracts/agent-tools.md), [JSON schemas](../../specs/contracts/agent-tools.json) and [rule register](../../specs/contracts/workflow-rules.md).

## CR-003 Scope and capacity impact

DEV-02/03/05/07/08 refine existing cards, with no duplicated estimate. New DEV-11/12/13 add specialist-result/feedback, retry/closure and exception slices: **11 developer-days + 2 BA-days + 3 QA-days = 16 person-days**, uncertainty 12–24. This is an uncalibrated incremental estimate. Expanded integration effort in DEV-08/QA/OPS needs checking in S02; do not assume it is free.

Previous total was 89.5 Dev + 28.5 BA + 30.5 QA = 148.5 person-days. Arithmetic scope total becomes 100.5 Dev + 30.5 BA + 33.5 QA = 164.5 person-days, before re-estimation. DEV-11/12/13 are not silently stuffed into S04/S05. Existing dates are a pre-change forecast, not a commitment for the expanded scope.

Sequence: S01 owner discovery/refinement; S02 close data/rule/tool/acceptance gates; S03 authorized lookup/policy; S04 reviewed referral and provider spike; then new continuation slices before B1 acceptance. Consider an additional two-week continuation iteration with 14 nominal developer-days for two developers, but confirm dependency sequencing, individual capacity and QA before assigning dates. At least one added iteration is the planning allowance; calendar forecast is pending, and voice/retail milestones inherit the shift. Do not use the original reserve as invisible extra capacity.

## Pending business and technical decisions

- DEV-13 exact escalation levels/recipients, repeated-update cadence, re-review authority and complaint intake remain proposed; accepted original deadline/progress duties still apply.
- Callback window calendar boundaries, holiday fixtures and technical-failure counting require S02 confirmation. Exhaustion never automatically resolves a case.
- API/schema review, role/action matrix, source authority, run limits and provider qualification remain Ready gates.
- The proposed 15% improvement threshold remains unapproved and unmeasured. Evaluate same-task guided baseline versus agent assistance with correction/verification effort included.

## Test and release plan

Schema contracts → pure calendar/state tests → database/authorization/idempotency integration → UI workflows → bounded provider qualification → controlled agent evaluation → owner UAT → staging migration/restore/rollback and manual fallback. Fake providers test orchestration, not model quality. Synthetic specialist returns demonstrate integration, not production-bank access.

Show a normal enquiry and end-to-end referral/feedback, unanswered retries, delayed result with stale proposal rejection, and customer correction. Audit the source IDs/tool results/proposal/person approval/operation receipt throughout. No raw sensitive data or private model reasoning in traces. A public demo uses synthetic users, records and phone outcomes.

## Trello publication

Update existing relevant cards and add only DEV-11/12/13. Keep detailed candidate cards in backlog/review; no implementation Done. GitHub repository URL remains pending. Trello carries self-contained text, not broken local document URLs. Actual saved-card verification is recorded separately after browser synchronization.

Publication completed: [23 card verification records](workflow-trello-sync.json); three new cards plus 20 updates, total board registry 54 cards. [Structural check](workflow-validation.json) passed; runtime acceptance remains Not executed.
