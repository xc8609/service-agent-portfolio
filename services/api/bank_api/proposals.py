"""Versioned human-reviewed proposals; no business effect at draft creation."""

import json
import re
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from .db import runtime_connection


def registry():
    from .app import CONTRACTS, TOOLS

    return {**TOOLS, **{c["name"]: c for c in CONTRACTS["human_or_system_only"]}}


def envelope(data, contact, now, refs=()):
    return {
        "data": data,
        "meta": {"as_of": now.isoformat(), "scope_ref": str(contact["id"]), "sources": list(refs)},
    }


def replay(conn, actor, contact_id, name, payload):
    from .app import digest, fail

    key = payload["operation_key"]
    if not 1 <= len(key) <= 128:
        fail("VALIDATION_ERROR")
    fingerprint = digest(json.dumps(payload, sort_keys=True))
    old = conn.execute(
        "SELECT * FROM operations WHERE actor_id=%s AND operation_key=%s", (actor, key)
    ).fetchone()
    if old:
        if (
            old["command"] != name
            or old["request_hash"] != fingerprint
            or old["contact_id"] != contact_id
        ):
            fail("IDEMPOTENCY_CONFLICT")
        return old["receipt"], None
    return None, (uuid4(), fingerprint)


def record_operation(conn, actor, contact_id, name, payload, operation, response, now):
    conn.execute(
        """INSERT INTO operations(id,actor_id,operation_key,command,request_hash,status,receipt,created_at,contact_id)
        VALUES (%s,%s,%s,%s,%s,'succeeded',%s,%s,%s)""",
        (
            operation[0],
            actor,
            payload["operation_key"],
            name,
            operation[1],
            Jsonb(response),
            now,
            contact_id,
        ),
    )


def unsupported_claims(body):
    # Conservative review aid, not a general NLP truth detector. Allegations have a separate field.
    pattern = r"\b(refund(?:ed)?|revers(?:al|ed)|funds?|money|payment)\b.{0,65}\b(completed|processed|sent|returned|issued|credited|moved)\b|\b(completed|processed|issued|sent)\b.{0,35}\b(refund|payment|reversal)\b"
    return (
        [
            "Unsupported financial completion claim. Put customer-reported claims in allegations; no execution evidence exists in this demo."
        ]
        if re.search(pattern, body, re.I)
        else []
    )


def current_sources(conn, contact, cards, refs):
    from .app import as_uuid, fail
    from .case_lookup import read_case
    from .policy_lookup import permitted

    if len(refs) > 30:
        fail("VALIDATION_ERROR")
    snapshots = []
    for ref in refs:
        ident = as_uuid(ref["id"])
        kind = ref["kind"]
        value = None
        if kind == "transaction":
            value = conn.execute(
                "SELECT * FROM card_transactions WHERE id=%s AND account_id=ANY(%s::uuid[])",
                (ident, [c["id"] for c in cards]),
            ).fetchone()
        elif kind == "contact" and ident == str(contact["id"]):
            value = contact
        elif kind == "case":
            detail, _ = read_case(conn, ident, contact, cards)
            value = {"version": detail["snapshot"]["case_version"], "detail": detail}
        elif kind == "policy":
            value = next(
                (
                    r
                    for r in permitted(conn, contact, cards)
                    if str(r["id"]) == ident and r["section"] == ref["section"]
                ),
                None,
            )
        if value is None:
            fail("FORBIDDEN_OR_NOT_FOUND")
        if str(value["version"]) != ref["version"]:
            fail("CONFLICT")
        snapshots.append(value)
    report = conn.execute(
        "SELECT revision,statement,recognition,transaction_versions,recognized_transaction_id FROM investigation_revisions WHERE contact_id=%s ORDER BY revision DESC LIMIT 1",
        (contact["id"],),
    ).fetchone()
    return {"records": snapshots, "report": report, "context_version": contact["version"]}


def snapshot_hash(value):
    from .app import digest

    return digest(json.dumps(value, sort_keys=True, default=str))


