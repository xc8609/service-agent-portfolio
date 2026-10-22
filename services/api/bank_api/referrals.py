"""Trusted synthetic enquiry intake. No financial adjudication or outbound calls."""

from uuid import uuid4

from psycopg.types.json import Jsonb

from .calendar import VERSION, add_hours


def route_config(conn):
    from .app import fail

    row = conn.execute("""SELECT r.*,q.name AS queue_name,f.name AS feedback_name FROM service_routes r
      JOIN service_queues q ON q.id=r.queue_id JOIN service_queues f ON f.id=r.feedback_queue_id
      JOIN staff_principals p ON p.id=r.lead_id WHERE r.concern_code='duplicate_charge'
      AND r.active AND q.active AND q.kind='specialist' AND f.active AND f.kind='feedback' AND p.active""").fetchone()
    if not row:
        fail("DEPENDENCY_UNAVAILABLE")
    return row


def pair_context(conn, contact, cards, ids):
    from .app import as_uuid, fail, recorded_relationships, source
    from .case_lookup import read_case
    from .policy_lookup import permitted

    ids = sorted(as_uuid(x) for x in ids)
    if len(ids) != 2 or len(set(ids)) != 2:
        fail("VALIDATION_ERROR")
    txs = conn.execute(
        "SELECT * FROM card_transactions WHERE id=ANY(%s::uuid[]) AND account_id=ANY(%s::uuid[]) ORDER BY id",
        (ids, [c["id"] for c in cards]),
    ).fetchall()
    if len(txs) != 2:
        fail("FORBIDDEN_OR_NOT_FOUND")
    if len({r["account_id"] for r in txs}) != 1 or any(r["status"] != "posted" for r in txs):
        fail("VALIDATION_ERROR")
    report = conn.execute(
        "SELECT * FROM investigation_revisions WHERE contact_id=%s ORDER BY revision DESC LIMIT 1",
        (contact["id"],),
    ).fetchone()
    if not report or report["recognition"] not in ("one_purchase_unresolved", "specific_entry"):
        fail("VALIDATION_ERROR")
    if {r["id"]: r["version"] for r in report["transaction_versions"]} != {
        str(t["id"]): str(t["version"]) for t in txs
    }:
        fail("CONFLICT")
    rows = conn.execute(
        "SELECT DISTINCT case_id FROM case_transactions WHERE transaction_id=ANY(%s::uuid[]) ORDER BY case_id LIMIT 51",
        (ids,),
    ).fetchall()
    if len(rows) > 50:
        fail("LIMIT_EXCEEDED")
    cases = []
    for row in rows:
        detail, linked = read_case(conn, str(row["case_id"]), contact, cards)
        cases.append(
            {
                "case_id": str(row["case_id"]),
                "version": detail["snapshot"]["case_version"],
                "status": detail["snapshot"]["case_status"],
                "reference": detail["reference"],
                "concern_code": detail["concern_code"],
                "owner_queue_name": detail["owner_queue_name"],
                "same_issue": set(ids).issubset(linked)
                and detail["concern_code"] == "duplicate_charge"
                and detail["snapshot"]["case_status"] != "closed",
                "work_items": detail["work_items"],
            }
        )
    account = next(c for c in cards if c["id"] == txs[0]["account_id"])
    permitted_rules = permitted(conn, contact, cards)
    if len(permitted_rules) > 100:
        fail("LIMIT_EXCEEDED")
    rules = [
        r
        for r in permitted_rules
        if r["product"] == account["product"] and r["jurisdiction"] == account["jurisdiction"]
    ]
    # Exact applicable posted-pair section; uncertainty never invents a policy.
    rules = [r for r in rules if r["transaction_pattern"] == "two_posted"]
    refs = [source("contact", contact["id"], contact["version"])] + [
        source("transaction", r["id"], r["version"]) for r in txs
    ]
    refs += [source("case", c["case_id"], c["version"]) for c in cases]
    refs += [source("policy", r["id"], r["version"], r["section"]) for r in rules]
    return {
        "transactions": txs,
        "relationships": recorded_relationships(conn, ids),
        "report": report,
        "cases": cases,
        "rules": rules,
        "refs": refs,
        "route": route_config(conn),
    }


