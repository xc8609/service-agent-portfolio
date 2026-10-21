"""Normalized provider boundary. Live routes are disabled until separately qualified."""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable, Protocol
from urllib.parse import urlsplit

import httpx
from jsonschema import Draft202012Validator

PROVIDER_TIMEOUT_SECONDS = 15


class ProviderFailure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Call:
    id: str
    name: str
    arguments: dict


@dataclass
class Reply:
    text: str = ""
    calls: list[Call] = field(default_factory=list)
    usage: dict | None = None
    status: str = "completed"


class Provider(Protocol):
    """Wire adapters return domain-neutral replies, never execute business tools."""

    def complete(
        self, messages: list[dict], schemas: dict, cancelled: Callable[[], bool]
    ) -> Reply: ...


@dataclass(frozen=True)
class Profile:
    name: str
    protocol: str
    model: str
    endpoint: str
    allowed_endpoints: tuple[str, ...]
    internal_only: bool = False
    internal_endpoints: tuple[str, ...] = ()
    live_enabled: bool = False
    qualified: bool = False
    credential_ref: str = ""
    qualified_fingerprint: str | None = None

    @property
    def fingerprint(self):
        """Route identity: what a qualification report evaluated. Excludes the enable
        flags and never includes credential values, only the environment reference."""
        identity = {
            "name": self.name,
            "protocol": self.protocol,
            "model": self.model,
            "endpoint": self.endpoint,
            "allowed_endpoints": list(self.allowed_endpoints),
            "internal_only": self.internal_only,
            "internal_endpoints": list(self.internal_endpoints),
            "credential_ref": self.credential_ref,
        }
        return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]

    @property
    def live_ready(self):
        # A qualification applies only to the exact route it evaluated.
        return (
            self.live_enabled
            and self.qualified
            and self.qualified_fingerprint is not None
            and self.qualified_fingerprint == self.fingerprint
        )

    def validate(self):
        u = urlsplit(self.endpoint)
        if (
            u.scheme != "https"
            or u.username
            or u.password
            or u.query
            or u.fragment
            or self.endpoint not in self.allowed_endpoints
        ):
            raise ProviderFailure("EGRESS_DENIED")
        if self.internal_only and self.endpoint not in self.internal_endpoints:
            raise ProviderFailure("EGRESS_DENIED")
        if self.protocol not in ("openai_responses", "claude_messages", "compatible_chat"):
            raise ProviderFailure("UNSUPPORTED_PROVIDER")
        if not self.live_ready:
            raise ProviderFailure("LIVE_NOT_QUALIFIED")


def checked_call(call_id, name, arguments, schemas):
    if name not in schemas:
        raise ProviderFailure("TOOL_DENIED")
    if isinstance(arguments, str):
        if len(arguments) > 16000:
            raise ProviderFailure("OUTPUT_LIMIT")
        try:
            arguments = json.loads(arguments)
        except (ValueError, TypeError):
            raise ProviderFailure("INVALID_TOOL_ARGUMENTS") from None
    if list(Draft202012Validator(schemas[name]).iter_errors(arguments)):
        raise ProviderFailure("INVALID_TOOL_ARGUMENTS")
    if not isinstance(call_id, str) or not call_id or len(call_id) > 200:
        raise ProviderFailure("INVALID_RESPONSE")
    return Call(call_id, name, arguments)


class ToolBuffer:
    """Never expose a partial call to execution. Finalize only on a completed event."""

    def __init__(self):
        self.parts = {}

    def delta(self, call_id, name, text):
        old = self.parts.get(call_id, (name, ""))
        if old[0] != name:
            raise ProviderFailure("INVALID_RESPONSE")
        value = old[1] + text
        if len(value) > 16000 or len(self.parts) > 8:
            raise ProviderFailure("OUTPUT_LIMIT")
        self.parts[call_id] = (name, value)

    def finish(self, call_id, schemas):
        if call_id not in self.parts:
            raise ProviderFailure("INVALID_RESPONSE")
        name, value = self.parts.pop(call_id)
        return checked_call(call_id, name, value, schemas)


def request_body(profile, messages, schemas):
    tools = [
        {
            "name": n,
            "description": "Scoped read or draft; never approve or execute a business action.",
            "parameters": s,
        }
        for n, s in schemas.items()
    ]
    if profile.protocol == "openai_responses":
        items = []
        for m in messages:
            if m["role"] == "tool":
                items.append(
                    {
                        "type": "function_call_output",
                        "call_id": m["call_id"],
                        "output": m["content"],
                    }
                )
            elif m.get("calls"):
                items.extend(
                    {
                        "type": "function_call",
                        "call_id": c["id"],
                        "name": c["name"],
                        "arguments": json.dumps(c["arguments"]),
                    }
                    for c in m["calls"]
                )
            else:
                items.append({"role": m["role"], "content": m["content"]})
        return {
            "model": profile.model,
            "input": items,
            "tools": [{"type": "function", **t, "strict": True} for t in tools],
            "parallel_tool_calls": False,
            "store": False,
            "max_output_tokens": 2000,
        }
    if profile.protocol == "claude_messages":
        items = []
        system = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
                continue
            if m["role"] == "tool":
                items.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": m["call_id"],
                                "content": m["content"],
                            }
                        ],
                    }
                )
            elif m.get("calls"):
                items.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": c["id"],
                                "name": c["name"],
                                "input": c["arguments"],
                            }
                            for c in m["calls"]
                        ],
                    }
                )
            else:
                items.append({"role": m["role"], "content": m["content"]})
        return {
            "model": profile.model,
            "system": system,
            "messages": items,
            "max_tokens": 2000,
            "tools": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": t["parameters"],
                }
                for t in tools
            ],
            "tool_choice": {"type": "auto", "disable_parallel_tool_use": True},
        }
    items = []
    for m in messages:
        if m["role"] == "tool":
            items.append({"role": "tool", "tool_call_id": m["call_id"], "content": m["content"]})
        elif m.get("calls"):
            items.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": c["id"],
                            "type": "function",
                            "function": {
                                "name": c["name"],
                                "arguments": json.dumps(c["arguments"]),
                            },
                        }
                        for c in m["calls"]
                    ],
                }
            )
        else:
            items.append(m)
    return {
        "model": profile.model,
        "messages": items,
        "tools": [{"type": "function", "function": t} for t in tools],
        "max_tokens": 2000,
    }


