import json
from datetime import timedelta
from uuid import uuid4

import psycopg
import pytest
from bank_api.app import CONTRACTS, TOOLS, create_app
from bank_api.config import Settings
from bank_api.db import migrate
from bank_api.fixtures import reset, seed, uid
from conftest import NOW, session
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker


def search_payload(contact, **changes):
    return {
        "contact_id": contact,
        "card_ref": "DEMO-4242",
        "date_from": "2026-10-01",
        "date_to": "2026-10-31",
        "amount_minor": None,
        "merchant_query": None,
        "cursor": None,
        "limit": 50,
        **changes,
    }


def call(client, tool, payload, headers):
    r = client.post("/v1/agent-tools/" + tool, json=payload, headers=headers)
    schema = TOOLS[tool]["success_schema"] if r.status_code == 200 else CONTRACTS["error_schema"]
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(r.json())
    return r


def test_migrations_seed_idempotent_constraints(environment):
    _, admin, _, target = environment

    def snapshot():
        with psycopg.connect(admin) as c:
            return [
                c.execute("SELECT * FROM " + table + " ORDER BY 1").fetchall()
                for table in [
                    "schema_migrations",
                    "customers",
                    "contacts",
                    "card_accounts",
                    "card_transactions",
                    "verification_assertions",
                ]
            ]

    before = snapshot()
    migrate(admin)
    seed(admin, target, now=NOW + timedelta(days=1))
    assert snapshot() == before
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM pg_constraint WHERE contype='f'").fetchone()[0] >= 70
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            c.execute("UPDATE card_transactions SET account_id=%s", (uuid4(),))
    with psycopg.connect(admin) as c:
        with pytest.raises(psycopg.errors.CheckViolation):
            c.execute("UPDATE card_transactions SET status='duplicate' ")


def test_verified_lookup_and_contract_provenance(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    context = call(client, "get_contact_context", {"contact_id": contact}, headers).json()
    assert context["data"]["masked_card_refs"] == ["DEMO-4242"]
    assert context["data"]["allowed_actions"] == [
        "customer.read_context",
        "transaction.read",
    ]
    result = call(client, "search_transactions", search_payload(contact), headers).json()
    assert len(result["data"]["records"]) == 6
    assert {r["status"] for r in result["data"]["records"]} == {
        "pending",
        "posted",
        "reversed",
    }
    assert all(r["version"] == "1" for r in result["data"]["records"])
    assert len(result["meta"]["sources"]) == 7
    assert "PRIVATE MERCHANT" not in json.dumps(result)
    with psycopg.connect(admin) as c:
        audits = c.execute("SELECT actor_ref,safe_details FROM audit_events").fetchall()
        assert len(audits) == 2
        assert all(set(a[1]) == {"outcome", "request_id"} for a in audits)
        assert "Bearer" not in json.dumps(audits)


@pytest.mark.parametrize(
    "persona,code",
    [
        ("unverified", "AUTH_REQUIRED"),
        ("expired", "AUTH_REQUIRED"),
        ("feedback_unclaimed", "FORBIDDEN_OR_NOT_FOUND"),
        ("agent", "FORBIDDEN_OR_NOT_FOUND"),
        ("lead", "FORBIDDEN_OR_NOT_FOUND"),
    ],
)
def test_unsupported_or_unverified_denied(environment, persona, code):
    client, *_ = environment
    headers, contact = session(client, persona)
    for tool, payload in [
        ("get_contact_context", {"contact_id": contact}),
        ("search_transactions", search_payload(contact)),
        (
            "get_transaction_evidence",
            {"contact_id": contact, "transaction_ids": [uid("tx_posted")]},
        ),
    ]:
        r = call(client, tool, payload, headers)
        assert r.json()["error"]["code"] == code and "data" not in r.json()


def test_sessions_and_revocation_rechecked(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    assert call(client, "get_contact_context", {"contact_id": contact}, {}).status_code == 401
    with TestClient(
        create_app(Settings(runtime), clock=lambda: NOW + timedelta(minutes=16))
    ) as later:
        assert (
            call(later, "get_contact_context", {"contact_id": contact}, headers).status_code == 401
        )
    with psycopg.connect(admin) as c:
        c.execute("UPDATE staff_principals SET active=false WHERE id=%s", (uid("rep_a"),))
    assert call(client, "get_contact_context", {"contact_id": contact}, headers).status_code == 401


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE queue_memberships SET active=false",
        "UPDATE service_queues SET active=false",
        "UPDATE contacts SET status='closed'",
        "UPDATE verification_assertions SET expires_at='2020-01-01'",
        "UPDATE verification_assertions SET state='unverified'",
        "UPDATE verification_assertions SET scope_json='{\"account_ids\":[]}'",
    ],
)
def test_scope_revocation_on_each_request(environment, mutation):
    client, admin, _, _ = environment
    headers, contact = session(client)
    assert call(client, "search_transactions", search_payload(contact), headers).status_code == 200
    with psycopg.connect(admin) as c:
        c.execute(mutation)
    r = call(client, "search_transactions", search_payload(contact), headers)
    assert r.status_code in (401, 404) and "data" not in r.json()


