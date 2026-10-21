"""Evaluation metrics and value estimate for the complaint-triage pilot."""

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass
class ClassReport:
    label: str
    precision: float
    recall: float
    f1: float
    support: int


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    _check_lengths(y_true, y_pred)
    if not y_true:
        return 0.0
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)


def per_class_report(y_true: Sequence[str], y_pred: Sequence[str]) -> List[ClassReport]:
    """Precision / recall / F1 per label, sorted by support (largest first)."""
    _check_lengths(y_true, y_pred)
    tp: Counter = Counter()
    fp: Counter = Counter()
    fn: Counter = Counter()
    for t, p in zip(y_true, y_pred):
        if t == p:
            tp[t] += 1
        else:
            fp[p] += 1
            fn[t] += 1

    support = Counter(y_true)
    reports = []
    for label in set(y_true) | set(y_pred):
        precision = _safe_div(tp[label], tp[label] + fp[label])
        recall = _safe_div(tp[label], tp[label] + fn[label])
        f1 = _safe_div(2 * precision * recall, precision + recall)
        reports.append(ClassReport(label, precision, recall, f1, support[label]))
    return sorted(reports, key=lambda r: (-r.support, r.label))


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    """Unweighted mean F1 over labels that appear in y_true."""
    reports = [r for r in per_class_report(y_true, y_pred) if r.support > 0]
    return _safe_div(sum(r.f1 for r in reports), len(reports))


def to_teams(labels: Sequence[str], product_team: Dict[str, str]) -> List[str]:
    """Map product labels to routing teams; a product confusion within one team is not a misroute.

    Raises on unmapped labels so out-of-scope predictions are caught, not silently dropped.
    """
    unmapped = sorted(set(labels) - set(product_team))
    if unmapped:
        raise ValueError(f"labels outside the routing scope: {unmapped}")
    return [product_team[label] for label in labels]


def estimate_hours_saved(
    monthly_volume: int,
    minutes_per_manual_triage: float,
    auto_route_rate: float,
    accuracy_on_auto_routed: float,
    minutes_per_misroute: float,
) -> Dict[str, float]:
    """Monthly triage hours saved by auto-routing, net of rework on misroutes.

    auto_route_rate: share of complaints routed without human review
        (e.g. those above a confidence threshold).
    accuracy_on_auto_routed: accuracy within that auto-routed share.
    minutes_per_misroute: extra handling time when a complaint lands on the wrong team.
    """
    for name, value in [("auto_route_rate", auto_route_rate),
                        ("accuracy_on_auto_routed", accuracy_on_auto_routed)]:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1, got {value}")

    auto_routed = monthly_volume * auto_route_rate
    misroutes = auto_routed * (1 - accuracy_on_auto_routed)
    gross_minutes = auto_routed * minutes_per_manual_triage
    rework_minutes = misroutes * minutes_per_misroute
    return {
        "auto_routed": auto_routed,
        "misroutes": misroutes,
        "gross_hours_saved": gross_minutes / 60,
        "rework_hours": rework_minutes / 60,
        "net_hours_saved": (gross_minutes - rework_minutes) / 60,
    }


def _check_lengths(y_true: Sequence[str], y_pred: Sequence[str]) -> None:
    if len(y_true) != len(y_pred):
        raise ValueError(f"length mismatch: {len(y_true)} true vs {len(y_pred)} predicted")


def _safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0
