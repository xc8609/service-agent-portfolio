# BA-03 Current service process and information flow

Version 0.1 · 19 October 2026 · **Simulated as-is for owner review**, not an observation of a named bank. External precedents and owner-reported experience are in the [evidence register](../../docs/sprint-01/evidence-register.md).

## Boundary and process ownership

Trigger: customer contacts the bank about a possible duplicate card charge (UC-01) or existing case (UC-02). Operational owner: service operations role. Start at contact acceptance; end when the representative has recorded the interaction and either explained the supported next step or assigned/queued further work explicitly. No clock/time data is available.

Systems are logical capabilities, not assertions about the owner's former architecture: telephony/contact channel; identity/authorization; account/transaction store; case/history store; procedure library; contact notes; specialist/complaint workflow.

## Common service flow

| Step | Actor / information needed | Work and output | Exception / pain / evidence status |
|---|---|---|---|
| AS-01 | Customer → representative; stated concern and channel | Open contact; capture original wording | Dropped contact: record interruption, never infer resolution |
| AS-02 | Identity process + representative; verification result and session scope | Establish which account/case data may be accessed | Unverified: no private lookup; offer safe identity/manual route. Assumed dependency |
| AS-03 | Representative; merchant/amount/date or case reference | Clarify the actual job and select UC-01/UC-02 | Ambiguous or multiple issues: confirm, do not silently choose |
| AS-04 | Representative; permitted accounts and records | Collect information page by page; search transactions / case history within access scope | P-01a/e: page-by-page collection and access constraints owner-reported (E-09); exact pages, permission model and time unverified |
| AS-05 | Representative; product/jurisdiction/date/audience/context | Find applicable procedure and assess evidence gaps | P-01b: learning burden owner-reported (E-09); wrong-version and consultation branches remain simulated |
| AS-06 | Representative + customer; facts and clarifications | Explain supported facts or identify required manual action | Corrected facts cause re-check; no guaranteed refund/date |
| AS-07 | Representative; dissatisfaction signals and process preference | Assess complaint-handling path independently | Do not suppress dissatisfaction because enquiry answered |
| AS-08 | Representative; work still required and prior task state | Decide no new task, link existing work, or prepare owned follow-up | P-03: duplicate/orphan task risk; task existence must be checked |
| AS-09 | Representative; facts/actions/policy and outcome | Write contact record; communicate what was actually done | P-02: retyping/correction effort is unmeasured |
| AS-10 | Representative / specialist queue | End contact; unresolved case/task retains accountable owner | Queue receipt is not actual investigation or resolution |

## UC-01 Current duplicate-charge enquiry

~~~mermaid
flowchart TD
    A["Customer reports two charges"] --> B["Establish identity and permitted context"]
    B --> C{"Permitted context?"}
    C -- No --> D["Safe verification or human route; no private disclosure"]
    C -- Yes --> E["Clarify merchant, amount, currency, date and recognition"]
    E --> F["Manually inspect transactions and prior related work"]
    F --> G{"Unrecognized purchase or changed facts?"}
    G -- Yes --> H["Follow authorized manual fraud path; no financial action in demo"]
    G -- No --> I["Look up applicable procedure and inspect transaction states"]
    I --> J{"Enough consistent evidence?"}
    J -- No --> K["Clarify or consult supervisor; state uncertainty"]
    J -- Yes --> L["Explain supported status and possible next step"]
    K --> M["Assess dissatisfaction separately"]
    L --> M
    H --> M
    M --> N{"Additional operational work required?"}
    N -- No --> O["Record contact without creating a new case"]
    N -- Yes --> P["Check existing work; link or assign explicit next action"]
    P --> Q["Record contact; case can remain open"]
    O --> R["End contact"]
    Q --> R
~~~

## UC-02 Current case-status enquiry

~~~mermaid
flowchart TD
    A["Customer asks for progress"] --> B["Establish permitted customer context"]
    B --> C{"Can access requested case?"}
    C -- No --> D["No disclosure; safe clarification or verification"]
    C -- Yes --> E["Search current case and contact history"]
    E --> F{"Case found and history consistent?"}
    F -- No --> G["Clarify reference or request manual review"]
    F -- Yes --> H["Read current status, owner and documented next step"]
    H --> I["Look up applicable explanation/escalation procedure"]
    I --> J["Explain only recorded facts; unknown ETA stays unknown"]
    J --> K{"New required action or dissatisfaction?"}
    K -- Neither --> L["Record enquiry; no duplicate work item"]
    K -- Yes --> M["Assess complaint path and operational task separately"]
    G --> M
    M --> N["Link existing task or assign justified follow-up"]
    N --> O["End contact; preserve case state"]
    L --> O
~~~

## Information and handoff map

| Source capability | Facts required | Recipient / decision | Quality question |
|---|---|---|---|
| Identity/session | Verification state, role and permitted customer/account scope | Every private read/write | Who established scope and when does it expire? |
| Transactions | Stable ID, account, merchant, amount/currency, status, timestamp and version | Duplicate enquiry | Are these separate posted entries, pending authorization, or insufficient evidence? |
| Case events | Stable case ID, permitted customer, status, owner, next step, event sequence/as-of | Case enquiry | Are events conflicting, stale or future relative to the enquiry? |
| Procedure library | ID/version, product, jurisdiction, audience, effective interval | Explanation/next step | Does the rule actually apply to this contact? |
| Prior contacts/tasks | Customer-scoped records, outcome, unresolved action, owner | Avoid repeat work | Is work already pending, and who is responsible? |
| Specialist intake | Reason, source references, missing facts, owner/queue and receipt | Human continuation | Was it only queued, accepted, or completed? |

## Bottleneck validation plan

Record an authorized user's search sequence and active time per AS-04/05; distinguish system wait and human verification. Ask what source proved the answer and what would change it. Compare tasks requiring one source with those requiring both facts and procedure. No timed observation has taken place. Process accuracy, source count and bottleneck size remain owner-review items, not verified findings.

BA-03-AC1: both flows include entry, authority, decisions, exceptions and outcomes. AC2: P-01/P-02/P-03 are labelled and linked to measurements. AC3: AS-08/10 retain ownership of unresolved work. Diagrams are Mermaid source; business walkthrough and rendered diagram review are pending.
