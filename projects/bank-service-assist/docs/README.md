# Business analysis and review evidence

Start with the [case study](../../../docs/case-study.md) for the problem, current/target
comparison and business decisions. The links below open the detailed BA artifacts;
Sprint folders retain their dated discovery and review history.

## One decision from discovery to verification

**Customer problem:** “I bought once, but I cannot tell which of these identical
entries is extra.” Forcing a choice would record certainty the customer does not have.

1. **Decision:** [D-23](sprint-01/decision-log.md#d-23--paired-enquiry-when-transaction-recognition-is-ambiguous)
   allows the pair to remain unresolved. This keeps investigation moving without
   inventing a disputed transaction.
2. **Requirement and stories:** [FR-23 in the traceability matrix](../../../docs/backlog/traceability-matrix.md)
   connects that rule to DEV-03 customer recognition and DEV-07 reviewed intake.
3. **Acceptance:** retain the original statement and both entries, leave the recognized
   entry unset, and link matching work without creating another case or resetting its deadline.
4. **Implementation and verification:** the [referral regressions](../../../services/api/tests/test_referrals.py)
   cover unresolved recognition, linking without duplication, and rejection of an
   invented recognized entry. The [observed handoff retest](../../../docs/uat/2026-10-22-lookup-gap-retest.md)
   checks that the customer's context reaches the working screen.

This is the portfolio's SDD pattern: business ambiguity → explicit decision →
requirement and acceptance criteria → working behavior → verification evidence.

## Detailed BA artifacts

| Subject | Start here |
|---|---|
| Business problem, pain and value hypothesis | [BA-01](../specs/BA-01/spec.md) |
| Stakeholders and decision rights | [BA-02](../specs/BA-02/spec.md) |
| Current process | [BA-03 information and service flow](../specs/BA-03/spec.md#common-service-flow) |
| Target flow and exceptions | [BA-04 current target lifecycle](../specs/BA-04/spec.md#target-lifecycle-v02) |
| Requirements and traceability | [Current requirement-to-test matrix](../../../docs/backlog/traceability-matrix.md), [requirements source](sprint-01/requirements.json) |
| Accepted decisions vs proposals | [Decision log](sprint-01/decision-log.md) |
| Detailed intake review | [DEV-07 intake](../specs/DEV-07/referral-intake-review.md) |
| Current completion and acceptance evidence | [Bank-core closeout](../../../docs/uat/bank-core-closeout.md) |
| First implementation increment (historical) | [Lookup execution record](sprint-02/implementation/lookup-evidence.md) |
| Technical readiness | [Intake readiness](../specs/DEV-07/referral-readiness.md) |

For work order use the [delivery plan](../../../docs/backlog/current-delivery.md).
For technical design use the [specification index](../specs/README.md).
For actual code use `apps/web/` and `services/api/` at repository root.

Business scenarios are simulated. Accepted rules, authored specs, passing tests,
owner UAT and measured outcomes are different evidence states. Earlier dated
Sprint reports remain historical where newer decision/implementation records
explicitly supersede them.
