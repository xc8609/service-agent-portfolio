from datetime import timedelta
from uuid import uuid4

import psycopg
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.fixtures import uid
from conftest import NOW, session
from fastapi.testclient import TestClient


def call(client, headers, name, payload):
    trusted = {
        "accept_specialist_work",
        "claim_feedback_task",
        "record_specialist_result",
        "record_callback_attempt",
    }
    path = (
        "/v1/demo/callback-verification"
        if name == "demo_callback_verification"
        else "/v1/" + ("commands" if name in trusted else "workspace") + "/" + name
    )
    return client.post(path, headers=headers, json=payload)


def find_work(client, headers, kind, case=None):
    r = call(client, headers, "list_work", {})
    assert r.status_code == 200, r.text
    return next(
        w for w in r.json()["items"] if w["kind"] == kind and (case is None or w["case_id"] == case)
    )


def pair(w):
    return {"case_id": w["case_id"], "work_item_id": w["id"]}


def detail(client, h, w):
    r = call(client, h, "get_work_detail", pair(w))
    assert r.status_code == 200, r.text
    return r.json()


def publish(client, h, w, version=None, **changes):
    d = detail(client, h, w)
    payload = {
        **pair(w),
        "expected_case_version": version or d["work"]["case_version"],
        "finding": "explanation_only",
        "evidence_refs": [
            {"kind": "transaction", "id": t["id"], "version": t["version"], "section": None}
            for t in d["transactions"]
        ],
        "approved_customer_explanation": "The reviewed records require no additional bank action. No refund has been executed.",
        "internal_notes": "PRIVATE SPECIALIST NOTE MUST NEVER ENTER FEEDBACK",
        "required_action_statuses": [],
        "operation_key": str(uuid4()),
        **changes,
    }
    return call(client, h, "record_specialist_result", payload), payload


def setup_feedback(client):
    specialist, _ = session(client, "specialist")
    w = find_work(client, specialist, "specialist_investigation", uid("duplicate_case"))
    # Seeded specialist work is already assigned to this synthetic specialist.
    r, p = publish(client, specialist, w)
    assert r.status_code == 200, r.text
    feedback, _ = session(client, "feedback_unclaimed")
    fw = find_work(client, feedback, "customer_feedback", w["case_id"])
    claim = call(
        client,
        feedback,
        "claim_feedback_task",
        {**pair(fw), "expected_work_version": fw["version"], "operation_key": str(uuid4())},
    )
    assert claim.status_code == 200, claim.text
    d = detail(client, feedback, fw)
    opened = call(
        client,
        feedback,
        "open_callback",
        {**pair(fw), "expected_work_version": d["work"]["version"], "operation_key": str(uuid4())},
    )
    assert opened.status_code == 200, opened.text
    return specialist, w, feedback, fw, opened.json()


def review(client, h, w, contact):
    d = detail(client, h, w)
    r = call(
        client,
        h,
        "prepare_feedback_review",
        {
            **pair(w),
            "callback_contact_id": contact,
            "expected_result_version": d["result"]["version"],
            "explanation": d["result"]["approved_customer_explanation"],
            "operation_key": str(uuid4()),
        },
    )
    assert r.status_code == 200, r.text
    review = r.json()
    r = call(
        client,
        h,
        "approve_feedback_review",
        {
            **pair(w),
            "review_id": review["review_id"],
            "expected_review_version": review["version"],
            "operation_key": str(uuid4()),
        },
    )
    assert r.status_code == 200, r.text
    return review


def attempt(client, h, w, opened, outcome="no_answer", dial="placed"):
    d = detail(client, h, w)
    return {
        **pair(w),
        "callback_contact_id": opened["contact_id"],
        "expected_case_version": d["work"]["case_version"],
        "expected_work_version": d["work"]["version"],
        "actual_attempt_at": NOW.isoformat(),
        "dial_state": dial,
        "outcome": outcome,
        "customer_response": None,
        "operation_key": str(uuid4()),
        "contact_plan_id": opened["plan_id"],
        "reservation_id": None,
    }


