"""Trusted specialist/feedback workflow; models cannot invoke these commands."""

from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from .db import runtime_connection
from .proposals import record_operation, registry, replay


def obj(fields):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": fields,
        "required": list(fields),
    }


ID = {"type": "string", "format": "uuid"}
TEXT = {"type": "string", "minLength": 1, "maxLength": 4000}
VER = {"type": "integer", "minimum": 1}
PAIR = {"case_id": ID, "work_item_id": ID}
KEY = {"operation_key": {"type": "string", "minLength": 1, "maxLength": 128}}
SCHEMAS = {
    "reserve_callback": obj(
        {
            **PAIR,
            "expected_work_version": VER,
            "contact_plan_id": ID,
            "scheduled_at": {"type": "string", "format": "date-time"},
            **KEY,
        }
    ),
    "evaluate_contact_window": obj({**PAIR, "expected_work_version": VER, **KEY}),
    "close_case": obj(
        {**PAIR, "expected_work_version": VER, "expected_case_version": VER, "reason": TEXT, **KEY}
    ),
    "open_progress_contact": obj({**PAIR, "expected_work_version": VER, **KEY}),
    "get_progress_disclosure": obj({**PAIR, "callback_contact_id": ID}),
    "record_progress_contact": obj(
        {
            **PAIR,
            "callback_contact_id": ID,
            "expected_case_version": VER,
            "expected_work_version": VER,
            "commitment_id": {"type": ["string", "null"], "format": "uuid"},
            "reviewed": {"const": True},
            **KEY,
        }
    ),
    "list_work": obj({}),
    "get_work_detail": obj(PAIR),
    "open_callback": obj({**PAIR, "expected_work_version": VER, **KEY}),
    "demo_callback_verification": obj(
        {"callback_contact_id": ID, "scenario": {"enum": ["verified", "failed"]}, **KEY}
    ),
    "prepare_feedback_review": obj(
        {
            **PAIR,
            "callback_contact_id": ID,
            "expected_result_version": VER,
            "explanation": TEXT,
            **KEY,
        }
    ),
    "approve_feedback_review": obj(
        {**PAIR, "review_id": ID, "expected_review_version": VER, **KEY}
    ),
    "get_callback_disclosure": obj({**PAIR, "callback_contact_id": ID, "review_id": ID}),
    "request_material": obj({**PAIR, "expected_case_version": VER, "question": TEXT, **KEY}),
    "record_complaint_receipt": obj(
        {
            **PAIR,
            "expected_work_version": VER,
            "outcome": {"enum": ["acknowledged", "delivery_failed"]},
            "external_receipt_ref": {
                "type": ["string", "null"],
                "pattern": "^SYN-[A-Z0-9-]{4,40}$",
            },
            "reason": {"type": ["string", "null"], "maxLength": 2000},
            **KEY,
        }
    ),
    "record_action_receipt": obj(
        {
            **PAIR,
            "action_id": ID,
            "expected_action_version": VER,
            "external_receipt_ref": {"type": "string", "pattern": "^SYN-[A-Z0-9-]{4,40}$"},
            **KEY,
        }
    ),
    "record_followup": obj(
        {
            **PAIR,
            "expected_work_version": VER,
            "state": {"enum": ["received", "unavailable", "declined", "contact_resolved"]},
            "statement": TEXT,
            "evidence_refs": {
                "type": "array",
                "maxItems": 20,
                "items": obj(
                    {
                        "kind": {"const": "transaction"},
                        "id": ID,
                        "version": {"type": "string"},
                        "section": {"type": ["string", "null"]},
                    }
                ),
            },
            "method_ref": {"type": ["string", "null"], "format": "uuid"},
            **KEY,
        }
    ),
}


def work_scope(
    conn, actor, work_id, case_id, roles=("specialist", "feedback_representative"), assigned=True
):
    from .app import as_uuid, fail

    w = conn.execute(
        """SELECT w.*,c.customer_id,c.origin_contact_id,c.status AS case_status,c.version AS case_version,c.timeline_sequence,
       c.concern_code,c.public_reference,q.name AS queue_name FROM work_items w JOIN cases c ON c.id=w.case_id
       JOIN service_queues q ON q.id=w.queue_id WHERE w.id=%s AND c.id=%s AND q.active
       AND EXISTS(SELECT 1 FROM queue_memberships m WHERE m.principal_id=%s AND m.queue_id=w.queue_id AND m.active AND m.role=ANY(%s))""",
        (as_uuid(work_id), as_uuid(case_id), actor, list(roles)),
    ).fetchone()
    if not w or (assigned and w["assignee_id"] != actor):
        fail("FORBIDDEN_OR_NOT_FOUND")
    return w


