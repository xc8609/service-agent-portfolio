# Case study — “I bought once. Why are there two charges?”

**From fragmented lookups to a complete customer-service workflow.**
[Five-minute walkthrough](demo.md) · [Run locally](../README.md#run-the-demo).

## Business problem and goal

A customer recognizes one purchase but sees two similar credit-card charges. The
representative needs transaction facts, the customer's account of events, existing
investigations and the applicable procedure.

The project owner's customer-service workstation experience identified page-by-page
information collection, access restrictions and knowledge-base learning as the main
pain points. This simulated card enquiry turns those observations into a concrete
workflow and acceptance criteria.

The goal is one workspace that makes the enquiry easier to understand, the next
action clearer and responsibility visible through investigation and customer feedback.

## Current process → target process

| Current process in this scenario | Target design | Intended business improvement |
|---|---|---|
| Gather customer, transaction and case information across separate views. | Compare permitted facts and existing work in one customer context. | Less navigation and repeated searching. |
| Search the knowledge base and work out which procedure applies. | Show the matching procedure, conditions and source version beside the evidence. | Less effort finding and checking the handling rule. |
| Reconstruct the customer's account and facts for a note or referral. | Preserve the statement and selected entries; optionally use an Agent draft. | More complete handoffs with fewer missing facts. |
| Decide whether more work is needed, then track the handoff and callback. | Save a contact note, or link/create owned work; separate feedback from closure. | Avoid unnecessary cases and keep unresolved work visible. |

The [detailed current process](../projects/bank-service-assist/specs/BA-03/spec.md#common-service-flow)
and [target lifecycle](../projects/bank-service-assist/specs/BA-04/spec.md#target-lifecycle-v02)
show the decisions and roles behind this comparison.

## The working journey

When the evidence supports an explanation and no further action is needed, staff
can answer and save a contact note. The example below follows an **unresolved
enquiry** that requires specialist review.

1. **Representative — establish the enquiry.** Verify identity, compare entries and
   record recognition, keeping the customer's statement separate from ledger facts.
2. **Representative — find the next step.** Check existing work, progress and owner;
   retrieve the applicable procedure and source version.
3. **Representative — approve the handoff.** Review the note, optionally using the
   Agent draft; continue existing work or submit a new enquiry.
4. **Specialist — investigate.** Take ownership, record findings and publish the
   customer explanation. Request additional material through customer service.
5. **Feedback representative — contact the customer.** Claim the task, verify identity,
   deliver the approved explanation and record the outcome.
6. **Feedback representative — confirm closure.** Check outstanding work and required
   receipts. Delivered feedback alone does not close the case; expired contact plans
   go to a queue lead for a continuation decision.

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
connect the analysis to working software. The
[worked evidence chain](../projects/bank-service-assist/docs/README.md#one-decision-from-discovery-to-verification)
follows one ambiguous-recognition decision through its requirement, implementation and tests.

## Agent and engineering design

The workspace reduces navigation; the Agent adds a **reviewable synthesis** of the
selected evidence and the representative's question. For this enquiry, the summary
structure makes three things visible:

- **Facts:** two CAD 85 entries are posted; the customer reports one purchase.
- **To confirm:** why there are two entries; which entry maps to the purchase remains unresolved.
- **Next step:** continue the existing investigation with the statement, transaction pair and missing-receipt gap.

Source references let staff check the draft. Staff approve the note and next action;
the application enforces permissions, evidence freshness and action receipts.

The [options analysis](../projects/bank-service-assist/specs/BA-01/spec.md#alternatives-and-recommendation)
compares manual lookup, a unified workspace, guided rules and Agent assistance.
The manual workspace already addresses the main lookup pain. Agent value should
be judged by draft completeness and total review effort against that same manual path.

**React/TypeScript → FastAPI/Python → PostgreSQL.** The Agent runs inside the API.
[Provider adapters and data-mapping interfaces](architecture.md) separate institution
integration from the workflow.

The local demonstration uses synthetic records and a scripted offline Agent provider.

## How value is assessed

Measure value through lookup steps, handoff completeness, clarification/rework and
whether unresolved actions have an owner.

The core passed [delegated workflow assessment](uat/bank-core-closeout.md), supported by
**294 API tests and 45 browser tests**, container smoke and offline checks
(23 October 2026).

A [four-task lookup rehearsal](../projects/bank-service-assist/evaluation/effort/results-20261022.md)
recorded zero page changes in the prepared workspace versus ten across simulated
source pages, with ten actions in each. It exposed missing transaction details and
customer context. After correction, the [targeted retest](uat/2026-10-22-lookup-gap-retest.md)
covered 5/5 transaction and 7/7 handoff checklist items. Handling-time savings remain
a goal to measure.

The immediate portfolio focus is the GitHub walkthrough, business decisions and
acceptance evidence. Hosting, live-model integration, voice and retail remain later
options.