def validate_note(note, contact, refs, case_id=None):
    from .app import as_uuid, fail

    if (
        note["contact_id"] != str(contact["id"])
        or note["case_id"] != case_id
        or note["source_refs"] != refs
    ):
        fail("VALIDATION_ERROR")
    if (
        not note["body"].strip()
        or len(note["body"]) > 4000
        or len(note["customer_allegations"]) > 10
        or any(len(a) > 2000 for a in note["customer_allegations"])
    ):
        fail("VALIDATION_ERROR")
    if case_id and not any(r["kind"] == "case" and as_uuid(r["id"]) == case_id for r in refs):
        fail("VALIDATION_ERROR")
    if not any(r["kind"] == "contact" and r["id"] == str(contact["id"]) for r in refs):
        fail("VALIDATION_ERROR")


def draft_read(conn, contact, actor, cards):
    rows = conn.execute(
        "SELECT * FROM proposals WHERE contact_id=%s AND author_ref=%s ORDER BY id",
        (contact["id"], str(actor)),
    ).fetchall()
    for row in rows:
        authorize_refs(conn, contact, cards, row["source_versions"])
    return [
        {
            "id": str(r["id"]),
            "version": r["version"],
            "kind": r["kind"],
            "payload": r["payload"],
            "status": r["status"],
            "source_refs": r["source_versions"],
            "validation_gaps": unsupported_claims(r["payload"].get("body", "")),
        }
        for r in rows
    ]