def normalize(protocol, data, schemas):
    try:
        calls = []
        text = []
        if protocol == "openai_responses":
            if data.get("status") != "completed":
                raise ProviderFailure("INCOMPLETE_RESPONSE")
            for item in data["output"]:
                if item["type"] == "function_call":
                    calls.append(
                        checked_call(item["call_id"], item["name"], item["arguments"], schemas)
                    )
                elif item["type"] == "message":
                    text.extend(c["text"] for c in item["content"] if c["type"] == "output_text")
        elif protocol == "claude_messages":
            if data.get("stop_reason") not in ("tool_use", "end_turn"):
                raise ProviderFailure("INCOMPLETE_RESPONSE")
            for item in data["content"]:
                if item["type"] == "tool_use":
                    calls.append(checked_call(item["id"], item["name"], item["input"], schemas))
                elif item["type"] == "text":
                    text.append(item["text"])
        else:
            choice = data["choices"][0]
            if choice.get("finish_reason") not in ("stop", "tool_calls"):
                raise ProviderFailure("INCOMPLETE_RESPONSE")
            msg = choice["message"]
            text.append(msg.get("content") or "")
            # Compatible servers may send an explicit null when no tool is called.
            for item in msg.get("tool_calls") or []:
                calls.append(
                    checked_call(
                        item["id"], item["function"]["name"], item["function"]["arguments"], schemas
                    )
                )
        if len(calls) > 1 or len("".join(text)) > 16000:
            raise ProviderFailure("OUTPUT_LIMIT")
        usage = data.get("usage")
        # Missing usage remains unknown; never infer zero cost.
        if usage is not None:
            usage = {
                k: v
                for k, v in usage.items()
                if k in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens")
                and isinstance(v, int)
                and v >= 0
            }
            if not usage:
                usage = None
        return Reply("".join(text), calls, usage)
    except (KeyError, IndexError, TypeError, ValueError):
        raise ProviderFailure("INVALID_RESPONSE") from None


class HttpProvider:
    def __init__(self, profile, key, transport=None):
        self.profile = profile
        self._key = key
        self._transport = transport

    def complete(self, messages, schemas, cancelled: Callable[[], bool] = lambda: False):
        self.profile.validate()
        if cancelled():
            raise ProviderFailure("CANCELLED")
        if not self._key:
            raise ProviderFailure("CREDENTIALS_UNAVAILABLE")
        if len(json.dumps(messages)) > 60000:
            raise ProviderFailure("INPUT_LIMIT")
        headers = (
            {"x-api-key": self._key, "anthropic-version": "2023-06-01"}
            if self.profile.protocol == "claude_messages"
            else {"Authorization": "Bearer " + self._key}
        )
        try:
            with httpx.Client(
                timeout=PROVIDER_TIMEOUT_SECONDS,
                follow_redirects=False,
                trust_env=False,
                transport=self._transport,
            ) as client:
                with client.stream(
                    "POST",
                    self.profile.endpoint,
                    headers=headers,
                    json=request_body(self.profile, messages, schemas),
                ) as r:
                    if r.status_code == 429:
                        raise ProviderFailure("RATE_LIMITED")
                    if r.status_code >= 300:
                        raise ProviderFailure("PROVIDER_UNAVAILABLE")
                    body = b""
                    for chunk in r.iter_bytes():
                        if cancelled():
                            raise ProviderFailure("CANCELLED")
                        body += chunk
                        if len(body) > 1000000:
                            raise ProviderFailure("OUTPUT_LIMIT")
            if cancelled():
                raise ProviderFailure("CANCELLED")
            return normalize(self.profile.protocol, json.loads(body), schemas)
        except httpx.TimeoutException:
            raise ProviderFailure("TIMEOUT") from None
        except httpx.HTTPError:
            raise ProviderFailure("PROVIDER_UNAVAILABLE") from None
        except ValueError:
            raise ProviderFailure("INVALID_RESPONSE") from None


class FakeProvider:
    """Explicit scripted fixture, not a language model or quality benchmark."""

    def __init__(self, replies):
        self.replies = iter(replies)

    def complete(self, messages, schemas, cancelled=lambda: False):
        if cancelled():
            raise ProviderFailure("CANCELLED")
        try:
            reply = next(self.replies)
        except StopIteration:
            raise ProviderFailure("INCOMPLETE_RESPONSE") from None
        if isinstance(reply, Exception):
            raise reply
        for c in reply.calls:
            checked_call(c.id, c.name, c.arguments, schemas)
        return reply


def safe_context(evidence):
    """Positive DTO projection; do not pass the workspace response wholesale."""
    allowed = {
        "facts": ("id", "version", "status", "amount_minor", "currency"),
        "rules": ("id", "version", "text"),
        "findings": ("id", "version", "approved_customer_explanation"),
        "work": ("id", "version", "status", "original_due_at"),
    }
    return {
        section: [{k: row[k] for k in keys if k in row} for row in evidence.get(section, [])][:50]
        for section, keys in allowed.items()
    }
