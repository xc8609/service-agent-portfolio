# Routing Evaluation — Baselines on Real Public Complaints

Evaluation date: 2026-10-21. Data: CFPB July 2026 archive, seven-product routing scope,
complaints with a public narrative. Machine-readable results:
[`results/model_baselines.json`](../results/model_baselines.json) (metrics only, no text or IDs).

## 1. Summary

A plain TF-IDF + logistic-regression suggestion reaches **81.7% team accuracy** on an
untouched hold-out set, against **31.5%** for always suggesting the largest product.
Confidence is rarely high enough for unattended routing: on development data only
**24%** of complaints clear a 0.5 confidence threshold (94.4% team accuracy there).

**Recommendation: proceed with an *assisted* routing pilot** — the analyst sees a
suggested team and confirms or overrides it — and do not automate routing. Fix the
prepaid-card label problem and pre-register pilot targets before the next evaluation.

These are offline scores on US proxy labels, not observed routing performance or savings.

## 2. Evaluation design (fixed before results were inspected)

| Item | Decision |
|---|---|
| Task | Predict the consumer-selected product from the narrative; score team accuracy via the simulated product-to-team map (a confusion inside one team is not a misroute) |
| Records | 6,409 in-scope complaints with text; 14 normalized duplicate texts removed (lowest ID kept), leaving 6,395 |
| Split | `sha256(complaint_id) mod 100 < 70` → development 4,492; otherwise hold-out 1,903. Duplicates removed before the split |
| Models | Majority class; TF-IDF word 1–2-grams (min_df 2, sublinear tf) + logistic regression (C 1.0, balanced class weights). No hyper-parameter search |
| Threshold analysis | Out-of-fold predictions from 5-fold cross-validation on development data; hold-out used once to confirm |
| Reproduce | [`scripts/evaluate_baselines.py`](../scripts/evaluate_baselines.py) on the locally profiled archive |

Pilot targets in the [requirements](01_business_requirements.md) were **not** set before
this run. These results are therefore a baseline, not a pass/fail decision; targets are
proposed below for the next, fresh hold-out.

## 3. Results

| Model | Product accuracy | Product macro F1 | Team accuracy |
|---|---:|---:|---:|
| Majority class (checking/savings) | 31.5% | 0.069 | 31.5% |
| TF-IDF + LR, 5-fold CV on development (mean ± sd) | 79.2% ± 1.4 | 0.727 ± 0.024 | 80.4% ± 1.1 |
| **TF-IDF + LR, hold-out** | **80.4%** | **0.756** | **81.7%** |

Hold-out results by product:

| Product | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Mortgage | 0.977 | 0.933 | 0.955 | 225 |
| Vehicle loan or lease | 0.901 | 0.855 | 0.877 | 159 |
| Credit card | 0.833 | 0.852 | 0.842 | 527 |
| Checking or savings account | 0.790 | 0.782 | 0.786 | 600 |
| Payday, title, personal or advance loan | 0.716 | 0.686 | 0.700 | 121 |
| Money transfer, virtual currency or money service | 0.620 | 0.740 | 0.675 | 227 |
| **Prepaid card** | 0.824 | **0.318** | 0.459 | 44 |

Main confusions (hold-out counts): checking → money transfer 71 and money transfer →
checking 51 (account transfers are described in both); checking → credit card 49;
credit card → checking 42; prepaid cards are mostly predicted as checking (13),
credit card (9) or money transfer (8). Prepaid and credit card share a team, so 9 of
the 30 prepaid misses are not misroutes.

## 4. Confidence threshold and human review

| Max probability ≥ | Development: share auto-eligible | Development: team accuracy | Hold-out: share | Hold-out: team accuracy |
|---:|---:|---:|---:|---:|
| 0.5 | 24.0% | 94.4% | 31.0% | 96.4% |
| 0.6 | 11.1% | 97.0% | 17.6% | 97.9% |
| 0.7 | 4.5% | 99.5% | 7.5% | 98.6% |
| 0.8 | 1.7% | 100% | 3.5% | 100% |

Balanced seven-class probabilities are spread out, so high-confidence coverage is
small. A suggestion with analyst confirmation uses the 81.7% team accuracy on every
complaint with text; unattended routing would cover only a minority. No pilot threshold
has been selected.

## 5. Value estimate (illustrative, not measured)

`estimate_hours_saved()` with **assumed** inputs: 1,000 text complaints/month, 4 minutes
manual triage, 15 minutes extra handling per misroute, auto-route share 24.0% and
accuracy 94.4% from development data. Result: 16.0 gross hours, 3.3 rework hours,
**12.6 net hours per month**. Every input except the two model figures is an assumption;
a real pilot must measure triage time, misroute cost and analyst override behaviour.
Assisted routing saves reading time rather than routing steps and needs its own study.

## 6. Limitations

- Consumer-selected product labels are noisy proxies; prepaid/checking/transfer
  boundaries are partly a taxonomy problem, not only a model problem.
- Only complaints with public narratives (23.7% of the scope) are scored; complaints
  without text follow the manual path and have no measured accuracy.
- One month of US data; no seasonality, no Canadian product taxonomy (OBSI, FCAC context).
- The 70-row discovery sample has not been human-annotated; no inter-rater agreement.
- No LLM was evaluated. An LLM comparison remains optional and must use the same split
  rules on a fresh hold-out, with cost and data-handling approval.

## 7. Next steps for a real pilot

1. Annotate the discovery sample; decide whether prepaid needs a merged label or rules.
2. Pre-register targets — proposed: team accuracy ≥ 80% on a fresh hold-out with
   no product below 0.6 F1 — and the threshold policy.
3. Pilot assisted routing with logged suggestions, overrides and reasons (US-1, US-3).
4. Measure triage minutes and misroute rework before estimating savings.