def bump_case(conn, w, now, event_type, summary, status=None):
    status = status or w["case_status"]
    version = w["case_version"] + 1
    seq = w["timeline_sequence"] + 1
    event = uuid4()
    conn.execute(
        "UPDATE cases SET version=%s,timeline_sequence=%s,status=%s,status_recorded_at=%s WHERE id=%s",
        (version, seq, status, now, w["case_id"]),
    )
    conn.execute(
        "INSERT INTO case_timeline_events VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            event,
            w["case_id"],
            seq,
            version,
            status,
            now,
            now,
            event_type,
            summary,
            "workflow:" + str(event),
        ),
    )
    conn.execute(
        "INSERT INTO outbox_events VALUES (%s,%s,%s,%s,%s,%s,'pending',NULL,0)",
        (
            event,
            "workflow:" + str(event),
            str(w["case_id"]),
            version,
            event_type,
            Jsonb({"case_id": str(w["case_id"]), "work_item_id": str(w["id"])}),
        ),
    )
    return event, version


def latest_result(conn, w):
    from .app import fail

    r = conn.execute(
        "SELECT * FROM investigation_results WHERE case_id=%s ORDER BY version DESC LIMIT 1",
        (w["case_id"],),
    ).fetchone()
    if not r:
        fail("CONFLICT")
    return r


def callback_context(conn, actor, contact_id, w):
    from .app import as_uuid, fail

    c = conn.execute(
        """SELECT c.*,x.plan_id FROM contacts c JOIN callback_contexts x ON x.contact_id=c.id
      WHERE c.id=%s AND x.work_item_id=%s AND c.actor_id=%s AND c.customer_id=%s AND c.kind='callback' AND c.status='open' """,
        (as_uuid(contact_id), w["id"], actor, w["customer_id"]),
    ).fetchone()
    if not c:
        fail("FORBIDDEN_OR_NOT_FOUND")
    return c


def proof(conn, contact, now):
    from .app import fail

    p = conn.execute(
        "SELECT * FROM verification_assertions WHERE contact_id=%s AND issuer_ref='local_synthetic_callback_adapter' AND state='verified' AND verified_at<=%s AND expires_at>%s",
        (contact["id"], now, now),
    ).fetchone()
    if not p:
        fail("AUTH_REQUIRED")
    return p


def result_refs(conn, w, refs):
    from .app import as_uuid, fail

    if len(refs) > 30:
        fail("VALIDATION_ERROR")
    for r in refs:
        if r["kind"] == "transaction":
            row = conn.execute(
                "SELECT t.version FROM card_transactions t JOIN case_transactions ct ON ct.transaction_id=t.id WHERE ct.case_id=%s AND t.id=%s",
                (w["case_id"], as_uuid(r["id"])),
            ).fetchone()
        elif r["kind"] == "case" and as_uuid(r["id"]) == str(w["case_id"]):
            row = {"version": w["case_version"]}
        else:
            fail("FORBIDDEN_OR_NOT_FOUND")
        if not row:
            fail("FORBIDDEN_OR_NOT_FOUND")
        if str(row["version"]) != r["version"]:
            fail("CONFLICT")


