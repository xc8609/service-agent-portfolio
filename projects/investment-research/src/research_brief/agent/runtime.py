"""Run a bounded planning/tool loop; only retrieved references can form a draft."""

from copy import deepcopy

from ..comparison import ComparisonError
from .provider import OfflineScriptedProvider
from .render import render_plan
from .tools import AgentError, ResearchTools, validate_passages


def run_research(packet, passage_pack, question, provider=None, max_tool_calls=8):
    provider = provider if provider is not None else OfflineScriptedProvider()
    result = {
        "status": "incomplete",
        "question": question.strip() if isinstance(question, str) else "",
        "source_id": "",
        "source_hash": "",
        "provider": getattr(provider, "name", "custom-provider"),
        "findings": [],
        "open_questions": [],
        "trace": [],
        "issues": [],
    }
    try:
        if (
            not 1 <= len(result["question"]) <= 1000
            or type(max_tool_calls) is not int
            or not 1 <= max_tool_calls <= 8
        ):
            raise AgentError(
                "INVALID_REQUEST",
                "Use a research question of 1–1000 characters and at most eight tool calls.",
            )
        tools = ResearchTools(packet, None)
        result.update(source_id=tools.source["id"], source_hash=tools.source["sha256"])
        tools.passages = validate_passages(deepcopy(passage_pack), tools.source)
        history = []
        for _ in range(max_tool_calls + 1):
            try:
                step = provider.next_step(result["question"], deepcopy(history))
            except Exception as exc:
                raise AgentError(
                    "PROVIDER_UNAVAILABLE",
                    "The draft could not be completed. Continue with your research notes.",
                ) from exc
            if not isinstance(step, dict):
                raise AgentError("INVALID_DRAFT", "The research planner returned an invalid step.")
            if set(step) == {"final"}:
                result["findings"], result["open_questions"] = render_plan(step["final"], tools)
                result["status"] = "draft"
                return result
            if set(step) != {"tool", "arguments"}:
                raise AgentError("INVALID_DRAFT", "The research planner returned an invalid step.")
            if len(history) >= max_tool_calls:
                raise AgentError(
                    "TOOL_BUDGET",
                    "The research tool budget was reached. Retry or continue manually.",
                )
            name = step["tool"]
            try:
                output = tools.call(name, step["arguments"])
            except AgentError:
                result["trace"].append(
                    {"tool": name if isinstance(name, str) else "invalid", "status": "error"}
                )
                raise
            result["trace"].append({"tool": name, "status": "ok"})
            history.append(
                {"tool": name, "arguments": deepcopy(step["arguments"]), "result": output}
            )
    except AgentError as exc:
        result["issues"].append({"code": exc.code, "message": exc.message})
    except (ComparisonError, ArithmeticError, TypeError, KeyError):
        result["issues"].append(
            {
                "code": "INVALID_SOURCE",
                "message": "The report facts cannot support a checked draft. Reload the source.",
            }
        )
    result["open_questions"] = ["Complete the evidence checks before using a research draft."]
    return result
