"""Trusted human transitions for specialist and shared-feedback work."""

from datetime import timedelta
from uuid import uuid4

from psycopg.types.json import Jsonb

from .calendar import VERSION, add_hours
from .callbacks import record_attempt
from .proposals import unsupported_claims
from .workflow import bump_case, callback_context, command_result, latest_result, result_refs


def execute(conn, name, p, w, actor, operation, request_id, now):
    from .app import as_uuid, fail

    if name in ("open_progress_contact", "record_progress_contact"):
        from .progress import execute as progress

        return progress(conn, name, p, w, actor, operation, request_id, now)
    if name in (
        "propose_next_update",
        "confirm_next_update",
        "capture_customer_objection",
        "register_complaint_intake",
    ):
        from .exceptions import execute as exception_command

        return exception_command(conn, name, p, w, actor, operation, request_id, now)
    if name in (
        "reserve_callback",
        "evaluate_contact_window",
        "close_case",
        "decide_contact_continuation",
    ):
        from .continuation import execute as continuation

        return continuation(conn, name, p, w, actor, operation, request_id, now)
    if name in ("accept_specialist_work", "claim_feedback_task"):
        allowed = (
            ("specialist_investigation", "specialist_rereview")
            if name == "accept_specialist_work"
            else (
                "customer_feedback",
                "contact_resolution",
                "material_followup",
                "progress_callback",
            )
        )
        if w["kind"] not in allowed or w["status"] not in ("queued", "assigned", "investigating"):
            fail("CONFLICT")
        state = "investigating" if name == "accept_specialist_work" else "assigned"
        conn.execute(
            "UPDATE work_items SET assignee_id=%s,status=%s,version=version+1 WHERE id=%s",
            (actor, state, w["id"]),
        )
        event, _ = bump_case(
            conn,
            w,
            now,
            "work.claimed",
            "Work accepted by its responsible specialist."
            if state == "investigating"
            else "Customer-service work assigned.",
            "investigating" if state == "investigating" else None,
        )
        return command_result(p["operation_key"], w["id"], w["version"] + 1, event, request_id)
    if name == "record_specialist_result":
        if w["kind"] not in ("specialist_investigation", "specialist_rereview") or w[
            "status"
        ] not in ("investigating", "awaiting_documents", "completed"):
            fail("CONFLICT")
        # A closed case reopens only through a captured customer objection (ST-13).
        if w["case_status"] == "closed":
            fail("CONFLICT")
        if (
            not p["approved_customer_explanation"].strip()
            or len(p["approved_customer_explanation"]) > 4000
            or len(p["internal_notes"] or "") > 4000
        ):
            fail("VALIDATION_ERROR")
        if unsupported_claims(p["approved_customer_explanation"]):
            fail("UNSUPPORTED_CLAIM")
        result_refs(conn, w, p["evidence_refs"])
        for action in p["required_action_statuses"]:
            existing = conn.execute(
                "SELECT * FROM required_actions WHERE id=%s AND case_id=%s",
                (as_uuid(action["action_ref"]), w["case_id"]),
            ).fetchone()
            if existing:
                if (
                    existing["status"] != action["status"]
                    or existing["receipt_ref"] != action["receipt_ref"]
                ):
                    fail("FORBIDDEN_OR_NOT_FOUND")
            else:
                if action["status"] != "pending" or action["receipt_ref"] is not None:
                    fail("FORBIDDEN_OR_NOT_FOUND")
                conn.execute(
                    "INSERT INTO required_actions VALUES (%s,%s,'external_financial_review','pending',%s,NULL,%s,1)",
                    (
                        as_uuid(action["action_ref"]),
                        w["case_id"],
                        "synthetic-action:" + action["action_ref"],
                        now,
                    ),
                )
        if p["finding"] == "further_action_required" and not p["required_action_statuses"]:
            fail("VALIDATION_ERROR")
        version = conn.execute(
            "SELECT coalesce(max(version),0)+1 AS v FROM investigation_results WHERE case_id=%s",
            (w["case_id"],),
        ).fetchone()["v"]
        rid = uuid4()
        conn.execute(
            "INSERT INTO investigation_results VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                rid,
                w["case_id"],
                w["id"],
                actor,
                version,
                p["finding"],
                Jsonb(p["evidence_refs"]),
                p["approved_customer_explanation"],
                now,
            ),
        )
        if p["internal_notes"]:
            conn.execute(
                "INSERT INTO result_private_notes VALUES (%s,%s,%s)",
                (uuid4(), rid, p["internal_notes"]),
            )
        conn.execute(
            "UPDATE work_items SET status='completed',version=version+1 WHERE id=%s", (w["id"],)
        )
        # A published finding replaces this investigation's interim progress task.
        # Preserve the old obligation/deadline rows, but do not leave unfinishable
        # work blocking closure or allow an already-open progress contact to disclose it.
        conn.execute(
            "UPDATE work_items SET status='cancelled',version=version+1 WHERE parent_work_id=%s AND kind='progress_callback' AND status NOT IN ('completed','cancelled')",
            (w["id"],),
        )
        conn.execute(
            "UPDATE update_commitments SET status='superseded',version=version+1,decided_by=coalesce(decided_by,%s),decided_at=coalesce(decided_at,%s),decision_reason=coalesce(decision_reason,'Superseded by published finding; not an approval') WHERE work_item_id=%s AND status IN ('pending_approval','approved')",
            (actor, now, w["id"]),
        )
        # The specialist decided on the available evidence. Outstanding material requests
        # are superseded, not deleted: requests and follow-up entries remain in history.
        conn.execute(
            "UPDATE work_items SET status='cancelled',version=version+1 WHERE parent_work_id=%s AND kind='material_followup' AND status NOT IN ('completed','cancelled')",
            (w["id"],),
        )
        feedback = conn.execute(
            "SELECT * FROM work_items WHERE case_id=%s AND kind='customer_feedback'",
            (w["case_id"],),
        ).fetchone()
        if feedback:
            fid = feedback["id"]
            if feedback["status"] == "completed":
                conn.execute(
                    "UPDATE contact_plans SET status='exhausted',version=version+1 WHERE work_item_id=%s AND status='completed'",
                    (fid,),
                )
            due = add_hours(now, 8)
            conn.execute(
                "UPDATE work_items SET version=version+1,due_at=coalesce(due_at,%s),original_due_at=coalesce(original_due_at,%s),status=CASE WHEN status='completed' THEN 'lead_review' WHEN status='waiting_for_result' THEN 'queued' ELSE status END WHERE id=%s",
                (due, due, fid),
            )
        else:
            from .referrals import route_config

            route = route_config(conn)
            fid = uuid4()
            due = add_hours(now, 8)
            conn.execute(
                "INSERT INTO work_items(id,case_id,kind,queue_id,status,due_at,original_due_at,calendar_ref,source_event_key,version,parent_work_id) VALUES (%s,%s,'customer_feedback',%s,'queued',%s,%s,%s,%s,1,%s)",
                (
                    fid,
                    w["case_id"],
                    route["feedback_queue_id"],
                    due,
                    due,
                    VERSION,
                    "feedback:" + str(w["case_id"]),
                    w["id"],
                ),
            )
        if not conn.execute("SELECT 1 FROM contact_plans WHERE work_item_id=%s", (fid,)).fetchone():
            conn.execute(
                "INSERT INTO contact_plans(id,case_id,work_item_id,kind,status,version,max_attempts,approved_slots,calendar_ref,created_at) VALUES (%s,%s,%s,'initial','active',1,3,'[]',%s,%s)",
                (uuid4(), w["case_id"], fid, VERSION, now),
            )
        event, _ = bump_case(
            conn,
            w,
            now,
            "result.published",
            "Specialist finding recorded; customer feedback remains outstanding.",
            "awaiting_feedback",
        )
        return command_result(p["operation_key"], rid, version, event, request_id)
    if name == "open_callback":
        if w["kind"] != "customer_feedback" or w["status"] not in ("assigned", "retry_scheduled"):
            fail("CONFLICT")
        plan = conn.execute(
            "SELECT * FROM contact_plans WHERE work_item_id=%s AND status='active'", (w["id"],)
        ).fetchone()
        if not plan or (plan["valid_until"] and now >= plan["valid_until"]):
            fail("CONFLICT")
        gaps = conn.execute(
            "SELECT 1 FROM work_items WHERE case_id=%s AND kind='contact_resolution' AND status<>'completed'",
            (w["case_id"],),
        ).fetchone()
        if gaps:
            fail("CONTACT_GAP")
        from .continuation import eligibility

        eligibility(conn, w, plan, now, now, preparing=True)
        cid = uuid4()
        conn.execute(
            "INSERT INTO contacts(id,customer_id,actor_id,kind,status,opened_at,version) VALUES (%s,%s,%s,'callback','open',%s,1)",
            (cid, w["customer_id"], actor, now),
        )
        conn.execute("INSERT INTO callback_contexts VALUES (%s,%s,%s)", (cid, w["id"], plan["id"]))
        conn.execute(
            "INSERT INTO verification_assertions VALUES (%s,%s,'local_synthetic_callback_adapter','unverified',%s,%s,%s)",
            (uuid4(), cid, now, now, Jsonb({"case_id": str(w["case_id"])})),
        )
        return {
            "contact_id": str(cid),
            "plan_id": str(plan["id"]),
            "verification": "unverified",
            "notice": "Synthetic callback context only; no phone call placed.",
        }
    if name == "demo_callback_verification":
        c = callback_context(conn, actor, p["callback_contact_id"], w)
        conn.execute(
            "UPDATE verification_assertions SET state=%s,verified_at=%s,expires_at=%s WHERE contact_id=%s AND issuer_ref='local_synthetic_callback_adapter'",
            (
                "verified" if p["scenario"] == "verified" else "unverified",
                now,
                now + timedelta(minutes=10) if p["scenario"] == "verified" else now,
                c["id"],
            ),
        )
        return {
            "verification": p["scenario"],
            "notice": "Synthetic identity adapter; not production verification.",
        }
    if name == "prepare_feedback_review":
        c = callback_context(conn, actor, p["callback_contact_id"], w)
        r = latest_result(conn, w)
        if p["expected_result_version"] != r["version"]:
            fail("CONFLICT")
        if unsupported_claims(p["explanation"]):
            fail("UNSUPPORTED_CLAIM")
        version = conn.execute(
            "SELECT coalesce(max(version),0)+1 AS v FROM feedback_reviews WHERE contact_id=%s",
            (c["id"],),
        ).fetchone()["v"]
        rid = uuid4()
        conn.execute(
            "INSERT INTO feedback_reviews VALUES (%s,%s,%s,%s,%s,%s,'draft',%s,%s,%s)",
            (rid, c["id"], w["id"], r["id"], r["version"], p["explanation"], version, actor, now),
        )
        return {
            "review_id": str(rid),
            "version": version,
            "status": "draft",
            "explanation": p["explanation"],
        }
    if name == "approve_feedback_review":
        r = latest_result(conn, w)
        review = conn.execute(
            "SELECT * FROM feedback_reviews WHERE id=%s AND work_item_id=%s AND actor_id=%s",
            (as_uuid(p["review_id"]), w["id"], actor),
        ).fetchone()
        latest = (
            conn.execute(
                "SELECT id FROM feedback_reviews WHERE contact_id=%s ORDER BY version DESC LIMIT 1",
                (review["contact_id"],),
            ).fetchone()
            if review
            else None
        )
        if (
            not review
            or latest["id"] != review["id"]
            or review["status"] != "draft"
            or review["version"] != p["expected_review_version"]
            or review["result_id"] != r["id"]
        ):
            fail("CONFLICT")
        callback_context(conn, actor, str(review["contact_id"]), w)
        conn.execute(
            "UPDATE feedback_reviews SET status='approved',version=version+1 WHERE id=%s",
            (review["id"],),
        )
        return {
            "review_id": str(review["id"]),
            "version": review["version"] + 1,
            "status": "approved",
            "notice": "Staff approval only; customer disclosure still requires fresh callback verification.",
        }
    if name == "record_callback_attempt":
        return record_attempt(conn, p, w, actor, request_id, now)
    if name in ("record_complaint_receipt", "record_action_receipt"):
        from .receipts import execute as receipt

        return receipt(conn, name, p, w, actor, request_id, now)
    if name == "request_material":
        if w["kind"] not in ("specialist_investigation", "specialist_rereview") or w[
            "status"
        ] not in ("investigating", "awaiting_documents"):
            fail("CONFLICT")
        from .referrals import route_config

        route = route_config(conn)
        rid, fid = uuid4(), uuid4()
        conn.execute(
            "INSERT INTO work_items(id,case_id,kind,queue_id,status,due_at,original_due_at,calendar_ref,source_event_key,version,parent_work_id) VALUES (%s,%s,'material_followup',%s,'queued',%s,%s,%s,%s,1,%s)",
            (
                fid,
                w["case_id"],
                route["feedback_queue_id"],
                w["due_at"],
                w["original_due_at"],
                w["calendar_ref"],
                "material:" + str(rid),
                w["id"],
            ),
        )
        conn.execute(
            "INSERT INTO evidence_requests VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (rid, w["case_id"], w["id"], fid, p["question"], actor, now),
        )
        conn.execute(
            "UPDATE work_items SET status='awaiting_documents',version=version+1 WHERE id=%s",
            (w["id"],),
        )
        event, _ = bump_case(
            conn,
            w,
            now,
            "material.requested",
            "Specialist requested supplementary information through customer service; original deadline retained.",
        )
        return command_result(p["operation_key"], fid, 1, event, request_id)
    if name == "record_followup":
        if (
            w["kind"] not in ("material_followup", "contact_resolution")
            or w["status"] != "assigned"
        ):
            fail("CONFLICT")
        result_refs(conn, w, p["evidence_refs"])
        if p["state"] == "contact_resolved":
            if w["kind"] != "contact_resolution" or not p["method_ref"]:
                fail("VALIDATION_ERROR")
            if not conn.execute(
                "SELECT 1 FROM customer_contact_methods WHERE id=%s AND customer_id=%s AND active",
                (as_uuid(p["method_ref"]), w["customer_id"]),
            ).fetchone():
                fail("FORBIDDEN_OR_NOT_FOUND")
        elif p["method_ref"] is not None:
            fail("VALIDATION_ERROR")
        # Material follow-up ends with the customer's answer (received, unavailable or
        # declined); the specialist then decides. An unreachable contact stays owned.
        resolved = w["kind"] == "material_followup" or p["state"] == "contact_resolved"
        if w["kind"] == "contact_resolution" and p["state"] == "received":
            fail("VALIDATION_ERROR")
        eid = uuid4()
        conn.execute(
            "INSERT INTO followup_entries VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                eid,
                w["id"],
                actor,
                now,
                p["state"],
                p["statement"],
                Jsonb(p["evidence_refs"]),
                p["method_ref"],
                operation[0],
            ),
        )
        conn.execute(
            "UPDATE work_items SET status=%s,version=version+1 WHERE id=%s",
            ("completed" if resolved else "assigned", w["id"]),
        )
        if w["kind"] == "material_followup":
            conn.execute(
                """UPDATE work_items SET status='investigating',version=version+1 WHERE id=%s AND status='awaiting_documents'
                AND NOT EXISTS(SELECT 1 FROM work_items m WHERE m.parent_work_id=%s AND m.kind='material_followup' AND m.status NOT IN ('completed','cancelled'))""",
                (w["parent_work_id"], w["parent_work_id"]),
            )
        event, _ = bump_case(
            conn,
            w,
            now,
            "followup.recorded",
            "Customer-service follow-up recorded; original investigation deadline retained.",
        )
        return command_result(p["operation_key"], eid, 1, event, request_id)
    fail("VALIDATION_ERROR")
