"""Deterministic, scoped simulated policy reads. No model or business writes."""

from collections import Counter
from datetime import datetime

import psycopg

from .db import runtime_connection

PAIR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["contact_id", "transaction_ids", "expected_versions"],
    "properties": {
        "contact_id": {"type": "string"},
        "transaction_ids": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "uniqueItems": True,
            "items": {"type": "string", "format": "uuid"},
        },
        "expected_versions": {
            "type": "object",
            "minProperties": 2,
            "maxProperties": 2,
            "additionalProperties": {"type": "string", "minLength": 1},
        },
    },
}
GAP = "No applicable handling rule. Keep the concern open and request manual policy review from the service lead; no refund or completion promise is inferred."
CONFLICT = "Applicable rule editions overlap. Ask the service lead to obtain policy-owner clarification before relying on an instruction; do not choose the newest upload."


def permitted(conn, contact, cards):
    """Filter all authorization/effective metadata before returning narrative."""
    return conn.execute(
        """SELECT p.*,s.section,s.title,s.decision_key,s.transaction_pattern,s.conditions,s.next_steps
        FROM policy_versions p JOIN policy_sections s ON s.policy_version_id=p.id
        WHERE p.published AND p.audience='inbound_representative'
        AND p.effective_from<=%s AND (p.effective_to IS NULL OR %s<p.effective_to)
        AND EXISTS (SELECT 1 FROM card_accounts a WHERE a.id=ANY(%s::uuid[])
                    AND a.product=p.product AND a.jurisdiction=p.jurisdiction)
        ORDER BY p.policy_key,p.version,s.section LIMIT 101""",
        (contact["opened_at"], contact["opened_at"], [c["id"] for c in cards]),
    ).fetchall()


def conflict_rows(rows):
    counts = Counter(
        (r["product"], r["jurisdiction"], r["decision_key"], r["transaction_pattern"]) for r in rows
    )
    return any(n > 1 for n in counts.values())


def citation(row):
    from .app import source

    return source("policy", row["id"], row["version"], row["section"])


def section_data(row):
    return {
        "text": row["body"],
        "policy_ref": citation(row),
        "applicability": [
            f"Product: {row['product']}; jurisdiction: {row['jurisdiction']}; audience: {row['audience']}.",
            f"Effective from {row['effective_from'].isoformat()} (inclusive) to {row['effective_to'].isoformat() if row['effective_to'] else 'no recorded end'} (exclusive).",
            *row["conditions"],
        ],
        "is_simulated": True,
    }


def pair_rules(conn, payload, contact, cards, rows):
    from .app import as_uuid, fail, source

    ids = [as_uuid(i) for i in payload["transaction_ids"]]
    expected = payload["expected_versions"]
    if len(set(ids)) != 2 or set(expected) != set(ids):
        fail("VALIDATION_ERROR")
    selected = conn.execute(
        "SELECT * FROM card_transactions WHERE id=ANY(%s::uuid[]) AND account_id=ANY(%s::uuid[]) ORDER BY id",
        (ids, [c["id"] for c in cards]),
    ).fetchall()
    if len(selected) != 2:
        fail("FORBIDDEN_OR_NOT_FOUND")
    if any(str(r["version"]) != expected[str(r["id"])] for r in selected):
        fail("EVIDENCE_CHANGED")
    same_account = len({r["account_id"] for r in selected}) == 1
    statuses = sorted(r["status"] for r in selected)
    pattern = (
        "two_posted"
        if statuses == ["posted", "posted"]
        else "pending_posted"
        if statuses == ["pending", "posted"]
        else None
    )
    account = next(c for c in cards if c["id"] == selected[0]["account_id"])
    matches = [
        r
        for r in rows
        if same_account
        and r["product"] == account["product"]
        and r["jurisdiction"] == account["jurisdiction"]
        and r["transaction_pattern"] == pattern
    ]
    conflict = conflict_rows(matches)
    state = "conflict" if conflict else "applicable" if matches else "gap"
    return {
        "state": state,
        "policy_as_of": contact["opened_at"].isoformat(),
        "context": {
            "product": account["product"],
            "jurisdiction": account["jurisdiction"],
            "transaction_pattern": pattern,
            "same_account": same_account,
        },
        "rules": [
            {
                **section_data(r),
                "title": r["title"],
                "source_label": r["source_label"],
                "next_steps": [] if conflict else r["next_steps"],
            }
            for r in matches
        ],
        "gaps": [CONFLICT] if conflict else [GAP] if not matches else [],
        "boundary": "Simulated procedure only. Applicability is not a duplicate-charge finding, approval to submit, or refund authorization. Customer recognition and existing work still require representative review.",
        "transaction_sources": [source("transaction", r["id"], r["version"]) for r in selected],
    }, matches


