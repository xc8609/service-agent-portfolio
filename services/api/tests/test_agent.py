from datetime import timedelta
from uuid import uuid4

import psycopg
import pytest
from bank_api.agent.providers import Call, FakeProvider, ProviderFailure, Reply
from bank_api.agent.runtime import run
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from test_continuation import verified_callback
from test_referrals import prepare
from test_workflow import setup_feedback


def initial(environment):
    client, admin, runtime, _ = environment
    h, c = session(client)
    prepare(client, h, c)
    p = {
        "contact_id": c,
        "case_id": None,
        "work_item_id": None,
        "transaction_ids": [uid("tx_equal_1"), uid("tx_equal_2")],
        "trigger_key": str(uuid4()),
    }
    return client, h, p, runtime


def test_agent_creates_only_draft_and_replays_persisted_run_after_restart(environment):
    client, h, p, runtime = initial(environment)
    r = client.post("/v1/assistant/run", headers=h, json=p)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "awaiting_human", data
    assert data["output"]["proposal_id"] and data["usage"] is None
    facts, remainder = data["output"]["summary"].split("\n\nTo confirm\n")
    uncertain, next_step = remainder.split("\n\nNext step\n")
    assert facts.startswith("Facts\nTwo posted entries")
    assert "customer statement, not an adjudicated outcome" in facts
    assert "do not establish a duplicate" in uncertain
    assert "existing enquiry rather than submit a duplicate" in next_step
    again = run(Settings(runtime), p, h["Authorization"], "restart", NOW)
    assert again == data
    with psycopg.connect(environment[1]) as c:
        assert c.execute("SELECT count(*) FROM agent_steps").fetchone()[0] == 3
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM proposals").fetchone()[0] == 1
        assert "Two posted entries" not in str(
            c.execute("SELECT safe_result FROM agent_steps").fetchall()
        )


@pytest.mark.parametrize(
    "provider,code",
    [
        (FakeProvider([Reply(calls=[Call("x", "refund", {})])]), "TOOL_DENIED"),
        (FakeProvider([Reply(calls=[Call("read_evidence", "read_rules", {})])]), "TOOL_ORDER"),
        (FakeProvider([ProviderFailure("TIMEOUT")]), "TIMEOUT"),
        (
            FakeProvider([Reply(calls=[Call("x", "read_evidence", {"widen_scope": True})])]),
            "INVALID_TOOL_ARGUMENTS",
        ),
        (
            FakeProvider([Reply(calls=[Call(str(i), "read_evidence", {})]) for i in range(4)]),
            "STEP_BUDGET",
        ),
    ],
)
def test_agent_failure_preserves_manual_work(environment, provider, code):
    _, h, p, runtime = initial(environment)
    r = run(Settings(runtime), p, h["Authorization"], "negative", NOW, provider)
    assert r["status"] == "failed" and r["error_code"] == code, r
    with psycopg.connect(environment[1]) as c:
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM proposals").fetchone()[0] == 0


def test_agent_rechecks_current_authority_and_source_versions(environment):
    client, h, p, runtime = initial(environment)
    r = run(Settings(runtime), p, h["Authorization"], "first", NOW)
    with psycopg.connect(environment[1]) as c:
        c.execute(
            "UPDATE card_transactions SET version=version+1 WHERE id=%s", (uid("tx_equal_1"),)
        )
    assert (
        client.post("/v1/assistant/get_run", headers=h, json={"run_id": r["run_id"]}).status_code
        == 409
    )
    assert client.post("/v1/assistant/run", headers=h, json=p).status_code == 409


def test_assigned_feedback_run_excludes_private_notes_and_rehydrates_current_result(environment):
    client, admin, runtime, _ = environment
    _, _, h, w, _ = setup_feedback(client)
    p = {
        "contact_id": None,
        "case_id": w["case_id"],
        "work_item_id": w["id"],
        "transaction_ids": [],
        "trigger_key": str(uuid4()),
    }
    r = run(Settings(runtime), p, h["Authorization"], "feedback", NOW)
    assert r["status"] == "awaiting_human", r
    assert "PRIVATE" not in str(r)
    assert r["output"]["proposal_id"] is None
    facts, remainder = r["output"]["summary"].split("\n\nTo confirm\n")
    assert facts.startswith("Facts\nApproved customer explanation:")
    assert "identity verification" in remainder
    assert "\n\nNext step\n" in remainder
    other, _ = session(client, "feedback_other")
    assert client.post("/v1/assistant/run", headers=other, json=p).status_code == 404
    assert (
        client.post(
            "/v1/assistant/get_run", headers=other, json={"run_id": r["run_id"]}
        ).status_code
        == 404
    )