def detail(conn, w):
    from .app import projection

    tx = conn.execute(
        "SELECT t.* FROM card_transactions t JOIN case_transactions ct ON ct.transaction_id=t.id WHERE ct.case_id=%s ORDER BY t.id",
        (w["case_id"],),
    ).fetchall()
    result = conn.execute(
        "SELECT id,version,finding_code,approved_customer_explanation,evidence_refs FROM investigation_results WHERE case_id=%s ORDER BY version DESC LIMIT 1",
        (w["case_id"],),
    ).fetchone()
    plan = conn.execute(
        "SELECT * FROM contact_plans WHERE work_item_id=%s ORDER BY created_at DESC,id DESC LIMIT 1",
        (w["id"],),
    ).fetchone()
    intakes = conn.execute(
        "SELECT id,payload,committed_at FROM referral_intakes WHERE case_id=%s ORDER BY committed_at,id",
        (w["case_id"],),
    ).fetchall()
    followup = conn.execute(
        """SELECT e.state,e.statement,e.evidence_refs,e.recorded_at FROM followup_entries e JOIN work_items wi ON wi.id=e.work_item_id WHERE wi.case_id=%s ORDER BY e.recorded_at""",
        (w["case_id"],),
    ).fetchall()
    requests = conn.execute(
        "SELECT question,requested_at FROM evidence_requests WHERE case_id=%s ORDER BY requested_at",
        (w["case_id"],),
    ).fetchall()
    actions = conn.execute(
        "SELECT id,status,receipt_ref,version FROM required_actions WHERE case_id=%s ORDER BY id",
        (w["case_id"],),
    ).fetchall()
    return {
        "work": {
            k: w[k]
            for k in (
                "id",
                "case_id",
                "kind",
                "status",
                "version",
                "case_version",
                "queue_name",
                "assignee_id",
                "original_due_at",
                "due_at",
                "acceptance_due_at",
                "case_status",
            )
        },
        "transactions": [projection(t) for t in tx],
        "result": result,
        "plan": plan,
        "intakes": intakes,
        "material_requests": requests,
        "followup": followup,
        "required_actions": actions,
        "plans": conn.execute(
            "SELECT * FROM contact_plans WHERE work_item_id=%s ORDER BY created_at,id", (w["id"],)
        ).fetchall(),
        "attempts": conn.execute(
            "SELECT * FROM callback_attempts WHERE work_item_id=%s ORDER BY occurred_at,id",
            (w["id"],),
        ).fetchall(),
        "reservations": conn.execute(
            "SELECT * FROM contact_reservations WHERE case_id=%s ORDER BY scheduled_at",
            (w["case_id"],),
        ).fetchall(),
        "lead_decisions": conn.execute(
            "SELECT * FROM lead_review_decisions WHERE work_item_id=%s ORDER BY decided_at",
            (w["id"],),
        ).fetchall(),
        "eligible_owners": conn.execute(
            "SELECT m.principal_id AS id,m.role FROM queue_memberships m WHERE m.queue_id=%s AND m.active AND m.role IN ('feedback_representative','queue_lead')",
            (w["queue_id"],),
        ).fetchall(),
        "commitments": conn.execute(
            "SELECT id,work_item_id,status,version,proposed_update_at,customer_safe_progress,reason FROM update_commitments WHERE case_id=%s ORDER BY proposed_at,id",
            (w["case_id"],),
        ).fetchall(),
        "objections": conn.execute(
            "SELECT * FROM customer_objections WHERE case_id=%s ORDER BY created_at,id",
            (w["case_id"],),
        ).fetchall(),
        "complaints": conn.execute(
            "SELECT id,work_item_id,status,external_receipt_ref FROM complaint_intakes WHERE case_id=%s",
            (w["case_id"],),
        ).fetchall(),
        "complaint_receipts": conn.execute(
            """SELECT r.intake_id,r.intake_version,r.outcome,r.reason,r.external_receipt_ref,
            r.recorded_at,r.actor_id FROM complaint_delivery_receipts r
            JOIN complaint_intakes ci ON ci.id=r.intake_id WHERE ci.case_id=%s
            ORDER BY r.recorded_at,r.intake_version""",
            (w["case_id"],),
        ).fetchall(),
        "overdue_events": conn.execute(
            "SELECT d.* FROM due_events d JOIN work_items wi ON wi.id=d.work_item_id WHERE wi.case_id=%s ORDER BY recorded_at",
            (w["case_id"],),
        ).fetchall(),
        "contact_methods": conn.execute(
            "SELECT id,masked_ref,version FROM customer_contact_methods WHERE customer_id=%s AND active ORDER BY id",
            (w["customer_id"],),
        ).fetchall(),
        "disclosure": "Staff preparation only. Fresh callback verification and approved current review are required before disclosing details.",
    }


def command_result(key, ref, version, event, request_id):
    return {
        "data": {
            "operation_key": key,
            "status": "succeeded",
            "domain_ref": str(ref),
            "domain_version": version,
            "event_ref": str(event) if event else None,
        },
        "request_id": request_id,
    }


