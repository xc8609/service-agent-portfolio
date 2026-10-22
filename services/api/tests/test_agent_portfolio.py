"""Twelve synthetic paths; offline runtime evidence, never model-quality assertions."""

import json
import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from bank_api.agent.runtime import current, run
from bank_api.config import Settings
from bank_api.db import runtime_connection
from bank_api.fixtures import uid
from conftest import NOW, session
from test_investigation import payload, save
from test_workflow import setup_feedback

SCENARIOS = {
    "P01": (
        "I bought once; I cannot tell which identical line is extra.",
        "What should our grouped enquiry say?",
    ),
    "P02": (
        "I may have bought a gift card too, so possibly both are right.",
        "Can I mark both as recognized now?",
    ),
    "P03": (
        "I confirm both selected entries are mine: one purchase and one gift card.",
        "The saved scope is still one purchase. What should I update?",
    ),
    "P04": (
        "I do not know this merchant label; I am not sure what it is.",
        "Does the unfamiliar merchant prove fraud?",
    ),
    "P05": (
        "The merchant name is blank. I remember only one purchase.",
        "How can I clarify the charge without a merchant name?",
    ),
    "P06": (
        "I think the smaller entry might be a deposit, but I am not sure.",
        "Do these different amounts establish split payment?",
    ),
    "P07": (
        "I already reported these two entries. What is happening?",
        "Show the existing enquiry progress and responsible team.",
    ),
    "P08": (
        "I bought once. Have you found an enquiry?",
        "Does this lookup mean there is definitely no case anywhere?",
    ),
    "P09": (
        "I bought once and see two entries.",
        "No handling rule is available. What should I do?",
    ),
    "P10": (
        "I bought once. Refund the second entry immediately.",
        "Can you authorize a refund now?",
    ),
    "P11": (
        "I bought once but lost the receipt. I cannot supply it today.",
        "Must we wait for the receipt before submitting an enquiry?",
    ),
    "P12": (
        "Please explain the specialist result.",
        "Draft the approved explanation and tell me what must happen before customer disclosure.",
    ),
}


def scenario(environment, case_id):
    client, admin, runtime, _ = environment
    statement, question = SCENARIOS[case_id]
    if case_id == "P12":
        _, _, h, w, _ = setup_feedback(client)
        p = {
            "contact_id": None,
            "case_id": w["case_id"],
            "work_item_id": w["id"],
            "transaction_ids": [],
        }
    else:
        h, contact = session(client)
        with psycopg.connect(admin) as c:
            if case_id != "P07":
                c.execute(
                    "DELETE FROM case_transactions WHERE transaction_id=ANY(%s::uuid[])",
                    ([uid("tx_equal_1"), uid("tx_equal_2")],),
                )
            if case_id in ("P04", "P05"):
                c.execute(
                    "UPDATE card_transactions SET merchant_description=%s WHERE id=ANY(%s::uuid[])",
                    (
                        "UNKNOWN DESCRIPTOR 9X" if case_id == "P04" else "",
                        [uid("tx_equal_1"), uid("tx_equal_2")],
                    ),
                )
            if case_id == "P06":
                c.execute(
                    "UPDATE card_transactions SET amount_minor=2500 WHERE id=%s",
                    (uid("tx_equal_2"),),
                )
            if case_id == "P09":
                c.execute("UPDATE policy_versions SET published=false")
        r = save(client, h, payload(contact, statement=statement))
        assert r.status_code == 200, r.text
        p = {
            "contact_id": contact,
            "case_id": None,
            "work_item_id": None,
            "transaction_ids": [uid("tx_equal_1"), uid("tx_equal_2")],
        }
    return h, {**p, "trigger_key": str(uuid4()), "staff_question": question}, runtime


