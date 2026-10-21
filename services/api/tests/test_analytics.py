import csv
import json
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree as ET

import psycopg
from bank_api.agent.providers import FakeProvider, ProviderFailure
from bank_api.agent.runtime import run
from bank_api.analytics import PROJECT, export
from bank_api.config import Settings
from conftest import NOW, session
from test_agent import initial
from test_continuation import exercise_contact_continuation
from test_notes import approve, draft, post
from test_workflow import attempt, call, detail, pair, setup_feedback


def read(environment, path, cutoff=NOW):
    report = export(Settings(environment[2]), path, cutoff)
    rows = list(csv.DictReader((path / "workflow_metrics.csv").open()))
    values = {(r["metric"], r["segment"]): r["value"] for r in rows}
    return report, rows, values


def test_run_outcomes_replay_and_unknown_usage_reconcile(environment, tmp_path):
    _, h, p, runtime = initial(environment)
    first = run(Settings(runtime), p, h["Authorization"], "first", NOW)
    assert run(Settings(runtime), p, h["Authorization"], "replay", NOW) == first
    for state in ("failed", "cancelled", "interrupted", "running"):
        p["trigger_key"] = str(uuid4())
        r = run(
            Settings(runtime),
            p,
            h["Authorization"],
            state,
            NOW,
            FakeProvider([ProviderFailure("TIMEOUT")]),
        )
        with psycopg.connect(environment[1]) as conn:
            conn.execute(
                "UPDATE agent_runs SET status=%s,finished_at=%s WHERE id=%s",
                (state, None if state == "running" else NOW, r["run_id"]),
            )
    report, rows, values = read(environment, tmp_path)
    assert report["source_totals"]["runs"] == 5
    assert all(
        values[("Run outcome", state)] == "1"
        for state in ("awaiting_human", "failed", "cancelled", "interrupted", "running")
    )
    assert values[("Missing terminal latency", "all")] == "1"
    assert values[("Missing usage", "all")] == "5"
    assert values[("Model cost", "all")] == ""
    assert values[("Measured ROI", "not studied")] == ""
    assert all(r["data_kind"] == "synthetic_operational" for r in rows)
    text = (tmp_path / "workflow_metrics.csv").read_text()
    assert "Two posted entries" not in text and first["run_id"] not in text


def test_proposal_multiple_edits_are_one_decision(environment, tmp_path):
    client = environment[0]
    h, contact = session(client)
    original, data = draft(client, h, contact)
    for version in (1, 2):
        result = post(
            client,
            h,
            "edit_proposal",
            {
                "proposal_id": data["proposal_id"],
                "expected_proposal_version": version,
                "expected_case_version": None,
                "expected_work_version": None,
                "replacement": {
                    "kind": "note",
                    "payload": {
                        **original["proposal"]["payload"],
                        "body": "Reviewed wording " + str(version),
                    },
                },
                "operation_key": str(uuid4()),
            },
        )
        assert result.status_code == 200, result.text
    command = approve(data, expected_proposal_version="3")
    committed = post(client, h, "approve_and_commit_proposal", command)
    assert committed.status_code == 200
    assert post(client, h, "approve_and_commit_proposal", command).json() == committed.json()
    _, unchanged = draft(client, h, contact)
    assert post(client, h, "approve_and_commit_proposal", approve(unchanged)).status_code == 200
    draft(client, h, contact)
    _, declined = draft(client, h, contact)
    rejected = post(client, h, "reject_proposal", reject(declined))
    assert rejected.status_code == 200, rejected.text
    _, _, values = read(environment, tmp_path)
    assert values[("All proposals", "all")] == "4"
    assert values[("Disposition", "accepted_edited")] == "1"
    assert values[("Disposition", "accepted_unchanged")] == "1"
    assert values[("Disposition", "rejected")] == "1"
    assert values[("Disposition", "pending")] == "1"
    assert values[("Decided denominator", "all")] == "3"
    assert float(values[("Accepted proportion", "decided only")]) == 2 / 3
    assert values[("Origin", "staff")] == "4" and values[("Origin", "agent")] == "0"
    assert values[("Accepted proportion", "agent drafts, decided only")] == ""


def reject(data, **changes):
    return {
        "proposal_id": data["proposal_id"],
        "expected_proposal_version": int(data["proposal_version"]),
        "reason": "Draft does not reflect the customer's recognition; not committed.",
        "operation_key": str(uuid4()),
        **changes,
    }


