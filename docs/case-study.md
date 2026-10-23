# Case study — “I bought once. Why are there two charges?”

**From fragmented lookups to a complete customer-service workflow.**
[Five-minute walkthrough](demo.md) · [Run locally](../README.md#run-the-demo).

## Business problem and goal

A customer recognizes one purchase but sees two similar credit-card charges. The
representative needs transaction facts, the customer's account of events, existing
investigations and the applicable procedure.

The starting problem is fragmented lookup: moving between customer records,
transaction screens, case history and a knowledge base. Access permissions and
learning procedures add work. Lost handoff context means asking the customer again.

The goal is one workspace that makes the enquiry easier to understand, the next
action clearer and responsibility visible through investigation and customer feedback.

## The working journey

1. **Customer and representative — establish the enquiry.** Verify identity, compare
   the two entries and record what the customer recognizes. Keep their statement
   separate from ledger facts; similar charges still need investigation.
2. **Representative — find the next step.** Check existing work, its progress and
   owner; retrieve the applicable procedure and its source version.
3. **Representative and Agent — prepare the handoff.** Review
   **Facts / To confirm / Next step**, edit the note and approve it. Continue an
   existing investigation or submit a new, reviewed enquiry.
4. **Specialist — investigate.** Take ownership, review the evidence and record
   findings with a customer-facing explanation. Request additional material through
   customer service where needed.
5. **Feedback representative — contact the customer.** Claim the shared-queue task,
   verify identity, deliver the approved explanation and record the contact outcome.
6. **Feedback representative — check completion.** Feedback delivered is a separate
   milestone from case closure. Check outstanding work and required action receipts
   before closing; unresolved contact attempts remain owned follow-up work.

Staff retain their decision rights: representatives approve notes and referrals,
specialists own findings, and feedback representatives own eligible closure. A queue
lead decides contact continuation when the normal plan expires.

## BA decisions translated into features

| Business question | Design choice | Implementation |
|---|---|---|
| What does the customer recognize? | Keep customer statements separate from source facts; allow one purchase with unresolved entry mapping. | [DEV-03](../projects/bank-service-assist/specs/DEV-03/acceptance.md): versioned statements and recognition. |
| Is someone already handling this? | Show existing work and responsibility before another enquiry is created. | [DEV-04](../projects/bank-service-assist/specs/DEV-04/acceptance.md): related cases, progress and linked intake. |
| Which procedure applies? | Match the selected evidence to a versioned rule, with explicit role permissions. | [DEV-05](../projects/bank-service-assist/specs/DEV-05/acceptance.md): cited rules and suggested next steps. |
| What happens when information is missing? | Allow submission, record material/contact gaps and retain the original deadline. | [DEV-07](../projects/bank-service-assist/specs/DEV-07/runtime-contract.md): reviewed intake with follow-up needs. |
| Who tells the customer the result? | A shared feedback queue carries the approved explanation and contact responsibility. | [DEV-11](../projects/bank-service-assist/specs/DEV-11/spec.md): specialist findings and verified feedback. |
| When is the work finished? | Distinguish delivered feedback from case closure; show remaining actions. | [DEV-12](../projects/bank-service-assist/specs/DEV-12/acceptance.md): callback evidence and closure checklist. |

[Decisions](../projects/bank-service-assist/docs/sprint-01/decision-log.md),
[story cards](backlog/story-cards.md) and [requirement-to-test traceability](backlog/traceability-matrix.md)
connect the analysis to working software.

## Agent and engineering design

The Agent's contribution is evidence assembly: bring the selected transactions,
customer statement, related work and procedure into a structured draft for review.
Source references help the representative check the answer. The application handles
approval, permissions, evidence freshness and action receipts. Staff can complete
the same workflow manually.

**React/TypeScript → FastAPI/Python → PostgreSQL.** The Agent runs inside the API.
[Provider adapters and data-mapping interfaces](architecture.md) separate institution
integration from the workflow.

The local demonstration uses synthetic records and a scripted offline Agent provider.

## How value is assessed

The business goals are fewer lookup steps, more complete handoffs and clear ownership
of unresolved work. Review measures are page changes, required facts present in a
handoff, clarification/rework needed and whether the next action has an owner.

The core passed [delegated workflow assessment](uat/bank-core-closeout.md), supported by
**294 API tests and 45 browser tests**, container smoke and offline checks
(23 October 2026).

A Codex-operated [four-task lookup rehearsal](../projects/bank-service-assist/evaluation/effort/results-20261022.md)
found zero page changes in the prepared workspace versus ten across separated source
pages, while total recorded actions were ten in each. It identified missing
currency/posting dates and customer context. After focused corrections, a
[targeted retest](uat/2026-10-22-lookup-gap-retest.md) covered all five transaction
checklist items and all seven handoff items. These observations support the design
improvements; handling-time savings remain a goal to measure.

The immediate portfolio focus is the GitHub walkthrough, business decisions and
acceptance evidence. Hosting, live-model integration, voice and retail remain later
options.
