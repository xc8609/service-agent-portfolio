# Case study — “I bought once. Why are there two charges?”

**From fragmented lookups to an owned customer-service workflow.**
A banking portfolio case connecting business analysis, Agent assistance and full-stack
engineering. [Five-minute demo](demo.md) · [Run locally](../README.md#run-the-demo).

## Business problem and goal

A representative moves between customer records, transaction screens, case history
and a knowledge base to understand a disputed charge. Different access permissions
and handling procedures add complexity, while incomplete handoffs make follow-up harder.

The goal is to bring the relevant information and next steps into one workspace:
help staff investigate the enquiry, apply the right procedure and keep responsibility
clear through specialist review and customer feedback.

## The working journey

1. **Understand the enquiry.** Find the two transactions and record what the customer
   recognizes. Keep their statement alongside the transaction facts.
2. **Find the right next step.** Check existing work, its progress and owner; retrieve
   the applicable procedure and its source version.
3. **Prepare the response.** The Agent assembles **Facts / To confirm / Next step**
   and an editable note. Staff review and approve the saved version.
4. **Hand off with context.** Link the existing investigation or submit a reviewed
   enquiry with the selected entries, customer statement and missing-material needs.
5. **Complete the follow-up.** The specialist records findings; customer service
   verifies identity, delivers the approved explanation and checks remaining work.

## BA decisions translated into features

| Business question | Design choice | Implementation |
|---|---|---|
| What does the customer recognize? | Keep customer statements separate from source facts; allow one purchase with unresolved entry mapping. | [DEV-03](../projects/bank-service-assist/specs/DEV-03/acceptance.md): versioned statements and recognition. |
| Is someone already handling this? | Show existing work and responsibility before another enquiry is created. | [DEV-04](../projects/bank-service-assist/specs/DEV-04/acceptance.md): related cases, progress and linked intake. |
| Which procedure applies? | Match the selected evidence to a versioned rule, with explicit role permissions. | [DEV-05](../projects/bank-service-assist/specs/DEV-05/acceptance.md): cited rules and suggested next steps. |
| What happens when information is missing? | Record the gap, its owner and follow-up responsibility while investigation continues. | [DEV-07](../projects/bank-service-assist/specs/DEV-07/acceptance.md): complete handoff context and preserved deadlines. |
| When is the work finished? | Distinguish delivered feedback from case closure; show remaining actions. | [DEV-12](../projects/bank-service-assist/specs/DEV-12/acceptance.md): callback evidence and closure checklist. |

[Decisions](../projects/bank-service-assist/docs/sprint-01/decision-log.md),
[story cards](backlog/story-cards.md) and [requirement-to-test traceability](backlog/traceability-matrix.md)
connect the analysis to working software.

## Agent and engineering design

The Agent gathers permitted transaction, case and procedure evidence through defined
tools. Its draft carries source references and the saved customer context into human
review. The application handles approval, permissions, evidence freshness and receipts.
Staff can also complete the same workflow manually.

**React/TypeScript → FastAPI/Python → PostgreSQL.** The Agent runs inside the API,
with separate provider adapters and transaction-source mapping interfaces.
[Architecture and extension points](architecture.md) keep institution-specific
integration separate from the service workflow.

The local demonstration uses synthetic records and a scripted offline Agent provider.

## Validation and improvement

The core passed [delegated workflow assessment](uat/bank-core-closeout.md), supported by
**294 API tests and 45 browser tests**, container smoke and offline checks
(23 October 2026).

A [four-task lookup rehearsal](../projects/bank-service-assist/evaluation/effort/results-20261022.md)
identified missing currency/posting dates and customer context in the first version.
Those findings became focused changes and a [targeted retest](uat/2026-10-22-lookup-gap-retest.md).
The result is a clearer transaction comparison and an Agent handoff that retains the
customer's exact statement and material gaps.

Next: hosted demonstration and live-model integration, then voice handoff and retail.