def test_agent_draft_rejection_is_a_separate_human_decision(environment, tmp_path):
    client, h, p, runtime = initial(environment)
    r = client.post("/v1/assistant/run", headers=h, json=p)
    assert r.status_code == 200, r.text
    proposal = r.json()["output"]["proposal_id"]
    other, _ = session(client, "unverified")
    command = reject({"proposal_id": proposal, "proposal_version": "1"})
    assert post(client, other, "reject_proposal", command).status_code in (401, 404)
    # Evidence drift blocks approval but never prevents a human from declining the draft.
    with psycopg.connect(environment[1]) as conn:
        conn.execute(
            "UPDATE card_transactions SET version=version+1 WHERE id=%s",
            (p["transaction_ids"][0],),
        )
    declined = post(client, h, "reject_proposal", command)
    assert declined.status_code == 200, declined.text
    assert post(client, h, "reject_proposal", command).json() == declined.json()
    assert (
        post(client, h, "reject_proposal", {**command, "operation_key": str(uuid4())}).status_code
        == 409
    )
    with psycopg.connect(environment[1]) as conn:
        assert conn.execute("SELECT count(*) FROM contact_notes").fetchone()[0] == 0
    # The run stamps its draft after elapsed runtime, so the cutoff follows the run.
    _, _, values = read(environment, tmp_path, NOW + timedelta(minutes=1))
    assert values[("Origin", "agent")] == "1"
    assert values[("Decided denominator", "agent")] == "1"
    assert values[("Accepted proportion", "agent drafts, decided only")] == "0.0"


def test_never_dialed_fault_and_replayed_actual_attempt(environment, tmp_path):
    client = environment[0]
    _, _, h, work, opened = setup_feedback(client)
    fault = attempt(client, h, work, opened, "technical_failure", "not_placed")
    r = call(client, h, "record_callback_attempt", fault)
    assert r.status_code == 200, r.text
    assert call(client, h, "record_callback_attempt", fault).json() == r.json()
    second = call(
        client,
        h,
        "open_callback",
        {
            **pair(work),
            "expected_work_version": detail(client, h, work)["work"]["version"],
            "operation_key": str(uuid4()),
        },
    ).json()
    assert (
        call(client, h, "record_callback_attempt", attempt(client, h, work, second)).status_code
        == 200
    )
    report, _, values = read(environment, tmp_path)
    assert report["source_totals"]["attempts"] == 2
    assert values[("Recorded outcomes", "initial")] == "2"
    assert values[("Quota-counted calls", "initial")] == "1"
    assert values[("Never-dialed faults", "initial")] == "1"


def test_continuation_retains_initial_window_and_reproducible_export(environment, tmp_path):
    # Reuse the verified API journey, not a fixture generated from the metric SQL.
    exercise_contact_continuation(environment)
    _, h, p, runtime = initial(environment)
    run(Settings(runtime), p, h["Authorization"], "demo", NOW)
    output = Path(os.environ.get("BANK_ANALYTICS_EXPORT", tmp_path))
    cutoff = NOW + timedelta(days=7)
    report, _, values = read(environment, output, cutoff)
    assert values[("Lifetime recorded outcomes", "all")] == "1"
    assert values[("Recorded outcomes", "initial")] == "1"
    assert values[("Recorded outcomes", "lead_approved")] == "0"
    assert values[("Retained window misses", "initial")] == "1"
    again, _, _ = read(environment, output, cutoff)
    assert again["csv_sha256"] == report["csv_sha256"]
    assert again["source_changed_since_previous_export"] is False


def test_late_correction_is_recorded_without_fake_historical_snapshot(environment, tmp_path):
    _, h, p, runtime = initial(environment)
    r = run(Settings(runtime), p, h["Authorization"], "first", NOW)
    before, _, _ = read(environment, tmp_path)
    with psycopg.connect(environment[1]) as conn:
        conn.execute("UPDATE agent_runs SET status='interrupted' WHERE id=%s", (r["run_id"],))
    after, _, values = read(environment, tmp_path)
    assert after["source_changed_since_previous_export"] is True
    assert after["previous_source_fingerprint"] == before["source_fingerprint"]
    assert values[("Run outcome", "interrupted")] == "1"
    assert "not historical time travel" in after["snapshot_semantics"]


def test_tableau_artifact_and_empty_denominators(environment, tmp_path):
    _, _, values = read(environment, tmp_path)
    assert values[("Accepted proportion", "decided only")] == ""
    assert values[("Mean terminal latency (ms)", "completed timing only")] == ""
    workbook = ET.parse(PROJECT / "dashboard/workflow_operations.twb")
    connection = workbook.find(".//connection")
    assert connection.attrib["class"] == "textscan"
    assert connection.attrib["directory"] == "../data/processed/tableau"
    assert connection.attrib["filename"] == "workflow_metrics.csv"
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["contains_customer_content"] is False
