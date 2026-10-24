"""Four read-only tools over a single validated evidence snapshot."""

from copy import deepcopy

from ..comparison import METRICS, compare
from .provider import focus_metrics


class AgentError(ValueError):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)


def validate_passages(pack, source):
    if pack is None:
        return []
    if (
        not isinstance(pack, dict)
        or type(pack.get("schema_version")) is not int
        or pack["schema_version"] != 1
        or pack.get("source_id") != source["id"]
        or pack.get("source_sha256") != source["sha256"]
        or not isinstance(pack.get("passages"), list)
        or len(pack["passages"]) > 20
    ):
        raise AgentError(
            "INVALID_EVIDENCE", "Report commentary does not match this source snapshot."
        )
    seen = set()
    for item in pack["passages"]:
        if (
            not isinstance(item, dict)
            or any(
                not isinstance(item.get(key), str) or not item[key].strip()
                for key in ("id", "source_id", "locator", "kind", "text")
            )
            or item["source_id"] != source["id"]
            or item["kind"] != "analyst_summary"
            or len(item["text"]) > 2000
            or not isinstance(item.get("topics"), list)
            or not item["topics"]
            or any(topic not in METRICS for topic in item["topics"])
            or item["id"] in seen
        ):
            raise AgentError(
                "INVALID_EVIDENCE", "Report commentary needs a valid source and locator."
            )
        seen.add(item["id"])
    return deepcopy(pack["passages"])


class ResearchTools:
    def __init__(self, packet, passage_pack):
        self.comparison = compare(deepcopy(packet))
        self.source = self.comparison["source"]
        self.passages = validate_passages(deepcopy(passage_pack), self.source)
        self.used = set()
        self.retrieved_passages = set()

    def call(self, name, args):
        allowed = {"list_sources", "read_facts", "compare_periods", "read_passages"}
        if not isinstance(name, str) or name not in allowed:
            raise AgentError("UNKNOWN_TOOL", "This research tool is not available.")
        keys = set() if name == "list_sources" else {"source_id"}
        if name == "read_passages":
            keys.add("query")
        if not isinstance(args, dict) or set(args) != keys:
            raise AgentError("INVALID_TOOL_ARGUMENTS", "The research tool arguments are invalid.")
        if keys and args["source_id"] != self.source["id"]:
            raise AgentError("SOURCE_SCOPE", "The tool must use the selected report.")
        if name == "list_sources":
            result = {
                "sources": [
                    {
                        "id": self.source["id"],
                        "title": self.source["title"],
                        "url": self.source["url"],
                        "issuer": self.comparison["issuer"],
                        "periods": self.comparison["periods"],
                    }
                ]
            }
        elif name == "read_facts":
            result = {"source_id": self.source["id"], "facts": self.comparison["facts"]}
        elif name == "compare_periods":
            result = self.comparison
        else:
            query = args["query"]
            if not isinstance(query, str) or not 1 <= len(query.strip()) <= 1000:
                raise AgentError("INVALID_TOOL_ARGUMENTS", "A short research query is required.")
            topics = set(focus_metrics(query))
            passages = [item for item in self.passages if topics.intersection(item["topics"])]
            self.retrieved_passages.update(item["id"] for item in passages)
            result = {"source_id": self.source["id"], "passages": passages}
        self.used.add(name)
        return deepcopy(result)