def test_completed_feedback_summary_does_not_suggest_another_callback_or_infer_closure(environment):
    client, h, p, runtime = initial(environment)
    _, _, fh, w, opened = setup_feedback(client)
    verified_callback(client, fh, w, opened)
    inbound = client.post("/v1/assistant/run", headers=h, json=p).json()
    assert inbound["status"] == "awaiting_human", inbound
    assert "feedback delivered; case remains open" in inbound["output"]["summary"]
    assert "awaiting_feedback" not in inbound["output"]["summary"]
    feedback = run(
        Settings(runtime),
        {
            "contact_id": None,
            "case_id": w["case_id"],
            "work_item_id": w["id"],
            "transaction_ids": [],
            "trigger_key": str(uuid4()),
        },
        fh["Authorization"],
        "delivered-feedback",
        NOW,
    )
    assert feedback["status"] == "awaiting_human", feedback
    summary = feedback["output"]["summary"]
    assert "Feedback delivery is recorded" in summary
    assert "closure checklist" in summary
    assert "record the actual callback outcome" not in summary


def test_interrupted_run_is_detected_without_duplicate_effect(environment):
    client, h, p, runtime = initial(environment)
    r = run(Settings(runtime), p, h["Authorization"], "first", NOW)
    with psycopg.connect(environment[1]) as c:
        c.execute(
            "UPDATE agent_runs SET status='running',output=NULL,lease_until=%s WHERE id=%s",
            (NOW - timedelta(seconds=1), r["run_id"]),
        )
    resumed = run(Settings(runtime), p, h["Authorization"], "resume", NOW)
    assert resumed["status"] == "interrupted"
    with psycopg.connect(environment[1]) as c:
        assert c.execute("SELECT count(*) FROM proposals").fetchone()[0] == 1


def test_cancellation_and_wall_time_budget_leave_no_draft(environment):
    _, h, p, runtime = initial(environment)

    class Cancelling:
        def complete(self, messages, schemas, cancelled):
            with psycopg.connect(environment[1]) as c:
                c.execute("UPDATE agent_runs SET cancelled=true")
            return Reply(calls=[Call("x", "read_evidence", {})])

    r = run(Settings(runtime), p, h["Authorization"], "cancel", NOW, Cancelling())
    assert r["status"] == "cancelled" and r["output"] is None
    p["trigger_key"] = str(uuid4())
    ticks = iter([0, 21, 22])
    r = run(
        Settings(runtime),
        p,
        h["Authorization"],
        "budget",
        NOW,
        FakeProvider([]),
        lambda: next(ticks),
    )
    assert r["error_code"] == "TIME_BUDGET"


def test_provider_cannot_invent_citations_or_read_then_widen_scope(environment):
    _, h, p, runtime = initial(environment)
    fake = FakeProvider(
        [
            Reply(calls=[Call("1", "read_evidence", {})]),
            Reply(calls=[Call("2", "read_rules", {})]),
            Reply(
                calls=[
                    Call(
                        "3",
                        "draft_recommendation",
                        {
                            "summary": "This needs manual review.",
                            "citations": ["invented-source"],
                            "gaps": [],
                        },
                    )
                ]
            ),
        ]
    )
    r = run(Settings(runtime), p, h["Authorization"], "citations", NOW, fake)
    assert r["error_code"] == "UNSUPPORTED_CITATION"


def test_allowlisted_business_event_replay_is_scoped(environment):
    client, admin, runtime, _ = environment
    _, _, h, w, _ = setup_feedback(client)
    with psycopg.connect(admin) as c:
        event = c.execute(
            "SELECT id FROM outbox_events WHERE aggregate_ref=%s AND event_type='result.published'",
            (w["case_id"],),
        ).fetchone()[0]
    p = {
        "contact_id": None,
        "case_id": w["case_id"],
        "work_item_id": w["id"],
        "transaction_ids": [],
        "trigger_key": "event:" + str(event),
    }
    r = run(Settings(runtime), p, h["Authorization"], "event", NOW)
    assert r["status"] == "awaiting_human"
    assert run(Settings(runtime), p, h["Authorization"], "duplicate", NOW) == r
    p["trigger_key"] = "event:" + str(uuid4())
    assert client.post("/v1/assistant/run", headers=h, json=p).status_code == 404
