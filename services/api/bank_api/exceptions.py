"""Trusted exception handling; uncertainty and complaints remain explicit."""

from uuid import uuid4

from psycopg.types.json import Jsonb

from .calendar import VERSION, add_hours
from .continuation import instant
from .proposals import unsupported_claims
from .workflow import bump_case, callback_context, command_result, proof, result_refs


def complaint(conn, w, objection, actor, now):
    from .app import fail
    from .referrals import route_config

    old = conn.execute(
        "SELECT * FROM complaint_intakes WHERE objection_id=%s", (objection["id"],)
    ).fetchone()
    if old:
        return old
    if not objection["complaint_requested"]:
        fail("CONFLICT")
    route = route_config(conn)
    queue = route.get("complaint_queue_id")
    if (
        not queue
        or not conn.execute(
            "SELECT 1 FROM service_queues WHERE id=%s AND active", (queue,)
        ).fetchone()
    ):
        fail("CONFLICT")
    wid, iid = uuid4(), uuid4()
    conn.execute(
        "INSERT INTO work_items(id,case_id,kind,queue_id,status,calendar_ref,source_event_key,version,parent_work_id) VALUES (%s,%s,'complaint_intake',%s,'queued',%s,%s,1,%s)",
        (wid, w["case_id"], queue, VERSION, "complaint:" + str(objection["id"]), w["id"]),
    )
    conn.execute(
        "INSERT INTO objection_work_links VALUES (%s,%s,%s,'complaint_intake',%s)",
        (uuid4(), objection["id"], wid, now),
    )
    conn.execute(
        "INSERT INTO complaint_intakes VALUES (%s,%s,%s,%s,%s,%s,%s,'recorded',NULL,NULL,1)",
        (iid, w["case_id"], objection["id"], wid, queue, actor, now),
    )
    return conn.execute("SELECT * FROM complaint_intakes WHERE id=%s", (iid,)).fetchone()


