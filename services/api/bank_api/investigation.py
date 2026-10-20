"""Trusted human statement capture; deliberately absent from model tools."""

import json

import psycopg
from psycopg.types.json import Jsonb

from .db import ROOT, runtime_connection

SAVE_SCHEMA = json.loads(
    (ROOT / "projects/bank-service-assist/specs/DEV-03/investigation-input.schema.json").read_text()
)
READ_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["contact_id"],
    "properties": {"contact_id": {"type": "string", "format": "uuid"}},
}


def dispatch_investigation(settings, name, payload, authorization, request_id, now):
    # Local import avoids a module initialization cycle with the shared HTTP boundary.
    from .app import BankError, as_uuid, audit, authenticate, digest, fail, scope, validate

    actor, error, result = None, None, None
    try:
        with runtime_connection(settings.database_url) as conn:
            try:
                # Savepoint keeps a constraint/concurrency failure out of the audit transaction.
                with conn.transaction():
                    session = authenticate(conn, authorization, now)
                    actor = session["principal_id"]
                    validate(SAVE_SCHEMA if name == "save_investigation" else READ_SCHEMA, payload)
                    # UUID spelling must not alter pair membership or replay identity.
                    payload = {**payload, "contact_id": as_uuid(payload["contact_id"])}
                    if name == "save_investigation":
                        payload["operation_key"] = as_uuid(payload["operation_key"])
                        payload["transaction_versions"] = [
                            {**v, "id": as_uuid(v["id"])} for v in payload["transaction_versions"]
                        ]
                        if payload["recognized_transaction_id"] is not None:
                            payload["recognized_transaction_id"] = as_uuid(
                                payload["recognized_transaction_id"]
                            )
                    contact, cards = scope(conn, session, payload["contact_id"], now)
                    history = conn.execute(
                        "SELECT * FROM investigation_revisions WHERE contact_id=%s ORDER BY revision",
                        (contact["id"],),
                    ).fetchall()

                    def permitted(versions):
                        ids = [v["id"] for v in versions]
                        rows = conn.execute(
                            """SELECT id,version,account_id FROM card_transactions
                            WHERE id=ANY(%s::uuid[]) AND account_id=ANY(%s::uuid[])""",
                            (ids, [c["id"] for c in cards]),
                        ).fetchall()
                        if len(rows) != len(ids):
                            fail("FORBIDDEN_OR_NOT_FOUND")
                        return rows

                    for old in history:
                        permitted(old["transaction_versions"])
                    receipt = None
                    if name == "save_investigation":
                        versions = payload["transaction_versions"]
                        ids = [v["id"] for v in versions]
                        mode = payload["recognition"]
                        recognized = payload["recognized_transaction_id"]
                        if (
                            len(ids) != len(set(ids))
                            or len(ids) != (0 if mode == "not_recorded" else 2)
                            or (mode == "specific_entry" and recognized not in ids)
                            or (mode != "specific_entry" and recognized is not None)
                        ):
                            fail("VALIDATION_ERROR")
                        rows = permitted(versions)
                        if len({r["account_id"] for r in rows}) > 1:
                            fail("VALIDATION_ERROR")
                        fingerprint = digest(json.dumps(payload, sort_keys=True))
                        old = next(
                            (
                                r
                                for r in history
                                if str(r["operation_key"]) == payload["operation_key"]
                            ),
                            None,
                        )
                        if old:
                            if old["input_hash"] != fingerprint:
                                fail("CONFLICT")
                            receipt = old["revision"]
                        else:
                            current = history[-1]["revision"] if history else 0
                            if payload["expected_revision"] != current or any(
                                str(r["version"])
                                != next(v["version"] for v in versions if v["id"] == str(r["id"]))
                                for r in rows
                            ):
                                fail("CONFLICT")
                            row = conn.execute(
                                """INSERT INTO investigation_revisions
                                (contact_id,revision,operation_key,input_hash,statement,recognition,
                                 transaction_versions,recognized_transaction_id,actor_id,recorded_at)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
                                (
                                    contact["id"],
                                    current + 1,
                                    payload["operation_key"],
                                    fingerprint,
                                    payload["statement"],
                                    mode,
                                    Jsonb(versions),
                                    recognized,
                                    actor,
                                    now,
                                ),
                            ).fetchone()
                            history.append(row)
                            receipt = row["revision"]
                    result = {
                        "current_revision": history[-1]["revision"] if history else 0,
                        "saved_revision": receipt,
                        "history": [
                            {
                                "revision": r["revision"],
                                "statement": r["statement"],
                                "recognition": r["recognition"],
                                "transaction_versions": r["transaction_versions"],
                                "recognized_transaction_id": str(r["recognized_transaction_id"])
                                if r["recognized_transaction_id"]
                                else None,
                                "recorded_at": r["recorded_at"].isoformat(),
                            }
                            for r in history
                        ],
                    }
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
