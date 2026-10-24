"""Compile reference choices into cited facts, explanations and explicit gaps."""

from decimal import Decimal

from ..comparison import METRICS
from .tools import AgentError

LABELS = {
    "revenue": "Revenue",
    "operating_income": "Operating income",
    "operating_cash_flow": "Operating cash flow",
}


def _choices(value, allowed):
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) for item in value)
        or len(set(value)) != len(value)
        or any(item not in allowed for item in value)
    ):
        raise AgentError(
            "UNSUPPORTED_REFERENCE", "The draft references evidence not retrieved in this run."
        )
    return value


def render_plan(plan, tools):
    if not isinstance(plan, dict) or set(plan) != {"metric_ids", "passage_ids"}:
        raise AgentError("INVALID_DRAFT", "The draft must select evidence references only.")
    metrics = _choices(plan["metric_ids"], METRICS)
    passage_ids = _choices(plan["passage_ids"], tools.retrieved_passages)
    if not metrics or not {"read_facts", "compare_periods"}.issubset(tools.used):
        raise AgentError(
            "UNSUPPORTED_REFERENCE", "Read the selected facts and calculations before drafting."
        )
    comparison, source = tools.comparison, tools.source
    prior, current = [item["id"] for item in comparison["periods"]]
    facts = {item["id"]: item for item in comparison["facts"]}
    findings, questions = [], []

    def citation(identifier, label, locator):
        return {"id": identifier, "label": label, "url": source["url"], "locator": locator}

    def numeric_finding(text, metric, ids):
        citations = [
            citation(
                "fact:" + ident,
                LABELS[facts[ident]["metric"]] + " · " + facts[ident]["period_id"],
                facts[ident]["locator"],
            )
            for ident in ids
        ]
        citations.append(
            citation(
                "calculation:" + metric,
                "Calculated " + metric.replace("_", " "),
                "Derived from " + "; ".join(facts[ident]["locator"] for ident in ids),
            )
        )
        findings.append({"kind": "calculated_fact", "text": text, "citations": citations})

    for metric in metrics:
        entry = comparison["metrics"][metric]
        before, after = entry["actuals"][prior], entry["actuals"][current]
        missing = [period for period in (prior, current) if entry["actuals"][period] is None]
        if missing:
            questions.append(
                "Find {} for {} before comparing this metric.".format(
                    LABELS[metric].lower(), " and ".join(missing)
                )
            )
            continue
        text = "{}: {} {} {} in {} versus {} {} {} in {}.".format(
            LABELS[metric],
            comparison["currency"],
            format(Decimal(after["value"]), ",f"),
            comparison["unit"],
            current,
            comparison["currency"],
            format(Decimal(before["value"]), ",f"),
            comparison["unit"],
            prior,
        )
        growth = entry["growth_pct"]
        if growth["value"] is not None:
            text += " Year-over-year change: {}%.".format(growth["value"])
        else:
            questions.append(
                "For {}, compare the absolute change; the prior value is zero or negative, so percentage growth is unavailable.".format(
                    LABELS[metric].lower()
                )
            )
        numeric_finding(text, metric, entry["delta"]["input_fact_ids"])
    if {"revenue", "operating_income"}.issubset(metrics):
        margin = comparison["operating_margin_change_pp"]
        if margin["value"] is not None:
            numeric_finding(
                "Operating margin changed from {}% to {}% ({} percentage points).".format(
                    comparison["operating_margin_pct"][prior]["value"],
                    comparison["operating_margin_pct"][current]["value"],
                    margin["value"],
                ),
                "operating_margin_change_pp",
                margin["input_fact_ids"],
            )
            questions.append(
                "What evidence quantifies each business driver's contribution to the operating-margin change?"
            )
        else:
            questions.append(
                "Find valid revenue and operating income for both years to establish the operating-margin change."
            )

    passages = {item["id"]: item for item in tools.passages}
    covered = set()
    for identifier in passage_ids:
        item = passages[identifier]
        covered.update(item["topics"])
        findings.append(
            {
                "kind": "reported_explanation",
                "text": item["text"],
                "citations": [
                    citation(
                        "passage:" + identifier,
                        "Report commentary — analyst summary",
                        item["locator"],
                    )
                ],
            }
        )
    for metric in metrics:
        if metric not in covered:
            questions.append(
                "Find report commentary explaining the {} change; no matching passage was retrieved.".format(
                    LABELS[metric].lower()
                )
            )
    if not questions:
        questions.append(
            "Which additional evidence would confirm or challenge the reported explanation?"
        )
    return findings, questions
