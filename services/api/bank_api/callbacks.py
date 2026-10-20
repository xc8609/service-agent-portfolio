"""Actual callback outcomes and independently verified customer disclosure."""

from datetime import timedelta
from uuid import uuid4

from .calendar import VERSION, ZONE, contact_window
from .workflow import bump_case, callback_context, command_result, latest_result, proof


def record_attempt(conn, p, w, actor, request_id, now):
    from datetime import datetime

    from .app import as_uuid, fail

    if w["kind"] != "customer_feedback" or w["status"] not in ("assigned", "retry_scheduled"):
        fail("CONFLICT")
    c = callback_context(conn, actor, p["callback_contact_id"], w)
    plan = conn.execute(
        "SELECT * FROM contact_plans WHERE id=%s AND work_item_id=%s",
        (as_uuid(p["contact_plan_id"]), w["id"]),
    ).fetchone()
    if not plan or plan["id"] != c["plan_id"]:
        fail("FORBIDDEN_OR_NOT_FOUND")
    actual = datetime.fromisoformat(p["actual_attempt_at"].replace("Z", "+00:00"))
    if actual > now + timedelta(seconds=30) or actual < c["opened_at"]:
        fail("VALIDATION_ERROR")
    if p["reservation_id"] is not None:
        fail("VALIDATION_ERROR")
    pairs = {
        "not_placed": {"technical_failure"},
        "placed": {"no_answer", "technical_failure"},
        "connected": {
            "connected_verified",
            "verification_failed",
            "customer_declined",
            "technical_failure",
        },
    }
    if p["outcome"] not in pairs[p["dial_state"]]:
        fail("VALIDATION_ERROR")
    verified = None
    review = None
    result = None
    if p["outcome"] == "connected_verified":
        verified = proof(conn, c, now)
        result = latest_result(conn, w)
        review = conn.execute(
            "SELECT * FROM feedback_reviews WHERE contact_id=%s AND actor_id=%s ORDER BY version DESC LIMIT 1",
            (c["id"], actor),
        ).fetchone()
        if not review or review["status"] != "approved" or review["result_id"] != result["id"]:
            fail("CONFLICT")
    counted = p["dial_state"] != "not_placed"
    aid = uuid4()
    localdate = actual.astimezone(ZONE).date()
    conn.execute(
        """INSERT INTO callback_attempts(id,case_id,work_item_id,contact_id,actor_id,occurred_at,service_date,dial_state,outcome,counts_toward_limit,rule_version,operation_key,contact_plan_id,reservation_id)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)""",
        (
            aid,
            w["case_id"],
            w["id"],
            c["id"],
            actor,
            actual,
            localdate,
            p["dial_state"],
            p["outcome"],
            counted,
            VERSION,
            p["operation_key"],
            plan["id"],
        ),
    )
    conn.execute(
        "INSERT INTO callback_details VALUES (%s,%s,%s,%s,%s)",
        (
            aid,
            result["id"] if result else None,
            review["id"] if review else None,
            p["customer_response"],
            verified["id"] if verified else None,
        ),
    )
    end = plan["valid_until"]
    if counted and plan["first_placed_at"] is None:
        end = contact_window(actual)
        conn.execute(
            "UPDATE contact_plans SET first_placed_at=%s,valid_from=%s,valid_until=%s,version=version+1 WHERE id=%s",
            (actual, actual, end, plan["id"]),
        )
    count = conn.execute(
        "SELECT count(*) AS n FROM callback_attempts WHERE contact_plan_id=%s AND counts_toward_limit",
        (plan["id"],),
    ).fetchone()["n"]
    status = (
        "completed"
        if verified
        else "lead_review"
        if count >= plan["max_attempts"] or (end and now >= end)
        else "retry_scheduled"
    )
    if not counted and not end:
        status = "assigned"
    conn.execute("UPDATE work_items SET status=%s,version=version+1 WHERE id=%s", (status, w["id"]))
    if status in ("completed", "lead_review"):
        conn.execute(
            "UPDATE contact_plans SET status=%s,version=version+1 WHERE id=%s",
            ("completed" if verified else "exhausted", plan["id"]),
        )
    event, _ = bump_case(
        conn,
        w,
        now,
        "callback.recorded",
        "Verified customer feedback recorded; closure requires separate checks."
        if verified
        else "Customer contact outcome recorded; feedback remains outstanding.",
    )
    return command_result(p["operation_key"], aid, 1, event, request_id)