def dispatch_workflow(settings, name, payload, authorization, request_id, now):
    from .app import BankError, as_uuid, audit, authenticate, fail, validate

    error, result, actor = None, None, None
    try:
        with runtime_connection(settings.database_url) as conn:
            try:
                with conn.transaction():
                    session = authenticate(conn, authorization, now)
                    actor = session["principal_id"]
                    validate(SCHEMAS.get(name) or registry()[name]["input_schema"], payload)
                    if name == "list_work":
                        rows = conn.execute(
                            """SELECT w.id,w.case_id,w.kind,w.status,w.version,w.original_due_at,c.public_reference,c.concern_code,
                         q.name AS queue_name,cu.display_alias,w.assignee_id,ci.status AS delivery_status FROM work_items w JOIN cases c ON c.id=w.case_id
                         JOIN customers cu ON cu.id=c.customer_id JOIN service_queues q ON q.id=w.queue_id
                         LEFT JOIN complaint_intakes ci ON ci.work_item_id=w.id
                         WHERE q.active AND EXISTS(SELECT 1 FROM queue_memberships m WHERE m.queue_id=w.queue_id AND m.principal_id=%s AND m.active AND m.role IN ('specialist','feedback_representative','queue_lead','complaint_coordinator'))
                         ORDER BY w.original_due_at,w.id LIMIT 101""",
                            (actor,),
                        ).fetchall()
                        if len(rows) > 100:
                            fail("LIMIT_EXCEEDED")
                        result = {
                            "items": rows,
                            "notice": "Masked queue summary only; claim before details.",
                        }
                    else:
                        w = None
                        if name in ("demo_callback_verification", "capture_customer_objection"):
                            link = conn.execute(
                                "SELECT x.work_item_id,w.case_id FROM callback_contexts x JOIN work_items w ON w.id=x.work_item_id WHERE x.contact_id=%s",
                                (
                                    as_uuid(
                                        payload["contact_id"]
                                        if name == "capture_customer_objection"
                                        else payload["callback_contact_id"]
                                    ),
                                ),
                            ).fetchone()
                            if link and name == "capture_customer_objection":
                                if as_uuid(payload["case_id"]) != str(link["case_id"]):
                                    fail("FORBIDDEN_OR_NOT_FOUND")
                            elif not link and name == "capture_customer_objection":
                                # A customer may call in to dispute an outcome (ST-13).
                                from .exceptions import inbound_objection_scope

                                w = inbound_objection_scope(conn, session, payload, now)
                            elif not link:
                                fail("FORBIDDEN_OR_NOT_FOUND")
                            if link:
                                wid, cid = link["work_item_id"], link["case_id"]
                        else:
                            wid, cid = payload["work_item_id"], payload["case_id"]
                        claiming = name in ("accept_specialist_work", "claim_feedback_task")
                        lead = name in ("decide_contact_continuation", "confirm_next_update")
                        # The complaint coordinator acts for the queue; intake has no claim step.
                        coordinator = name == "record_complaint_receipt"
                        roles = (
                            ("queue_lead",)
                            if lead
                            else ("complaint_coordinator",)
                            if coordinator
                            else ("specialist",)
                            if name
                            in (
                                "accept_specialist_work",
                                "record_specialist_result",
                                "request_material",
                                "propose_next_update",
                                "record_action_receipt",
                            )
                            else ("feedback_representative",)
                            if name not in ("get_work_detail",)
                            else ("specialist", "feedback_representative", "queue_lead")
                        )
                        w = w or work_scope(
                            conn,
                            actor,
                            str(wid),
                            str(cid),
                            roles,
                            assigned=not claiming
                            and not lead
                            and not coordinator
                            and not (
                                name == "get_work_detail"
                                and conn.execute(
                                    "SELECT 1 FROM queue_memberships WHERE principal_id=%s AND role='queue_lead' AND active AND queue_id=(SELECT queue_id FROM work_items WHERE id=%s)",
                                    (actor, as_uuid(str(wid))),
                                ).fetchone()
                            ),
                        )
                        if claiming and w["assignee_id"] not in (None, actor):
                            fail("FORBIDDEN_OR_NOT_FOUND")
                        if name == "get_work_detail":
                            result = detail(conn, w)
                        elif name == "get_progress_disclosure":
                            from .progress import execute as progress

                            result = progress(conn, name, payload, w, actor, None, request_id, now)
                        elif name == "get_callback_disclosure":
                            c = callback_context(conn, actor, payload["callback_contact_id"], w)
                            proof(conn, c, now)
                            r = latest_result(conn, w)
                            review = conn.execute(
                                "SELECT * FROM feedback_reviews WHERE id=%s AND contact_id=%s AND actor_id=%s AND status='approved'",
                                (as_uuid(payload["review_id"]), c["id"], actor),
                            ).fetchone()
                            latest = conn.execute(
                                "SELECT id FROM feedback_reviews WHERE contact_id=%s ORDER BY version DESC LIMIT 1",
                                (c["id"],),
                            ).fetchone()
                            if (
                                not review
                                or latest["id"] != review["id"]
                                or review["result_id"] != r["id"]
                            ):
                                fail("CONFLICT")
                            result = {
                                "explanation": review["explanation"],
                                "result_version": r["version"],
                                "financial_execution": False,
                            }
                        else:
                            old, operation = replay(conn, actor, None, name, payload)
                            if old:
                                result = old
                            else:
                                if (
                                    payload.get("expected_case_version", w["case_version"])
                                    != w["case_version"]
                                    or payload.get("expected_work_version", w["version"])
                                    != w["version"]
                                ):
                                    fail("CONFLICT")
                                from .workflow_commands import execute

                                result = execute(
                                    conn, name, payload, w, actor, operation, request_id, now
                                )
                                record_operation(
                                    conn, actor, None, name, payload, operation, result, now
                                )
                    if name in registry():
                        validate(registry()[name]["success_schema"], result)
            except (psycopg.errors.UniqueViolation, psycopg.errors.SerializationFailure):
                error = BankError("CONFLICT")
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
