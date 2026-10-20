"""Authored synthetic fixtures, v2; stable IDs and no external data source."""

from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from .case_fixtures import seed_cases
from .db import MARKER, assert_demo_target

FIXTURE_VERSION = "bank-cases-synthetic-v2"


def uid(name):
    return str(uuid5(NAMESPACE_URL, "service-agent-portfolio/synthetic/" + name))


PERSONAS = {
    "verified": ("rep_a", "contact_a", "inbound_representative", "customer_a"),
    "unverified": (
        "rep_unverified",
        "contact_unverified",
        "inbound_representative",
        "customer_a",
    ),
    "expired": (
        "rep_expired",
        "contact_expired",
        "inbound_representative",
        "customer_a",
    ),
    "other_customer": ("rep_b", "contact_b", "inbound_representative", "customer_b"),
    "feedback_unclaimed": (
        "feedback",
        "contact_feedback",
        "feedback_representative",
        "customer_a",
    ),
    "agent": ("agent", "contact_agent", "agent_runtime", "customer_a"),
    "lead": ("lead", "contact_lead", "queue_lead", "customer_a"),
}


def insert(conn, table, row):
    conn.execute(
        sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
            sql.Identifier(table),
            sql.SQL(",").join(map(sql.Identifier, row)),
            sql.SQL(",").join(sql.Placeholder() for _ in row),
        ),
        list(row.values()),
    )


def seed(dsn, target, initialize=False, now=None):
    now = now or datetime.now(UTC)
    with psycopg.connect(dsn) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(8271601)")
        database = assert_demo_target(conn, target, require_marker=not initialize)
        if initialize and not conn.execute("SELECT 1 FROM demo_environment").fetchone():
            # An explicit initialize operation is allowed only on empty domain tables.
            for table in [
                "customers",
                "contacts",
                "staff_principals",
                "cases",
                "card_transactions",
            ]:
                if conn.execute(
                    sql.SQL("SELECT 1 FROM {} LIMIT 1").format(sql.Identifier(table))
                ).fetchone():
                    raise ValueError("Refusing to mark a populated database disposable")
            insert(
                conn,
                "demo_environment",
                {
                    "singleton": True,
                    "marker": MARKER,
                    "database_name": database,
                    "fixture_version": FIXTURE_VERSION,
                },
            )
        insert(
            conn,
            "service_queues",
            {
                "id": uid("inbound_queue"),
                "name": "Synthetic service desk",
                "kind": "inbound",
                "active": True,
            },
        )
        for name, alias, card in [
            ("customer_a", "Demo customer A", "DEMO-4242"),
            ("customer_b", "Demo customer B", "DEMO-8585"),
        ]:
            insert(
                conn,
                "customers",
                {
                    "id": uid(name),
                    "external_ref": name,
                    "display_alias": alias,
                    "data_origin": "synthetic",
                },
            )
            insert(
                conn,
                "card_accounts",
                {
                    "id": uid("card_" + name),
                    "customer_id": uid(name),
                    "masked_ref": card,
                    "product": "credit_card",
                    "currency": "CAD",
                    "version": 1,
                },
            )
        for persona, (actor, contact, role, customer) in PERSONAS.items():
            insert(
                conn,
                "staff_principals",
                {"id": uid(actor), "subject_ref": actor, "active": True},
            )
            insert(
                conn,
                "queue_memberships",
                {
                    "id": uid("membership_" + actor),
                    "principal_id": uid(actor),
                    "queue_id": uid("inbound_queue"),
                    "role": role,
                    "active": True,
                },
            )
            insert(
                conn,
                "contacts",
                {
                    "id": uid(contact),
                    "customer_id": uid(customer),
                    "actor_id": uid(actor),
                    "kind": "inbound",
                    "status": "open",
                    "opened_at": now,
                    "version": 1,
                },
            )
            insert(
                conn,
                "verification_assertions",
                {
                    "id": uid("proof_" + contact),
                    "contact_id": uid(contact),
                    "issuer_ref": "local_synthetic_adapter",
                    "state": "unverified" if persona == "unverified" else "verified",
                    "verified_at": now - timedelta(minutes=1),
                    "expires_at": now + timedelta(minutes=-1 if persona == "expired" else 60),
                    "scope_json": Jsonb({"account_ids": [uid("card_" + customer)]}),
                },
            )
        transactions = [
            ("pending", "customer_a", 4200, "DEMO NORTH CAFE", "pending", None),
            (
                "posted",
                "customer_a",
                4200,
                "DEMO NORTH CAFE",
                "posted",
                "2026-10-19T12:00:00+00:00",
            ),
            (
                "equal_1",
                "customer_a",
                8500,
                "DEMO STORE",
                "posted",
                "2026-10-19T12:00:00+00:00",
            ),
            (
                "equal_2",
                "customer_a",
                8500,
                "DEMO STORE",
                "posted",
                "2026-10-19T12:00:00+00:00",
            ),
            ("reversed", "customer_a", 1900, "DEMO PARKING", "reversed", None),
            (
                "missing",
                "customer_a",
                9900,
                "Merchant unavailable",
                "posted",
                "2026-10-19T12:00:00+00:00",
            ),
            (
                "private",
                "customer_b",
                7100,
                "OTHER CUSTOMER PRIVATE MERCHANT",
                "posted",
                "2026-10-19T12:00:00+00:00",
            ),
        ]
        for name, customer, amount, merchant, status, posted in transactions:
            insert(
                conn,
                "card_transactions",
                {
                    "id": uid("tx_" + name),
                    "account_id": uid("card_" + customer),
                    "amount_minor": amount,
                    "currency": "CAD",
                    "merchant_description": merchant,
                    "status": status,
                    "occurred_at": "2026-10-18T12:00:00+00:00",
                    "posted_at": posted,
                    "source_ref": "synthetic-ledger-v1:" + name,
                    "version": 1,
                },
            )
        insert(
            conn,
            "transaction_relationships",
            {
                "id": uid("relationship_pending_posted"),
                "left_transaction_id": uid("tx_pending"),
                "right_transaction_id": uid("tx_posted"),
                "relation": "source_linked_authorization",
                "evidence_ref": "synthetic-ledger-v1:authorization-link",
                "version": 1,
            },
        )

        seed_cases(conn)
        conn.execute(
            "UPDATE demo_environment SET fixture_version=%s WHERE singleton", (FIXTURE_VERSION,)
        )


def reset(dsn, target):
    with psycopg.connect(dsn) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(8271601)")
        assert_demo_target(conn, target)
        # Never drop schemas or run against an unmarked database. Keep migrations/marker.
        conn.execute(
            "TRUNCATE staff_principals, service_queues, customers, audit_events, operations, outbox_events CASCADE"
        )
