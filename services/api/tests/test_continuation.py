from datetime import datetime, timedelta
from uuid import uuid4

import psycopg
from bank_api.app import create_app
from bank_api.calendar import ZONE, contact_window
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient
from test_workflow import attempt, call, detail, pair, review, setup_feedback


def test_holiday_dst_and_boundary_calendar():
    assert (
        contact_window(datetime(2026, 10, 9, 16, 59, tzinfo=ZONE)).isoformat()
        == "2026-10-14T17:00:00-05:00"
    )
    assert (
        contact_window(datetime(2026, 10, 30, 16, 59, tzinfo=ZONE), ()).isoformat()
        == "2026-11-03T17:00:00-06:00"
    )
    assert (
        contact_window(datetime(2026, 10, 19, 9, tzinfo=ZONE)).isoformat()
        == "2026-10-21T17:00:00-05:00"
    )


def test_one_reserved_date_and_actual_duplicate_retained(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    d = detail(client, h, w)
    p = {
        **pair(w),
        "expected_work_version": d["work"]["version"],
        "contact_plan_id": opened["plan_id"],
        "scheduled_at": NOW.isoformat(),
        "operation_key": str(uuid4()),
    }
    reserved = call(client, h, "reserve_callback", p)
    assert reserved.status_code == 200, reserved.text
    assert call(client, h, "reserve_callback", p).json() == reserved.json()
    p.update(
        expected_work_version=detail(client, h, w)["work"]["version"], operation_key=str(uuid4())
    )
    assert call(client, h, "reserve_callback", p).status_code == 409
    # Two contexts opened before the first actual result: later duplicate must be audited.
    other = call(
        client,
        h,
        "open_callback",
        {
            **pair(w),
            "expected_work_version": detail(client, h, w)["work"]["version"],
            "operation_key": str(uuid4()),
        },
    ).json()
    first = attempt(client, h, w, opened)
    first["reservation_id"] = reserved.json()["reservation_id"]
    assert call(client, h, "record_callback_attempt", first).status_code == 200
    assert (
        call(
            client,
            h,
            "open_callback",
            {
                **pair(w),
                "expected_work_version": detail(client, h, w)["work"]["version"],
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 409
    )
    actual = call(client, h, "record_callback_attempt", attempt(client, h, w, other))
    assert actual.status_code == 200, actual.text
    assert detail(client, h, w)["work"]["status"] == "lead_review"
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM callback_attempts").fetchone()[0] == 2
        assert c.execute("SELECT reasons FROM callback_anomalies").fetchone()[0] == [
            "multiple_calls_same_date"
        ]


def exercise_contact_continuation(environment):
    client, admin, runtime, _ = environment
    _, _, h, w, opened = setup_feedback(client)
    original = detail(client, h, w)["work"]["original_due_at"]
    assert (
        call(client, h, "record_callback_attempt", attempt(client, h, w, opened)).status_code == 200
    )
    end = datetime.fromisoformat(detail(client, h, w)["plan"]["valid_until"])
    with TestClient(create_app(Settings(runtime), clock=lambda: end)) as later:
        h, _ = session(later, "feedback_unclaimed")
        d = detail(later, h, w)
        expired = call(
            later,
            h,
            "evaluate_contact_window",
            {
                **pair(w),
                "expected_work_version": d["work"]["version"],
                "operation_key": str(uuid4()),
            },
        )
        assert expired.status_code == 200, expired.text
        assert detail(later, h, w)["work"]["status"] == "lead_review"
        lead, _ = session(later, "lead")
        d = detail(later, lead, w)
        p = {
            **pair(w),
            "expected_case_version": d["work"]["case_version"],
            "expected_work_version": d["work"]["version"],
            "operation_key": str(uuid4()),
            "exhausted_plan_id": opened["plan_id"],
            "reason": "Customer unavailable; lead review required.",
            "decision": {
                "kind": "review_hold",
                "payload": {
                    "owner_id": uid("lead"),
                    "review_at": (end + timedelta(days=1)).isoformat(),
                },
            },
        }
        r = later.post("/v1/commands/decide_contact_continuation", headers=lead, json=p)
        assert r.status_code == 200, r.text
        assert (
            later.post("/v1/commands/decide_contact_continuation", headers=lead, json=p).json()
            == r.json()
        )
        d = detail(later, lead, w)
        slot = datetime.combine(
            (end + timedelta(days=1)).astimezone(ZONE).date(), datetime.min.time(), ZONE
        ) + timedelta(hours=10)
        p.update(
            expected_case_version=d["work"]["case_version"],
            expected_work_version=d["work"]["version"],
            operation_key=str(uuid4()),
            decision={
                "kind": "new_plan",
                "payload": {
                    "owner_id": uid("feedback"),
                    "valid_from": slot.isoformat(),
                    "valid_until": (slot + timedelta(hours=2)).isoformat(),
                    "max_attempts": 1,
                    "approved_slots": [slot.isoformat()],
                },
            },
        )
        assert (
            later.post("/v1/commands/decide_contact_continuation", headers=h, json=p).status_code
            == 404
        )
        r = later.post("/v1/commands/decide_contact_continuation", headers=lead, json=p)
        assert r.status_code == 200, r.text
        d = detail(later, h, w)
        assert len(d["plans"]) == 2 and len(d["attempts"]) == 1 and len(d["lead_decisions"]) == 2
        assert d["work"]["original_due_at"] == original
        assert d["plan"]["max_attempts"] == 1
        # No access outside the newly approved slot/window.
        assert (
            call(
                later,
                h,
                "open_callback",
                {
                    **pair(w),
                    "expected_work_version": d["work"]["version"],
                    "operation_key": str(uuid4()),
                },
            ).status_code
            == 409
        )


def test_window_expires_then_lead_hold_and_bounded_new_plan(environment):
    exercise_contact_continuation(environment)


def test_closure_denies_pending_work_then_requires_current_verified_result(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    review(client, h, w, opened["contact_id"])
    call(
        client,
        h,
        "demo_callback_verification",
        {
            "callback_contact_id": opened["contact_id"],
            "scenario": "verified",
            "operation_key": str(uuid4()),
        },
    )
    assert (
        call(
            client,
            h,
            "record_callback_attempt",
            attempt(client, h, w, opened, "connected_verified", "connected"),
        ).status_code
        == 200
    )

    def close():
        d = detail(client, h, w)
        return call(
            client,
            h,
            "close_case",
            {
                **pair(w),
                "expected_case_version": d["work"]["case_version"],
                "expected_work_version": d["work"]["version"],
                "reason": "All required work checked and feedback delivered.",
                "operation_key": str(uuid4()),
            },
        )

    assert close().status_code == 409
    # Test setup only: simulate independent required-work completion, not a runtime financial command.
    with psycopg.connect(admin) as c:
        c.execute("UPDATE work_items SET status='completed' WHERE case_id=%s", (w["case_id"],))
        c.execute(
            "UPDATE required_actions SET status='completed',receipt_ref='synthetic-independent-receipt' WHERE case_id=%s",
            (w["case_id"],),
        )
    r = close()
    assert r.status_code == 200, r.text
    with psycopg.connect(admin) as c:
        assert (
            c.execute("SELECT closed_at FROM cases WHERE id=%s", (w["case_id"],)).fetchone()[0]
            == NOW
        )
        assert c.execute("SELECT count(*) FROM case_closures").fetchone()[0] == 1


def test_three_daily_attempts_exhaust_without_closing(environment):
    client, admin, runtime, _ = environment
    _, _, h, w, opened = setup_feedback(client)
    assert (
        call(client, h, "record_callback_attempt", attempt(client, h, w, opened)).status_code == 200
    )
    for day in (1, 2):
        now = NOW + timedelta(days=day)
        with TestClient(create_app(Settings(runtime), clock=lambda: now)) as later:
            h, _ = session(later, "feedback_unclaimed")
            d = detail(later, h, w)
            opened = call(
                later,
                h,
                "open_callback",
                {
                    **pair(w),
                    "expected_work_version": d["work"]["version"],
                    "operation_key": str(uuid4()),
                },
            ).json()
            p = attempt(later, h, w, opened)
            p["actual_attempt_at"] = now.isoformat()
            r = call(later, h, "record_callback_attempt", p)
            assert r.status_code == 200, r.text
            d = detail(later, h, w)
            assert len(d["attempts"]) == day + 1
            if day == 2:
                assert d["work"]["status"] == "lead_review" and d["plan"]["status"] == "exhausted"
                assert (
                    call(
                        later,
                        h,
                        "open_callback",
                        {
                            **pair(w),
                            "expected_work_version": d["work"]["version"],
                            "operation_key": str(uuid4()),
                        },
                    ).status_code
                    == 409
                )
    with psycopg.connect(admin) as c:
        assert (
            c.execute("SELECT closed_at FROM cases WHERE id=%s", (w["case_id"],)).fetchone()[0]
            is None
        )
