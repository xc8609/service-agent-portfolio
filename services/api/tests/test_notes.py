from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg
import pytest
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient


def post(client, headers, name, payload):
    group = "agent-tools" if name in ("create_proposal", "get_operation_status") else "commands"
    if name in ("prepare_note", "get_proposals"):
        group = "workspace"
    return client.post(f"/v1/{group}/{name}", headers=headers, json=payload)


def draft(
    client,
    headers,
    contact,
    body="Reviewed two posted transactions. Awaiting specialist review.",
    allegations=None,
):
    prepared = post(
        client,
        headers,
        "prepare_note",
        {"contact_id": contact, "transaction_ids": [uid("tx_equal_1"), uid("tx_equal_2")]},
    )
    assert prepared.status_code == 200, prepared.text
    data = prepared.json()["data"]
    payload = {
        "contact_id": contact,
        "expected_context_version": data["context_version"],
        "source_refs": data["source_refs"],
        "operation_key": str(uuid4()),
        "proposal": {
            "kind": "note",
            "payload": {
                "case_id": None,
                "contact_id": contact,
                "body": body,
                "customer_allegations": allegations or [],
                "source_refs": data["source_refs"],
            },
        },
    }
    response = post(client, headers, "create_proposal", payload)
    assert response.status_code == 200, response.text
    return payload, response.json()["data"]


def approve(data, **changes):
    return {
        "proposal_id": data["proposal_id"],
        "expected_proposal_version": str(data["proposal_version"]),
        "expected_case_version": None,
        "expected_work_version": None,
        "operation_key": str(uuid4()),
        **changes,
    }