def test_result_replay_and_masked_claimed_feedback_boundary(environment):
    client, admin, *_ = environment
    h, _ = session(client, "specialist")
    w = find_work(client, h, "specialist_investigation", uid("duplicate_case"))
    r, p = publish(client, h, w)
    assert r.status_code == 200, r.text
    assert call(client, h, "record_specialist_result", p).json() == r.json()
    f, _ = session(client, "feedback_other")
    q = call(client, f, "list_work", {})
    assert (
        "approved_customer_explanation" not in q.text
        and "PRIVATE SPECIALIST" not in q.text
        and "8500" not in q.text
    )
    fw = find_work(client, f, "customer_feedback", w["case_id"])
    assert call(client, f, "get_work_detail", pair(fw)).status_code == 404
    claim = {**pair(fw), "expected_work_version": fw["version"], "operation_key": str(uuid4())}
    assert call(client, f, "claim_feedback_task", claim).status_code == 200
    d = detail(client, f, fw)
    assert d["result"]["approved_customer_explanation"] == p["approved_customer_explanation"]
    assert "PRIVATE SPECIALIST" not in str(d)
    other, _ = session(client, "feedback_unclaimed")
    assert call(client, other, "get_work_detail", pair(fw)).status_code == 404
    with psycopg.connect(admin) as c:
        assert (
            c.execute(
                "SELECT count(*) FROM investigation_results WHERE case_id=%s", (w["case_id"],)
            ).fetchone()[0]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) FROM work_items WHERE case_id=%s AND kind='customer_feedback'",
                (w["case_id"],),
            ).fetchone()[0]
            == 1
        )


