"""Scoped, customer-safe case progress shared by manual UI and the read tool."""

import psycopg

from .db import runtime_connection


def read_case(conn, case_id, contact, cards):
    from .app import as_uuid, fail, source

    case = conn.execute(
        """SELECT c.*,q.name AS queue_name,q.active AS queue_active FROM cases c
        JOIN service_queues q ON q.id=c.owner_queue_id WHERE c.id=%s AND c.customer_id=%s""",
        (as_uuid(case_id), contact["customer_id"]),
    ).fetchone()
    if not case:
        fail("FORBIDDEN_OR_NOT_FOUND")
    links = conn.execute(
        """SELECT t.id,t.account_id FROM case_transactions ct
        JOIN card_transactions t ON t.id=ct.transaction_id WHERE ct.case_id=%s""",
        (case["id"],),
    ).fetchall()
    if not links or any(r["account_id"] not in {c["id"] for c in cards} for r in links):
        fail("FORBIDDEN_OR_NOT_FOUND")
    events = conn.execute(
        "SELECT * FROM case_timeline_events WHERE case_id=%s ORDER BY aggregate_sequence LIMIT 201",
        (case["id"],),
    ).fetchall()
    if len(events) > 200:
        fail("LIMIT_EXCEEDED")
    if (
        not events
        or [e["aggregate_sequence"] for e in events] != list(range(1, len(events) + 1))
        or events[-1]["aggregate_sequence"] != case["timeline_sequence"]
        or events[-1]["case_version"] != case["version"]
        or events[-1]["case_status"] != case["status"]
        or events[-1]["recorded_at"] != case["status_recorded_at"]
    ):
        fail("STALE_VERSION")
    work = conn.execute(
        """SELECT w.*,q.name AS queue_name,q.active AS queue_active,
        p.subject_ref AS assignee_name,p.active AS assignee_active
        FROM work_items w JOIN service_queues q ON q.id=w.queue_id
        LEFT JOIN staff_principals p ON p.id=w.assignee_id WHERE w.case_id=%s ORDER BY w.id""",
        (case["id"],),
    ).fetchall()
    primary = [w for w in work if w["kind"] == "specialist_investigation"]
    feedback = [w for w in work if w["kind"] == "customer_feedback"]
    if len(primary) > 1 or len(feedback) > 1:
        fail("STALE_VERSION")
    commitments = conn.execute(
        """SELECT id,version,status,proposed_update_at,customer_safe_progress
        FROM update_commitments WHERE case_id=%s
        AND status IN ('approved','superseded','missed') ORDER BY proposed_at,id""",
        (case["id"],),
    ).fetchall()
    actions = conn.execute(
        "SELECT * FROM required_actions WHERE case_id=%s ORDER BY updated_at,id", (case["id"],)
    ).fetchall()
    result = conn.execute(
        """SELECT id,version,approved_customer_explanation FROM investigation_results
        WHERE case_id=%s ORDER BY version DESC LIMIT 1""",
        (case["id"],),
    ).fetchone()
    objection_links = conn.execute(
        """SELECT l.work_item_id,l.objection_id FROM objection_work_links l
        JOIN work_items w ON w.id=l.work_item_id WHERE w.case_id=%s""",
        (case["id"],),
    ).fetchall()
    snapshot = {
        "case_id": str(case["id"]),
        "case_version": str(case["version"]),
        "investigation_status": primary[0]["status"] if primary else "not_recorded",
        "feedback_status": feedback[0]["status"] if feedback else "not_recorded",
        "case_status": case["status"],
        "owner_queue": str(case["owner_queue_id"]),
        "assignee_ref": str(primary[0]["assignee_id"])
        if primary and primary[0]["assignee_id"]
        else None,
        "approved_customer_explanation": result["approved_customer_explanation"]
        if result
        else None,
        "required_actions": [
            {"action_ref": str(a["id"]), "status": a["status"], "receipt_ref": a["receipt_ref"]}
            for a in actions
        ],
        "unresolved_items": [a["action_kind"] for a in actions if a["status"] != "completed"],
        "timeline": [
            {
                "event_id": str(e["id"]),
                "sequence": e["aggregate_sequence"],
                "occurred_at": e["occurred_at"].isoformat(),
                "recorded_at": e["recorded_at"].isoformat(),
                "event_type": e["event_type"],
                "customer_safe_summary": e["customer_safe_summary"],
                "source_ref": source("case", case["id"], e["case_version"], e["source_ref"]),
            }
            for e in events
        ],
        "progress_commitments": [
            {
                "id": str(c["id"]),
                "version": c["version"],
                "status": c["status"],
                "approved_update_at": c["proposed_update_at"].isoformat(),
                "customer_safe_progress": c["customer_safe_progress"],
            }
            for c in commitments
        ],
        "linked_work": [
            {
                "work_item_id": str(w["id"]),
                "kind": w["kind"],
                "status": w["status"],
                "owner_queue": str(w["queue_id"]),
                "source_objection_id": next(
                    (
                        str(o["objection_id"])
                        for o in objection_links
                        if o["work_item_id"] == w["id"]
                    ),
                    None,
                ),
            }
            for w in work
            if w["kind"]
            in ("specialist_rereview", "complaint_intake", "progress_callback", "lead_review")
        ],
        # Outbound contact-plan projection is not part of the inbound increment.
        "contact_plan": None,
    }
    provenance = [source("case", case["id"], case["version"])]
    provenance += [source("work_item", w["id"], w["version"]) for w in work]
    provenance += [source("commitment", c["id"], c["version"]) for c in commitments]
    if result:
        provenance.append(source("result", result["id"], result["version"]))
    details = {
        "sources": provenance,
        "reference": case["public_reference"] or str(case["id"]),
        "concern": case["concern"],
        "concern_code": case["concern_code"],
        "status_as_of": case["status_recorded_at"].isoformat(),
        "owner_queue_name": case["queue_name"],
        "owner_queue_active": case["queue_active"],
        "work_items": [
            {
                "id": str(w["id"]),
                "version": str(w["version"]),
                "kind": w["kind"],
                "status": w["status"],
                "queue_name": w["queue_name"],
                "queue_active": w["queue_active"],
                "assignee_name": w["assignee_name"],
                "assignee_active": w["assignee_active"],
                "original_due_at": w["original_due_at"].isoformat()
                if w["original_due_at"]
                else None,
                "due_at": w["due_at"].isoformat() if w["due_at"] else None,
            }
            for w in work
        ],
        "snapshot": snapshot,
    }
    return details, [str(r["id"]) for r in links]


