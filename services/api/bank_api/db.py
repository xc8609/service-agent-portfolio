import hashlib
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / "services/api/migrations"
SCHEMA_VERSION = "004_case_lookup.sql"
MARKER = "service-agent-disposable-v1"


@contextmanager
def runtime_connection(dsn):
    with psycopg.connect(
        dsn,
        row_factory=dict_row,
        connect_timeout=3,
        options="-c statement_timeout=3000",
    ) as conn:
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        role = conn.execute(
            "SELECT current_user AS name, rolsuper FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if role["name"] != "bank_app" or role["rolsuper"]:
            raise RuntimeError("Runtime requires the restricted bank_app database role")
        yield conn


def migrate(dsn):
    with psycopg.connect(dsn) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(8271601)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, sha256 text NOT NULL)"
        )
        for path in sorted(MIGRATIONS.glob("*.sql")):
            content = path.read_text()
            digest = hashlib.sha256(content.encode()).hexdigest()
            old = conn.execute(
                "SELECT sha256 FROM schema_migrations WHERE name=%s", (path.name,)
            ).fetchone()
            if old:
                if old[0] != digest:
                    raise ValueError("Applied migration checksum mismatch")
                continue
            conn.execute(content)
            conn.execute("INSERT INTO schema_migrations VALUES (%s,%s)", (path.name, digest))


def provision_runtime(dsn, password):
    if len(password) < 24:
        raise ValueError("Runtime password must have at least 24 characters")
    with psycopg.connect(dsn) as conn:
        database = conn.execute("SELECT current_database()").fetchone()[0]
        assert_demo_target(conn, database)
        if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname='bank_app'").fetchone():
            conn.execute("CREATE ROLE bank_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT")
        conn.execute(sql.SQL("ALTER ROLE bank_app PASSWORD {}").format(sql.Literal(password)))
        conn.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        tables = [
            "staff_principals",
            "queue_memberships",
            "service_queues",
            "contacts",
            "verification_assertions",
            "card_accounts",
            "card_transactions",
            "transaction_relationships",
            "cases",
            "case_timeline_events",
            "work_items",
            "required_actions",
            "investigation_results",
            "update_commitments",
            "objection_work_links",
            "case_transactions",
            "schema_migrations",
            "demo_environment",
            "demo_sessions",
            "investigation_revisions",
        ]
        for table in tables:
            conn.execute(sql.SQL("GRANT SELECT ON {} TO bank_app").format(sql.Identifier(table)))
        conn.execute(
            "GRANT INSERT ON demo_sessions, audit_events, investigation_revisions TO bank_app"
        )


def assert_demo_target(conn, target, require_marker=True):
    if os.environ.get("BANK_MODE", "local") != "local":
        raise ValueError("Demo operation requires local mode")
    database = conn.execute("SELECT current_database()").fetchone()[0]
    if target != database or not database.startswith("bank_demo"):
        raise ValueError("Explicit matching bank_demo database name required")
    marker = conn.execute(
        "SELECT marker,database_name FROM demo_environment WHERE singleton"
    ).fetchone()
    if (require_marker or marker is not None) and marker != (MARKER, database):
        raise ValueError("Existing disposable marker required; no records deleted")
    return database
