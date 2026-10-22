"""Actual runtime/DB evidence with offline providers; never a real-model result."""

from copy import deepcopy

import psycopg
import pytest
from bank_api.agent.evaluation_evidence import capture, configuration, digest, inspect_scenario
from bank_api.agent.providers import Call, FakeProvider, Reply
from bank_api.agent.selection import ProviderRoute
from bank_api.config import Settings
from conftest import NOW
from test_agent import initial


def test_capture_reads_actual_trace_and_only_a_draft(environment):
    _, h, p, runtime = initial(environment)
    e = capture(Settings(runtime), environment[1], p, h["Authorization"], "TEST-01", now=NOW)
    assert e["mode"] == "engineering_fixture"
    assert e["fresh_run"] and e["status"] == "awaiting_human"
    assert all(e["checks"].values()), e
    assert e["step_names"] == ["read_evidence", "read_rules", "draft_recommendation"]
    assert e["business_before_sha256"] == e["business_after_sha256"]
    assert e["sha256"] == digest({k: v for k, v in e.items() if k != "sha256"})
    assert e["configuration_sha256"] == digest(configuration(ProviderRoute()))
    assert h["Authorization"] not in str(e) and environment[1] not in str(e)
    assert set(e["output"]) == {"case_id", "summary", "citations", "gaps"}
    again = capture(Settings(runtime), environment[1], p, h["Authorization"], "TEST-01", now=NOW)
    assert again["run_id"] == e["run_id"] and not again["fresh_run"]


def test_failed_tool_call_is_recorded_not_invented_as_a_good_answer(environment):
    _, h, p, runtime = initial(environment)
    provider = FakeProvider([Reply(calls=[Call("x", "refund", {})])])
    e = capture(
        Settings(runtime),
        environment[1],
        p,
        h["Authorization"],
        "TEST-02",
        now=NOW,
        provider=provider,
    )
    assert e["mode"] == "engineering_fixture" and e["status"] == "failed"
    assert e["error_code"] == "TOOL_DENIED" and e["output"] is None
    assert e["checks"]["business_unchanged"] and e["checks"]["draft_only"]
    assert not e["checks"]["tool_trace"]


def test_invalid_identity_never_runs_provider_or_exports_transaction_details(environment):
    _, _, p, runtime = initial(environment)
    e = capture(Settings(runtime), environment[1], p, "Bearer invalid", "TEST-03", now=NOW)
    assert e["status"] == "rejected" and e["run_id"] is None and e["output"] is None
    assert e["checks"]["business_unchanged"] and e["checks"]["draft_only"]
    assert not e["checks"]["scope_current"]


def test_concurrent_business_write_is_detected(environment):
    _, h, p, runtime = initial(environment)

    class MutatingProvider:
        def complete(self, *args):
            with psycopg.connect(environment[1]) as conn:
                conn.execute(
                    "UPDATE card_transactions SET version=version+1 WHERE id=%s",
                    (p["transaction_ids"][0],),
                )
            return Reply(calls=[Call("read", "read_evidence", {})])

    e = capture(
        Settings(runtime),
        environment[1],
        deepcopy(p),
        h["Authorization"],
        "TEST-04",
        now=NOW,
        provider=MutatingProvider(),
    )
    assert e["status"] == "failed" and e["error_code"] in {"STALE_EVIDENCE", "CONFLICT"}
    with psycopg.connect(environment[1]) as conn:
        original = conn.execute(
            "SELECT error_code FROM agent_runs WHERE id=%s", (e["run_id"],)
        ).fetchone()[0]
    assert e["error_code"] == original
    assert not e["checks"]["business_unchanged"] and not e["checks"]["scope_current"]


def test_refuses_database_without_matching_disposable_marker(environment):
    _, h, p, runtime = initial(environment)
    with psycopg.connect(environment[1]) as conn:
        conn.execute("UPDATE demo_environment SET database_name='not-this-db'")
    try:
        with pytest.raises(ValueError, match="marked disposable"):
            capture(Settings(runtime), environment[1], p, h["Authorization"], "TEST-05", now=NOW)
    finally:
        with psycopg.connect(environment[1]) as conn:
            conn.execute("UPDATE demo_environment SET database_name=current_database()")


def test_inspect_binds_scenario_before_freeze_without_generating_answer(environment):
    _, h, p, runtime = initial(environment)
    pre = inspect_scenario(Settings(runtime), p, h["Authorization"], "TEST-06", now=NOW)
    assert pre["generated_answer"] is False
    with psycopg.connect(environment[1]) as conn:
        assert conn.execute("SELECT count(*) FROM agent_runs").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM proposals").fetchone()[0] == 0
    actual = capture(Settings(runtime), environment[1], p, h["Authorization"], "TEST-06", now=NOW)
    assert actual["evidence_sha256"] == pre["evidence_sha256"]
    assert actual["configuration_sha256"] == pre["configuration_sha256"]
