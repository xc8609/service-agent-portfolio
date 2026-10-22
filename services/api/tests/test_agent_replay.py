"""Synthetic engineering fixtures, not recorded model quality or owner UAT."""

import json
from copy import deepcopy
from uuid import uuid4

import psycopg
import pytest
from bank_api.agent.providers import Call, ProviderFailure, Reply
from bank_api.agent.replay import RecordedProvider, RecordingProvider, request_digest
from bank_api.agent.runtime import TOOLS, current, fixture, run
from bank_api.app import BankError
from bank_api.config import Settings
from bank_api.db import runtime_connection
from conftest import NOW, session
from test_agent import initial


def capture(environment):
    _, headers, payload, runtime = initial(environment)
    with runtime_connection(runtime) as conn:
        _, _, stage, evidence, refs, _ = current(conn, headers["Authorization"], payload, NOW)
    recorder = RecordingProvider(
        fixture(evidence, refs, stage), kind="synthetic_fixture", label="bank inbound fixture"
    )
    result = run(Settings(runtime), payload, headers["Authorization"], "capture", NOW, recorder)
    assert result["status"] == "awaiting_human"
    return headers, payload, runtime, recorder.document()


def replay(headers, payload, runtime, provider, **kwargs):
    return run(
        Settings(runtime),
        {**payload, "trigger_key": str(uuid4())},
        headers["Authorization"],
        "replay",
        NOW,
        provider,
        **kwargs,
    )


def counts(admin):
    with psycopg.connect(admin) as conn:
        return {
            table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in ("proposals", "contact_notes", "referral_intakes", "cases")
        }


def test_recorded_turns_traverse_real_runtime_and_only_create_an_uncommitted_draft(
    environment, tmp_path
):
    headers, payload, runtime, document = capture(environment)
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(document))
    provider = RecordedProvider.load(path)
    before = counts(environment[1])
    result = replay(headers, payload, runtime, provider)
    assert result["status"] == "awaiting_human", result
    assert result["output"]["proposal_id"] and result["usage"] is None
    provider.assert_consumed()
    assert provider.consumed == 3
    assert len(provider.fingerprint) == 64
    after = counts(environment[1])
    assert after == {**before, "proposals": before["proposals"] + 1}
    with psycopg.connect(environment[1]) as conn:
        steps = conn.execute(
            "SELECT tool_name FROM agent_steps WHERE run_id=%s ORDER BY sequence",
            (result["run_id"],),
        ).fetchall()
        assert [s[0] for s in steps] == ["read_evidence", "read_rules", "draft_recommendation"]


@pytest.mark.parametrize(
    "change,code",
    [
        ("citation", "UNSUPPORTED_CITATION"),
        ("tool", "TOOL_DENIED"),
        ("arguments", "INVALID_TOOL_ARGUMENTS"),
        ("duplicate_call", "DUPLICATE_TOOL_CALL"),
        ("order", "TOOL_ORDER"),
        ("exhausted", "RECORDING_EXHAUSTED"),
    ],
)
def test_recorded_responses_do_not_bypass_runtime_guards(environment, change, code):
    headers, payload, runtime, document = capture(environment)
    turns = document["turns"]
    draft = turns[-1]["reply"]["calls"][0]
    if change == "citation":
        draft["arguments"]["citations"] = ["fabricated:source:1"]
    elif change == "tool":
        draft.update(name="execute_refund", arguments={})
    elif change == "arguments":
        draft["arguments"]["summary"] = ""
    elif change == "duplicate_call":
        draft["id"] = turns[0]["reply"]["calls"][0]["id"]
    elif change == "order":
        turns[0]["reply"]["calls"][0]["name"] = "read_rules"
    else:
        document["turns"] = turns[:1]
    before = counts(environment[1])
    result = replay(headers, payload, runtime, RecordedProvider(document))
    assert result["status"] == "failed" and result["error_code"] == code, result
    assert result["output"] is None
    assert counts(environment[1]) == before


def test_recording_cannot_supply_stale_tool_results(environment):
    headers, payload, runtime, document = capture(environment)
    before = counts(environment[1])
    with psycopg.connect(environment[1]) as conn:
        conn.execute("UPDATE policy_versions SET published=false")
    result = replay(headers, payload, runtime, RecordedProvider(document))
    assert result["error_code"] == "RECORDING_MISMATCH", result
    assert counts(environment[1]) == before


