"""Replaceable planning boundary; the included provider makes no model call."""

from ..comparison import METRICS


def focus_metrics(question):
    query = question.lower()
    words = {
        "revenue": ("revenue", "sales", "margin", "营收", "收入", "利润率"),
        "operating_income": ("income", "profit", "margin", "earnings", "利润"),
        "operating_cash_flow": ("cash", "现金"),
    }
    selected = [metric for metric in METRICS if any(word in query for word in words[metric])]
    return selected or list(METRICS)


class OfflineScriptedProvider:
    """Exercise the real tool loop using a small, deterministic research plan."""

    name = "offline-scripted-v1"

    def next_step(self, question, history):
        if not history:
            return {"tool": "list_sources", "arguments": {}}
        source_id = history[0]["result"]["sources"][0]["id"]
        sequence = ("read_facts", "compare_periods", "read_passages")
        if len(history) <= len(sequence):
            tool = sequence[len(history) - 1]
            args = {"source_id": source_id}
            if tool == "read_passages":
                args["query"] = question
            return {"tool": tool, "arguments": args}
        return {
            "final": {
                "metric_ids": focus_metrics(question),
                "passage_ids": [item["id"] for item in history[-1]["result"]["passages"]],
            }
        }
