"""Authored synthetic case progress, never real bank records."""

from datetime import UTC, datetime, timedelta


def seed_cases(conn):
    from .fixtures import insert, uid

    base = datetime(2026, 10, 19, 14, tzinfo=UTC)
    for key, name in [
        ("specialist_queue", "Demo card investigations"),
        ("feedback_queue", "Demo customer feedback"),
        ("complaint_queue", "Demo complaint review"),
    ]:
        insert(
            conn,
            "service_queues",
            {"id": uid(key), "name": name, "kind": key.removesuffix("_queue"), "active": True},
        )
    for key in ["Demo specialist Alex", "Demo callback Sam", "Demo complaint Casey"]:
        insert(conn, "staff_principals", {"id": uid(key), "subject_ref": key, "active": True})
    for key, customer, txs, status, concern, code, ref in [
        (
            "duplicate_case",
            "customer_a",
            ["equal_1", "equal_2"],
            "investigating",
            "Customer reports one purchase and two posted entries; mapping unresolved.",
            "duplicate_charge",
            "DEMO-CASE-001",
        ),
        (
            "closed_case",
            "customer_a",
            ["reversed"],
            "closed",
            "Previous parking charge enquiry; customer feedback recorded.",
            "charge_query",
            "DEMO-CASE-002",
        ),
        (
            "private_case",
            "customer_b",
            ["private"],
            "investigating",
            "Other customer confidential enquiry",
            "duplicate_charge",
            "DEMO-CASE-PRIVATE",
        ),
    ]:
        insert(
            conn,
            "cases",
            {
                "id": uid(key),
                "customer_id": uid(customer),
                "origin_contact_id": uid("contact_a" if customer == "customer_a" else "contact_b"),
                "owner_queue_id": uid("specialist_queue"),
                "status": status,
                "concern": concern,
                "created_at": base,
                "closed_at": base + timedelta(hours=3) if status == "closed" else None,
                "version": 2,
                "public_reference": ref,
                "concern_code": code,
                "status_recorded_at": base + timedelta(hours=3),
                "timeline_sequence": 2,
            },
        )
        for tx in txs:
            insert(
                conn,
                "case_transactions",
                {"id": uid(key + "_" + tx), "case_id": uid(key), "transaction_id": uid("tx_" + tx)},
            )
        for seq, occurred, recorded, summary in [
            (
                1,
                base,
                base + timedelta(hours=2),
                "Enquiry received and linked to the selected transactions.",
            ),
            (
                2,
                base + timedelta(hours=1),
                base + timedelta(hours=3),
                "Recorded investigation update; no completion date approved."
                if status != "closed"
                else "Case closed after recorded feedback. This does not establish merchant refund execution.",
            ),
        ]:
            insert(
                conn,
                "case_timeline_events",
                {
                    "id": uid(key + "_event_" + str(seq)),
                    "case_id": uid(key),
                    "aggregate_sequence": seq,
                    "case_version": seq,
                    "case_status": "open" if seq == 1 else status,
                    "occurred_at": occurred,
                    "recorded_at": recorded,
                    "event_type": "received" if seq == 1 else "status_recorded",
                    "customer_safe_summary": summary,
                    "source_ref": "synthetic-case-v1:" + key + ":" + str(seq),
                },
            )
    for key, kind, queue, assignee, status, parent in [
        (
            "investigation_work",
            "specialist_investigation",
            "specialist_queue",
            "Demo specialist Alex",
            "awaiting_documents",
            None,
        ),
        ("feedback_work", "customer_feedback", "feedback_queue", None, "waiting_for_result", None),
        (
            "rereview_work",
            "specialist_rereview",
            "specialist_queue",
            "Demo specialist Alex",
            "completed",
            "investigation_work",
        ),
        (
            "complaint_work",
            "complaint_intake",
            "complaint_queue",
            "Demo complaint Casey",
            "in_progress",
            "investigation_work",
        ),
    ]:
        insert(
            conn,
            "work_items",
            {
                "id": uid(key),
                "case_id": uid("duplicate_case"),
                "kind": kind,
                "queue_id": uid(queue),
                "assignee_id": uid(assignee) if assignee else None,
                "status": status,
                "due_at": base + timedelta(days=2) if kind == "specialist_investigation" else None,
                "original_due_at": base + timedelta(days=2)
                if kind == "specialist_investigation"
                else None,
                "calendar_ref": "synthetic-calendar-v1",
                "source_event_key": "synthetic-case-v1:" + key,
                "version": 1,
                "parent_work_id": uid(parent) if parent else None,
            },
        )
    insert(
        conn,
        "required_actions",
        {
            "id": uid("receipt_request"),
            "case_id": uid("duplicate_case"),
            "action_kind": "Customer service to request purchase receipt if available; investigation continues.",
            "status": "pending",
            "external_ref": "synthetic-case-v1:receipt-request",
            "receipt_ref": None,
            "updated_at": base + timedelta(hours=3),
            "version": 1,
        },
    )
    insert(
        conn,
        "update_commitments",
        {
            "id": uid("pending_commitment"),
            "case_id": uid("duplicate_case"),
            "work_item_id": uid("investigation_work"),
            "proposed_by": uid("Demo specialist Alex"),
            "proposed_at": base,
            "proposed_update_at": base + timedelta(days=1),
            "customer_safe_progress": "UNAPPROVED PRIVATE UPDATE",
            "reason": "INTERNAL PENDING REASON",
            "status": "pending_approval",
            "version": 1,
            "operation_key": "synthetic-pending-update",
        },
    )