def test_authority_is_checked_before_a_recording_is_consumed(environment):
    headers, payload, runtime, document = capture(environment)
    unauthorized, contact = session(environment[0], "unverified")
    provider = RecordedProvider(document)
    with pytest.raises(BankError) as exc:
        replay(unauthorized, {**payload, "contact_id": contact}, runtime, provider)
    assert exc.value.code == "AUTH_REQUIRED"
    assert provider.consumed == 0


@pytest.mark.parametrize(
    "change,code", [("stale", "STALE_EVIDENCE"), ("cancel", "CANCELLED"), ("time", "TIME_BUDGET")]
)
def test_mid_run_changes_and_time_budget_still_apply(environment, change, code):
    headers, payload, runtime, document = capture(environment)
    recorded = RecordedProvider(document)
    clock = [0]

    class Interrupting:
        def complete(self, messages, schemas, cancelled):
            reply = recorded.complete(messages, schemas, cancelled)
            if change == "time":
                clock[0] = 21
            else:
                with psycopg.connect(environment[1]) as conn:
                    if change == "stale":
                        conn.execute("UPDATE policy_versions SET published=false")
                    else:
                        conn.execute("UPDATE agent_runs SET cancelled=true WHERE status='running'")
            return reply

    before = counts(environment[1])
    result = replay(headers, payload, runtime, Interrupting(), monotonic=lambda: clock[0])
    assert result["error_code"] == code and result["output"] is None, result
    assert counts(environment[1]) == before


def test_replayed_read_loop_hits_runtime_step_budget(environment):
    _, headers, payload, runtime = initial(environment)

    class ReadLoop:
        n = 0

        def complete(self, messages, schemas, cancelled):
            self.n += 1
            return Reply(calls=[Call(str(self.n), "read_evidence", {})])

    recorder = RecordingProvider(ReadLoop(), kind="synthetic_fixture", label="step boundary")
    assert replay(headers, payload, runtime, recorder)["error_code"] == "STEP_BUDGET"
    provider = RecordedProvider(recorder.document())
    assert replay(headers, payload, runtime, provider)["error_code"] == "STEP_BUDGET"
    provider.assert_consumed()
    assert provider.consumed == 4


def test_replay_format_is_bounded_and_unused_turns_are_not_success(tmp_path):
    document = {
        "version": "runtime-recording-v1",
        "provenance": {"kind": "synthetic_fixture", "label": "unit", "synthetic_only": True},
        "turns": [
            {
                "request_sha256": request_digest([], TOOLS),
                "reply": {"text": "", "calls": [], "usage": None, "status": "completed"},
            }
        ],
    }
    provider = RecordedProvider(document)
    with pytest.raises(ProviderFailure, match="RECORDING_UNUSED_TURNS"):
        provider.assert_consumed()
    with pytest.raises(ProviderFailure, match="CANCELLED"):
        provider.complete([], TOOLS, lambda: True)
    assert provider.consumed == 0
    for messages, schemas in [
        ([], {**TOOLS, "new_tool": {}}),
        ([{"role": "user", "content": "changed"}], TOOLS),
    ]:
        with pytest.raises(ProviderFailure, match="RECORDING_MISMATCH"):
            provider.complete(messages, schemas)
    assert provider.consumed == 0
    document["turns"][0]["reply"]["text"] = "mutated by caller"
    assert provider.complete([], TOOLS).text == ""
    provider.assert_consumed()
    for invalid in [
        {**document, "unexpected": True},
        {**document, "turns": []},
        {**document, "provenance": {**document["provenance"], "synthetic_only": False}},
        {**document, "turns": document["turns"] * 9},
    ]:
        with pytest.raises(ProviderFailure, match="INVALID_RECORDING"):
            RecordedProvider(invalid)
    bad = deepcopy(document)
    bad["turns"][0]["reply"]["usage"] = {"input_tokens": 10}
    with pytest.raises(ProviderFailure, match="INVALID_RECORDING"):
        RecordedProvider(bad)
    path = tmp_path / "invalid.json"
    for content in ["{", "x" * 1_000_001]:
        path.write_text(content)
        with pytest.raises(ProviderFailure, match="INVALID_RECORDING"):
            RecordedProvider.load(path)