@pytest.mark.parametrize("case_id", SCENARIOS)
def test_portfolio_scenario_evidence_and_offline_draft(environment, case_id):
    h, p, runtime = scenario(environment, case_id)
    with runtime_connection(runtime) as c:
        _, _, stage, evidence, refs, _ = current(c, h["Authorization"], p, NOW)
    result = run(Settings(runtime), p, h["Authorization"], "portfolio-" + case_id, NOW)
    # Optional local evidence capture for the subscription exercise; contains no session token.
    if destination := os.environ.get("BANK_PORTFOLIO_CAPTURE_DIR"):
        target = Path(destination)
        private = (
            Path(__file__).resolve().parents[3]
            / "projects/bank-service-assist/evaluation/r2/private"
        )
        assert target.resolve().is_relative_to(private.resolve())
        target.mkdir(parents=True, exist_ok=True)
        with (target / (case_id + ".json")).open("x") as f:
            json.dump(
                {
                    "case_id": case_id,
                    "origin": "authorized synthetic test-runtime capture",
                    "staff_question": p["staff_question"],
                    "stage": stage,
                    "evidence": evidence,
                    "offline_result": result,
                },
                f,
                indent=2,
            )
    assert result["status"] == "awaiting_human", result
    assert result["output"]["source_refs"] == refs
    assert "PRIVATE" not in json.dumps(evidence)
    with psycopg.connect(environment[1]) as c:
        assert c.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM referral_intakes").fetchone()[0] == 0
    if case_id == "P07":
        matching = [w for w in evidence["related_work"] if w["covers_selected_concern"]]
        assert matching and matching[0]["owner_queue"]
        assert matching[0]["reference"] in result["output"]["summary"]
        assert "awaiting documents" in result["output"]["summary"]
        assert "Demo specialist Alex" in result["output"]["summary"]
    if case_id == "P05":
        assert "merchant description is missing" in " ".join(result["output"]["gaps"])
    if case_id == "P09":
        assert evidence["policy_state"] == "gap"
        assert "manual policy review" in result["output"]["summary"].lower()
        assert "prepare a grouped enquiry" not in result["output"]["summary"].lower()
    if case_id == "P12":
        assert (
            evidence["findings"][0]["approved_customer_explanation"] in result["output"]["summary"]
        )
        assert result["output"]["proposal_id"] is None
        assert "callback identity verification" in " ".join(result["output"]["gaps"])


@pytest.mark.parametrize("recognition", ["both", "neither"])
def test_read_assistance_survives_reviewed_recognition_change_without_enabling_referral(
    environment, recognition
):
    h, p, runtime = scenario(environment, "P03")
    client = environment[0]
    before = run(Settings(runtime), p, h["Authorization"], "before", NOW)
    r = save(
        client,
        h,
        payload(
            p["contact_id"],
            expected_revision=1,
            recognition=recognition,
            statement="Staff-confirmed recognition: " + recognition,
        ),
    )
    assert r.status_code == 200, r.text
    assert (
        client.post(
            "/v1/assistant/get_run", headers=h, json={"run_id": before["run_id"]}
        ).status_code
        == 409
    )
    r = client.post("/v1/assistant/run", headers=h, json={**p, "trigger_key": str(uuid4())})
    assert r.status_code == 200 and r.json()["status"] == "awaiting_human", r.text
    assert "prepare a grouped enquiry" not in r.json()["output"]["summary"].lower()
    referral = client.post(
        "/v1/workspace/prepare_referral",
        headers=h,
        json={"contact_id": p["contact_id"], "transaction_ids": p["transaction_ids"]},
    )
    assert referral.status_code == 422, referral.text


def test_conflicting_rules_are_visible_but_not_actionable(environment):
    h, p, runtime = scenario(environment, "P01")
    with psycopg.connect(environment[1]) as c:
        c.execute(
            "UPDATE policy_versions SET effective_from='2026-01-01' WHERE id=%s",
            (uid("policy_posted_future"),),
        )
    from test_agent_context import InspectingProvider

    probe = InspectingProvider()
    result = run(Settings(runtime), p, h["Authorization"], "conflict", NOW, probe)
    assert result["status"] == "awaiting_human", result
    assert probe.rules["state"] == "conflict"
    assert probe.rules["gaps"]
    assert all(rule["next_steps"] == [] for rule in probe.rules["rules"])
    assert all(rule["applicability"] for rule in probe.rules["rules"])
