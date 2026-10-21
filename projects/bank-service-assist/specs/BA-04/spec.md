# BA-04 Target process, decisions and exceptions

Version 0.2 · 21 October 2026 · **Target process aligned with D-17–D-28 and the implemented workflow** (see [lifecycle v0.2](#target-lifecycle-v02)); v0.1 sections below remain as design history. B0 is a usable human workflow; B1 adds bounded evidence assistance. Formal rule/data/NFR baselines are S02 work.

## User-visible target experience

The representative sees a contact header and verification/scope state, customer/account facts, transaction or case timeline, and a policy/evidence panel. The assistant's panel separates: the customer's statement, verified records, applicable policy references, unresolved questions and suggested next action. A draft note/task is editable and separate from committed activity.

Do not show a reassuring confidence percentage in place of evidence. Use explicit states: evidence available, clarification needed, policy unavailable, conflicting evidence, manual handling required, draft stale, saving, saved, save failed. Keep the manual tabs and draft accessible on model failure.

## Future workflow and responsibility

Owner review input E-09 confirms fragmented lookup, permission constraints and knowledge-base learning effort in prior experience. Proposed response: assemble relevant permitted evidence with source links; provide context-specific handling guidance with applicable references and missing-information prompts. The backend must enforce access before information reaches the model, not hide unauthorized information only in the UI. Candidate distinctions include allowed/masked/denied information and permitted next steps; the actual permission matrix and handoff mechanism remain S02 review items. These are design proposals, not owner acceptance or implemented capabilities.

| Step | Human task | System responsibility | Persistent evidence / acceptance |
|---|---|---|---|
| TO-01 Open contact | Confirm contact purpose and verification state | Derive authorized scope from session | Contact ID; no model-supplied role accepted |
| TO-02 Clarify | Confirm selected transaction/case and missing facts | Show known vs reported facts, timestamps and sources | Relevant turn/fact references; no future-turn leakage |
| TO-03 Find evidence | Search manually or request assistance | Read only scoped records; filter policy applicability | Selected record IDs/versions and policy ID/version/section |
| TO-04 Review result | Verify facts/rule; correct or reject | Flag evidence gaps; propose explanation, clarification or manual path | Supported recommendation; no unsupported financial promise |
| TO-05 Handle dissatisfaction | Review complaint signal independently | Preserve signal and applicable manual procedure route | Complaint-review flag/reference; no automatic dismissal |
| TO-06 Decide follow-up | Select none / existing work / justified new work | Require reason/owner and duplicate check | Explicit next action; no mandatory new case for every call |
| TO-07 Draft and edit | Edit note and proposed task | Keep original proposal and human edits distinguishable | Draft version, source versions and edits |
| TO-08 Approve | Explicitly approve current proposal | Recheck authorization, facts/policy versions and allowed transition; commit once | Domain record + audit + outbox transaction; operation receipt |
| TO-09 Conclude contact | State actual result and unresolved next step | Distinguish saved, queued, assigned and completed | Contact disposition; case remains open when appropriate |

## Manual and assisted paths

### UC-01 review increment: transaction explanation and privileged continuation

Accepted simulated boundary D-11: an ordinary representative can read transaction details and status within an established authorized customer/account scope. Refunds and similar privileged actions require separately authorized personnel; higher seniority alone does not grant authority. No financial execution is added to this release, and the assistant cannot perform such an action on the representative's behalf.

Proposed continuation, not yet owner-approved:

1. Confirm the selected entries, purchase recognition, statuses and any reliable relationship evidence. Do not infer duplicate settlement from matching amount/merchant or infer a relationship from pending/posted statuses alone.
2. Retrieve the applicable versioned simulated handling rule. Show source facts, customer assertions, missing evidence and the rule separately. Unavailable or conflicting evidence leads to clarification/manual review.
3. Where evidence and the rule support an explanation with no additional work, the representative explains and records the enquiry. A customer's continued disagreement or dissatisfaction must still be assessed; contact closure does not prove transaction resolution.
4. For a possible duplicate requiring investigation, propose a review request rather than a refund instruction. Include transaction references, the customer's account, checked facts, applicable rule, missing information and desired review. Check existing related work first.
5. The representative reviews/edits and explicitly submits only if permitted. The server rechecks authority and returns the actual receipt. Queued, assigned, failed and outcome unknown remain distinct; a failed submission is not a successful referral.
6. Communicate the actual reference/status and only a supported next-update commitment. Specialist review and any financial action remain outside this first-release workflow. Preserve unresolved ownership after the call ends.

Accepted continuation D-12: asynchronous specialist-review work item and later customer feedback are the default non-urgent path; live transfer is an exception. The owner wants the highest-volume cases prioritized, but no frequency data exists. This does not imply that referrals dominate initial-contact explanations. Urgent/risk and dissatisfaction branches still need separate rules. These draft steps have not been implemented or tested.

### Routine post-referral lifecycle — proposed for review

The walkthrough assumes a non-urgent enquiry needs investigation and the initial evidence package is complete. This is a chosen design path, not a measured majority of contacts.

1. Intake receipt records the work reference and accountable queue. Queue ownership exists before an individual specialist accepts; elapsed targets and escalation rules must be defined before implementation.
2. An authorized specialist accepts and reviews the package and relevant records. Further evidence can be requested without discarding ownership or creating a second case for the same issue.
3. Specialist return distinguishes findings/evidence, approved customer-facing explanation, next action, and any external financial-action status. Review complete is not equivalent to refund executed. Internal-only details must not enter a customer-facing draft.
4. Accepted responsibility split D-13: specialists own investigation and a shared customer-service feedback queue owns customer communication, with a named assignee when work starts; the original representative is not the only possible recipient. An assistant can draft from approved results but cannot originate adjudication or claim payment execution. Human review precedes communication.
5. Record communication attempts and their actual outcomes separately from review completion. Sent is not necessarily delivered or acknowledged; failed contact remains actionable under a defined follow-up rule. Human callback, normal closure and retry exhaustion are accepted in D-14/D-16; exact exceptional disposition rules remain under review.
6. Close the service work only when the defined disposition, required action evidence and communication conditions are met, with no unowned outstanding work. Further disagreement or new evidence uses a linked continuation/review route; do not mark the issue resolved merely because the customer is silent.

First-release boundary: demonstrate the referral, structured synthetic specialist return, feedback draft and status/history in the representative workflow. Do not silently add a full specialist adjudication system, actual refunds or real customer messaging. Technical scope/estimates require reassessment if those capabilities are requested. Proposed evaluation covers package completeness, ownership, truthful status and feedback follow-through; volume and savings remain unmeasured.

### Accepted simulated normal feedback channel, time targets and closure

Owner accepted this normal-path proposal in D-14 on 19 October 2026. All numbers remain authored portfolio service targets, not observed performance, bank policy, regulatory deadlines or guaranteed financial-resolution dates. Implementation and tests are pending; references to a proposal below describe the accepted simulated design, not a real bank procedure.

- Channel: propose a human callback as the initial phone-originated journey. At intake, confirm an approved contact number and preferred callback window using the established contact process; a number change is not implicitly authorized by this workflow. Re-establish required identity assurance before discussing private transaction details. Do not disclose transaction details in voicemail. Secure in-app messages and generic SMS notifications are possible later alternatives, not accepted scope. First release records simulated attempts/results, with no real outbound calling or messaging.
- Time model: use a versioned service calendar. For a deterministic demonstration, propose Monday–Friday 09:00–17:00 America/Winnipeg, excluding configured holidays; one service day equals eight service hours. Service hours are accepted in D-14; holiday fixtures remain pending. Store actual timestamps as well as calculated due times.
- Intake and ownership: issue a receipt on successful submission; queue owns the item immediately. Target named specialist acceptance within one service day of submission.
- Investigation: target an approved result within two service days of submission, including the acceptance period. If unfinished, provide a progress update by that same deadline, state outstanding work and set the next review/update time. A progress update does not erase an overdue investigation target.
- Result feedback: target the first callback attempt within one service day of an approved result. This is an attempt target, not a promise of successful contact; earlier promised updates still apply. Honour recorded callback windows and flag any deadline conflict rather than silently extending it. Reminder/escalation does not automatically close work or pause the clock.
- Normal closure: an authorized result and supporting references exist; all required business actions are complete (or no action is needed); verified customer feedback is recorded with its actual outcome; no outstanding enquiry/review task remains. A completed explanation does not require a positive satisfaction score, but continued substantive disagreement must follow the review/complaint path before routine closure. Silence, unanswered calls, sent messages and refund approval alone do not establish resolution.
- Proposed normal state sequence: queued → investigating → awaiting feedback → closed. Additional-action and unsuccessful-contact branches remain open work, not routine closure. Human confirmation and server-side preconditions govern closure; the model may propose a summary but cannot decide completion.

### Exception review and agent orchestration — proposed, not accepted

> Superseded for implemented rules by the [v0.2 lifecycle](#target-lifecycle-v02); kept as the original design reasoning.

D-15 emphasizes a demonstrable agent-connected workflow. The following candidate rules and acceptance examples require incorporation into BA-06 decision tables, BA-07 data contracts and the machine-readable scenario/requirement register after review. They do not establish new implemented or tested coverage.

**Unanswered callback — business rule accepted in D-16; detailed contract pending:** record an actual human-entered call outcome. Keep the case awaiting feedback and retain feedback-queue ownership. Allow at most three total attempts, including the first, over three service days starting with that attempt, at most one per service date and within approved contact windows. Scheduling/window conflicts go to the queue lead. After exhaustion, route to human review as unable-to-contact; do not automatically close as resolved or silently switch channels. A later administrative closure policy is not yet approved. Agent retrieves previous attempts and the latest approved result, prepares an updated briefing and proposes a permissible retry; deterministic scheduling/limits decide when it may occur. No model-only claim of a completed call counts as evidence.

**Investigation overdue:** a scheduler detects the deadline; the existing specialist/queue retains ownership. Re-read case status before action to avoid escalating an already completed case. Agent gathers recorded blockers, pending evidence and previous commitments; unknown reasons stay unknown. Propose a concise escalation to the queue lead and a fact-grounded progress-update draft for the feedback team. Human confirms customer-facing content and next commitment. Preserve the original deadline and overdue history; updates do not reset the clock. Deduplicate escalation by case, deadline and escalation level.

**Customer disputes result:** retain the customer's exact objection alongside the existing conclusion. Agent compares it with the prior evidence and suggests clarification, linked re-review for new evidence/possible error, or the appropriate complaint-review path. These may overlap; a complaint request must not be delayed until a re-review completes. A person confirms the route. Invalidate affected drafts on new evidence, retain versions and link work rather than creating disconnected duplicates. Only an authorized specialist can revise the finding; the agent cannot adjudicate, refund or pressure the customer into acceptance. A contact after closure enters an explicit linked reopen/review path rather than erasing the original disposition.

**Application boundaries:** representative workspace → authenticated API → durable workflow/case state plus event worker → bounded agent run → typed evidence/search tools → versioned proposal → human approval → server authorization/freshness/transition checks → atomic domain write and outbox event. The UI reads persisted receipts, not model prose as execution proof. Timer/limit/permission enforcement works without an LLM. Runs start on relevant events or staff requests and stop after a proposal; they do not remain running across days of waiting. Resume from persisted business state and refreshed evidence. A provider failure retains work and permits manual continuation. Provider choice sits behind an adapter; this increment makes no SDK compatibility claim.

**Candidate executable demonstrations:** unanswered call produces one valid retry proposal and no resolved closure; exhausted attempts require review; overdue event produces one escalation despite duplicate delivery; result arriving during escalation invalidates stale action; new customer evidence preserves old findings and routes for review; an explicit complaint request is preserved; restart/provider timeout loses no committed work. These are future acceptance cases, not executed tests. Compare manual/guided and assisted completion effort, package completeness, correction effort and safe business outcomes on the same tasks.

~~~mermaid
flowchart TD
    A["Authorized representative opens contact"] --> B{"Use assistance?"}
    B -- No --> C["Manual fact lookup and policy search"]
    B -- Yes --> D["Bounded assistant selects permitted reads"]
    D --> E{"Supported result within limits?"}
    E -- No --> C
    E -- Yes --> F["Evidence-linked proposal and missing-fact prompts"]
    C --> G["Representative reviews facts and applicable rule"]
    F --> G
    G --> H{"Customer or source facts changed?"}
    H -- Yes --> I["Mark affected proposal stale and re-check evidence"]
    I --> G
    H -- No --> J["Assess complaint signal independently"]
    J --> K{"Further operational work required?"}
    K -- No --> L["Editable contact note only"]
    K -- Yes --> M["Link existing work or propose owned next action"]
    L --> N["Explicit approval of current content"]
    M --> N
    N --> O{"Server checks authority and freshness"}
    O -- Failed --> P["No write; preserve edits and explain recovery"]
    P --> G
    O -- Passed --> Q["Atomic commit with idempotency and audit"]
    Q --> R["Show actual receipt; end contact without implying case resolution"]
~~~

## Target lifecycle v0.2

Simulated target process after the post-referral and exception decisions. Each branch is
enforced by a trusted command or the worker; the Agent only reads and drafts.

~~~mermaid
flowchart TD
    A["Verified inbound contact: customer reports two charges"] --> B["Scoped transaction search and explicit pair selection"]
    B --> C["Record what the customer recognizes, separate from source facts"]
    C --> D["Applicable simulated rules and existing related work"]
    D --> E{"Existing active work for the same pair?"}
    E -- Yes --> F["Link existing work; no duplicate case"]
    E -- No --> G{"Specialist review needed?"}
    G -- No --> H["Reviewed contact note; Agent draft may be approved or returned with a reason"]
    G -- Yes --> I["Reviewed enquiry: unresolved pair allowed (D-23); material gaps (D-24) and contact gaps (D-25) recorded"]
    I --> J["Queued in specialist queue with receipt and original deadline"]
    J --> K{"Contact details unusable?"}
    K -- Yes --> K1["Customer service owns contact resolution; callback blocked until resolved"]
    J --> L["Specialist accepts and investigates"]
    L --> M{"Material needed?"}
    M -- Yes --> M1["Awaiting documents: customer service asks; answer received, unavailable or declined returns work to specialist"]
    M1 --> L
    L --> N{"Original deadline missed?"}
    N -- Yes --> N1["One escalation; lead-approved next update; separate progress contact"]
    N1 --> L
    L --> O["Published finding with approved customer explanation; open material and progress work superseded"]
    O --> P{"Further action required?"}
    P -- Yes --> P1["Pending until an external system receipt is recorded"]
    O --> Q["Shared feedback queue: claim, callback, fresh identity, approved explanation"]
    Q --> R{"Actual outcome"}
    R -- "No answer, failed identity, declined" --> S{"Three attempts or window used?"}
    S -- No --> Q
    S -- Yes --> T["Lead review: new bounded plan or review hold; never auto-closed"]
    T --> Q
    R -- "Verified feedback delivered" --> U{"All work and actions complete?"}
    U -- No --> U1["Case stays open with owners"]
    U -- Yes --> V["Human-confirmed closure with references"]
    V --> W{"Customer disputes later?"}
    W -- Yes --> X["Verified caller's objection reopens for re-review; closure history kept; complaint delivered independently if requested"]
    X --> L
~~~

| Exception | Rule | Requirement | Transitions |
|---|---|---|---|
| Customer cannot tell which entry is extra | D-23 | FR-23 | — |
| Supporting material missing or refused | D-24 | FR-24 | ST-26–ST-28 |
| Contact details unusable | D-25 | FR-25 | ST-29 |
| Investigation overdue | D-20 | FR-20 | ST-12, ST-19, ST-20, ST-30 |
| Callback unanswered or identity fails | D-16, D-18, D-19, D-22 | FR-19 | ST-05–ST-07, ST-17, ST-18, ST-24, ST-25 |
| Draft not acceptable | D-26 | FR-26 | ST-31 |
| Disagreement after closure | D-21 | FR-27 | ST-13, ST-32 |
| Complaint requested; further action needed | D-21 | FR-28 | ST-21–ST-23, ST-33 |

Every requirement's current evidence is listed in the
[traceability matrix](../../../../docs/backlog/traceability-matrix.md).

## Draft decision rules for S02 elaboration

All RULE IDs below are **simulated design constraints**, not copied bank SOPs. BA-06 will specify complete decision tables/state transitions, BA-07 data contracts, BA-08 numerical NFRs and BA-09 versioned API/acceptance baseline.

| Rule | Condition | Required behavior | Prohibited inference |
|---|---|---|---|
| RULE-01 | No verified permitted scope, cross-customer request or expired scope | No private disclosure/write; safe verification/manual route | Caller wording or known account number proves authority |
| RULE-02 | Same amount/merchant or pending + posted | Show statuses and uncertainty; collect missing facts | Confirmed duplicate or guaranteed reversal |
| RULE-03 | Customer denies purchase, including after correction | Switch to designated manual risk path; invalidate conflicting advice | Autonomous fraud decision/card action |
| RULE-04 | Current case has documented next action but no ETA | State recorded status/next step and explicitly unknown ETA | Invented resolution/refund date |
| RULE-05 | Missing, conflicting, wrong-jurisdiction/audience or non-effective policy | Exclude invalid evidence, disclose gap and seek manual clarification | Best guess becomes authoritative guidance |
| RULE-06 | Immediate supported answer; no further operational action | Save contact; no unnecessary case/task | Every contact must be escalated |
| RULE-07 | Dissatisfaction or request for complaint handling | Preserve signal and refer for representative policy-based assessment, independently of task need | Quick answer or contact closure proves complaint resolved |
| RULE-08 | Additional work required | Link existing work or propose one allowed owner/queue, reason, next step and review time | Created task means specialist accepted it |
| RULE-09 | Human-edited proposal approved | Server checks scope, permitted transition and source/proposal versions | Model approval substitutes for employee approval |
| RULE-10 | Repeated commit or delivery callback | Idempotent business effect and consistent receipt | Blind retries are harmless |
| RULE-11 | Source/customer correction after proposal | Mark impacted proposal stale; preserve human edit; refresh before commit | Earlier evidence remains adequate without review |
| RULE-12 | Model/tool timeout or malformed output | Bounded stop, typed error and usable manual path | False success, lost saved work or unbounded retries |
| RULE-13 | Narrative contains instructions to change permissions or policy | Treat as untrusted customer content | Customer text can override system authority |
| RULE-14 | Proposed action lacks persisted success/recipient evidence | Say draft/queued/failed as applicable; show operation state | Promise execution or human connection from model prose |
| RULE-15 | New effective policy edition becomes applicable | Select by contact as-of and policy interval; record decision/version | Latest uploaded policy is always the right policy |
| RULE-16 | Metrics/evaluation | Keep real/public, synthetic, role-play and measured event data distinct | Synthetic success proves real savings |

## Exceptions and recovery contract

| Exception | User-visible response | Data/state requirement | Owner / next step |
|---|---|---|---|
| Unknown customer verification | Safe verification route, no private facts | Minimal contact stub only where approved; no account detail exposure | Representative/identity process |
| Multiple possible transactions | Ask which entry; show allowed distinguishing fields | No guessed selection | Representative/customer clarification |
| Policy gap/conflict | Explain no supported recommendation available | Keep gap and source metadata; no authoritative answer | Supervisor/policy steward |
| Purchase recognition changes | Warn that prior proposal is stale; use manual risk path | Record correction and invalidation | Representative |
| Existing task already open | Show reference/owner/next action | Link instead of duplicating unless distinct action justified | Representative |
| No available owner/queue | Show unassigned/failed; do not claim completion | Prevent falsely assigned task; preserve draft/contact evidence | Supervisor exception route, finalized in S02 |
| Approval raced with record update | Reject without losing human edits | No domain mutation; require fresh version | Representative refresh |
| Network timeout after save | Show outcome unknown; reconcile using operation ID | Check existing result before retry; no duplicate | Application/operations |
| Assistant unavailable | Manual lookup and editing remain usable | Persisted work unaffected | Representative; operational incident if recurring |
| Contact disconnect | Interrupted outcome, no inferred resolution | Keep approved state and existing unresolved ownership | Representative/operations |
| Request outside two intents | Explain scope and route safely | No unsupported action/tool | Human service route |

## State distinctions

Contact: open → in service → wrap-up → concluded or interrupted.
Proposal: draft → reviewed → approved → committed; stale/rejected/failed are explicit alternatives. Approval is not commit.
Case: existing/open/awaiting evidence/in review/closed per synthetic fixture; this MVP reads case status and proposes follow-up, not financial adjudication.
Task: proposed → queued → assigned → completed/failed/cancelled by allowed actors. Not every demo needs all transitions implemented; S02 selects exact permitted subset.

## Candidate acceptance walkthroughs

[Scenario catalogue](../../docs/sprint-01/scenarios.md) defines SC-01–SC-22. Manual paths cover SC-01/04/12; security and state failures cover SC-06/07/09/10/18; assistance adds SC-03/08/11/15/17 without changing write authority. SC-19–22 cover measurement, accessibility, data isolation and release evidence.

BA-04-AC1: B0 and fallback permit manual completion. AC2: gaps produce clarification/manual review. AC3: corrections invalidate affected proposals. Process design is reviewable; no runtime behavior is claimed tested.


## Detailed delivery increment

See [v0.2 story index](../../docs/sprint-01/workflow-increment.md), [tools](../contracts/agent-tools.md) and [rule register](../contracts/workflow-rules.md). Normal rules and unanswered-attempt limit have owner acceptance; overdue/escalation and objection routing details remain proposed.