def dispatch_cases(settings, name, payload, authorization, request_id, now):
    from .app import TOOLS, BankError, as_uuid, audit, authenticate, fail, scope, validate

    error, result, actor = None, None, None
    try:
        with runtime_connection(settings.database_url) as conn:
            try:
                session = authenticate(conn, authorization, now)
                actor = session["principal_id"]
                validate(
                    TOOLS[
                        "get_case_snapshot"
                        if name == "get_case_snapshot"
                        else "get_transaction_evidence"
                    ]["input_schema"],
                    payload,
                )
                contact, cards = scope(conn, session, payload["contact_id"], now)
                if name == "get_case_snapshot":
                    if payload["expected_work_version"] is not None:
                        fail("VALIDATION_ERROR")
                    details, _ = read_case(conn, payload["case_id"], contact, cards)
                    result = {
                        "data": details["snapshot"],
                        "meta": {
                            "as_of": now.isoformat(),
                            "scope_ref": str(contact["id"]),
                            "sources": details["sources"],
                        },
                    }
                    validate(TOOLS["get_case_snapshot"]["success_schema"], result)
                else:
                    ids = [as_uuid(i) for i in payload["transaction_ids"]]
                    selected = conn.execute(
                        "SELECT id FROM card_transactions WHERE id=ANY(%s::uuid[]) AND account_id=ANY(%s::uuid[])",
                        (ids, [c["id"] for c in cards]),
                    ).fetchall()
                    if len(ids) != len(set(ids)):
                        fail("VALIDATION_ERROR")
                    if len(selected) != len(ids):
                        fail("FORBIDDEN_OR_NOT_FOUND")
                    related = conn.execute(
                        "SELECT DISTINCT case_id FROM case_transactions WHERE transaction_id=ANY(%s::uuid[]) ORDER BY case_id LIMIT 51",
                        (ids,),
                    ).fetchall()
                    if len(related) > 50:
                        fail("LIMIT_EXCEEDED")
                    entries = []
                    for row in related:
                        details, linked_ids = read_case(conn, str(row["case_id"]), contact, cards)
                        full = set(ids).issubset(linked_ids)
                        details["matched_transaction_ids"] = sorted(set(ids) & set(linked_ids))
                        details["coverage"] = "full_selection" if full else "partial_selection"
                        details["review_hint"] = (
                            "review_closed_case"
                            if details["snapshot"]["case_status"] == "closed"
                            else "potential_existing_enquiry"
                            if full
                            and details["concern_code"] == "duplicate_charge"
                            and details["snapshot"]["case_status"]
                            in ("open", "investigating", "awaiting_feedback")
                            else "review_overlap_and_concern"
                        )
                        validate(
                            TOOLS["get_case_snapshot"]["success_schema"],
                            {
                                "data": details["snapshot"],
                                "meta": {
                                    "as_of": now.isoformat(),
                                    "scope_ref": str(contact["id"]),
                                    "sources": [],
                                },
                            },
                        )
                        entries.append(details)
                    result = {
                        "cases": entries,
                        "as_of": now.isoformat(),
                        "review_state": "review_existing_work"
                        if entries
                        else "no_linked_case_found",
                    }
            except BankError as exc:
                error = exc
            audit(conn, actor, name, error.code if error else "allowed", request_id, now)
    except psycopg.errors.QueryCanceled:
        fail("TIMEOUT")
    except (psycopg.Error, RuntimeError):
        fail("DEPENDENCY_UNAVAILABLE")
    if error:
        raise error
    return result
