import json
from dataclasses import replace

import httpx
import pytest
from bank_api.agent.providers import (
    Call,
    FakeProvider,
    HttpProvider,
    Profile,
    ProviderFailure,
    Reply,
    ToolBuffer,
    normalize,
    request_body,
)

SCHEMAS = {
    "read_evidence": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
}
PROFILE = Profile(
    "fixture",
    "openai_responses",
    "fixture-model",
    "https://approved.example/v1/responses",
    ("https://approved.example/v1/responses",),
    live_enabled=True,
    qualified=True,
)
# Test-only qualification evidence for this exact mock route.
PROFILE = replace(PROFILE, qualified_fingerprint=PROFILE.fingerprint)


def test_partial_arguments_are_not_executable():
    b = ToolBuffer()
    b.delta("c", "read_evidence", "{")
    with pytest.raises(ProviderFailure, match="INVALID_TOOL_ARGUMENTS"):
        b.finish("c", SCHEMAS)
    b.delta("d", "read_evidence", "{")
    b.delta("d", "read_evidence", "}")
    assert b.finish("d", SCHEMAS) == Call("d", "read_evidence", {})
    b.delta("x", "refund", "{}")
    with pytest.raises(ProviderFailure, match="TOOL_DENIED"):
        b.finish("x", SCHEMAS)


@pytest.mark.parametrize(
    "protocol,data",
    [
        (
            "openai_responses",
            {
                "status": "completed",
                "output": [
                    {
                        "type": "function_call",
                        "call_id": "c",
                        "name": "read_evidence",
                        "arguments": "{}",
                    }
                ],
            },
        ),
        (
            "claude_messages",
            {
                "stop_reason": "tool_use",
                "content": [{"type": "tool_use", "id": "c", "name": "read_evidence", "input": {}}],
            },
        ),
        (
            "compatible_chat",
            {
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "tool_calls": [
                                {
                                    "id": "c",
                                    "function": {"name": "read_evidence", "arguments": "{}"},
                                }
                            ]
                        },
                    }
                ]
            },
        ),
    ],
)
def test_normalized_calls_and_dependent_results(protocol, data):
    reply = normalize(protocol, data, SCHEMAS)
    assert reply.calls == [Call("c", "read_evidence", {})] and reply.usage is None
    history = [
        {"role": "system", "content": "Read only."},
        {"role": "user", "content": "Synthetic request."},
        {"role": "assistant", "calls": [{"id": "c", "name": "read_evidence", "arguments": {}}]},
        {"role": "tool", "call_id": "c", "content": '{"status":"posted"}'},
    ]
    body = request_body(replace(PROFILE, protocol=protocol), history, SCHEMAS)
    assert "posted" in json.dumps(body) and "c" in json.dumps(body)
    assert body["model"] == "fixture-model"


@pytest.mark.parametrize(
    "status,code",
    [(429, "RATE_LIMITED"), (500, "PROVIDER_UNAVAILABLE"), (302, "PROVIDER_UNAVAILABLE")],
)
def test_http_errors_never_leak_body_or_follow_redirect(status, code):
    requests = []

    def handler(req):
        requests.append(req)
        return httpx.Response(
            status,
            text="PRIVATE CREDENTIAL FAILURE",
            headers={"Location": "https://unapproved.example"},
        )

    p = HttpProvider(PROFILE, "fixture-key", httpx.MockTransport(handler))
    with pytest.raises(ProviderFailure, match=code) as e:
        p.complete([], SCHEMAS)
    assert "PRIVATE" not in str(e.value) and len(requests) == 1


def test_endpoint_internal_gate_and_live_qualification_prevent_transport():
    def unexpected(req):
        raise AssertionError("No outbound transport allowed")

    for profile, code in [
        (replace(PROFILE, qualified=False), "LIVE_NOT_QUALIFIED"),
        # Changing the model or credential reference invalidates an earlier qualification.
        (replace(PROFILE, model="other-model"), "LIVE_NOT_QUALIFIED"),
        (replace(PROFILE, credential_ref="OTHER_TENANT_KEY"), "LIVE_NOT_QUALIFIED"),
        (replace(PROFILE, internal_only=True), "EGRESS_DENIED"),
        (replace(PROFILE, endpoint="https://evil.example"), "EGRESS_DENIED"),
    ]:
        with pytest.raises(ProviderFailure, match=code):
            HttpProvider(profile, "key", httpx.MockTransport(unexpected)).complete([], SCHEMAS)


def test_timeout_cancel_invalid_reply_and_missing_usage():
    def timeout(req):
        raise httpx.ReadTimeout("private transport details")

    with pytest.raises(ProviderFailure, match="TIMEOUT"):
        HttpProvider(PROFILE, "key", httpx.MockTransport(timeout)).complete([], SCHEMAS)
    with pytest.raises(ProviderFailure, match="CANCELLED"):
        FakeProvider([]).complete([], SCHEMAS, lambda: True)
    with pytest.raises(ProviderFailure, match="INVALID_RESPONSE"):
        normalize("openai_responses", {"status": "completed"}, SCHEMAS)
    fake = FakeProvider([Reply(calls=[Call("1", "read_evidence", {})]), Reply("draft only")])
    assert fake.complete([], SCHEMAS).calls
    assert fake.complete([], SCHEMAS).usage is None


def test_positive_dto_projection_excludes_contact_internal_notes_and_credentials():
    from bank_api.agent.providers import safe_context

    dto = safe_context(
        {
            "facts": [
                {
                    "id": "t",
                    "version": "1",
                    "status": "posted",
                    "customer_name": "private",
                    "full_pan": "private",
                }
            ],
            "findings": [
                {
                    "id": "r",
                    "version": 1,
                    "approved_customer_explanation": "Approved explanation.",
                    "internal_notes": "private",
                }
            ],
            "credentials": "private",
            "contact_details": "private",
        }
    )
    assert "private" not in json.dumps(dto)
    assert dto["facts"][0]["status"] == "posted"
