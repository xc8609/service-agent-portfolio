from datetime import timedelta
from uuid import uuid4

import psycopg
from bank_api.config import Settings
from bank_api.fixtures import uid
from bank_api.worker import tick
from conftest import NOW, session
from test_workflow import call, detail, find_work, pair, publish, setup_feedback


def command(client, h, name, p):
    return client.post("/v1/commands/" + name, headers=h, json=p)


def overdue(environment):
    client, admin, runtime, _ = environment
    h, _ = session(client, "specialist")
    w = find_work(client, h, "specialist_investigation", uid("duplicate_case"))
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE work_items SET due_at=%s,original_due_at=%s WHERE id=%s",
            (NOW - timedelta(hours=1), NOW - timedelta(hours=1), w["id"]),
        )
    return client, h, w, runtime


def propose(client, h, w):
    d = detail(client, h, w)
    p = {
        **pair(w),
        "expected_case_version": d["work"]["case_version"],
        "expected_work_version": d["work"]["version"],
        "proposed_update_at": (NOW + timedelta(hours=4)).isoformat(),
        "customer_safe_progress": "Investigation continues; the blocker has not been confirmed.",
        "reason": "Pending specialist evidence review.",
        "operation_key": str(uuid4()),
    }
    r = command(client, h, "propose_next_update", p)
    assert r.status_code == 200, r.text
    return r.json()["data"]


def confirm(client, h, w, c):
    d = detail(client, h, w)
    return command(
        client,
        h,
        "confirm_next_update",
        {
            **pair(w),
            "expected_case_version": d["work"]["case_version"],
            "expected_work_version": d["work"]["version"],
            "commitment_id": c["commitment_id"],
            "expected_commitment_version": c["version"],
            "decision": "approve",
            "reason": "Reviewed current investigation and update feasibility.",
            "operation_key": str(uuid4()),
        },
    )


def test_overdue_deduplicates_and_keeps_original_owner_and_deadline(environment):
    client, h, w, runtime = overdue(environment)
    before = detail(client, h, w)["work"]
    tick(Settings(runtime), NOW)
    tick(Settings(runtime), NOW)
    d = detail(client, h, w)
    assert (
        d["work"]["original_due_at"] == before["original_due_at"]
        and d["work"]["assignee_id"] == before["assignee_id"]
    )
    # One escalation per case, deadline and level: the new progress task is not born overdue.
    assert [e["work_item_id"] for e in d["overdue_events"]] == [w["id"]]
    with psycopg.connect(environment[1]) as c:
        assert (
            c.execute(
                "SELECT count(*) FROM work_items WHERE parent_work_id=%s AND kind='progress_callback'",
                (w["id"],),
            ).fetchone()[0]
            == 1
        )
        assert c.execute("SELECT count(*) FROM local_notifications").fetchone()[0] > 0
        assert (
            c.execute(
                "SELECT count(*) FROM case_timeline_events WHERE case_id=%s AND event_type='work.overdue'",
                (w["case_id"],),
            ).fetchone()[0]
            == 1
        )
        progress_due = c.execute(
            "SELECT original_due_at FROM work_items WHERE parent_work_id=%s AND kind='progress_callback'",
            (w["id"],),
        ).fetchone()[0]
        assert progress_due > NOW


def test_update_commitment_requires_lead_and_current_investigation(environment):
    client, h, w, _ = overdue(environment)
    proposal = propose(client, h, w)
    assert confirm(client, h, w, proposal).status_code == 404
    lead, _ = session(client, "lead")
    r = confirm(client, lead, w, proposal)
    assert r.status_code == 200, r.text
    second = propose(client, h, w)
    r, _ = publish(client, h, w)
    assert r.status_code == 200
    assert confirm(client, lead, w, second).status_code == 409
    with psycopg.connect(environment[1]) as conn:
        pending = conn.execute(
            "SELECT status,decision_reason FROM update_commitments WHERE id=%s",
            (second["commitment_id"],),
        ).fetchone()
        assert pending == ("superseded", "Superseded by published finding; not an approval")


