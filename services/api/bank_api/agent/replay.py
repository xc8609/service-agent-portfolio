"""Offline, request-bound recordings for the real runtime; never a live route.

Record only explicitly synthetic sessions. Responses may still contain sensitive
text: exports are local evaluation artifacts, not application audit logs. Declared
subscription provenance is an operator assertion, not verified model attribution.
"""

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict

from jsonschema import Draft202012Validator

from .providers import Call, ProviderFailure, Reply

MAX_BYTES = 1_000_000
MAX_TURNS = 8


def obj(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


TEXT = {"type": "string", "maxLength": 16000}
SCHEMA = obj(
    {
        "version": {"const": "runtime-recording-v1"},
        "provenance": obj(
            {
                "kind": {"enum": ["synthetic_fixture", "subscription_session"]},
                "label": {"type": "string", "minLength": 1, "maxLength": 200},
                "synthetic_only": {"const": True},
            }
        ),
        "turns": {
            "type": "array",
            "minItems": 1,
            "maxItems": MAX_TURNS,
            "items": obj(
                {
                    "request_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                    "reply": obj(
                        {
                            "text": TEXT,
                            "calls": {
                                "type": "array",
                                "maxItems": 8,
                                "items": obj(
                                    {
                                        "id": TEXT,
                                        "name": TEXT,
                                        "arguments": {"type": "object"},
                                    }
                                ),
                            },
                            "usage": {"type": "null"},
                            "status": {"const": "completed"},
                        }
                    ),
                }
            ),
        },
    }
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def request_digest(messages, schemas):
    # Includes previous real tool results, prompt and full domain schemas. Never
    # silently adapt an old recording to changed evidence or a changed contract.
    return hashlib.sha256(canonical({"messages": messages, "schemas": schemas})).hexdigest()


def validate_document(document):
    try:
        raw = canonical(document)
        if len(raw) > MAX_BYTES or not Draft202012Validator(SCHEMA).is_valid(document):
            raise ValueError()
    except (TypeError, ValueError, RecursionError):
        raise ProviderFailure("INVALID_RECORDING") from None
    return raw


class RecordingProvider:
    """Wrap an offline exchange provider, including a human-operated subscription bridge.

    The wrapper does not open a subscription, call an API or infer a model name.
    Do not wrap a live provider under this offline story. Unknown replay cost and
    latency are not copied from the original exchange or measured as model quality.
    """

    def __init__(self, provider, *, kind, label):
        self.provider = provider
        self.provenance = {"kind": kind, "label": label, "synthetic_only": True}
        self.turns = []

    def complete(self, messages, schemas, cancelled=lambda: False):
        if cancelled():
            raise ProviderFailure("CANCELLED")
        if len(self.turns) >= MAX_TURNS:
            raise ProviderFailure("RECORDING_LIMIT")
        digest = request_digest(messages, schemas)
        reply = self.provider.complete(messages, schemas, cancelled)
        recorded = asdict(reply)
        recorded["usage"] = None
        turn = {"request_sha256": digest, "reply": recorded}
        validate_document(
            {
                "version": "runtime-recording-v1",
                "provenance": self.provenance,
                "turns": [*self.turns, turn],
            }
        )
        self.turns.append(deepcopy(turn))
        return reply

    def document(self):
        result = {
            "version": "runtime-recording-v1",
            "provenance": self.provenance,
            "turns": self.turns,
        }
        validate_document(result)
        return deepcopy(result)


class RecordedProvider:
    """Replay normalized responses only when the actual request matches exactly.

    Domain checks are still performed by runtime.run. This is not a wire-protocol
    replay and cannot qualify reasoning blocks, strict schemas or API availability.
    """

    def __init__(self, document):
        raw = validate_document(document)
        self.fingerprint = hashlib.sha256(raw).hexdigest()
        self._document = deepcopy(document)
        self.consumed = 0

    @classmethod
    def load(cls, path):
        try:
            with open(path, "rb") as source:
                raw = source.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError()
            document = json.loads(raw)
        except (OSError, ValueError, RecursionError):
            raise ProviderFailure("INVALID_RECORDING") from None
        return cls(document)

    def complete(self, messages, schemas, cancelled=lambda: False):
        if cancelled():
            raise ProviderFailure("CANCELLED")
        if self.consumed >= len(self._document["turns"]):
            raise ProviderFailure("RECORDING_EXHAUSTED")
        turn = self._document["turns"][self.consumed]
        if request_digest(messages, schemas) != turn["request_sha256"]:
            raise ProviderFailure("RECORDING_MISMATCH")
        self.consumed += 1
        reply = deepcopy(turn["reply"])
        return Reply(**{**reply, "calls": [Call(**c) for c in reply["calls"]]})

    def assert_consumed(self):
        """Positive scenario harnesses must fail on an unused suffix, not silently pass."""
        if self.consumed != len(self._document["turns"]):
            raise ProviderFailure("RECORDING_UNUSED_TURNS")