def execute(conn, name, p, w, actor, operation, request_id, now):
    from .app import as_uuid, fail

    if name in ("propose_next_update", "confirm_next_update"):
        if w["kind"] not in ("specialist_investigation", "specialist_rereview") or w[
            "status"
        ] not in ("investigating", "awaiting_documents"):
            fail("CONFLICT")
        if not w["original_due_at"] or now < w["original_due_at"]:
            fail("CONFLICT")
        if name == "propose_next_update":
            update = instant(p["proposed_update_at"])
            if update <= now or len(p["customer_safe_progress"]) > 4000 or len(p["reason"]) > 4000:
                fail("VALIDATION_ERROR")
            if unsupported_claims(p["customer_safe_progress"]):
                fail("UNSUPPORTED_CLAIM")
            cid = uuid4()
            conn.execute(
                "INSERT INTO update_commitments(id,case_id,work_item_id,proposed_by,proposed_at,proposed_update_at,customer_safe_progress,reason,status,version,operation_key) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pending_approval',1,%s)",
                (
                    cid,
                    w["case_id"],
                    w["id"],
                    actor,
                    now,
                    update,
                    p["customer_safe_progress"],
                    p["reason"],
                    p["operation_key"],
                ),
            )
            bump_case(
                conn,
                w,
                now,
                "commitment.proposed",
                "Specialist proposed next update; lead approval required.",
            )
            return {
                "data": {"commitment_id": str(cid), "version": 1, "status": "pending_approval"},
                "request_id": request_id,
            }
        c = conn.execute(
            "SELECT * FROM update_commitments WHERE id=%s AND work_item_id=%s",
            (as_uuid(p["commitment_id"]), w["id"]),
        ).fetchone()
        if (
            not c
            or c["status"] != "pending_approval"
            or c["version"] != p["expected_commitment_version"]
            or c["proposed_update_at"] <= now
        ):
            fail("CONFLICT")
        status = "approved" if p["decision"] == "approve" else "rejected"
        if status == "approved":
            conn.execute(
                "UPDATE update_commitments SET status='superseded',version=version+1 WHERE work_item_id=%s AND status='approved'",
                (w["id"],),
            )
        conn.execute(
            "UPDATE update_commitments SET status=%s,version=version+1,decided_by=%s,decided_at=%s,decision_reason=%s WHERE id=%s",
            (status, actor, now, p["reason"], c["id"]),
        )
        bump_case(
            conn,
            w,
            now,
            "commitment.decided",
            "Lead decision recorded; original overdue deadline retained.",
        )
        return {
            "data": {
                "commitment_id": str(c["id"]),
                "version": c["version"] + 1,
                "status": status,
                "approved_update_at": c["proposed_update_at"].isoformat()
                if status == "approved"
                else None,
            },
            "request_id": request_id,
        }
    if name == "capture_customer_objection":
        if w["kind"] != "customer_feedback" or w["case_status"] == "closed":
            fail("CONFLICT")
        contact = callback_context(conn, actor, p["contact_id"], w)
        proof(conn, contact, now)
        if len(p["customer_statement"]) > 4000 or not p["customer_statement"].strip():
            fail("VALIDATION_ERROR")
        for ref in p["evidence_refs"]:
            if ref["kind"] == "transaction":
                tx = conn.execute(
                    "SELECT t.id,t.version FROM card_transactions t JOIN card_accounts a ON a.id=t.account_id WHERE t.id=%s AND a.customer_id=%s",
                    (as_uuid(ref["id"]), w["customer_id"]),
                ).fetchone()
                if not tx:
                    fail("FORBIDDEN_OR_NOT_FOUND")
                if str(tx["version"]) != ref["version"]:
                    fail("CONFLICT")
                conn.execute(
                    "INSERT INTO case_transactions VALUES (%s,%s,%s) ON CONFLICT(case_id,transaction_id) DO NOTHING",
                    (uuid4(), w["case_id"], tx["id"]),
                )
            else:
                result_refs(conn, w, [ref])
        oid, rid = uuid4(), uuid4()
        conn.execute(
            "INSERT INTO customer_objections VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                oid,
                w["case_id"],
                contact["id"],
                p["customer_statement"],
                Jsonb(p["evidence_refs"]),
                p["complaint_requested"],
                now,
            ),
        )
        from .referrals import route_config

        route = route_config(conn)
        conn.execute(
            "INSERT INTO work_items(id,case_id,kind,queue_id,status,due_at,original_due_at,calendar_ref,source_event_key,version,parent_work_id,acceptance_due_at) VALUES (%s,%s,'specialist_rereview',%s,'queued',%s,%s,%s,%s,1,%s,%s)",
            (
                rid,
                w["case_id"],
                route["queue_id"],
                add_hours(now, 16),
                add_hours(now, 16),
                VERSION,
                "objection:" + str(oid),
                w["id"],
                add_hours(now, 8),
            ),
        )
        conn.execute(
            "INSERT INTO objection_work_links VALUES (%s,%s,%s,'specialist_rereview',%s)",
            (uuid4(), oid, rid, now),
        )
        if p["complaint_requested"]:
            complaint(conn, w, {"id": oid, "complaint_requested": True}, actor, now)
        event, _ = bump_case(
            conn,
            w,
            now,
            "objection.captured",
            "Customer disagreement recorded for independent re-review; complaint request tracked separately.",
            "under_review",
        )
        return command_result(p["operation_key"], oid, 1, event, request_id)
    if name == "register_complaint_intake":
        objection = conn.execute(
            "SELECT * FROM customer_objections WHERE id=%s AND case_id=%s",
            (as_uuid(p["objection_id"]), w["case_id"]),
        ).fetchone()
        if not objection:
            fail("FORBIDDEN_OR_NOT_FOUND")
        row = complaint(conn, w, objection, actor, now)
        return {
            "data": {
                "intake_id": str(row["id"]),
                "work_item_id": str(row["work_item_id"]),
                "queue_id": str(row["queue_id"]),
                "status": row["status"],
                "external_receipt_ref": row["external_receipt_ref"],
            },
            "request_id": request_id,
        }
    fail("VALIDATION_ERROR")