def prepare(conn, contact, cards, ids):
    from .proposals import snapshot_hash

    context = pair_context(conn, contact, cards, ids)
    report = context["report"]
    route = context["route"]
    existing = next((c for c in context["cases"] if c["same_issue"]), None)
    method = conn.execute(
        "SELECT * FROM customer_contact_methods WHERE customer_id=%s AND active ORDER BY id LIMIT 1",
        (contact["customer_id"],),
    ).fetchone()
    payload = {
        "transaction_ids": sorted(ids),
        "concern": report["statement"],
        "checked_facts": context["refs"],
        "missing_evidence": ["Relationship between the posted entries has not been established."],
        "requested_review": "Investigate whether the additional entry is a separate valid purchase or requires correction.",
        "queue_id": str(route["queue_id"]),
        "related_case_id": existing["case_id"] if existing else None,
        "intake": {
            "statement_revision": report["revision"],
            "recognition": report["recognition"],
            "recognized_transaction_id": str(report["recognized_transaction_id"])
            if report["recognized_transaction_id"]
            else None,
            "clarifications": {
                field: {"state": "unknown", "value": None}
                for field in ("purchase_date", "purchase_count", "purchase_amount", "prior_contact")
            },
            "material_gaps": [],
            "contact": {
                "state": "available" if method else "unknown",
                "method_ref": str(method["id"]) if method else None,
                "method_version": method["version"] if method else None,
                "reason": None
                if method
                else "Contact method not available; customer service must resolve.",
            },
            "mode": "link_existing" if existing else "new",
            "distinct_work_reason": None,
            "customer_summary_confirmed": False,
            "route_version": route["version"],
            "route_basis": "applicable_policy"
            if len(context["rules"]) == 1
            else "manual_policy_review",
        },
    }
    return {
        "payload": payload,
        "source_refs": context["refs"],
        "context_version": str(contact["version"]),
        "queue_name": route["queue_name"],
        "feedback_queue_name": route["feedback_name"],
        "contact_mask": method["masked_ref"] if method else None,
        "existing_cases": context["cases"],
        "policy_state": "applicable" if len(context["rules"]) == 1 else "manual_review_required",
        "snapshot": snapshot_hash(context),
    }


def validate_referral(conn, contact, cards, payload, refs, committing=False):
    from .app import as_uuid, fail

    context = pair_context(conn, contact, cards, payload["transaction_ids"])
    report = context["report"]
    intake = payload["intake"]
    route = context["route"]
    if refs != context["refs"] or payload["checked_facts"] != refs:
        fail("CONFLICT")
    if (
        str(route["queue_id"]) != as_uuid(payload["queue_id"])
        or route["version"] != intake["route_version"]
    ):
        fail("CONFLICT")
    if (
        intake["statement_revision"] != report["revision"]
        or intake["recognition"] != report["recognition"]
        or intake["recognized_transaction_id"]
        != (
            str(report["recognized_transaction_id"])
            if report["recognized_transaction_id"]
            else None
        )
    ):
        fail("CONFLICT")
    if (
        not payload["concern"].strip()
        or not payload["requested_review"].strip()
        or max(len(payload["concern"]), len(payload["requested_review"])) > 2000
    ):
        fail("VALIDATION_ERROR")
    if not intake["customer_summary_confirmed"] and committing:
        fail("VALIDATION_ERROR")
    for entry in intake["clarifications"].values():
        if (entry["state"] == "answered") != bool(entry["value"] and entry["value"].strip()):
            fail("VALIDATION_ERROR")
    if intake["route_basis"] != (
        "applicable_policy" if len(context["rules"]) == 1 else "manual_policy_review"
    ):
        fail("CONFLICT")
    contact_method = intake["contact"]
    if contact_method["state"] == "available":
        method = (
            conn.execute(
                "SELECT * FROM customer_contact_methods WHERE id=%s AND customer_id=%s AND active",
                (as_uuid(contact_method["method_ref"]), contact["customer_id"]),
            ).fetchone()
            if contact_method["method_ref"]
            else None
        )
        if not method:
            fail("FORBIDDEN_OR_NOT_FOUND")
        if method["version"] != contact_method["method_version"]:
            fail("CONFLICT")
    elif (
        contact_method["method_ref"] is not None
        or contact_method["method_version"] is not None
        or not (contact_method["reason"] or "").strip()
    ):
        fail("VALIDATION_ERROR")
    active = [c for c in context["cases"] if c["same_issue"]]
    related = payload["related_case_id"]
    if intake["mode"] == "link_existing":
        if related not in [c["case_id"] for c in active]:
            fail("VALIDATION_ERROR")
        case = next(c for c in active if c["case_id"] == related)
        if not any(
            w["kind"] == "specialist_investigation"
            and w["status"] not in ("completed", "cancelled")
            for w in case["work_items"]
        ):
            fail("CONFLICT")
    elif active:
        if (
            related not in [c["case_id"] for c in active]
            or not (intake["distinct_work_reason"] or "").strip()
        ):
            fail("DUPLICATE_REVIEW_REQUIRED")
    elif related is not None and related not in [c["case_id"] for c in context["cases"]]:
        fail("FORBIDDEN_OR_NOT_FOUND")
    return context


