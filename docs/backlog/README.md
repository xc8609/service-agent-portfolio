# Delivery planning

| Question | Canonical document |
|---|---|
| What are we building next, and what is deferred? | [Current delivery scope](current-delivery.md) |
| Which stories exist? | [Story catalogue](story-cards.md) |
| What is the detailed requirement/design for a story? | [Specification index](../../projects/bank-service-assist/specs/README.md) |
| What is the small-team Sprint forecast? | [Sprint sequence and illustrative dates](sprints.md) |
| Where are capacity and allocation calculations? | [Structured forecast](sprint-forecast.json) |
| Where can a reviewer follow progress? | [Public Trello](https://trello.com/b/wtNhuN0q/ai-agent) |

Stories have stable IDs across schedule revisions. Detailed story folders hold
`spec.md`, `design.md`, `tasks.md` and `acceptance.md`; the catalogue and Trello are
navigation/planning views, not competing copies of runtime acceptance.

The forecast models two developers with BA/QA allocations, not actual staffing or
personal hours. Dates and effort are estimates, not completed work. Current scope
controls what enters the next increment; deferred scenarios retain their original
specifications and must be re-estimated before being pulled into implementation.
