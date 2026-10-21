"""Deterministic continuation. Only trusted staff can reserve, approve or close."""

from datetime import datetime
from uuid import uuid4

from psycopg.types.json import Jsonb

from .calendar import HOLIDAYS, VERSION, ZONE, service_date
from .workflow import bump_case, command_result, latest_result

# Explicit synthetic fixture, not a statutory Canadian holiday calendar.


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def permitted_slot(value):
    local = value.astimezone(ZONE)
    return service_date(local.date(), HOLIDAYS) and 9 <= local.hour < 17


def latest_plan(conn, w):
    from .app import fail

    plan = conn.execute(
        "SELECT * FROM contact_plans WHERE work_item_id=%s ORDER BY created_at DESC,id DESC LIMIT 1",
        (w["id"],),
    ).fetchone()
    if not plan:
        fail("CONFLICT")
    return plan


def lead_review(conn, w, plan, now):
    conn.execute(
        "UPDATE contact_plans SET status='exhausted',version=version+1 WHERE id=%s AND status='active'",
        (plan["id"],),
    )
    conn.execute(
        "UPDATE work_items SET status='lead_review',version=version+1 WHERE id=%s AND status<>'lead_review'",
        (w["id"],),
    )
    conn.execute(
        "UPDATE contact_reservations SET state='cancelled',version=version+1 WHERE contact_plan_id=%s AND state='reserved'",
        (plan["id"],),
    )


def eligibility(conn, w, plan, slot, now, preparing=False):
    from .app import fail

    if w["status"] not in ("assigned", "retry_scheduled") or plan["status"] != "active":
        fail("CONFLICT")
    if slot < now or (not preparing and not permitted_slot(slot)):
        fail("VALIDATION_ERROR")
    if plan["valid_from"] and slot < plan["valid_from"]:
        fail("CONFLICT")
    if plan["valid_until"] and slot >= plan["valid_until"]:
        fail("CONFLICT")
    if (
        plan["kind"] == "initial"
        and plan["first_placed_at"] is None
        and w["original_due_at"]
        and slot >= w["original_due_at"]
    ):
        fail("CONFLICT")
    if plan["kind"] == "lead_approved" and slot not in [instant(s) for s in plan["approved_slots"]]:
        fail("CONFLICT")
    count = conn.execute(
        "SELECT count(*) AS n FROM callback_attempts WHERE contact_plan_id=%s AND counts_toward_limit",
        (plan["id"],),
    ).fetchone()["n"]
    if count >= plan["max_attempts"]:
        fail("CONFLICT")
    day = slot.astimezone(ZONE).date()
    if conn.execute(
        "SELECT 1 FROM callback_attempts WHERE case_id=%s AND service_date=%s AND counts_toward_limit",
        (w["case_id"], day),
    ).fetchone():
        fail("CONFLICT")