def dispatch_policy(settings, name, payload, authorization, request_id, now):
    from .app import TOOLS, BankError, as_uuid, audit, authenticate, fail, scope, validate

    result, error, actor = None, None, None
    try:
        with runtime_connection(settings.database_url) as conn:
            try:
                session = authenticate(conn, authorization, now)
                actor = session["principal_id"]
                validate(
                    PAIR_SCHEMA if name == "get_handling_rules" else TOOLS[name]["input_schema"],
                    payload,
                )
                contact, cards = scope(conn, session, payload["contact_id"], now)
                rows = permitted(conn, contact, cards)
                if len(rows) > 100:
                    fail("LIMIT_EXCEEDED")
                if name == "get_handling_rules":
                    data, used = pair_rules(conn, payload, contact, cards, rows)
                elif name == "search_policy":
                    # Query parameters narrow authorized metadata, never establish identity/scope/time.
                    if len(payload["query"]) > 200 or not payload["query"].strip():
                        fail("VALIDATION_ERROR")
                    if (
                        datetime.fromisoformat(payload["as_of"].replace("Z", "+00:00"))
                        != contact["opened_at"]
                    ):
                        fail("VALIDATION_ERROR")
                    if not any(
                        c["product"] == payload["product"]
                        and c["jurisdiction"] == payload["jurisdiction"]
                        for c in cards
                    ):
                        fail("FORBIDDEN_OR_NOT_FOUND")
                    patterns = {
                        None: ("two_posted", "pending_posted"),
                        "posted": ("two_posted", "pending_posted"),
                        "pending": ("pending_posted",),
                    }
                    candidates = [
                        r
                        for r in rows
                        if r["product"] == payload["product"]
                        and r["jurisdiction"] == payload["jurisdiction"]
                        and r["transaction_pattern"]
                        in patterns.get(payload["transaction_status"], ())
                    ]
                    # Determine overlap BEFORE text filtering, so a query cannot hide an edition conflict.
                    conflict = conflict_rows(candidates)
                    query = payload["query"].lower().strip()
                    used = [
                        r for r in candidates if query in (r["title"] + " " + r["body"]).lower()
                    ]
                    data = {
                        "matches": [
                            {
                                "policy_id": str(r["id"]),
                                "version": r["version"],
                                "section": r["section"],
                                "title": r["title"],
                                "effective_from": r["effective_from"].isoformat(),
                                "effective_to": r["effective_to"].isoformat()
                                if r["effective_to"]
                                else None,
                            }
                            for r in used
                        ],
                        "gaps": [CONFLICT] if conflict else [] if used else [GAP],
                    }
                else:
                    ident = as_uuid(payload["policy_id"])
                    match = next(
                        (
                            r
                            for r in rows
                            if str(r["id"]) == ident
                            and r["version"] == payload["version"]
                            and r["section"] == payload["section"]
                        ),
                        None,
                    )
                    if not match:
                        fail("FORBIDDEN_OR_NOT_FOUND")
                    siblings = [
                        r
                        for r in rows
                        if (
                            r["product"],
                            r["jurisdiction"],
                            r["decision_key"],
                            r["transaction_pattern"],
                        )
                        == (
                            match["product"],
                            match["jurisdiction"],
                            match["decision_key"],
                            match["transaction_pattern"],
                        )
                    ]
                    if conflict_rows(siblings):
                        fail("POLICY_CONFLICT")
                    used, data = [match], section_data(match)
                result = {
                    "data": data,
                    "meta": {
                        "as_of": now.isoformat(),
                        "scope_ref": str(contact["id"]),
                        "sources": [citation(r) for r in used],
                    },
                }
                if name != "get_handling_rules":
                    validate(TOOLS[name]["success_schema"], result)
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
