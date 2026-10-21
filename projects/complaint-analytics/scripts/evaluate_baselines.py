"""Frozen product-routing baselines on the local CFPB discovery table.

Design fixed before any result was inspected (2026-10-21):
- Input: the 6,409 in-scope complaints with public narratives (banking_discovery.parquet).
- Duplicates: whitespace/case-normalized narratives are grouped; only the lowest
  complaint ID per group is kept, so no text appears on both sides of the split.
- Split: sha256(complaint_id) mod 100 < 70 is development, otherwise hold-out (30%).
- Models: majority class; TF-IDF word 1-2 grams (min_df=2, sublinear tf) with
  logistic regression (C=1.0, class_weight="balanced", max_iter=2000).
  No hyper-parameter search; 5-fold cross-validation on development only.
- Confidence thresholds are compared on out-of-fold development predictions; the
  hold-out set is scored once to confirm. Outputs are metrics only: no text or IDs.
"""

import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
from triage.metrics import accuracy, macro_f1, per_class_report, to_teams  # noqa: E402

SOURCE = PROJECT / "data/processed/banking_discovery.parquet"
OUTPUT = PROJECT / "data/processed/model_baselines.json"
THRESHOLDS = (0.5, 0.6, 0.7, 0.8, 0.9)


def load():
    with duckdb.connect() as con:
        rows = con.execute(
            "SELECT complaint_id, product, routing_team, narrative FROM read_parquet(?) ORDER BY complaint_id",
            [str(SOURCE)],
        ).fetchall()
    teams = {product: team for _, product, team, _ in rows}
    seen, kept, excess = set(), [], 0
    for complaint_id, product, _, text in rows:
        key = re.sub(r"\s+", " ", text.strip().lower())
        if key in seen:
            excess += 1
            continue
        seen.add(key)
        kept.append((complaint_id, product, text))
    return kept, teams, len(rows), excess


def holdout(complaint_id):
    return int(hashlib.sha256(str(complaint_id).encode()).hexdigest(), 16) % 100 >= 70


def model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000),
    )


def scores(y_true, y_pred, teams):
    return {
        "product_accuracy": round(accuracy(y_true, y_pred), 4),
        "product_macro_f1": round(macro_f1(y_true, y_pred), 4),
        "team_accuracy": round(
            accuracy(to_teams(y_true, teams), to_teams(y_pred, teams)), 4
        ),
    }


def main():
    records, teams, total, excess = load()
    dev = [r for r in records if not holdout(r[0])]
    test = [r for r in records if holdout(r[0])]
    x_dev, y_dev = [r[2] for r in dev], [r[1] for r in dev]
    x_test, y_test = [r[2] for r in test], [r[1] for r in test]

    majority = Counter(y_dev).most_common(1)[0][0]
    folds = []
    oof_pred, oof_conf = [None] * len(dev), [0.0] * len(dev)
    for train, valid in StratifiedKFold(5, shuffle=True, random_state=20261021).split(x_dev, y_dev):
        fitted = model().fit([x_dev[i] for i in train], [y_dev[i] for i in train])
        part = list(fitted.predict([x_dev[i] for i in valid]))
        probs = fitted.predict_proba([x_dev[i] for i in valid]).max(axis=1)
        for j, i in enumerate(valid):
            oof_pred[i], oof_conf[i] = part[j], float(probs[j])
        folds.append(scores([y_dev[i] for i in valid], part, teams))

    final = model().fit(x_dev, y_dev)
    predicted = list(final.predict(x_test))
    confidence = final.predict_proba(x_test).max(axis=1)
    labels = sorted(teams)
    confusion = {
        t: {p: sum(1 for a, b in zip(y_test, predicted) if a == t and b == p) for p in labels}
        for t in labels
    }
    def threshold_curve(truth, pred, conf):
        team_true, team_pred = to_teams(truth, teams), to_teams(pred, teams)
        curve = []
        for threshold in THRESHOLDS:
            chosen = [i for i, c in enumerate(conf) if c >= threshold]
            curve.append(
                {
                    "threshold": threshold,
                    "auto_route_share": round(len(chosen) / len(truth), 4),
                    "team_accuracy_on_auto_routed": round(
                        accuracy([team_true[i] for i in chosen], [team_pred[i] for i in chosen]), 4
                    )
                    if chosen
                    else None,
                }
            )
        return curve

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "CFPB July 2026 archive, seven-product routing scope, public narratives only",
        "contains_text_or_ids": False,
        "records_with_text": total,
        "normalized_duplicate_excess_removed": excess,
        "development_records": len(dev),
        "holdout_records": len(test),
        "holdout_by_product": dict(sorted(Counter(y_test).items())),
        "majority_baseline": {"label": majority, **scores(y_test, [majority] * len(y_test), teams)},
        "tfidf_logistic_regression": {
            "cross_validation_on_development": {
                k: {
                    "mean": round(float(np.mean([f[k] for f in folds])), 4),
                    "std": round(float(np.std([f[k] for f in folds])), 4),
                }
                for k in folds[0]
            },
            "holdout": scores(y_test, predicted, teams),
            "holdout_per_product": [
                {
                    "product": r.label,
                    "precision": round(r.precision, 4),
                    "recall": round(r.recall, 4),
                    "f1": round(r.f1, 4),
                    "support": r.support,
                }
                for r in per_class_report(y_test, predicted)
            ],
            "holdout_confusion": confusion,
            # Thresholds are compared on out-of-fold development predictions; the
            # hold-out curve only confirms. No pilot threshold has been selected.
            "threshold_curve_development_out_of_fold": threshold_curve(y_dev, oof_pred, oof_conf),
            "threshold_curve_holdout_confirmation": threshold_curve(y_test, predicted, confidence),
        },
        "environment": {
            "python": sys.version.split()[0],
            "duckdb": duckdb.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("development_records", "holdout_records", "majority_baseline")}, indent=2))
    print(json.dumps(report["tfidf_logistic_regression"]["holdout"], indent=2))


if __name__ == "__main__":
    main()