def commit(conn, contact, cards, proposal, actor, operation_id, now):
    from .app import fail

    payload = proposal["payload"]
    # Updating an aggregate guard serializes competing distinct keys under REPEATABLE READ.
    key = str(contact["customer_id"]) + ":" + ":".join(sorted(payload["transaction_ids"]))
    conn.execute(
        "INSERT INTO referral_pair_guards VALUES (%s,1) ON CONFLICT (pair_key) DO UPDATE SET revision=referral_pair_guards.revision+1",
        (key,),
    )
    context = validate_referral(
        conn, contact, cards, payload, proposal["source_versions"], committing=True
    )
    route = context["route"]
    intake = payload["intake"]
    iid, event = uuid4(), uuid4()
    if intake["mode"] == "link_existing":
        case_id = payload["related_case_id"]
        case = next(c for c in context["cases"] if c["case_id"] == case_id)
        work = next(
            w
            for w in case["work_items"]
            if w["kind"] == "specialist_investigation"
            and w["status"] not in ("completed", "cancelled")
        )
        work_id = work["id"]
        version = int(case["version"])
        disposition = "linked_existing"
        due = work["original_due_at"]
    else:
        case_id, work_id = uuid4(), uuid4()
        version = 1
        disposition = "queued"
        due = add_hours(now, 16)
        conn.execute(
            """INSERT INTO cases(id,customer_id,origin_contact_id,owner_queue_id,status,concern,created_at,version,public_reference,concern_code,status_recorded_at,timeline_sequence)
          VALUES (%s,%s,%s,%s,'open',%s,%s,1,%s,'duplicate_charge',%s,1)""",
            (
                case_id,
                contact["customer_id"],
                contact["id"],
                route["queue_id"],
                payload["concern"],
                now,
                "DEMO-" + str(case_id)[:8].upper(),
                now,
            ),
        )
        for tid in payload["transaction_ids"]:
            conn.execute("INSERT INTO case_transactions VALUES (%s,%s,%s)", (uuid4(), case_id, tid))
        conn.execute(
            """INSERT INTO work_items(id,case_id,kind,queue_id,status,due_at,original_due_at,calendar_ref,source_event_key,version,acceptance_due_at)
          VALUES (%s,%s,'specialist_investigation',%s,'queued',%s,%s,%s,%s,1,%s)""",
            (
                work_id,
                case_id,
                route["queue_id"],
                due,
                due,
                VERSION,
                "referral:" + str(proposal["id"]),
                add_hours(now, 8),
            ),
        )
        conn.execute(
            "INSERT INTO case_timeline_events VALUES (%s,%s,1,1,'open',%s,%s,'enquiry.queued','Enquiry queued for specialist investigation; not yet accepted.',%s)",
            (uuid4(), case_id, now, now, "referral:" + str(proposal["id"])),
        )
    if not due:
        fail("CONFLICT")
    if intake["contact"]["state"] != "available":
        conn.execute(
            """INSERT INTO work_items(id,case_id,kind,queue_id,status,due_at,original_due_at,calendar_ref,source_event_key,version,parent_work_id)
          VALUES (%s,%s,'contact_resolution',%s,'queued',%s,%s,%s,%s,1,%s)""",
            (
                uuid4(),
                case_id,
                route["feedback_queue_id"],
                due,
                due,
                VERSION,
                "contact-gap:" + str(proposal["id"]),
                work_id,
            ),
        )
    conn.execute(
        "INSERT INTO referral_intakes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            iid,
            proposal["id"],
            case_id,
            work_id,
            contact["id"],
            Jsonb(payload),
            Jsonb(proposal["source_versions"]),
            actor,
            now,
            operation_id,
            disposition,
        ),
    )
    conn.execute(
        "INSERT INTO outbox_events VALUES (%s,%s,%s,%s,'referral.reviewed',%s,'pending',NULL,0)",
        (
            event,
            "referral:" + str(iid),
            str(case_id),
            version,
            Jsonb(
                {
                    "intake_id": str(iid),
                    "case_id": str(case_id),
                    "work_item_id": str(work_id),
                    "disposition": disposition,
                }
            ),
        ),
    )
    return {"domain_ref": str(case_id), "domain_version": version, "event_ref": str(event)}
