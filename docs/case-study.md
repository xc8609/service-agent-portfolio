# Case study — “I bought once. Why are there two charges?”

**Business analysis → working service workflow → bounded Agent assistance.**
Independent portfolio, informed by banking service-desktop and product/BA experience.
All operational records and handling rules are simulated. [Five-minute demo](demo.md).

## Business problem

A representative moves between customer records, transactions, case history and a
knowledge base. Access varies by role; learning which procedure applies adds effort.
The customer needs an explanation or an owned investigation, without repeated
questions, duplicate work or an unsupported refund promise.

**Target outcome:** less information-search effort and more consistent handoffs.
Time/cost savings remain hypotheses; no bank deployment or measured ROI is claimed.

## BA decisions made concrete

| Business question | Design choice | Working evidence |
|---|---|---|
| What happened, and what does the customer recognize? | Separate source facts from statements; allow one purchase with unresolved entry mapping. | [DEV-03](../projects/bank-service-assist/specs/DEV-03/acceptance.md): versioned recognition; changed evidence invalidates drafts. |
| Is someone already handling this? | Show existing work, progress and ownership before another enquiry. | [DEV-04](../projects/bank-service-assist/specs/DEV-04/acceptance.md): scoped lookup and linked intake. |
| Which rule applies, and who may act? | Cited applicability; server-enforced identity, role and assignment. | [DEV-05](../projects/bank-service-assist/specs/DEV-05/acceptance.md): ordinary staff inspect; financial execution stays outside the demo. |
| When can the case close? | Record missing material and its owner; preserve deadlines; distinguish delivery from closure. | [DEV-07](../projects/bank-service-assist/specs/DEV-07/acceptance.md), [DEV-12](../projects/bank-service-assist/specs/DEV-12/acceptance.md): reviewed handoff, callback evidence and closure blockers. |

[Decisions](../projects/bank-service-assist/docs/sprint-01/decision-log.md),
[stories](backlog/story-cards.md) and the [requirement-to-test matrix](backlog/traceability-matrix.md)
connect business intent to implementation and acceptance.

## Agent contribution

The bounded runtime assembles authorized transaction, rule and case evidence into an
editable **Facts → To confirm → Next step** draft with source references. Staff approve
business writes; the manual path remains available.

The **app uses a scripted offline provider** to demonstrate tool access, evidence
freshness and review, not arbitrary language understanding. A separate
[12-case Codex subscription exercise](../projects/bank-service-assist/evaluation/r2/subscription-results-20261022.md)
explored tentative recognition, unfamiliar merchants and missing receipts. Answers
addressed distinctions the template missed; same-session AI review judged 11 usable
and one needing a grammar edit. This is development evidence, not independent accuracy
or proof of deployed model benefit. No API integration is claimed.

## Engineering and evidence

React/TypeScript → FastAPI/Python → PostgreSQL. One small application with documented
[source/model extension points](architecture.md). Permissions, approval and receipts
stay outside model control.

At merged `761aeaf` (22 October 2026), [runtime CI](https://github.com/xc8609/service-agent-portfolio/actions/runs/39859494492)
passed **286 API tests, 44 browser tests and container smoke**;
[offline CI](https://github.com/xc8609/service-agent-portfolio/actions/runs/39859494440)
passed on Python 3.9/3.12. [Delegated UAT](uat/2026-10-22-core-clarity.md) observed guarded
disclosure and closure. Owner acceptance, live-model qualification and measured human
benefits remain separate.

## Next useful evidence

Compare 3–5 identical tasks in a simulated separate-source lookup and the integrated
workspace: steps, time, omissions and corrections. Publish the assessor and actual
observations, even if there is no gain. Model API, voice and retail expansion stay deferred.