def test_cross_customer_uniform_denial_and_no_partial_response(environment):
    client, *_ = environment
    headers, contact = session(client)
    inaccessible = call(
        client,
        "get_transaction_evidence",
        {
            "contact_id": contact,
            "transaction_ids": [uid("tx_posted"), uid("tx_private")],
        },
        headers,
    )
    nonexistent = call(
        client,
        "get_transaction_evidence",
        {"contact_id": contact, "transaction_ids": [str(uuid4())]},
        headers,
    )
    assert inaccessible.status_code == nonexistent.status_code == 404
    assert inaccessible.json()["error"] == nonexistent.json()["error"]
    assert "records" not in inaccessible.text
    for cid in [uid("contact_b"), str(uuid4())]:
        assert call(client, "get_contact_context", {"contact_id": cid}, headers).status_code == 404
    for card in ["DEMO-8585", "MISSING"]:
        assert (
            call(
                client,
                "search_transactions",
                search_payload(contact, card_ref=card),
                headers,
            ).status_code
            == 404
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"role": "queue_lead"},
        {"customer_id": "other"},
        {"amount_minor": 1.1},
        {"limit": 51},
        {"limit": True},
        {"date_from": "2026-02-30"},
        {"date_from": "2027-01-01"},
        {"merchant_query": "x" * 121},
        {"cursor": "notbase64"},
        {"amount_minor": 10**40},
    ],
)
def test_validation_rejects_scope_injection_and_bad_inputs(environment, changes):
    client, *_ = environment
    headers, contact = session(client)
    r = call(client, "search_transactions", search_payload(contact, **changes), headers)
    assert r.status_code == 422
    assert "other" not in r.text


def test_pagination_filter_binding_literal_search(environment):
    client, *_ = environment
    headers, contact = session(client)
    payload = search_payload(contact, limit=2)
    ids = []
    while True:
        data = call(client, "search_transactions", payload, headers).json()["data"]
        ids.extend(r["id"] for r in data["records"])
        if not data["next_cursor"]:
            break
        payload["cursor"] = data["next_cursor"]
    assert len(set(ids)) == len(ids) == 6
    mismatch = search_payload(contact, cursor=payload["cursor"], merchant_query="other")
    assert call(client, "search_transactions", mismatch, headers).status_code == 422
    filtered = call(
        client,
        "search_transactions",
        search_payload(contact, amount_minor=8500, merchant_query="demo store"),
        headers,
    ).json()
    assert len(filtered["data"]["records"]) == 2
    for text in ["%' OR 1=1 --", "%", "_"]:
        assert (
            call(
                client,
                "search_transactions",
                search_payload(contact, merchant_query=text),
                headers,
            ).json()["data"]["records"]
            == []
        )


def test_evidence_does_not_infer_duplicate_or_financial_action(environment):
    client, *_ = environment
    headers, contact = session(client)

    def evidence(*names):
        return call(
            client,
            "get_transaction_evidence",
            {"contact_id": contact, "transaction_ids": [uid("tx_" + n) for n in names]},
            headers,
        ).json()["data"]

    equal = evidence("equal_1", "equal_2")
    assert (
        equal["relationships"] == []
        and "do not establish a duplicate" in equal["missing_evidence"][0]
    )
    pair = evidence("pending", "posted")
    assert len(pair["relationships"]) == 1
    assert "not a refund" in pair["missing_evidence"][0]
    assert evidence("reversed")["records"][0]["status"] == "reversed"
    assert evidence("missing")["missing_evidence"]
    assert client.post("/v1/commands/refund", headers=headers, json={}).status_code == 404
    assert (
        client.post(
            "/v1/commands/approve_and_commit_proposal", headers=headers, json={}
        ).status_code
        == 404
    )


def test_runtime_db_cannot_modify_ledger_or_read_internal_notes(environment):
    _, _, runtime, _ = environment
    for statement in [
        "DELETE FROM card_transactions",
        "SELECT * FROM result_private_notes",
        "DROP TABLE contacts",
    ]:
        with psycopg.connect(runtime) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)


def test_readiness_outage_and_public_mode(environment):
    client, _, _, _ = environment
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").json()["schema_version"] == "002_lookup.sql"
    with TestClient(
        create_app(Settings("postgresql://bank_app:unused@127.0.0.1:1/bank_demo"))
    ) as broken:
        assert broken.get("/health/live").status_code == 200
        r = broken.get("/health/ready")
        assert r.status_code == 503 and "127.0.0.1" not in r.text
        r = call(
            broken,
            "get_contact_context",
            {"contact_id": uid("contact_a")},
            {"Authorization": "Bearer fake"},
        )
        assert r.status_code == 503 and "data" not in r.json()
    with pytest.raises(ValueError):
        Settings("postgresql://localhost/bank_demo", mode="production")
    with pytest.raises(ValueError):
        Settings("sqlite://local")
    assert (
        client.post(
            "/v1/demo/session",
            json={"persona": "verified"},
            headers={"Origin": "https://evil.invalid"},
        ).status_code
        == 404
    )
    assert client.get("/health/live", headers={"Host": "evil.invalid"}).status_code == 400


def test_reset_requires_marker_and_matching_target(environment):
    _, admin, _, target = environment
    with pytest.raises(ValueError):
        reset(admin, "bank_demo_wrong")
    with psycopg.connect(admin) as c:
        c.execute("DELETE FROM demo_environment")
    with pytest.raises(ValueError):
        reset(admin, target)
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM card_transactions").fetchone()[0] == 7
    # Restore the marker for subsequent tests only using an explicit test fixture.
    with psycopg.connect(admin) as c:
        c.execute(
            "INSERT INTO demo_environment VALUES (true,'service-agent-disposable-v1',%s,'bank-lookup-synthetic-v1')",
            (target,),
        )
