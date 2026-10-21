# Risk and Governance — Assisted Complaint Routing

Proposed controls for the simulated pilot. They are design recommendations, not an
approved policy or a legal opinion.

## Privacy

- CFPB redacts public narratives (`XXXX`); a bank's own complaints contain personal
  information. Treat complaint text as confidential customer data.
- Collect and use it only for complaint handling (PIPEDA purpose limitation); keep the
  model and its logs in the approved data region; mask direct identifiers before any
  third-party model call; confirm vendor retention and training-use terms in writing.
- This repository publishes only aggregate counts and metrics. Raw text, complaint IDs,
  ZIP codes and the 70-row review worksheet stay local.

## Fairness and vulnerable customers

- Accuracy differs by product: prepaid-card recall is 0.32 versus 0.93 for mortgage.
  Prepaid users can include customers without a traditional bank account, so lower
  recall may fall on a more vulnerable group. Monitor recall by product, channel and
  (where lawful) customer segment before and during a pilot.
- Complaints without public text cannot be scored; they must never be deprioritized
  because no suggestion exists.

## Human oversight

- Suggestion only: the analyst confirms or overrides every routing decision (US-1).
- Overrides need a reason; weekly sampling compares suggestions, overrides and final
  outcomes. A rising override rate pauses the suggestion feature.
- Any unattended routing requires a separately approved threshold, a pre-registered
  target and evidence from a fresh hold-out; current coverage above 0.5 confidence
  is about 24% on development data.

## Model risk

- Record model version, training data window, split rule and evaluation results for
  every release ([evaluation](04_ai_pilot_evaluation.md)).
- Re-evaluate on new monthly data before reuse; watch for taxonomy changes and drift
  in product mix and wording. Fall back to manual routing on errors or failed checks.
- Apply the institution's model-risk framework (for federally regulated lenders,
  OSFI Guideline E-23) proportionately to an assistive, human-reviewed model.

## Audit trail

For every complaint: complaint ID, received time, model version, suggested team and
confidence (or "manual: no text / model unavailable"), final team, analyst, decision
time and override reason (US-3). Logs follow the complaint record's retention period.
