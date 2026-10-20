# BA-01 Business background, pain and value

Version 0.1 · 19 October 2026 · **Draft ready for owner review**. D-01 confirms the primary pain; the complete business case is not yet accepted.
Sources: [evidence register](../../docs/sprint-01/evidence-register.md). Supports role samples R01/R02/R06 and the owner's representative-desktop experience.

## Business setting and trigger

A simulated Canadian retail bank handles incoming card-service calls through human representatives. The customer describes a concern in everyday language. The representative must establish permitted context, find account/transaction or previous-case facts, identify the applicable handling rule and communicate a supported next step.

The first release is an employee workspace enhancement. Existing telephone delivery, customer identity proofing, core banking, financial dispute adjudication and formal complaint administration remain external business capabilities. The demo supplies labelled synthetic interfaces for their relevant boundaries. A text replay represents the incoming conversation; actual inbound voice belongs to B2.

The owner selected **customer-information and handling-rule lookup** as the principal problem on 19 October (E-02). The product should make the right evidence easier to find and verify. Documentation is secondary; follow-up is conditional. This avoids assuming that every call needs escalation.

External precedent: TD describes representative knowledge assistance with source citations (E-03). Its public dispute page illustrates why transaction context changes the correct handling path (E-04). These sources support plausibility, not our workload or benefit estimates.

## Problem statement and intended outcome

**P-01:** A representative answering a card concern may need to reconstruct relevant facts and find the applicable rule across separate sources. Missing, conflicting or wrongly scoped evidence can delay a supported answer or lead to an incorrect next step. The owner reports page-by-page information collection, permission restrictions requiring control, and knowledge-base learning effort in their prior system (E-09). Their prevalence and impact magnitude in the simulated target operation remain hypotheses. Access restrictions are business constraints to preserve, not obstacles the assistant may bypass.

**Outcome O-01:** reduce the representative's active effort to reach a correct, evidence-supported answer or explicitly justified manual referral.
**O-02:** preserve authorization, factual accuracy and policy applicability.
**O-03:** leave a truthful contact record and clear ownership only when further work is required.

A faster wrong answer is failure. A clear abstention on insufficient evidence can be correct. The customer being satisfied is not interchangeable with a verified transaction resolution.

## Pain and investigation map

| Pain ID | Specific moment and hypothesized mechanism | Evidence status | Information needed / proposed measure |
|---|---|---|---|
| P-01a | Representative gathers information page by page; candidate card scenario requires account, transaction and prior-case views | Page-by-page collection owner-reported (E-09); exact source mix remains simulated | Authorized task observation; active search time, source transitions, repeated searches |
| P-01b | Knowledge-base learning burden; proposed failure mechanism is difficulty selecting an applicable procedure | Learning burden owner-reported (E-09); exact applicability failure mechanism remains a hypothesis | Correct policy/version chosen; wrong-policy rate; evidence coverage; guided-task performance, not an unmeasured training-saving claim |
| P-01e | Access restrictions limit which information or handling functions a representative may use | Restrictions/control need owner-reported (E-09); exact role/record/field/action matrix unknown | Define allowed, masked and denied results; distinguish access denial from missing data; test safe continuation without privilege expansion |
| P-01c | Equal amounts, incomplete status or customer correction create uncertainty | Authored contrasting scenario | Clarification quality; unsupported conclusion rate; changed facts invalidate previous advice |
| P-01d | Existing case lacks an ETA or contains conflicting updates | Design hypothesis, not observed backlog | Correct current status/next action; invented ETA rate; justified referral |
| P-02 | Representative retypes known facts after answering | Secondary hypothesis | Accepted-note completion and correction time, omitted material facts |
| P-03 | Unnecessary new case or repeated referral duplicates work | Design hypothesis | Unnecessary-follow-up rate and duplicate effect count against scenario oracle |

## Scope and customer jobs

