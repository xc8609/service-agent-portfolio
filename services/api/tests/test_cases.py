import json
from datetime import datetime, timedelta
from uuid import uuid4

import psycopg
import pytest
from bank_api.app import TOOLS, create_app
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker


def related(client, headers, contact, names=("equal_1", "equal_2")):
    return client.post(
        "/v1/workspace/get_related_cases",
        headers=headers,
        json={"contact_id": contact, "transaction_ids": [uid("tx_" + n) for n in names]},
    )


def snapshot(client, headers, contact, case="duplicate_case", **changes):
    return client.post(
        "/v1/agent-tools/get_case_snapshot",
        headers=headers,
        json={
            "contact_id": contact,
            "case_id": uid(case),
            "expected_work_version": None,
            **changes,
        },
    )


def test_pair_progress_owners_due_dates_and_canonical_contract(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    response = related(client, headers, contact)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["review_state"] == "review_existing_work"
    case = data["cases"][0]
    assert case["reference"] == "DEMO-CASE-001"
    assert (
        case["coverage"] == "full_selection" and case["review_hint"] == "potential_existing_enquiry"
    )
    assert len(case["matched_transaction_ids"]) == 2
    assert case["snapshot"]["investigation_status"] == "awaiting_documents"
    assert case["snapshot"]["feedback_status"] == "waiting_for_result"
    work = {w["kind"]: w for w in case["work_items"]}
    assert work["specialist_investigation"]["assignee_name"] == "Demo specialist Alex"
    assert work["customer_feedback"]["assignee_name"] is None
    assert work["customer_feedback"]["due_at"] is None
    assert work["customer_feedback"]["original_due_at"] is None
    assert datetime.fromisoformat(
        work["specialist_investigation"]["original_due_at"]
    ) == datetime.fromisoformat("2026-10-21T14:00:00+00:00")
    r = snapshot(client, headers, contact)
    assert r.status_code == 200, r.text
    Draft202012Validator(
        TOOLS["get_case_snapshot"]["success_schema"], format_checker=FormatChecker()
    ).validate(r.json())
    assert r.json()["data"] == case["snapshot"]
    assert len([s for s in r.json()["meta"]["sources"] if s["kind"] == "work_item"]) == 4
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM cases").fetchone()[0] == 3
        audits = c.execute("SELECT safe_details FROM audit_events").fetchall()
        assert all(set(a[0]) == {"outcome", "request_id"} for a in audits)


def test_pending_and_private_information_never_disclosed(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute(
            """INSERT INTO investigation_results VALUES (%s,%s,%s,%s,1,'review', '[]','Published synthetic explanation',%s)""",
            (
                uid("published_result"),
                uid("duplicate_case"),
                uid("investigation_work"),
                uid("Demo specialist Alex"),
                NOW,
            ),
        )
        c.execute(
            "INSERT INTO result_private_notes VALUES (%s,%s,%s)",
            (uuid4(), uid("published_result"), "SECRET PRIVATE FINDING"),
        )
    data = related(client, headers, contact).json()["cases"][0]["snapshot"]
    assert data["progress_commitments"] == []
    assert data["approved_customer_explanation"] == "Published synthetic explanation"
    assert "PRIVATE" not in json.dumps(data) and "INTERNAL" not in json.dumps(data)
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE update_commitments SET status='approved',decided_by=%s,decided_at=%s,customer_safe_progress='Approved progress only'",
            (uid("lead"), NOW),
        )
    data = related(client, headers, contact).json()["cases"][0]["snapshot"]
    assert data["progress_commitments"][0]["customer_safe_progress"] == "Approved progress only"
    assert data["progress_commitments"][0]["status"] == "approved"


def test_timeline_uses_sequence_not_ingestion_or_occurrence_order(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE case_timeline_events SET recorded_at=%s,occurred_at=%s WHERE id=%s",
            (NOW + timedelta(days=1), NOW, uid("duplicate_case_event_1")),
        )
    data = snapshot(client, headers, contact).json()["data"]
    assert [e["sequence"] for e in data["timeline"]] == [1, 2]
    assert data["timeline"][0]["recorded_at"] > data["timeline"][1]["recorded_at"]
    assert data["case_status"] == "investigating"


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE cases SET version=99 WHERE public_reference='DEMO-CASE-001'",
        "UPDATE cases SET status='closed' WHERE public_reference='DEMO-CASE-001'",
        "UPDATE cases SET timeline_sequence=99 WHERE public_reference='DEMO-CASE-001'",
        "DELETE FROM case_timeline_events WHERE aggregate_sequence=1",
        "UPDATE cases SET status_recorded_at=NULL WHERE public_reference='DEMO-CASE-001'",
    ],
)
def test_conflicting_head_is_not_empty_or_closed_success(environment, mutation):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute(mutation)
    for r in [related(client, headers, contact), snapshot(client, headers, contact)]:
        assert r.status_code == 409 and r.json()["error"]["code"] == "STALE_VERSION"
        assert "cases" not in r.json() and "data" not in r.json()