def test_exact_reviewed_revision_receipt_and_retry(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    original, data = draft(
        client, headers, contact, allegations=["Customer says refund was processed."]
    )
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
    replacement = {
        **original["proposal"]["payload"],
        "body": "Two posted entries; customer confirms one purchase. No determination yet.",
    }
    edit = {
        "proposal_id": data["proposal_id"],
        "expected_proposal_version": 1,
        "expected_case_version": None,
        "expected_work_version": None,
        "replacement": {"kind": "note", "payload": replacement},
        "operation_key": str(uuid4()),
    }
    r = post(client, headers, "edit_proposal", edit)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["version"] == 2
    command = approve(data, expected_proposal_version="2")
    r = post(client, headers, "approve_and_commit_proposal", command)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "succeeded"
    with psycopg.connect(admin) as c:
        row = c.execute(
            "SELECT body,customer_allegations,reviewed_proposal_version,committed_by FROM contact_notes"
        ).fetchone()
        assert row == (
            replacement["body"],
            replacement["customer_allegations"],
            2,
            __import__("uuid").UUID(uid("rep_a")),
        )
        c.execute("UPDATE card_transactions SET version=2 WHERE id=%s", (uid("tx_equal_1"),))
    assert post(client, headers, "approve_and_commit_proposal", command).json() == r.json()
    receipt = post(
        client,
        headers,
        "get_operation_status",
        {"contact_id": contact, "operation_key": command["operation_key"]},
    )
    assert receipt.json()["data"]["domain_ref"] == r.json()["data"]["domain_ref"]
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 1
        assert c.execute("SELECT count(*) FROM proposal_revisions").fetchone()[0] == 2
        assert (
            c.execute(
                "SELECT count(*) FROM outbox_events WHERE event_type='note.committed'"
            ).fetchone()[0]
            == 1
        )
    assert (
        post(
            client,
            headers,
            "approve_and_commit_proposal",
            {**command, "expected_proposal_version": "1"},
        ).json()["error"]["code"]
        == "IDEMPOTENCY_CONFLICT"
    )


@pytest.mark.parametrize("change", ["transaction", "report", "scope"])
def test_stale_or_unauthorized_commit_retains_draft(environment, change):
    client, admin, *_ = environment
    headers, contact = session(client)
    original, data = draft(client, headers, contact)
    if change == "report":
        from test_investigation import payload, save

        assert save(client, headers, payload(contact)).status_code == 200
    else:
        with psycopg.connect(admin) as c:
            c.execute(
                "UPDATE card_transactions SET version=2"
                if change == "transaction"
                else "UPDATE queue_memberships SET active=false"
            )
    r = post(client, headers, "approve_and_commit_proposal", approve(data))
    assert r.status_code == (404 if change == "scope" else 409), r.text
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
        assert c.execute("SELECT payload,status FROM proposals").fetchone() == (
            original["proposal"]["payload"],
            "draft",
        )


def test_unsupported_financial_claim_requires_edit(environment):
    client, *_ = environment
    headers, contact = session(client)
    original, data = draft(client, headers, contact, "Refund was processed.")
    assert data["validation_gaps"] and data["permitted_next_command"] == "none"
    r = post(client, headers, "approve_and_commit_proposal", approve(data))
    assert r.json()["error"]["code"] == "UNSUPPORTED_CLAIM"
    replacement = {
        **original["proposal"]["payload"],
        "body": "No execution evidence available.",
        "customer_allegations": ["Customer reports refund was processed."],
    }
    edit = {
        "proposal_id": data["proposal_id"],
        "expected_proposal_version": 1,
        "expected_case_version": None,
        "expected_work_version": None,
        "replacement": {"kind": "note", "payload": replacement},
        "operation_key": str(uuid4()),
    }
    assert post(client, headers, "edit_proposal", edit).status_code == 200
    assert (
        post(
            client,
            headers,
            "approve_and_commit_proposal",
            approve(data, expected_proposal_version="2"),
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "persona,status",
    [
        ("agent", 404),
        ("lead", 404),
        ("feedback_unclaimed", 404),
        ("unverified", 401),
        ("expired", 401),
    ],
)
def test_note_authority_is_server_owned(environment, persona, status):
    client, *_ = environment
    headers, contact = session(client, persona)
    assert (
        post(
            client, headers, "prepare_note", {"contact_id": contact, "transaction_ids": []}
        ).status_code
        == status
    )
    assert post(client, headers, "get_proposals", {"contact_id": contact}).status_code == status


def test_foreign_sources_and_scope_rechecked_on_replay(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    original, data = draft(client, headers, contact)
    foreign = {
        **original,
        "operation_key": str(uuid4()),
        "source_refs": [
            {"kind": "transaction", "id": uid("tx_private"), "version": "1", "section": None}
        ],
    }
    assert post(client, headers, "create_proposal", foreign).status_code == 404
    command = approve(data)
    assert post(client, headers, "approve_and_commit_proposal", command).status_code == 200
    with psycopg.connect(admin) as c:
        c.execute("UPDATE queue_memberships SET active=false")
    assert post(client, headers, "approve_and_commit_proposal", command).status_code == 404


def test_concurrent_edits_and_atomic_failure(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    original, data = draft(client, headers, contact)

    def edit(i):
        with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as parallel:
            return post(
                parallel,
                headers,
                "edit_proposal",
                {
                    "proposal_id": data["proposal_id"],
                    "expected_proposal_version": 1,
                    "expected_case_version": None,
                    "expected_work_version": None,
                    "replacement": {
                        "kind": "note",
                        "payload": {
                            **original["proposal"]["payload"],
                            "body": f"Reviewed revision {i}.",
                        },
                    },
                    "operation_key": str(uuid4()),
                },
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(edit, range(2))) == [200, 409]
    with psycopg.connect(admin) as c:
        c.execute("REVOKE INSERT ON outbox_events FROM bank_app")
    try:
        assert (
            post(
                client,
                headers,
                "approve_and_commit_proposal",
                approve(data, expected_proposal_version="2"),
            ).status_code
            == 503
        )
        with psycopg.connect(admin) as c:
            assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
            assert (
                c.execute(
                    "SELECT count(*) FROM operations WHERE command='approve_and_commit_proposal'"
                ).fetchone()[0]
                == 0
            )
            assert c.execute("SELECT status FROM proposals").fetchone()[0] == "draft"
    finally:
        with psycopg.connect(admin) as c:
            c.execute("GRANT INSERT ON outbox_events TO bank_app")
