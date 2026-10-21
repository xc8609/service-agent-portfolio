import json
from dataclasses import replace
from pathlib import Path

import httpx
import psycopg
import pytest
from bank_api.agent.providers import Profile
from bank_api.agent.runtime import current, run
from bank_api.agent.selection import ProviderRoute, load_route
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.db import runtime_connection
from conftest import NOW
from fastapi.testclient import TestClient
from test_agent import initial

EXAMPLE = Path(__file__).resolve().parents[3] / "examples/providers/profiles.example.json"


def write_config(tmp_path, mutation=lambda c: None):
    config = json.loads(EXAMPLE.read_text())
    config["selected"] = "openai-candidate"
    mutation(config)
    p = tmp_path / "provider.json"
    p.write_text(json.dumps(config))
    return p


def test_default_offline_and_strict_server_configuration(tmp_path):
    assert load_route().audit_name == "offline-scripted-v1"
    assert load_route(EXAMPLE).audit_name == "offline-scripted-v1"
    path = write_config(tmp_path)
    route = load_route(path, environ={"BANK_MODEL_API_KEY": "test-secret"})
    assert "test-secret" not in repr(route)
    assert (
        route.audit_name
        != replace(route, profile=replace(route.profile, model="changed")).audit_name
    )
    assert route.profile.credential_ref == "BANK_MODEL_API_KEY" and not route.live_ready
    renamed = load_route(
        write_config(
            tmp_path,
            lambda c: c["profiles"]["openai-candidate"].update(credential_env="OTHER_TENANT_KEY"),
        ),
        environ={},
    )
    assert renamed.audit_name != route.audit_name
    # A qualified flag alone is not enough: it must cite this route's fingerprint.
    flagged = load_route(
        write_config(
            tmp_path,
            lambda c: c["profiles"]["openai-candidate"].update(live_enabled=True, qualified=True),
        ),
        environ={},
    )
    assert flagged.audit_name == route.audit_name and not flagged.live_ready
    cited = load_route(
        write_config(
            tmp_path,
            lambda c: c["profiles"]["openai-candidate"].update(
                live_enabled=True, qualified=True, qualified_fingerprint=route.profile.fingerprint
            ),
        ),
        environ={},
    )
    assert cited.live_ready
    for mutation in (
        lambda c: c["profiles"]["openai-candidate"].update(qualified_fingerprint="not-a-hash"),
        lambda c: c.update(selected="unknown"),
        lambda c: c["profiles"]["openai-candidate"].update(live_enabled="false"),
        lambda c: c["profiles"]["openai-candidate"].update(api_key="must-not-be-in-config"),
    ):
        with pytest.raises(ValueError, match="^Invalid server provider configuration$"):
            load_route(write_config(tmp_path, mutation))


def test_unqualified_route_records_failure_without_transport_and_manual_path_remains(
    environment, tmp_path
):
    _, h, p, runtime = initial(environment)

    def forbidden_transport(request):
        pytest.fail("Unqualified configuration must never reach transport")

    route = load_route(
        write_config(tmp_path), environ={}, transport=httpx.MockTransport(forbidden_transport)
    )
    with TestClient(
        create_app(Settings(runtime), clock=lambda: NOW, provider_route=route)
    ) as client:
        result = client.post("/v1/assistant/run", headers=h, json=p)
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == "failed" and data["error_code"] == "LIVE_NOT_QUALIFIED"
        ready = client.get("/health/ready")
        assert ready.status_code == 200
        # Health reports the configured route honestly: selected, but not live.
        assert ready.json()["assistant_route"] == route.audit_name
        assert ready.json()["agent_enabled"] is False
        assert ready.json()["offline_assistant_available"] is False
        manual = client.post(
            "/v1/agent-tools/get_contact_context", headers=h, json={"contact_id": p["contact_id"]}
        )
        assert manual.status_code == 200 and manual.json()["data"]["masked_card_refs"] == [
            "DEMO-4242"
        ]
        with psycopg.connect(environment[1]) as conn:
            assert (
                conn.execute("SELECT provider_profile FROM agent_runs").fetchone()[0]
                == route.audit_name
            )
            assert conn.execute("SELECT count(*) FROM proposals").fetchone()[0] == 0
        # A provider switch never silently reruns an already persisted trigger.
        assert run(Settings(runtime), p, h["Authorization"], "replay", NOW) == data


@pytest.mark.parametrize("protocol", ["openai_responses", "claude_messages", "compatible_chat"])
@pytest.mark.parametrize("rate_limit", [False, True])
def test_server_selected_protocol_uses_same_scoped_runtime_and_persists_route(
    environment, protocol, rate_limit
):
    _, h, p, runtime = initial(environment)
    calls = []
    with runtime_connection(runtime) as conn:
        _, _, _, _, refs, _ = current(conn, h["Authorization"], p, NOW)
    citations = [r["kind"] + ":" + r["id"] + ":" + r["version"] for r in refs]

    def respond(request):
        body = json.loads(request.content)
        calls.append(body)
        name = "read_evidence" if len(calls) == 1 else "read_rules"
        if len(calls) == 3 and rate_limit:
            return httpx.Response(429)  # A partial run must preserve manual workflow.
        arguments = {}
        if len(calls) == 3:
            name = "draft_recommendation"
            arguments = {
                "summary": "Review the recorded evidence with the customer.",
                "citations": citations,
                "gaps": [],
            }
        assert "refund" not in str(body["tools"])
        if protocol == "openai_responses":
            data = {
                "status": "completed",
                "output": [
                    {
                        "type": "function_call",
                        "call_id": str(len(calls)),
                        "name": name,
                        "arguments": json.dumps(arguments),
                    }
                ],
            }
        elif protocol == "claude_messages":
            data = {
                "stop_reason": "tool_use",
                "content": [
                    {"type": "tool_use", "id": str(len(calls)), "name": name, "input": arguments}
                ],
            }
        else:
            data = {
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "tool_calls": [
                                {
                                    "id": str(len(calls)),
                                    "function": {"name": name, "arguments": json.dumps(arguments)},
                                }
                            ]
                        },
                    }
                ]
            }
        return httpx.Response(200, json=data)

    endpoint = "https://approved.example/v1/test"
    profile = Profile(
        "mock-only",
        protocol,
        "fixture-model",
        endpoint,
        (endpoint,),
        live_enabled=True,
        qualified=True,
    )
    profile = replace(profile, qualified_fingerprint=profile.fingerprint)
    route = ProviderRoute(profile, "synthetic-test-key", httpx.MockTransport(respond))
    with TestClient(
        create_app(Settings(runtime), clock=lambda: NOW, provider_route=route)
    ) as client:
        r = client.post("/v1/assistant/run", headers=h, json=p)
        assert r.status_code == 200, r.text
        if rate_limit:
            assert r.json()["error_code"] == "RATE_LIMITED"
        else:
            assert r.json()["status"] == "awaiting_human", r.text
            assert "Provider-generated" in r.json()["output"]["notice"]
            assert "Scripted fixture" not in r.json()["output"]["notice"]
    assert len(calls) == 3
    with psycopg.connect(environment[1]) as conn:
        assert (
            conn.execute("SELECT provider_profile FROM agent_runs").fetchone()[0]
            == route.audit_name
        )
        assert conn.execute("SELECT count(*) FROM agent_steps").fetchone()[0] == (
            2 if rate_limit else 3
        )
        assert conn.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