def test_parallel_work_has_separate_status_and_refreshes_owner(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    before = related(client, headers, contact).json()["cases"][0]
    linked = {w["kind"]: w for w in before["snapshot"]["linked_work"]}
    assert linked["specialist_rereview"]["status"] == "completed"
    assert linked["complaint_intake"]["status"] == "in_progress"
    assert linked["specialist_rereview"]["owner_queue"] != linked["complaint_intake"]["owner_queue"]
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE work_items SET assignee_id=%s,version=2,due_at=%s WHERE id=%s",
            (uid("Demo callback Sam"), NOW + timedelta(days=3), uid("investigation_work")),
        )
    after = related(client, headers, contact).json()["cases"][0]
    work = next(w for w in after["work_items"] if w["kind"] == "specialist_investigation")
    assert work["assignee_name"] == "Demo callback Sam" and work["version"] == "2"
    assert work["original_due_at"] != work["due_at"]
    assert after["snapshot"]["case_status"] == "investigating"


def test_same_customer_case_requires_every_linked_account_in_scope(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute(
            "INSERT INTO case_transactions VALUES (%s,%s,%s)",
            (uuid4(), uid("duplicate_case"), uid("tx_private")),
        )
    assert snapshot(client, headers, contact).status_code == 404
    assert related(client, headers, contact).status_code == 404


def test_foreign_missing_and_mixed_selection_uniform_denial(environment):
    client, *_ = environment
    headers, contact = session(client)
    a = snapshot(client, headers, contact, "private_case")
    b = snapshot(client, headers, contact, "missing_case")
    assert a.status_code == b.status_code == 404 and a.json()["error"] == b.json()["error"]
    assert related(client, headers, contact, ("equal_1", "private")).status_code == 404
    assert related(client, headers, uid("contact_b")).status_code == 404
    other, cid = session(client, "other_customer")
    assert (
        related(client, other, cid, ("private",)).json()["cases"][0]["reference"]
        == "DEMO-CASE-PRIVATE"
    )


@pytest.mark.parametrize(
    "persona,status",
    [
        ("unverified", 401),
        ("expired", 401),
        ("feedback_unclaimed", 404),
        ("agent", 404),
        ("lead", 404),
    ],
)
def test_unsupported_context_denies_case_reads(environment, persona, status):
    client, *_ = environment
    headers, contact = session(client, persona)
    assert related(client, headers, contact).status_code == status
    assert snapshot(client, headers, contact).status_code == status


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE queue_memberships SET active=false",
        "UPDATE verification_assertions SET expires_at='2020-01-01'",
        "UPDATE contacts SET status='closed'",
    ],
)
def test_each_refresh_rechecks_authority(environment, mutation):
    client, admin, _, _ = environment
    headers, contact = session(client)
    assert related(client, headers, contact).status_code == 200
    with psycopg.connect(admin) as c:
        c.execute(mutation)
    assert related(client, headers, contact).status_code in (401, 404)
    assert snapshot(client, headers, contact).status_code in (401, 404)


def test_review_hints_do_not_overstate_duplicates(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    assert (
        related(client, headers, contact, ("pending", "posted")).json()["review_state"]
        == "no_linked_case_found"
    )
    partial = related(client, headers, contact, ("equal_1", "posted")).json()["cases"][0]
    assert partial["coverage"] == "partial_selection"
    assert partial["review_hint"] == "review_overlap_and_concern"
    closed = related(client, headers, contact, ("reversed",)).json()["cases"][0]
    assert closed["review_hint"] == "review_closed_case"
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE cases SET concern_code='merchant_information' WHERE public_reference='DEMO-CASE-001'"
        )
    assert (
        related(client, headers, contact).json()["cases"][0]["review_hint"]
        == "review_overlap_and_concern"
    )


def test_bad_inputs_and_outage_never_look_like_no_case(environment):
    client, _, runtime, _ = environment
    headers, contact = session(client)
    assert related(client, headers, contact, ()).status_code == 422
    assert related(client, headers, contact, ("equal_1", "equal_1")).status_code == 422
    assert snapshot(client, headers, contact, expected_work_version=1).status_code == 422
    assert snapshot(client, headers, contact, role="lead").status_code == 422
    with TestClient(
        create_app(Settings("postgresql://bank_app:unused@127.0.0.1:1/bank_demo"))
    ) as broken:
        assert related(broken, headers, contact).status_code == 503
        assert snapshot(broken, headers, contact).status_code == 503
    for statement in [
        "UPDATE cases SET status='closed'",
        "DELETE FROM case_timeline_events",
        "SELECT * FROM result_private_notes",
    ]:
        with psycopg.connect(runtime) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)


def test_unknown_case_status_requires_review_not_active_duplicate_hint(environment):
    client, admin, _, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute("UPDATE cases SET status='source_unknown' WHERE id=%s", (uid("duplicate_case"),))
        c.execute(
            "UPDATE case_timeline_events SET case_status='source_unknown' WHERE case_id=%s AND aggregate_sequence=2",
            (uid("duplicate_case"),),
        )
    case = related(client, headers, contact).json()["cases"][0]
    assert case["review_hint"] == "review_overlap_and_concern"
