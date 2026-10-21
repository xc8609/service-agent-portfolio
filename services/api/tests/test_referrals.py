from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import uuid4

import psycopg
import pytest
from bank_api.app import create_app
from bank_api.calendar import add_hours, contact_window
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient
from test_investigation import payload as report_payload
from test_investigation import save as save_report
from test_notes import approve, post


def prepare(client, headers, contact):
    report = save_report(client, headers, report_payload(contact))
    assert report.status_code == 200, report.text
    r = client.post(
        "/v1/workspace/prepare_referral",
        headers=headers,
        json={"contact_id": contact, "transaction_ids": [uid("tx_equal_1"), uid("tx_equal_2")]},
    )
    assert r.status_code == 200, r.text
    return r.json()["data"]


def create(client, headers, contact, prepared):
    p = {
        "contact_id": contact,
        "expected_context_version": prepared["context_version"],
        "source_refs": prepared["source_refs"],
        "proposal": {"kind": "referral", "payload": prepared["payload"]},
        "operation_key": str(uuid4()),
    }
    r = post(client, headers, "create_proposal", p)
    assert r.status_code == 200, r.text
    return r.json()["data"]


def test_link_existing_preserves_deadline_and_no_duplicate(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    prepared = prepare(client, headers, contact)
    assert prepared["policy_state"] == "applicable"
    assert prepared["payload"]["intake"]["recognition"] == "one_purchase_unresolved"
    assert prepared["payload"]["intake"]["recognized_transaction_id"] is None
    prepared["payload"]["intake"]["customer_summary_confirmed"] = True
    with psycopg.connect(admin) as c:
        before = c.execute("SELECT count(*) FROM cases").fetchone()[0]
        due = c.execute(
            "SELECT original_due_at FROM work_items WHERE case_id=%s AND kind='specialist_investigation'",
            (uid("duplicate_case"),),
        ).fetchone()[0]
    draft = create(client, headers, contact, prepared)
    command = approve(draft)
    r = post(client, headers, "approve_and_commit_proposal", command)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["domain_ref"] == uid("duplicate_case")
    assert post(client, headers, "approve_and_commit_proposal", command).json() == r.json()
    history = client.post(
        "/v1/workspace/get_referrals", headers=headers, json={"contact_id": contact}
    )
    assert history.json()["referrals"][0]["disposition"] == "linked_existing"
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM cases").fetchone()[0] == before
        assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 1
        assert (
            c.execute(
                "SELECT count(*) FROM outbox_events WHERE event_type='referral.reviewed'"
            ).fetchone()[0]
            == 1
        )
        assert (
            c.execute(
                "SELECT original_due_at FROM work_items WHERE case_id=%s AND kind='specialist_investigation'",
                (uid("duplicate_case"),),
            ).fetchone()[0]
            == due
        )


def test_distinct_enquiry_with_material_contact_gaps_has_owned_work(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    i = p["payload"]["intake"]
    i.update(
        mode="new",
        distinct_work_reason="Separate posted-entry concern requiring distinct source reconciliation.",
        customer_summary_confirmed=True,
    )
    i["material_gaps"] = [
        {
            "item": "Receipt",
            "state": "unavailable",
            "owner": "specialist",
            "next_action": "assess_need",
            "review_trigger": "specialist_acceptance",
        }
    ]
    i["contact"] = {
        "state": "unavailable",
        "method_ref": None,
        "method_version": None,
        "reason": "Customer reports existing phone is unusable.",
    }
    draft = create(client, headers, contact, p)
    r = post(client, headers, "approve_and_commit_proposal", approve(draft))
    assert r.status_code == 200, r.text
    case = r.json()["data"]["domain_ref"]
    with psycopg.connect(admin) as c:
        work = c.execute(
            "SELECT kind,status,queue_id,due_at,original_due_at,acceptance_due_at FROM work_items WHERE case_id=%s ORDER BY kind",
            (case,),
        ).fetchall()
        assert [w[0] for w in work] == ["contact_resolution", "specialist_investigation"]
        assert all(w[1] == "queued" and w[3] == w[4] for w in work)
        assert str(work[0][2]) == uid("feedback_queue")
        assert work[1][3] == add_hours(NOW, 16) and work[1][5] == add_hours(NOW, 8)
        assert c.execute("SELECT closed_at FROM cases WHERE id=%s", (case,)).fetchone()[0] is None
    snap = client.post(
        "/v1/agent-tools/get_case_snapshot",
        headers=headers,
        json={"contact_id": contact, "case_id": case, "expected_work_version": None},
    )
    assert snap.status_code == 200, snap.text
    assert snap.json()["data"]["investigation_status"] == "queued"


def test_duplicate_reason_required_and_summary_not_optional(environment):
    client, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    draft = create(client, headers, contact, p)
    assert post(client, headers, "approve_and_commit_proposal", approve(draft)).status_code == 422
    p["payload"]["intake"]["mode"] = "new"
    r = post(
        client,
        headers,
        "create_proposal",
        {
            "contact_id": contact,
            "expected_context_version": p["context_version"],
            "source_refs": p["source_refs"],
            "operation_key": str(uuid4()),
            "proposal": {"kind": "referral", "payload": p["payload"]},
        },
    )
    assert r.json()["error"]["code"] == "DUPLICATE_REVIEW_REQUIRED"


@pytest.mark.parametrize("change", ["queue", "policy", "report", "contact", "scope"])
def test_changed_context_blocks_referral_without_partial_write(environment, change):
    client, admin, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    p["payload"]["intake"]["customer_summary_confirmed"] = True
    draft = create(client, headers, contact, p)
    with psycopg.connect(admin) as c:
        if change == "queue":
            c.execute(
                "UPDATE service_queues SET active=false WHERE id=%s", (uid("specialist_queue"),)
            )
        if change == "policy":
            c.execute("UPDATE policy_versions SET version=version || '-changed'")
        if change == "contact":
            c.execute("UPDATE customer_contact_methods SET version=2")
        if change == "scope":
            c.execute("UPDATE queue_memberships SET active=false")
    if change == "report":
        assert (
            save_report(
                client,
                headers,
                report_payload(contact, expected_revision=1, statement="New account of events."),
            ).status_code
            == 200
        )
    r = post(client, headers, "approve_and_commit_proposal", approve(draft))
    assert r.status_code in (404, 409, 503), r.text
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 0
        assert (
            c.execute(
                "SELECT count(*) FROM operations WHERE command='approve_and_commit_proposal'"
            ).fetchone()[0]
            == 0
        )


def test_reject_unresolved_mapping_with_invented_recognized_entry(environment):
    client, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    p["payload"]["intake"]["recognized_transaction_id"] = uid("tx_equal_1")
    r = post(
        client,
        headers,
        "create_proposal",
        {
            "contact_id": contact,
            "expected_context_version": p["context_version"],
            "source_refs": p["source_refs"],
            "operation_key": str(uuid4()),
            "proposal": {"kind": "referral", "payload": p["payload"]},
        },
    )
    assert r.status_code == 409


def test_competing_keys_for_same_draft_commit_one_referral(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    p["payload"]["intake"].update(
        mode="new",
        distinct_work_reason="Separate issue for review.",
        customer_summary_confirmed=True,
    )
    draft = create(client, headers, contact, p)

    def submit(_):
        with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as other:
            return post(other, headers, "approve_and_commit_proposal", approve(draft)).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(submit, range(2))) == [200, 409]
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 1


def test_referral_atomicity_and_no_model_authority(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    p["payload"]["intake"].update(
        mode="new", distinct_work_reason="Separate concern.", customer_summary_confirmed=True
    )
    draft = create(client, headers, contact, p)
    model, _ = session(client, "agent")
    assert post(client, model, "approve_and_commit_proposal", approve(draft)).status_code == 404
    with psycopg.connect(admin) as c:
        count = c.execute("SELECT count(*) FROM cases").fetchone()[0]
        c.execute("REVOKE INSERT ON outbox_events FROM bank_app")
    try:
        assert (
            post(client, headers, "approve_and_commit_proposal", approve(draft)).status_code == 503
        )
        with psycopg.connect(admin) as c:
            assert c.execute("SELECT count(*) FROM cases").fetchone()[0] == count
            assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 0
    finally:
        with psycopg.connect(admin) as c:
            c.execute("GRANT INSERT ON outbox_events TO bank_app")


def test_calendar_service_hours_and_day_window():
    friday = datetime.fromisoformat("2026-10-23T16:00:00-05:00")
    assert add_hours(friday, 16, ["2026-10-26"]).isoformat() == "2026-10-28T16:00:00-05:00"
    assert contact_window(friday, ["2026-10-26"]).isoformat() == "2026-10-28T17:00:00-05:00"


def test_no_existing_work_concurrent_drafts_do_not_create_duplicate(environment):
    client, admin, runtime, _ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE cases SET concern_code='other_enquiry' WHERE id=%s", (uid("duplicate_case"),)
        )
    p = prepare(client, headers, contact)
    assert p["payload"]["intake"]["mode"] == "new"
    p["payload"]["intake"]["customer_summary_confirmed"] = True
    drafts = [create(client, headers, contact, p) for _ in range(2)]

    def submit(d):
        with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as other:
            return post(other, headers, "approve_and_commit_proposal", approve(d)).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(submit, drafts)) == [200, 409]
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 1


def test_missing_policy_has_explicit_configured_manual_route(environment):
    client, admin, *_ = environment
    headers, contact = session(client)
    with psycopg.connect(admin) as c:
        c.execute("UPDATE policy_versions SET published=false")
    p = prepare(client, headers, contact)
    assert p["policy_state"] == "manual_review_required"
    assert p["payload"]["intake"]["route_basis"] == "manual_policy_review"
    assert not any(r["kind"] == "policy" for r in p["source_refs"])
    p["payload"]["intake"]["customer_summary_confirmed"] = True
    draft = create(client, headers, contact, p)
    assert post(client, headers, "approve_and_commit_proposal", approve(draft)).status_code == 200


@pytest.mark.parametrize("mode", ["new", "link_existing"])
def test_assigned_handoff_preserves_intake_revisions_and_scope(environment, mode):
    from test_workflow import call, detail, find_work, pair

    client, _, *_ = environment
    headers, contact = session(client)
    p = prepare(client, headers, contact)
    i = p["payload"]["intake"]
    i.update(
        mode=mode,
        customer_summary_confirmed=True,
        distinct_work_reason="Independent synthetic handoff check." if mode == "new" else None,
    )
    i["material_gaps"] = [
        {
            "item": "Receipt",
            "state": "unavailable",
            "owner": "specialist",
            "next_action": "assess_need",
            "review_trigger": "specialist_acceptance",
        }
    ]
    i["contact"] = {
        "state": "unavailable",
        "method_ref": None,
        "method_version": None,
        "reason": "Phone is unusable; customer service must resolve.",
    }
    first_payload = p["payload"]
    result = post(
        client, headers, "approve_and_commit_proposal", approve(create(client, headers, contact, p))
    )
    assert result.status_code == 200, result.text
    case = result.json()["data"]["domain_ref"]
    specialist, _ = session(client, "specialist")
    work = find_work(client, specialist, "specialist_investigation", case)
    outsider, _ = session(client, "feedback_other")
    assert call(client, outsider, "get_work_detail", pair(work)).status_code == 404
    if mode == "new":
        assert call(client, specialist, "get_work_detail", pair(work)).status_code == 404
        assert (
            call(
                client,
                specialist,
                "accept_specialist_work",
                {
                    **pair(work),
                    "expected_work_version": work["version"],
                    "operation_key": str(uuid4()),
                },
            ).status_code
            == 200
        )
    before = detail(client, specialist, work)
    assert before["intakes"][0]["payload"] == first_payload
    assert before["intakes"][0]["id"] and before["intakes"][0]["committed_at"]
    assert {t["id"] for t in before["transactions"]} == set(first_payload["transaction_ids"])
    assert all(
        t["amount_minor"] == 8500 and t["currency"] and t["occurred_at"]
        for t in before["transactions"]
    )
    saved = save_report(
        client,
        headers,
        report_payload(
            contact,
            expected_revision=1,
            statement="Updated customer statement; still only one purchase.",
        ),
    )
    assert saved.status_code == 200, saved.text
    fresh = client.post(
        "/v1/workspace/prepare_referral",
        headers=headers,
        json={"contact_id": contact, "transaction_ids": first_payload["transaction_ids"]},
    ).json()["data"]
    fresh["payload"]["related_case_id"] = case
    fresh["payload"]["intake"].update(mode="link_existing", customer_summary_confirmed=True)
    result = post(
        client,
        headers,
        "approve_and_commit_proposal",
        approve(create(client, headers, contact, fresh)),
    )
    assert result.status_code == 200, result.text
    after = detail(client, specialist, work)
    assert {r["payload"]["intake"]["statement_revision"] for r in after["intakes"]} == {1, 2}
    assert (
        next(r for r in after["intakes"] if r["id"] == before["intakes"][0]["id"])
        == before["intakes"][0]
    )
    assert after["work"]["original_due_at"] == before["work"]["original_due_at"]
