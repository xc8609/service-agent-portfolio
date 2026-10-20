# BA-02 Stakeholders and decision rights

Version 0.1 · 19 October 2026 · **Draft ready for owner review**. All operational personas below are simulated roles. Actual feedback so far comes from the portfolio owner only.

## Stakeholders and jobs

| Role | Job / need | Likely tension to investigate | Participation |
|---|---|---|---|
| Customer | Understand a charge or existing case without repeating details | Wants certainty where evidence may be incomplete | Future consented role-play; no real customer interviews held |
| Representative | Find trustworthy facts/rules, explain next step, retain control | Speed vs checking burden and responsibility | Owner plausibility review; later representative-like task study |
| Service supervisor | Resolve uncertain ownership and procedure gaps | Queue pressure vs quality | Simulated exception owner, no actual appointment |
| Dispute/fraud specialist | Receive correct facts for authorized review | Incomplete/duplicated handoffs | Define intake contract; no external integration yet |
| Complaint owner | Ensure dissatisfaction reaches the applicable process | Fast contact closure can obscure unresolved dissatisfaction | Simulated policy review role; not statutory approval |
| Product/service owner | Prioritize outcomes and accept business behavior | Scope and cost vs desired coverage | Actual portfolio owner decides portfolio scope |
| BA | Clarify evidence, options, requirements and acceptance | Unverified assumptions may appear as facts | Analysis produced with agent assistance; owner accountable for claimed experience |
| Engineering | Implement contracts, persistence and controls | Technical feasibility vs deadline | Simulated A/B(/C) allocation; no named real team |
| QA | Challenge examples and report verification results | Testability vs ambiguous requirements | Independent QA is a staffing assumption; current checks are agent self-review |
| Operations/security/privacy | Access boundaries, source updates, support and recovery | Convenience vs disclosure/operability | Define requirements; no bank sign-off asserted |

## Decision-right matrix

R = performs/prepares; A = accountable decision owner; C = consulted. Exactly one A per row in the simulated operating model. Actual portfolio acceptance belongs to the owner; simulated titles are not actual approvals.

| Decision/action | R | A | C | Boundary |
|---|---|---|---|---|
| Define business priority / accept scope | BA | Product/service owner | Representatives, engineering, QA | Record rationale and change impact |
| Decide which data a session can see | Identity/access service | Security/access owner | Operations, engineering | Model and caller text cannot change scope |
| Establish customer verification | Authorized identity process | Identity/control owner | Representative | Demo fixture status only; no real proofing implementation |
| Choose and publish procedure version | Policy steward | Designated policy owner | Service, specialist, complaint/legal reviewers | Jurisdiction and effective dates explicit |
| Explain facts during a contact | Representative | Handling representative | Assistant, policy reference | Do not promise unsupported outcomes |
| Save edited contact note | Representative, server | Handling representative | QA/operations | Server enforces permission, freshness and idempotency |
| Create operational follow-up | Representative, server | Handling representative | Target supervisor/queue | Allowed owner and reason required; creating task is not acceptance by a human |
| Accept/assign specialist work | Authorized queue workflow | Target queue supervisor | Originating representative | Queued, assigned and completed are distinct |
| Handle complaint classification/escalation | Representative/complaint workflow | Designated complaint owner | Supervisor, policy steward | Separate from whether an operational case is needed |
| Select technical design | Engineering | Technical lead role | BA, QA, operations | Must satisfy accepted business/security constraints |
| Recommend UAT acceptance | QA and BA | Product/service owner | Representative role | Self-review is labelled if no independent participant |
| Authorize demo release | Engineering/operations | Portfolio release owner | BA, QA | Failed critical gates block release |

The assistant may propose, retrieve within scope and explain evidence. It may not approve itself, silently change ownership, close an unresolved case, issue a refund or mark a human transfer completed.

## Elicitation record

EL-01 · 19 October 2026 · Actual participant: portfolio owner via this conversation. Question: which prior representative-system pain is most relevant? Answer: customer-information and handling-rule lookup. Result: D-01 selected as primary; notes and follow-up secondary. This is owner experience-based prioritization, not a Canadian-bank interview or time study.

EL-02 · Planned: walkthrough of one duplicate-charge enquiry and one existing-case enquiry, asking which information is seen first, which step causes repeat lookup and when supervisor help is needed.
EL-03 · Planned: review policy sources, freshness, wrong-product cases and when the employee must stop.
EL-04 · Planned: evaluate lookup/search versus assistance using the measurement contract.

## Review questions and conflict resolution

- Primary pain selected (D-01). Still verify actual frequency, lookup surfaces and where staff know the answer without searching.
- If speed and evidence completeness conflict, preserve the critical facts/authorization; measure active review time rather than hiding it.
- If a customer wants a definite refund/date but evidence does not support it, state the known facts and manual next step.
- If caller dissatisfaction is answered on the spot, retain the complaint-review path appropriate to policy; do not create unrelated specialist work.
- Unassigned work goes to a defined supervisor exception queue or remains visibly uncommitted; never represent it as assigned.

## Organizational change and support

Representatives need training on evidence references, uncertainty, overrides and the difference between proposal and saved action. Supervisors need a policy-gap/owner exception route. Policy stewards need version-change review and regression cases. Operations needs reproducible error IDs and a manual fallback procedure. Record concerns and test adoption rather than assuming users trust the tool.

BA-02-AC1 is covered by the decision matrix; AC2 by conflict rules and D-log; AC3 by actual/planned elicitation labels. Full owner review remains pending.