def execute(conn, name, p, w, actor, operation, request_id, now):
    from .app import as_uuid, fail

    if name == "close_case":
        if (
            w["kind"] != "customer_feedback"
            or w["status"] != "completed"
            or w["case_status"] == "closed"
        ):
            fail("CONFLICT")
        result = latest_result(conn, w)
        attempt = conn.execute(
            "SELECT a.id FROM callback_attempts a JOIN callback_details d ON d.attempt_id=a.id WHERE a.case_id=%s AND a.outcome='connected_verified' AND d.result_id=%s ORDER BY a.occurred_at DESC LIMIT 1",
            (w["case_id"], result["id"]),
        ).fetchone()
        if (
            not attempt
            or conn.execute(
                "SELECT 1 FROM required_actions WHERE case_id=%s AND (status<>'completed' OR receipt_ref IS NULL)",
                (w["case_id"],),
            ).fetchone()
            or conn.execute(
                "SELECT 1 FROM work_items WHERE case_id=%s AND status NOT IN ('completed','cancelled')",
                (w["case_id"],),
            ).fetchone()
        ):
            fail("CONFLICT")
        cid = uuid4()
        conn.execute(
            "INSERT INTO case_closures VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (cid, w["case_id"], result["id"], attempt["id"], actor, p["reason"], now, operation[0]),
        )
        conn.execute("UPDATE cases SET closed_at=%s WHERE id=%s", (now, w["case_id"]))
        event, version = bump_case(
            conn,
            w,
            now,
            "case.closed",
            "Human-confirmed closure after required work and verified feedback.",
            "closed",
        )
        return command_result(p["operation_key"], w["case_id"], version, event, request_id)
    if w["kind"] != "customer_feedback":
        fail("CONFLICT")
    plan = latest_plan(conn, w)
    if name == "evaluate_contact_window":
        count = conn.execute(
            "SELECT count(*) AS n FROM callback_attempts WHERE contact_plan_id=%s AND counts_toward_limit",
            (plan["id"],),
        ).fetchone()["n"]
        due = plan["valid_until"] or w["original_due_at"]
        if plan["status"] == "active" and (count >= plan["max_attempts"] or (due and now >= due)):
            lead_review(conn, w, plan, now)
            bump_case(
                conn,
                w,
                now,
                "contact.lead_review",
                "Contact limit reached; responsible queue lead review required.",
            )
        return {
            "status": "lead_review"
            if plan["status"] == "exhausted"
            or (due and now >= due)
            or count >= plan["max_attempts"]
            else w["status"],
            "original_due_at": w["original_due_at"].isoformat() if w["original_due_at"] else None,
            "plan_id": str(plan["id"]),
        }
    if name == "reserve_callback":
        if str(plan["id"]) != p["contact_plan_id"]:
            fail("CONFLICT")
        slot = instant(p["scheduled_at"])
        eligibility(conn, w, plan, slot, now)
        # Serialize plans against attempts and other reservations.
        conn.execute("UPDATE work_items SET version=version+1 WHERE id=%s", (w["id"],))
        rid = uuid4()
        conn.execute(
            "INSERT INTO contact_reservations VALUES (%s,%s,%s,%s,'reserved',1,%s)",
            (rid, w["case_id"], slot.astimezone(ZONE).date(), slot, plan["id"]),
        )
        bump_case(
            conn, w, now, "callback.reserved", "Permitted contact slot reserved; no call placed."
        )
        return {
            "reservation_id": str(rid),
            "scheduled_at": slot.isoformat(),
            "contact_plan_id": str(plan["id"]),
        }
    if name == "decide_contact_continuation":
        if (
            str(plan["id"]) != p["exhausted_plan_id"]
            or plan["status"] != "exhausted"
            or w["status"] not in ("lead_review", "review_hold")
        ):
            fail("CONFLICT")
        decision = p["decision"]
        d = decision["payload"]
        owner = as_uuid(d["owner_id"])
        if not conn.execute(
            "SELECT 1 FROM queue_memberships WHERE queue_id=%s AND principal_id=%s AND active AND role=ANY(%s)",
            (
                w["queue_id"],
                owner,
                ["feedback_representative"]
                if decision["kind"] == "new_plan"
                else ["feedback_representative", "queue_lead"],
            ),
        ).fetchone():
            fail("FORBIDDEN_OR_NOT_FOUND")
        review_at = instant(d["review_at"]) if decision["kind"] == "review_hold" else None
        if review_at and review_at <= now:
            fail("VALIDATION_ERROR")
        if decision["kind"] == "new_plan":
            start, end = instant(d["valid_from"]), instant(d["valid_until"])
            slots = [instant(s) for s in d["approved_slots"]]
            if (
                start < now
                or end <= start
                or d["max_attempts"] > len(slots)
                or len(set(s.astimezone(ZONE).date() for s in slots)) != len(slots)
                or any(s < start or s >= end or not permitted_slot(s) for s in slots)
            ):
                fail("VALIDATION_ERROR")
            for s in slots:
                if conn.execute(
                    "SELECT 1 FROM callback_attempts WHERE case_id=%s AND service_date=%s AND counts_toward_limit",
                    (w["case_id"], s.astimezone(ZONE).date()),
                ).fetchone():
                    fail("CONFLICT")
        did = uuid4()
        conn.execute(
            "INSERT INTO lead_review_decisions VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                did,
                w["case_id"],
                w["id"],
                plan["id"],
                actor,
                now,
                p["reason"],
                decision["kind"],
                owner,
                review_at,
                p["operation_key"],
                w["version"],
            ),
        )
        new_plan_id = uuid4() if decision["kind"] == "new_plan" else None
        if decision["kind"] == "new_plan":
            conn.execute(
                "INSERT INTO contact_plans VALUES (%s,%s,%s,'lead_approved','active',1,%s,%s,%s,%s,%s,%s,%s,%s,NULL,%s)",
                (
                    new_plan_id,
                    w["case_id"],
                    w["id"],
                    plan["id"],
                    did,
                    owner,
                    d["max_attempts"],
                    start,
                    end,
                    Jsonb(d["approved_slots"]),
                    VERSION,
                    now,
                ),
            )
        conn.execute(
            "UPDATE work_items SET status=%s,assignee_id=%s,version=version+1 WHERE id=%s",
            ("assigned" if decision["kind"] == "new_plan" else "review_hold", owner, w["id"]),
        )
        event, _ = bump_case(
            conn,
            w,
            now,
            "contact.continuation_approved",
            "Reasoned lead continuation recorded; original contact history retained.",
        )
        return {
            "data": {
                "decision_id": str(did),
                "receipt_ref": str(operation[0]),
                "status": "plan_approved" if new_plan_id else "review_hold",
                "new_plan_id": str(new_plan_id) if new_plan_id else None,
                "review_at": review_at.isoformat() if review_at else None,
            },
            "request_id": request_id,
        }
    fail("VALIDATION_ERROR")