def dispatch_proposals(settings, name, payload, authorization, request_id, now):
    from .app import BankError, as_uuid, audit, authenticate, fail, scope, source, validate

    error, result, actor = None, None, None
    try:
        with runtime_connection(settings.database_url) as conn:
            try:
                with conn.transaction():
                    session = authenticate(conn, authorization, now)
                    actor = session["principal_id"]
                    if name in (
                        "get_proposals",
                        "prepare_note",
                        "prepare_referral",
                        "get_referrals",
                    ):
                        schema = {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["contact_id"],
                            "properties": {"contact_id": {"type": "string", "format": "uuid"}},
                        }
                        if name in ("prepare_note", "prepare_referral"):
                            schema["required"].append("transaction_ids")
                            schema["properties"]["transaction_ids"] = {
                                "type": "array",
                                "maxItems": 10,
                                "uniqueItems": True,
                                "items": {"type": "string", "format": "uuid"},
                            }
                    elif name == "reject_proposal":
                        schema = {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "proposal_id",
                                "expected_proposal_version",
                                "reason",
                                "operation_key",
                            ],
                            "properties": {
                                "proposal_id": {"type": "string", "format": "uuid"},
                                "expected_proposal_version": {"type": "integer", "minimum": 1},
                                "reason": {"type": "string", "minLength": 1, "maxLength": 2000},
                                "operation_key": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 128,
                                },
                            },
                        }
                    else:
                        schema = registry()[name]["input_schema"]
                    validate(schema, payload)
                    proposal = None
                    if name in ("edit_proposal", "approve_and_commit_proposal", "reject_proposal"):
                        proposal = conn.execute(
                            "SELECT * FROM proposals WHERE id=%s AND author_ref=%s",
                            (as_uuid(payload["proposal_id"]), str(actor)),
                        ).fetchone()
                        if not proposal:
                            fail("FORBIDDEN_OR_NOT_FOUND")
                        cid = str(proposal["contact_id"])
                    else:
                        cid = payload["contact_id"]
                    contact, cards = scope(conn, session, cid, now)
                    if name == "prepare_referral":
                        from .referrals import prepare

                        result = {"data": prepare(conn, contact, cards, payload["transaction_ids"])}
                    elif name == "get_referrals":
                        rows = conn.execute(
                            """SELECT i.*,q.name AS queue_name,w.status AS work_status,w.original_due_at FROM referral_intakes i JOIN work_items w ON w.id=i.work_item_id JOIN service_queues q ON q.id=w.queue_id WHERE i.contact_id=%s AND i.committed_by=%s ORDER BY i.committed_at""",
                            (contact["id"], actor),
                        ).fetchall()
                        for row in rows:
                            authorize_refs(conn, contact, cards, row["source_versions"])
                        result = {
                            "referrals": [
                                {
                                    "proposal_id": str(r["proposal_id"]),
                                    "case_id": str(r["case_id"]),
                                    "work_item_id": str(r["work_item_id"]),
                                    "disposition": r["disposition"],
                                    "queue_name": r["queue_name"],
                                    "work_status": r["work_status"],
                                    "original_due_at": r["original_due_at"].isoformat()
                                    if r["original_due_at"]
                                    else None,
                                    "payload": r["payload"],
                                }
                                for r in rows
                            ]
                        }
                    elif name == "prepare_note":
                        refs = [source("contact", contact["id"], contact["version"])]
                        rows = conn.execute(
                            "SELECT * FROM card_transactions WHERE id=ANY(%s::uuid[]) AND account_id=ANY(%s::uuid[]) ORDER BY id",
                            (payload["transaction_ids"], [c["id"] for c in cards]),
                        ).fetchall()
                        if len(rows) != len(payload["transaction_ids"]):
                            fail("FORBIDDEN_OR_NOT_FOUND")
                        refs += [source("transaction", r["id"], r["version"]) for r in rows]
                        report = conn.execute(
                            "SELECT statement FROM investigation_revisions WHERE contact_id=%s ORDER BY revision DESC LIMIT 1",
                            (contact["id"],),
                        ).fetchone()
                        result = envelope(
                            {
                                "body": "Reviewed source facts:\n"
                                + "\n".join(
                                    f"{r['merchant_description']}: {r['amount_minor']} minor units {r['currency']}; {r['status']}."
                                    for r in rows
                                )
                                + "\nNext step: review evidence and applicable rules; no financial action executed.",
                                "customer_allegations": [report["statement"]] if report else [],
                                "source_refs": refs,
                                "context_version": str(contact["version"]),
                            },
                            contact,
                            now,
                            refs,
                        )
                    elif name == "get_proposals":
                        result = {"proposals": draft_read(conn, contact, actor, cards)}
                    elif name == "get_operation_status":
                        op = conn.execute(
                            "SELECT * FROM operations WHERE actor_id=%s AND contact_id=%s AND operation_key=%s",
                            (actor, contact["id"], payload["operation_key"]),
                        ).fetchone()
                        result = envelope(
                            {
                                "status": "succeeded" if op else "not_found",
                                "receipt_ref": str(op["id"]) if op else None,
                                "domain_ref": (
                                    op["receipt"].get("data", {}).get("domain_ref")
                                    or op["receipt"].get("data", {}).get("proposal_id")
                                )
                                if op
                                else None,
                            },
                            contact,
                            now,
                        )
                    else:
                        # Recheck referenced account access even when returning a prior receipt.
                        authorize_refs(
                            conn,
                            contact,
                            cards,
                            proposal["source_versions"] if proposal else payload["source_refs"],
                        )
                        receipt, operation = replay(conn, actor, contact["id"], name, payload)
                        if receipt:
                            result = receipt
                        elif name == "reject_proposal":
                            # A human may always decline a draft, including one whose evidence
                            # went stale. Nothing is committed; the reason stays in the receipt.
                            if (
                                proposal["status"] != "draft"
                                or proposal["version"] != payload["expected_proposal_version"]
                            ):
                                fail("CONFLICT")
                            if not payload["reason"].strip():
                                fail("VALIDATION_ERROR")
                            conn.execute(
                                "UPDATE proposals SET status='rejected' WHERE id=%s",
                                (proposal["id"],),
                            )
                            result = {
                                "data": {
                                    "proposal_id": str(proposal["id"]),
                                    "version": proposal["version"],
                                    "status": "rejected",
                                    "reason": payload["reason"],
                                },
                                "request_id": request_id,
                            }
                        elif name == "create_proposal":
                            item = payload["proposal"]
                            refs = payload["source_refs"]
                            if item["kind"] not in ("note", "referral"):
                                fail("VALIDATION_ERROR")
                            if str(contact["version"]) != payload["expected_context_version"]:
                                fail("CONFLICT")
                            note = item["payload"]
                            case_id = (
                                as_uuid(note["case_id"])
                                if item["kind"] == "note" and note["case_id"]
                                else None
                            )
                            if item["kind"] == "note":
                                validate_note(note, contact, refs, case_id)
                            else:
                                from .referrals import validate_referral

                                validate_referral(conn, contact, cards, note, refs)
                            current = current_sources(conn, contact, cards, refs)
                            pid = uuid4()
                            conn.execute(
                                "INSERT INTO proposals VALUES (%s,%s,%s,%s,%s,%s,%s,1,%s,%s)",
                                (
                                    pid,
                                    case_id,
                                    contact["id"],
                                    item["kind"],
                                    Jsonb(note),
                                    Jsonb(refs),
                                    "draft",
                                    str(actor),
                                    snapshot_hash(current),
                                ),
                            )
                            conn.execute(
                                "INSERT INTO proposal_revisions VALUES (%s,1,%s,%s,%s)",
                                (pid, Jsonb(note), actor, now),
                            )
                            gaps = unsupported_claims(note.get("body", ""))
                            result = envelope(
                                {
                                    "proposal_id": str(pid),
                                    "proposal_version": "1",
                                    "status": "draft",
                                    "validation_gaps": gaps,
                                    "requires_human_approval": True,
                                    "permitted_next_command": "none"
                                    if gaps
                                    else "approve_and_commit_proposal",
                                },
                                contact,
                                now,
                                refs,
                            )
                        else:
                            if proposal["status"] != "draft" or str(proposal["version"]) != str(
                                payload["expected_proposal_version"]
                            ):
                                fail("CONFLICT")
                            if payload["expected_work_version"] is not None:
                                fail("VALIDATION_ERROR")
                            if proposal["case_id"]:
                                case = conn.execute(
                                    "SELECT version FROM cases WHERE id=%s", (proposal["case_id"],)
                                ).fetchone()
                                if payload["expected_case_version"] != case["version"]:
                                    fail("CONFLICT")
                            elif payload["expected_case_version"] is not None:
                                fail("VALIDATION_ERROR")
                            current = current_sources(
                                conn, contact, cards, proposal["source_versions"]
                            )
                            if snapshot_hash(current) != proposal["rendered_source_hash"]:
                                fail("CONFLICT")
                            if name == "edit_proposal":
                                replacement = payload["replacement"]
                                if replacement["kind"] != proposal["kind"]:
                                    fail("VALIDATION_ERROR")
                                if proposal["kind"] == "note":
                                    validate_note(
                                        replacement["payload"],
                                        contact,
                                        proposal["source_versions"],
                                        str(proposal["case_id"]) if proposal["case_id"] else None,
                                    )
                                else:
                                    from .referrals import validate_referral

                                    validate_referral(
                                        conn,
                                        contact,
                                        cards,
                                        replacement["payload"],
                                        proposal["source_versions"],
                                    )
                                version = proposal["version"] + 1
                                conn.execute(
                                    "UPDATE proposals SET payload=%s,version=%s WHERE id=%s",
                                    (Jsonb(replacement["payload"]), version, proposal["id"]),
                                )
                                conn.execute(
                                    "INSERT INTO proposal_revisions VALUES (%s,%s,%s,%s,%s)",
                                    (
                                        proposal["id"],
                                        version,
                                        Jsonb(replacement["payload"]),
                                        actor,
                                        now,
                                    ),
                                )
                                result = {
                                    "data": {
                                        "proposal_id": str(proposal["id"]),
                                        "version": version,
                                        "status": "draft",
                                    },
                                    "request_id": request_id,
                                }
                            elif proposal["kind"] == "referral":
                                from .referrals import commit

                                committed = commit(
                                    conn, contact, cards, proposal, actor, operation[0], now
                                )
                                result = {
                                    "data": {
                                        "operation_key": payload["operation_key"],
                                        "status": "succeeded",
                                        **committed,
                                    },
                                    "request_id": request_id,
                                }
                                record_operation(
                                    conn,
                                    actor,
                                    contact["id"],
                                    name,
                                    payload,
                                    operation,
                                    result,
                                    now,
                                )
                                conn.execute(
                                    "UPDATE proposals SET status='committed' WHERE id=%s",
                                    (proposal["id"],),
                                )
                            else:
                                note = proposal["payload"]
                                if unsupported_claims(note["body"]):
                                    fail("UNSUPPORTED_CLAIM")
                                nid, event = uuid4(), uuid4()
                                result = {
                                    "data": {
                                        "operation_key": payload["operation_key"],
                                        "status": "succeeded",
                                        "domain_ref": str(nid),
                                        "domain_version": 1,
                                        "event_ref": str(event),
                                    },
                                    "request_id": request_id,
                                }
                                record_operation(
                                    conn,
                                    actor,
                                    contact["id"],
                                    name,
                                    payload,
                                    operation,
                                    result,
                                    now,
                                )
                                conn.execute(
                                    "INSERT INTO contact_notes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (
                                        nid,
                                        contact["id"],
                                        proposal["case_id"],
                                        proposal["id"],
                                        proposal["version"],
                                        note["body"],
                                        Jsonb(note["customer_allegations"]),
                                        Jsonb(proposal["source_versions"]),
                                        actor,
                                        now,
                                        operation[0],
                                    ),
                                )
                                conn.execute(
                                    "UPDATE proposals SET status='committed' WHERE id=%s",
                                    (proposal["id"],),
                                )
                                conn.execute(
                                    "INSERT INTO outbox_events VALUES (%s,%s,%s,1,'note.committed',%s,'pending',NULL,0)",
                                    (
                                        event,
                                        "note:" + str(nid),
                                        str(nid),
                                        Jsonb(
                                            {"note_id": str(nid), "contact_id": str(contact["id"])}
                                        ),
                                    ),
                                )
                        if not receipt and name != "approve_and_commit_proposal":
                            record_operation(
                                conn, actor, contact["id"], name, payload, operation, result, now
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


def authorize_refs(conn, contact, cards, refs):
    """Replay checks permission, not stale versions, after a successful effect."""
    from .app import as_uuid, fail
    from .case_lookup import read_case

    for ref in refs:
        ident = as_uuid(ref["id"])
        if ref["kind"] == "transaction":
            if not conn.execute(
                "SELECT 1 FROM card_transactions WHERE id=%s AND account_id=ANY(%s::uuid[])",
                (ident, [c["id"] for c in cards]),
            ).fetchone():
                fail("FORBIDDEN_OR_NOT_FOUND")
        elif ref["kind"] == "policy":
            if not conn.execute(
                """SELECT 1 FROM policy_versions p WHERE p.id=%s AND p.audience='inbound_representative'
                AND EXISTS (SELECT 1 FROM card_accounts a WHERE a.id=ANY(%s::uuid[]) AND a.product=p.product AND a.jurisdiction=p.jurisdiction)""",
                (ident, [c["id"] for c in cards]),
            ).fetchone():
                fail("FORBIDDEN_OR_NOT_FOUND")
        elif ref["kind"] == "case":
            read_case(conn, ident, contact, cards)
        elif ref["kind"] == "contact" and ident != str(contact["id"]):
            fail("FORBIDDEN_OR_NOT_FOUND")
        elif ref["kind"] not in ("transaction", "case", "contact", "policy"):
            fail("FORBIDDEN_OR_NOT_FOUND")