def test_verified_disclosure_and_completion_requires_current_callback_proof(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    r = review(client, h, w, opened["contact_id"])
    request = {**pair(w), "callback_contact_id": opened["contact_id"], "review_id": r["review_id"]}
    assert call(client, h, "get_callback_disclosure", request).status_code == 401
    assert (
        call(
            client,
            h,
            "record_callback_attempt",
            attempt(client, h, w, opened, "connected_verified", "connected"),
        ).status_code
        == 401
    )
    proof = call(
        client,
        h,
        "demo_callback_verification",
        {
            "callback_contact_id": opened["contact_id"],
            "scenario": "verified",
            "operation_key": str(uuid4()),
        },
    )
    assert proof.status_code == 200
    disclosure = call(client, h, "get_callback_disclosure", request)
    assert disclosure.status_code == 200, disclosure.text
    assert "PRIVATE" not in disclosure.text and disclosure.json()["financial_execution"] is False
    command = attempt(client, h, w, opened, "connected_verified", "connected")
    result = call(client, h, "record_callback_attempt", command)
    assert result.status_code == 200, result.text
    assert call(client, h, "record_callback_attempt", command).json() == result.json()
    assert detail(client, h, w)["work"]["status"] == "completed"
    with psycopg.connect(admin) as c:
        assert (
            c.execute("SELECT closed_at FROM cases WHERE id=%s", (w["case_id"],)).fetchone()[0]
            is None
        )
        assert c.execute("SELECT count(*) FROM callback_attempts").fetchone()[0] == 1


def test_verification_failure_and_never_dialed_fault_remain_outstanding(environment):
    client, admin, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    command = attempt(client, h, w, opened, "technical_failure", "not_placed")
    r = call(client, h, "record_callback_attempt", command)
    assert r.status_code == 200, r.text
    d = detail(client, h, w)
    assert d["plan"]["first_placed_at"] is None
    assert d["work"]["status"] == "assigned"
    opened = call(
        client,
        h,
        "open_callback",
        {**pair(w), "expected_work_version": d["work"]["version"], "operation_key": str(uuid4())},
    ).json()
    command = attempt(client, h, w, opened, "verification_failed", "connected")
    r = call(client, h, "record_callback_attempt", command)
    assert r.status_code == 200, r.text
    d = detail(client, h, w)
    assert d["work"]["status"] == "retry_scheduled"
    with psycopg.connect(admin) as c:
        assert (
            c.execute("SELECT sum(counts_toward_limit::int) FROM callback_attempts").fetchone()[0]
            == 1
        )
        assert (
            c.execute("SELECT closed_at FROM cases WHERE id=%s", (w["case_id"],)).fetchone()[0]
            is None
        )


def test_changed_result_invalidates_review_and_reassignment_revokes_access(environment):
    client, admin, *_ = environment
    sh, sw, h, w, opened = setup_feedback(client)
    d = detail(client, h, w)
    draft = call(
        client,
        h,
        "prepare_feedback_review",
        {
            **pair(w),
            "callback_contact_id": opened["contact_id"],
            "expected_result_version": d["result"]["version"],
            "explanation": "Reviewed explanation.",
            "operation_key": str(uuid4()),
        },
    ).json()
    result, _ = publish(
        client, sh, sw, approved_customer_explanation="Updated explanation; please review."
    )
    assert result.status_code == 200, result.text
    assert (
        call(
            client,
            h,
            "approve_feedback_review",
            {
                **pair(w),
                "review_id": draft["review_id"],
                "expected_review_version": 1,
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 409
    )
    with psycopg.connect(admin) as c:
        c.execute(
            "UPDATE work_items SET assignee_id=%s WHERE id=%s", (uid("feedback_other"), w["id"])
        )
    assert call(client, h, "get_work_detail", pair(w)).status_code == 404


def test_pending_financial_action_is_never_completed_by_specialist(environment):
    client, *_ = environment
    h, _ = session(client, "specialist")
    w = find_work(client, h, "specialist_investigation", uid("duplicate_case"))
    action = {
        "action_ref": str(uuid4()),
        "status": "completed",
        "receipt_ref": "invented-bank-receipt",
    }
    r, _ = publish(client, h, w, required_action_statuses=[action])
    assert r.status_code == 404
    action.update(status="pending", receipt_ref=None)
    r, _ = publish(
        client,
        h,
        w,
        finding="further_action_required",
        required_action_statuses=[action],
        approved_customer_explanation="Further action is pending; no financial execution is confirmed.",
    )
    assert r.status_code == 200, r.text
    f, _ = session(client, "feedback_unclaimed")
    fw = find_work(client, f, "customer_feedback", w["case_id"])
    assert (
        call(
            client,
            f,
            "claim_feedback_task",
            {**pair(fw), "expected_work_version": fw["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    assert detail(client, f, fw)["required_actions"][0]["status"] == "pending"


def test_fresh_proof_expires_and_material_followup_preserves_deadlines(environment):
    client, admin, runtime, _ = environment
    sh, _ = session(client, "specialist")
    sw = find_work(client, sh, "specialist_investigation", uid("duplicate_case"))
    d = detail(client, sh, sw)
    requested = call(
        client,
        sh,
        "request_material",
        {
            **pair(sw),
            "expected_case_version": d["work"]["case_version"],
            "question": "Please provide the purchase receipt if available.",
            "operation_key": str(uuid4()),
        },
    )
    assert requested.status_code == 200, requested.text
    h, _ = session(client, "feedback_other")
    mw = find_work(client, h, "material_followup", sw["case_id"])
    assert (
        call(
            client,
            h,
            "claim_feedback_task",
            {**pair(mw), "expected_work_version": mw["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    md = detail(client, h, mw)
    done = call(
        client,
        h,
        "record_followup",
        {
            **pair(mw),
            "expected_work_version": md["work"]["version"],
            "state": "received",
            "statement": "Customer reports purchase receipt date; synthetic evidence only.",
            "evidence_refs": [],
            "method_ref": None,
            "operation_key": str(uuid4()),
        },
    )
    assert done.status_code == 200, done.text
    assert detail(client, sh, sw)["work"]["original_due_at"] == d["work"]["original_due_at"]
    _, _, h, w, opened = setup_feedback(client)
    reviewed = review(client, h, w, opened["contact_id"])
    assert (
        call(
            client,
            h,
            "demo_callback_verification",
            {
                "callback_contact_id": opened["contact_id"],
                "scenario": "verified",
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 200
    )
    with TestClient(
        create_app(Settings(runtime), clock=lambda: NOW + timedelta(minutes=11))
    ) as later:
        assert (
            call(
                later,
                h,
                "get_callback_disclosure",
                {
                    **pair(w),
                    "callback_contact_id": opened["contact_id"],
                    "review_id": reviewed["review_id"],
                },
            ).status_code
            == 401
        )


def test_claim_concurrency_and_unauthorized_result_write(environment):
    from concurrent.futures import ThreadPoolExecutor

    client, admin, runtime, _ = environment
    sh, _ = session(client, "specialist")
    sw = find_work(client, sh, "specialist_investigation", uid("duplicate_case"))
    r, payload = publish(client, sh, sw)
    assert r.status_code == 200
    inbound, _ = session(client)
    assert call(client, inbound, "record_specialist_result", payload).status_code == 404
    a, _ = session(client, "feedback_unclaimed")
    b, _ = session(client, "feedback_other")
    fw = find_work(client, a, "customer_feedback", sw["case_id"])

    def claim(h):
        with TestClient(create_app(Settings(runtime), clock=lambda: NOW)) as other:
            return call(
                other,
                h,
                "claim_feedback_task",
                {**pair(fw), "expected_work_version": fw["version"], "operation_key": str(uuid4())},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = sorted(pool.map(claim, [a, b]))
    assert outcomes[0] == 200 and outcomes[1] in (404, 409)


def test_result_and_feedback_roll_back_with_outbox_failure(environment):
    client, admin, *_ = environment
    h, _ = session(client, "specialist")
    w = find_work(client, h, "specialist_investigation", uid("duplicate_case"))
    with psycopg.connect(admin) as c:
        c.execute("REVOKE INSERT ON outbox_events FROM bank_app")
    try:
        r, _ = publish(client, h, w)
        assert r.status_code == 503
        with psycopg.connect(admin) as c:
            assert c.execute("SELECT count(*) FROM investigation_results").fetchone()[0] == 0
            assert c.execute("SELECT count(*) FROM contact_plans").fetchone()[0] == 0
            assert (
                c.execute(
                    "SELECT status FROM work_items WHERE id=%s", (uid("feedback_work"),)
                ).fetchone()[0]
                == "waiting_for_result"
            )
    finally:
        with psycopg.connect(admin) as c:
            c.execute("GRANT INSERT ON outbox_events TO bank_app")


def test_contact_gap_survives_result_until_owned_resolution(environment):
    from test_notes import approve, post
    from test_referrals import create, prepare

    client, admin, *_ = environment
    inbound, contact = session(client)
    prepared = prepare(client, inbound, contact)
    intake = prepared["payload"]["intake"]
    intake.update(
        mode="new",
        distinct_work_reason="Separate synthetic contact-gap case.",
        customer_summary_confirmed=True,
    )
    intake["contact"] = {
        "state": "unavailable",
        "method_ref": None,
        "method_version": None,
        "reason": "Existing callback method needs confirmation.",
    }
    draft = create(client, inbound, contact, prepared)
    submitted = post(client, inbound, "approve_and_commit_proposal", approve(draft))
    assert submitted.status_code == 200
    case = submitted.json()["data"]["domain_ref"]
    sh, _ = session(client, "specialist")
    sw = find_work(client, sh, "specialist_investigation", case)
    assert (
        call(
            client,
            sh,
            "accept_specialist_work",
            {**pair(sw), "expected_work_version": sw["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    original = detail(client, sh, sw)["work"]["original_due_at"]
    published, _ = publish(client, sh, sw)
    assert published.status_code == 200
    h, _ = session(client, "feedback_unclaimed")
    fw = find_work(client, h, "customer_feedback", case)
    assert (
        call(
            client,
            h,
            "claim_feedback_task",
            {**pair(fw), "expected_work_version": fw["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    fd = detail(client, h, fw)
    blocked = call(
        client,
        h,
        "open_callback",
        {**pair(fw), "expected_work_version": fd["work"]["version"], "operation_key": str(uuid4())},
    )
    assert blocked.json()["error"]["code"] == "CONTACT_GAP"
    gap = find_work(client, h, "contact_resolution", case)
    assert (
        call(
            client,
            h,
            "claim_feedback_task",
            {**pair(gap), "expected_work_version": gap["version"], "operation_key": str(uuid4())},
        ).status_code
        == 200
    )
    gd = detail(client, h, gap)
    resolved = call(
        client,
        h,
        "record_followup",
        {
            **pair(gap),
            "expected_work_version": gd["work"]["version"],
            "state": "contact_resolved",
            "statement": "Existing authorized contact method confirmed through manual follow-up.",
            "evidence_refs": [],
            "method_ref": uid("customer_a_phone"),
            "operation_key": str(uuid4()),
        },
    )
    assert resolved.status_code == 200, resolved.text
    fd = detail(client, h, fw)
    assert (
        call(
            client,
            h,
            "open_callback",
            {
                **pair(fw),
                "expected_work_version": fd["work"]["version"],
                "operation_key": str(uuid4()),
            },
        ).status_code
        == 200
    )
    assert detail(client, sh, sw)["work"]["original_due_at"] == original
    with psycopg.connect(admin) as c:
        assert c.execute("SELECT closed_at FROM cases WHERE id=%s", (case,)).fetchone()[0] is None


def test_new_feedback_draft_invalidates_previous_approval(environment):
    client, *_ = environment
    _, _, h, w, opened = setup_feedback(client)
    old = review(client, h, w, opened["contact_id"])
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
    d = detail(client, h, w)
    new = call(
        client,
        h,
        "prepare_feedback_review",
        {
            **pair(w),
            "callback_contact_id": opened["contact_id"],
            "expected_result_version": d["result"]["version"],
            "explanation": "Revised explanation awaiting approval.",
            "operation_key": str(uuid4()),
        },
    )
    assert new.status_code == 200, new.text
    assert new.json()["version"] > old["version"]
    assert (
        call(
            client,
            h,
            "get_callback_disclosure",
            {**pair(w), "callback_contact_id": opened["contact_id"], "review_id": old["review_id"]},
        ).status_code
        == 409
    )
    assert (
        call(
            client,
            h,
            "record_callback_attempt",
            attempt(client, h, w, opened, "connected_verified", "connected"),
        ).status_code
        == 409
    )
