"""Synthetic external receipts. The application records what another system reports;
it never delivers a complaint or executes a financial action itself."""

from .workflow import bump_case, command_result


def execute(conn, name, p, w, actor, request_id, now):
    from .app import as_uuid, fail

    if name == "record_complaint_receipt":
        if w["kind"] != "complaint_intake":
            fail("CONFLICT")
        intake = conn.execute(
            "SELECT * FROM complaint_intakes WHERE work_item_id=%s", (w["id"],)
        ).fetchone()
        # ST-23: only a delivery the worker actually requested can be acknowledged or fail.
        if not intake or intake["status"] != "pending_delivery":
            fail("CONFLICT")
        if p["outcome"] == "acknowledged":
            if not p["external_receipt_ref"] or p["reason"] is not None:
                fail("VALIDATION_ERROR")
            conn.execute(
                "UPDATE complaint_intakes SET status='acknowledged',external_receipt_ref=%s,acknowledged_at=%s,version=version+1 WHERE id=%s",
                (p["external_receipt_ref"], now, intake["id"]),
            )
            # Intake is done; the complaint continues under the external reference.
            conn.execute(
                "UPDATE work_items SET status='completed',assignee_id=%s,version=version+1 WHERE id=%s",
                (actor, w["id"]),
            )
            summary = "Complaint intake acknowledged by the complaint unit; handled under its own reference."
        else:
            if p["external_receipt_ref"] is not None or not (p["reason"] or "").strip():
                fail("VALIDATION_ERROR")
            conn.execute(
                "UPDATE complaint_intakes SET status='delivery_failed',version=version+1 WHERE id=%s",
                (intake["id"],),
            )
            conn.execute("UPDATE work_items SET version=version+1 WHERE id=%s", (w["id"],))
            summary = "Complaint delivery failed; the request is retained and will be retried."
        event, _ = bump_case(conn, w, now, "complaint." + p["outcome"], summary)
        return command_result(
            p["operation_key"], intake["id"], intake["version"] + 1, event, request_id
        )
    if w["kind"] not in ("specialist_investigation", "specialist_rereview"):
        fail("CONFLICT")
    action = conn.execute(
        "SELECT * FROM required_actions WHERE id=%s AND case_id=%s",
        (as_uuid(p["action_id"]), w["case_id"]),
    ).fetchone()
    if not action:
        fail("FORBIDDEN_OR_NOT_FOUND")
    if action["status"] != "pending" or action["version"] != p["expected_action_version"]:
        fail("CONFLICT")
    conn.execute(
        "UPDATE required_actions SET status='completed',receipt_ref=%s,updated_at=%s,version=version+1 WHERE id=%s",
        (p["external_receipt_ref"], now, action["id"]),
    )
    event, _ = bump_case(
        conn,
        w,
        now,
        "action.receipt_recorded",
        "External system reported the required action complete; no action was executed here.",
    )
    return command_result(
        p["operation_key"], action["id"], action["version"] + 1, event, request_id
    )
