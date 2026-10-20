"""Integration tests require an explicit disposable PostgreSQL database."""

import os
import secrets
from datetime import UTC, datetime

import pytest
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.db import migrate, provision_runtime
from bank_api.fixtures import reset, seed
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict

NOW = datetime(2026, 10, 20, 15, tzinfo=UTC)


@pytest.fixture(scope="session")
def db_urls():
    admin = os.environ.get("BANK_TEST_ADMIN_URL")
    if not admin:
        pytest.fail(
            "BANK_TEST_ADMIN_URL must identify an isolated bank_demo database; no SQLite fallback"
        )
    target = conninfo_to_dict(admin)["dbname"]
    migrate(admin)
    seed(admin, target, initialize=True, now=NOW)
    password = secrets.token_urlsafe(32)
    provision_runtime(admin, password)
    options = conninfo_to_dict(admin)
    options.update(user="bank_app", password=password)
    # Settings accepts URL; parameter-form DSNs remain internal to tests.
    from urllib.parse import quote

    host = options.get("host", "localhost")
    port = options.get("port", "5432")
    if host.startswith("/"):
        runtime = f"postgresql://bank_app:{quote(password)}@/{target}?host={quote(host, safe='')}"
    else:
        runtime = f"postgresql://bank_app:{quote(password)}@{host}:{port}/{target}"
    return admin, runtime, target


@pytest.fixture
def environment(db_urls):
    admin, runtime, target = db_urls
    reset(admin, target)
    seed(admin, target, now=NOW)
    with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as client:
        yield client, admin, runtime, target


def session(client, persona="verified"):
    result = client.post("/v1/demo/session", json={"persona": persona})
    assert result.status_code == 200, result.text
    s = result.json()
    return {"Authorization": "Bearer " + s["access_token"]}, s["contact_id"]
