from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import psycopg
import pytest
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient


def payload(contact, **changes):
    return {
        "contact_id": contact,
        "expected_revision": 0,
        "operation_key": str(uuid4()),
        "statement": "I bought once but cannot distinguish the two entries.",
        "recognition": "one_purchase_unresolved",
        "transaction_versions": [
            {"id": uid(n), "version": "1"} for n in ("tx_equal_1", "tx_equal_2")
        ],
        "recognized_transaction_id": None,
        **changes,
    }


def save(client, headers, data):
    return client.post("/v1/workspace/save_investigation", headers=headers, json=data)


def history(client, headers, contact):
    return client.post(
        "/v1/workspace/get_investigation", headers=headers, json={"contact_id": contact}
    )


def test_revision_history_replay_and_safe_audit(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    first = payload(contact)
    response = save(client, headers, first)
    assert response.status_code == 200, response.text
    assert response.json()["history"][0]["recognized_transaction_id"] is None
    assert save(client, headers, first).json() == response.json()
    second = payload(
        contact,
        expected_revision=1,
        statement="Correction: I recognize neither purchase.",
        recognition="neither",
    )
    assert save(client, headers, second).json()["current_revision"] == 2
    assert save(client, headers, first).json()["saved_revision"] == 1
    headers2, _ = session(client)
    data = history(client, headers2, contact).json()
    assert [r["statement"] for r in data["history"]] == [first["statement"], second["statement"]]
    assert (
        save(client, headers, {**first, "statement": "Changed under same key"}).status_code == 409
    )
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM investigation_revisions").fetchone()[0] == 2
        assert str(
            c.execute("SELECT DISTINCT actor_id FROM investigation_revisions").fetchone()[0]
        ) == uid("rep_a")
        audits = c.execute("SELECT safe_details FROM audit_events").fetchall()
        assert all(set(a[0]) == {"outcome", "request_id"} for a in audits)
        assert "purchase" not in str(audits)
        assert (
            c.execute("SELECT count(*) FROM card_transactions WHERE version<>1").fetchone()[0] == 0
        )


@pytest.mark.parametrize("mode", ["specific_entry", "both", "neither", "not_recorded"])
def test_explicit_recognition_modes(environment, mode):
    client, *_ = environment
    headers, contact = session(client)
    data = payload(contact, recognition=mode)
    if mode == "specific_entry":
        data["recognized_transaction_id"] = uid("tx_equal_2")
    if mode == "not_recorded":
        data["transaction_versions"] = []
    r = save(client, headers, data)
    assert r.status_code == 200, r.text
    assert r.json()["history"][0]["recognition"] == mode


@pytest.mark.parametrize(
    "changes",
    [
        {"statement": "   "},
        {"statement": "x" * 2001},
        {"role": "lead"},
        {"expected_revision": True},
        {"recognition": "duplicate"},
        {"recognized_transaction_id": uid("tx_equal_1")},
        {"recognition": "specific_entry"},
        {"recognition": "specific_entry", "recognized_transaction_id": uid("tx_posted")},
        {"transaction_versions": []},
        {"transaction_versions": [{"id": uid("tx_equal_1"), "version": "1"}] * 2},
        {"recognition": "not_recorded"},
    ],
)
def test_invalid_report_has_no_write(environment, changes):
    client, *_ = environment
    headers, contact = session(client)
    assert save(client, headers, payload(contact, **changes)).status_code == 422
    assert history(client, headers, contact).json()["current_revision"] == 0


@pytest.mark.parametrize(
    "persona,status",
    [
        ("unverified", 401),
        ("expired", 401),
        ("agent", 404),
        ("feedback_unclaimed", 404),
        ("lead", 404),
    ],
)
def test_report_requires_verified_owned_inbound_contact(environment, persona, status):
    client, *_ = environment
    headers, contact = session(client, persona)
    assert save(client, headers, payload(contact)).status_code == status
    assert history(client, headers, contact).status_code == status


def test_scope_rechecked_on_read_save_and_replay(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    data = payload(contact)
    assert save(client, headers, data).status_code == 200
    other, other_contact = session(client, "other_customer")
    assert history(client, other, other_contact).json()["history"] == []
    assert history(client, other, contact).status_code == 404
    foreign = payload(
        contact,
        expected_revision=1,
        transaction_versions=[
            {"id": uid("tx_equal_1"), "version": "1"},
            {"id": uid("tx_private"), "version": "1"},
        ],
    )
    assert save(client, headers, foreign).status_code == 404
    with TestClient(
        create_app(Settings(runtime), clock=lambda: NOW + timedelta(minutes=16))
    ) as later:
        assert save(later, headers, data).status_code == 401
    with psycopg.connect(admin) as c:
        c.execute("UPDATE queue_memberships SET active=false")
    assert save(client, headers, data).status_code == 404
    assert history(client, headers, contact).status_code == 404


def test_stale_source_and_optimistic_conflict(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute("UPDATE card_transactions SET version=2 WHERE id=%s", (uid("tx_equal_1"),))
    assert save(client, headers, payload(contact)).status_code == 409
    plain = payload(contact, recognition="not_recorded", transaction_versions=[])
    assert save(client, headers, plain).status_code == 200
    assert save(client, headers, {**plain, "operation_key": str(uuid4())}).status_code == 409
    assert history(client, headers, contact).json()["current_revision"] == 1


def test_competing_saves_create_only_one_revision(environment):
    client, _, runtime, _ = environment
    headers, contact = session(client)

    def submit(_):
        with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as parallel:
            return save(parallel, headers, payload(contact)).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(submit, range(2))) == [200, 409]
    assert history(client, headers, contact).json()["current_revision"] == 1


def test_append_only_privileges_and_audit_atomicity(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    for sql in [
        "UPDATE investigation_revisions SET statement='overwrite'",
        "DELETE FROM investigation_revisions",
    ]:
        with psycopg.connect(runtime) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(sql)
    with psycopg.connect(admin) as c:
        c.execute("REVOKE INSERT ON audit_events FROM bank_app")
    try:
        assert save(client, headers, payload(contact)).status_code == 503
        with psycopg.connect(admin) as c:
            assert c.execute("SELECT count(*) FROM investigation_revisions").fetchone()[0] == 0
    finally:
        with psycopg.connect(admin) as c:
            c.execute("GRANT INSERT ON audit_events TO bank_app")


def test_uuid_spelling_does_not_break_membership_or_replay(environment):
    client, *_ = environment
    headers, contact = session(client)
    data = payload(
        contact, recognition="specific_entry", recognized_transaction_id=uid("tx_equal_1")
    )
    original = save(client, headers, data)
    assert original.status_code == 200
    data["operation_key"] = data["operation_key"].upper()
    data["recognized_transaction_id"] = data["recognized_transaction_id"].upper()
    for item in data["transaction_versions"]:
        item["id"] = item["id"].upper()
    assert save(client, headers, data).json() == original.json()
