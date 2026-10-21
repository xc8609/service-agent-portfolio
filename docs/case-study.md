# Case study — from a "charged twice" call to a governed service workflow

A one-page reading guide for reviewers. Scenario, data and rules are simulated; every
number below links to the evidence that produced it.

## 1. Problem

A customer calls: *"I bought once — why do I see two charges?"* A representative must
find permitted transactions, existing cases and the right procedure across several
screens, explain what is actually known, and — when the answer is unclear — hand the
case to a specialist without losing ownership, deadlines or the customer's own words.
The design draws on banking customer-service desktop and BA experience; no employer
data or sponsorship is involved.

## 2. Approach

| Stage | What was produced | Evidence |
|---|---|---|
| Discovery | Current process, pain points, stakeholders and decision rights | [BA-01](../projects/bank-service-assist/specs/BA-01/spec.md) – [BA-03](../projects/bank-service-assist/specs/BA-03/spec.md) |
| Rules | 28 dated owner decisions, e.g. paired enquiry when the customer cannot tell which entry is extra (D-23), callbacks capped at three attempts without automatic closure (D-16) | [Decision log](../projects/bank-service-assist/docs/sprint-01/decision-log.md) |
| Requirements | 38 requirements with acceptance criteria and a generated requirement → test matrix | [Requirements](../projects/bank-service-assist/docs/sprint-01/requirements.json) · [Traceability](backlog/traceability-matrix.md) |
| Design | Target lifecycle with every exception path; 33 state transitions; permissions per role | [BA-04 lifecycle](../projects/bank-service-assist/specs/BA-04/spec.md#target-lifecycle-v02) · [Transitions](../projects/bank-service-assist/specs/contracts/state-transitions.md) |
| Build | React workspace, FastAPI trusted commands, PostgreSQL workflow store, bounded Agent | [Architecture](architecture.md) |
| Verify | API, browser and offline tests in CI; owner UAT pack | [Ledger](backlog/dev-execution-ledger.md) · [UAT](uat/README.md) |
| Evaluate | Frozen comparison of a decision table and three models | [QA-02 pilot](../projects/bank-service-assist/evaluation/README.md) |

## 3. Decisions that shaped the system

- **Authority stays server-side.** Every read and write rechecks identity, customer scope
  and evidence versions; the Agent can read and draft, never approve or execute.
- **Uncertainty is a state, not a guess.** Two equal charges are not a duplicate; a pending
  authorization is not a refund; an unanswered call is not resolution.
- **Exceptions keep an owner.** Missing material, unusable contact details, overdue work,
  objections after closure and complaints each have an accountable queue and keep the
  original deadline.
- **Small, swappable edges.** One app, one API, one database; model APIs and bank data
  connect through server-owned profiles and validated source mappings.

## 4. What the evidence shows

| Claim | Status |
|---|---|
| The whole workflow runs end to end with permissions and exception paths | Automated: 221 API and 40 browser tests pass in CI |
| A model chooses the right next step more often than rules | **Only for free-text statements**: models 4/5 vs decision table 2/5; equal on structured cases (QA-02 pilot) |
| Assistance stays safe under prompt injection and missing verification | The pilot used 48 hold-out model answers; review found scorer false negatives. Versioned regression checks are published; independent safety assessment remains pending |
| Complaint data analysis supports assisted, not automatic, routing | 81.7% team accuracy vs 31.5% baseline on real CFPB data ([analytics](../projects/complaint-analytics/README.md)) |
| Representatives save time | **Not measured** — requires the owner UAT and an effort study |

## 5. What I would do next

1. Run the owner UAT and a timed comparison with the manual path (QA-03).
2. Repeat the evaluation with an independently written hold-out and a negation-aware
   promise guard; qualify one API route when budget allows.
3. Deploy a read-only synthetic demo for reviewers (OPS-02).