def test_result_supersedes_open_progress_contact_without_erasing_overdue_history(environment):
    client, specialist, investigation, runtime = overdue(environment)
    tick(Settings(runtime), NOW)
    proposed = propose(client, specialist, investigation)
    lead, _ = session(client, "lead")
    assert confirm(client, lead, investigation, proposed).status_code == 200
    feedback, _ = session(client, "feedback_unclaimed")
    progress = find_work(client, feedback, "progress_callback", investigation["case_id"])
    assert (
        call(
            client,
            feedback,
            "claim_feedback_task",
            {
                **pair(progress),
                "expected_work_version": progress["version"],
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 200
    )
    before = detail(client, feedback, progress)
    opened = call(
        client,
        feedback,
        "open_progress_contact",
        {
            **pair(progress),
            "expected_work_version": before["work"]["version"],
            "operation_key": str(uuid4()),
        },
    ).json()
    assert (
        call(
            client,
            feedback,
            "demo_callback_verification",
            {
                "callback_contact_id": opened["contact_id"],
                "scenario": "verified",
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 200
    )
    disclosure = {**pair(progress), "callback_contact_id": opened["contact_id"]}
    assert call(client, feedback, "get_progress_disclosure", disclosure).status_code == 200
    result, payload = publish(client, specialist, investigation)
    assert result.status_code == 200, result.text
    assert call(client, specialist, "record_specialist_result", payload).json() == result.json()
    after = detail(client, feedback, progress)
    assert after["work"]["status"] == "cancelled"
    assert after["work"]["version"] == before["work"]["version"] + 1
    assert after["work"]["original_due_at"] == before["work"]["original_due_at"]
    assert call(client, feedback, "get_progress_disclosure", disclosure).status_code == 409
    assert (
        call(
            client,
            feedback,
            "record_progress_contact",
            {
                **disclosure,
                "expected_case_version": before["work"]["case_version"],
                "expected_work_version": before["work"]["version"],
                "commitment_id": proposed["commitment_id"],
                "reviewed": True,
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 409
    )
    assert find_work(client, feedback, "customer_feedback", investigation["case_id"])
    tick(Settings(runtime), NOW)
    with psycopg.connect(environment[1]) as conn:
        assert (
            conn.execute(
                "SELECT status FROM update_commitments WHERE id=%s", (proposed["commitment_id"],)
            ).fetchone()[0]
            == "superseded"
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM due_events WHERE work_item_id=%s", (investigation["id"],)
            ).fetchone()[0]
            == 1
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM work_items WHERE parent_work_id=%s AND kind='progress_callback'",
                (investigation["id"],),
            ).fetchone()[0]
            == 1
        )


def test_progress_without_result_requires_fresh_proof_and_does_not_consume_final_quota(environment):
    client, h, w, runtime = overdue(environment)
    tick(Settings(runtime), NOW)
    f, _ = session(client, "feedback_unclaimed")
    pw = find_work(client, f, "progress_callback", w["case_id"])
    assert (
        call(
            client,
            f,
            "claim_feedback_task",
            {**pair(pw), "expected_work_version": pw["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    d = detail(client, f, pw)
    opened = call(
        client,
        f,
        "open_progress_contact",
        {**pair(pw), "expected_work_version": d["work"]["version"], "operation_key": str(uuid4())},
    )
    assert opened.status_code == 200, opened.text
    cid = opened.json()["contact_id"]
    p = {**pair(pw), "callback_contact_id": cid}
    assert call(client, f, "get_progress_disclosure", p).status_code == 401
    call(
        client,
        f,
        "demo_callback_verification",
        {"callback_contact_id": cid, "scenario": "verified", "operation_key": str(uuid4())},
    )
    response = call(client, f, "get_progress_disclosure", p)
    assert response.status_code == 200, response.text
    assert (
        "not confirmed" in response.json()["explanation"]
        and response.json()["commitment_id"] is None
    )
    r = call(
        client,
        f,
        "record_progress_contact",
        {
            **p,
            "expected_case_version": d["work"]["case_version"],
            "expected_work_version": d["work"]["version"],
            "commitment_id": None,
            "reviewed": True,
            "operation_key": str(uuid4()),
        },
    )
    assert r.status_code == 200, r.text
    with psycopg.connect(environment[1]) as c:
        assert c.execute("SELECT count(*) FROM callback_attempts").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM progress_contacts").fetchone()[0] == 1


def test_objection_without_new_evidence_and_parallel_complaint_are_idempotent(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    p = {
        "case_id": w["case_id"],
        "contact_id": opened["contact_id"],
        "expected_case_version": detail(client, h, w)["work"]["case_version"],
        "customer_statement": "I still disagree and explicitly request complaint handling.",
        "evidence_refs": [],
        "complaint_requested": True,
        "operation_key": str(uuid4()),
    }
    assert command(client, h, "capture_customer_objection", p).status_code == 401
    call(
        client,
        h,
        "demo_callback_verification",
        {
            "callback_contact_id": opened["contact_id"],
            "scenario": "verified",
            "operation_key": str(uuid4()),
        },
    )
    r = command(client, h, "capture_customer_objection", p)
    assert r.status_code == 200, r.text
    assert command(client, h, "capture_customer_objection", p).json() == r.json()
    d = detail(client, h, w)
    assert d["objections"][0]["statement"] == p["customer_statement"]
    assert len(d["complaints"]) == 1 and d["complaints"][0]["status"] == "recorded"
    with psycopg.connect(admin) as c:
        oid = r.json()["data"]["domain_ref"]
        assert (
            c.execute(
                "SELECT count(*) FROM objection_work_links WHERE objection_id=%s", (oid,)
            ).fetchone()[0]
            == 2
        )
        assert c.execute("SELECT count(*) FROM investigation_results").fetchone()[0] == 1
        assert (
            c.execute("SELECT closed_at FROM cases WHERE id=%s", (w["case_id"],)).fetchone()[0]
            is None
        )


def test_objection_rejects_cross_customer_evidence_and_rolls_back(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    call(
        client,
        h,
        "demo_callback_verification",
        {
            "callback_contact_id": opened["contact_id"],
            "scenario": "verified",
            "operation_key": str(uuid4()),
        },
    )
    p = {
        "case_id": w["case_id"],
        "contact_id": opened["contact_id"],
        "expected_case_version": detail(client, h, w)["work"]["case_version"],
        "customer_statement": "Different customer evidence must be denied.",
        "evidence_refs": [
            {
                "kind": "transaction",
                "id": uid("other_customer_transaction"),
                "version": "1",
                "section": None,
            }
        ],
        "complaint_requested": True,
        "operation_key": str(uuid4()),
    }
    assert command(client, h, "capture_customer_objection", p).status_code == 404
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT count(*) FROM customer_objections").fetchone()[0] == 0


def test_new_same_customer_transaction_is_linked_without_overwriting_prior_finding(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    call(
        client,
        h,
        "demo_callback_verification",
        {
            "callback_contact_id": opened["contact_id"],
            "scenario": "verified",
            "operation_key": str(uuid4()),
        },
    )
    with psycopg.connect(admin) as c:
        tx = c.execute(
            "SELECT t.id,t.version FROM card_transactions t JOIN card_accounts a ON a.id=t.account_id JOIN cases cs ON cs.customer_id=a.customer_id WHERE cs.id=%s AND t.id NOT IN (SELECT transaction_id FROM case_transactions WHERE case_id=%s) LIMIT 1",
            (w["case_id"], w["case_id"]),
        ).fetchone()
    assert tx
    r = command(
        client,
        h,
        "capture_customer_objection",
        {
            "case_id": w["case_id"],
            "contact_id": opened["contact_id"],
            "expected_case_version": detail(client, h, w)["work"]["case_version"],
            "customer_statement": "Please also investigate this other entry.",
            "evidence_refs": [
                {"kind": "transaction", "id": str(tx[0]), "version": str(tx[1]), "section": None}
            ],
            "complaint_requested": False,
            "operation_key": str(uuid4()),
        },
    )
    assert r.status_code == 200, r.text
    d = detail(client, h, w)
    assert any(t["id"] == str(tx[0]) for t in d["transactions"])
    assert len(d["complaints"]) == 0 and d["result"]["version"] == 1


def inbound_objection(client, h, contact, case_id, version, **changes):
    return command(
        client,
        h,
        "capture_customer_objection",
        {
            "case_id": case_id,
            "contact_id": contact,
            "expected_case_version": version,
            "customer_statement": "I still believe I was charged twice for one purchase.",
            "evidence_refs": [],
            "complaint_requested": False,
            "operation_key": str(uuid4()),
            **changes,
        },
    )


def case_version(admin, case_id):
    with psycopg.connect(admin) as c:
        return c.execute("SELECT version FROM cases WHERE id=%s", (case_id,)).fetchone()[0]


def test_inbound_objection_reopens_closed_case_and_keeps_closure_history(environment):
    from test_continuation import close_case, complete_unrelated_seed_work, verified_callback

    client, admin, *_ = environment
    sh, sw, h, w, opened = setup_feedback(client)
    verified_callback(client, h, w, opened)
    complete_unrelated_seed_work(admin, w["case_id"])
    assert close_case(client, h, w).status_code == 200
    inbound, contact = session(client)
    other, other_contact = session(client, "other_customer")
    assert (
        inbound_objection(
            client, other, other_contact, w["case_id"], case_version(admin, w["case_id"])
        ).status_code
        == 404
    )
    stale = inbound_objection(client, inbound, contact, w["case_id"], 1)
    assert stale.status_code == 409
    p_version = case_version(admin, w["case_id"])
    captured = inbound_objection(client, inbound, contact, w["case_id"], p_version)
    assert captured.status_code == 200, captured.text
    with psycopg.connect(admin) as c:
        status, closed_at = c.execute(
            "SELECT status,closed_at FROM cases WHERE id=%s", (w["case_id"],)
        ).fetchone()
        assert status == "under_review" and closed_at is None
        assert c.execute("SELECT count(*) FROM case_closures").fetchone()[0] == 1
        assert c.execute("SELECT count(*) FROM case_reopenings").fetchone()[0] == 1
    rereview = find_work(client, sh, "specialist_rereview", w["case_id"])
    accepted = command(
        client,
        sh,
        "accept_specialist_work",
        {
            **pair(rereview),
            "expected_work_version": rereview["version"],
            "operation_key": str(uuid4()),
        },
    )
    assert accepted.status_code == 200, accepted.text
    revised, _ = publish(client, sh, rereview)
    assert revised.status_code == 200, revised.text
    # A revised result after delivered feedback needs lead-approved contact, not auto-closure.
    assert detail(client, h, w)["work"]["status"] == "lead_review"


def test_inbound_objection_requires_a_communicated_finding(environment):
    client, admin, *_ = environment
    inbound, contact = session(client)
    case_id = uid("duplicate_case")
    r = inbound_objection(client, inbound, contact, case_id, case_version(admin, case_id))
    assert r.status_code == 409
    unverified, unverified_contact = session(client, "unverified")
    r = inbound_objection(client, unverified, unverified_contact, case_id, 2)
    assert r.status_code in (401, 404)