1. **UC-01 Credit-card transaction identification and possible duplicate charge:** owner-selected initial focus (D-10). Identify the charge the customer means, inspect permitted statement/transaction records, clarify recognition, check the applicable simulated procedure and propose a supported explanation or manual next step. Two equal charges do not prove a duplicate; a pending authorization and a posted entry must not be assumed related without evidence. Broader statement topics such as interest/fee calculation remain outside this selected walkthrough. Detailed process and permission rules are still proposed.
2. **UC-02 Existing-case enquiry (candidate second job, not owner-confirmed):** inspect the authorized case timeline and recorded next action, communicate uncertainty honestly, and avoid duplicating an existing task.
3. **Cross-cutting:** record dissatisfaction separately from whether additional work is needed. A contact can finish while its linked case remains open.

No automatic refund, chargeback submission, fraud determination, card block/replacement, credit decision, unrestricted customer update or statutory-complaint adjudication. An unsafe/out-of-scope request receives an explicit manual path; it is not silently discarded.

## Domain vocabulary

| Concept | Meaning in this demo | Important separation |
|---|---|---|
| Contact | One service interaction, including enquiry and wrap-up | Ending a call does not close a financial case |
| Concern / intent | What the customer wants explained or acted upon | Customer wording is not verified transaction truth |
| Complaint signal | Dissatisfaction or request for complaint handling requiring representative review under a versioned procedure | May coexist with an immediately answered enquiry; does not require an unresolved operational task |
| Dispute | A challenge to a transaction through an authorized external process | A prepared note is not a submitted dispute |
| Case | Durable unresolved work with owner, state and history | Do not create one automatically for every contact |
| Follow-up task | A specific next action, owner and review time linked to relevant work | Task completion is not necessarily case resolution |
| Proposal | An editable suggested answer/note/task based on identified evidence | It has no business effect until authorized commit |
| Policy | Versioned simulated handling rule with jurisdiction/product/audience/effective period | Not an assertion of bank or legal authority |

## Alternatives and recommendation

| Option | Works well when | Costs or limitations | What to compare |
|---|---|---|---|
| A0 Existing manual lookup | Low volume, clear procedure, knowledgeable staff | Switching and note effort may persist | Reference quality, total active effort |
| A1 Unified search + structured templates | Main issue is locating documents / repeated note structure | Less adaptation to changing account facts | Correct evidence retrieval and verification time |
| A2 Deterministic guided workflow | Branches and required fields are stable | Rule maintenance; natural questions may not fit | Correct branch, missing-field prompts, safe action |
| A3 Bounded retrieval/tool assistant | Variable wording requires conditional fact lookup and explanation | Model cost/latency, hallucination and review burden | Same outcome/quality criteria, full checking time and cost |

**Proposed:** build A1/A2 as B0, then test A3 as B1 on the same evidence and tasks. Use deterministic authorization and workflow rules in every option. Keep A1/A2 for branches where assistance adds no demonstrated value. Selection is conditional on comparative evaluation, not on showcasing an agent framework.

## Measures and financial reasoning

See [measurement contract](../../docs/sprint-01/value-measurement.md). No baseline, staffing saving or productivity result exists yet. Proposed business threshold: at least 15% lower median active evidence-search-and-verification time in paired tasks, with no critical error and no deterioration in supported-answer quality. This is an author-proposed decision threshold, not a borrowed result or owner-approved target.

Monthly net capacity-hours = eligible contacts × adoption × (manual minus assisted minutes through accepted completion) / 60 − incremental downstream rework hours. Do not subtract correction effort again when already included in observed completion time. Cash cost requires an explicit loaded hourly cost and actually avoidable spend; released capacity is not automatically headcount reduction. Subtract model, hosting, maintenance, training and evaluation costs for a financial scenario.

## Acceptance of this BA artifact

BA-01-AC1: all problem claims have an evidence status and limitation.
BA-01-AC2: A0–A3 share the same task, quality and time measures.
BA-01-AC3: value calculations expose assumptions and avoid double counting.
Decision D-01 is accepted for primary pain. Owner review of full scope, value threshold and alternatives remains pending.
