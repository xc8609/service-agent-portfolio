"""Fabricated manifests/reviews exercise gates, never an independent holdout or model result."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import r2_experiment as experiment


def signed(e):
    e["sha256"] = experiment.fingerprint({k: v for k, v in e.items() if k != "sha256"})
    return e


@pytest.fixture
def package():
    m = experiment.scaffold()
    config = {"route": "TEST-ONLY", "code_sha256": "a" * 64}
    m.update(
        frozen=True,
        frozen_at="2026-10-21T12:00:00Z",
        approved_by="TEST-ONLY",
        configuration_sha256=experiment.fingerprint(config),
        baseline_sha256="b" * 64,
        baseline_selection_evidence="Test-only locked selection",
        development_families=["dev-%s" % i for i in range(60)],
        exposure_audit={"reviewer": "TEST", "evidence": "TEST-only audit"},
        criteria={"quality": {"severity": "quality"}, "safe": {"severity": "critical"}},
    )
    for i, c in enumerate(m["cases"]):
        c.update(
            family="unseen-%s" % i,
            prompt="Test-only prompt %s" % i,
            evidence_sha256=experiment.fingerprint(i),
            expected_business_state="awaiting_customer",
            criteria=["quality", "safe"],
        )
        c["provenance"].update(
            author="TEST-A",
            reviewer="TEST-B",
            author_kind="independent_human",
            independence_evidence="Fabricated unit-test declaration",
            model_assistance="none",
            answer_approved=True,
        )
    corpus = experiment.corpus_for(m)
    outputs = [
        {"case_id": c["id"], "summary": "TEST-only draft", "citations": [], "gaps": []}
        for c in m["cases"]
    ]
    reviews = [
        {
            "case_id": c["id"],
            "output_sha256": experiment.fingerprint(o),
            "corpus_sha256": experiment.fingerprint(corpus),
            "reviewer": "TEST-only",
            "kind": "human",
            "business_state": "awaiting_customer",
            "criteria": {
                key: {"verdict": "met", "evidence": "Fabricated test observation"}
                for key in c["criteria"]
            },
        }
        for c, o in zip(m["cases"], outputs)
    ]
    baseline = deepcopy(reviews)
    for r in baseline[:6]:
        r["criteria"]["quality"]["verdict"] = "not_met"
    bundle = {
        "manifest_sha256": experiment.fingerprint(m),
        "baseline": {
            "configuration_sha256": m["baseline_sha256"],
            "repeatability_evidence": "TEST-only",
            "outputs": deepcopy(outputs),
            "reviews": baseline,
        },
        "runs": [],
    }
    for n in range(1, 4):
        evidence = [
            signed(
                {
                    "version": "r2-runtime-evidence-v1",
                    "mode": "live_api",
                    "configuration": config,
                    "configuration_sha256": m["configuration_sha256"],
                    "evidence_sha256": c["evidence_sha256"],
                    "run_id": "%s:%s" % (n, c["id"]),
                    "case_id": c["id"],
                    "output": deepcopy(o),
                    "fresh_run": True,
                    "step_names": ["read_evidence", "read_rules", "draft_recommendation"],
                    "status": "awaiting_human",
                    "started_at": "2026-10-21T13:00:00Z",
                    "finished_at": "2026-10-21T13:00:01Z",
                    "business_before_sha256": "d" * 64,
                    "business_after_sha256": "d" * 64,
                    "checks": {k: True for k in experiment.CHECKS},
                }
            )
            for c, o in zip(m["cases"], outputs)
        ]
        bundle["runs"].append(
            {
                "iteration": n,
                "evidence": evidence,
                "first_reviews": deepcopy(reviews),
                "final_reviews": deepcopy(reviews),
                "first_reviewed_at": "2026-10-21T14:00:00Z",
                "final_reviewed_at": "2026-10-21T15:00:00Z",
            }
        )
    return m, bundle


def verdict(
    bundle, ids, value="not_met", criterion="quality", stages=("first_reviews", "final_reviews")
):
    for stage in stages:
        for r in bundle["runs"][0][stage]:
            if r["case_id"] in ids:
                r["criteria"][criterion]["verdict"] = value


def test_gates_compute_all_three_runs_without_granting_qualification(package):
    result = experiment.evaluate(*package)
    assert result["gate_checks_passed"]
    assert not result["adoption_eligible"] and result["runtime_qualification"] == "not_granted"
    assert len(result["runs"]) == 3
    assert all(r["narrative_wins"] == 6 and r["runtime_passes"] == 64 for r in result["runs"])


@pytest.mark.parametrize("failures,expected", [(3, True), (4, False)])
def test_narrative_ninety_percent_and_net_three_boundary(package, failures, expected):
    m, b = package
    verdict(b, ["narrative-%02d" % i for i in range(1, failures + 1)])
    result = experiment.evaluate(m, b)["runs"][0]
    assert result["gates"]["G2"] is expected
    assert result["gates"]["G3"] is expected


def test_total_quality_boundary_and_structured_regression(package):
    m, b = package
    verdict(b, ["structured-%02d" % i for i in range(1, 5)])
    result = experiment.evaluate(m, b)["runs"][0]
    assert result["gates"]["G2"] and not result["gates"]["G4"]
    assert len(result["structured_regressions"]) == 4
    verdict(b, ["structured-05"])
    assert not experiment.evaluate(m, b)["runs"][0]["gates"]["G2"]


@pytest.mark.parametrize("cid,criterion", [("critical-01", "quality"), ("narrative-01", "safe")])
def test_one_critical_challenge_failure_or_any_critical_violation_blocks(package, cid, criterion):
    m, b = package
    verdict(b, [cid], criterion=criterion)
    assert not experiment.evaluate(m, b)["runs"][0]["gates"]["G1"]


@pytest.mark.parametrize("count,allowed", [(2, True), (3, False)])
def test_initial_pending_keeps_denominator_after_final_resolution(package, count, allowed):
    m, b = package
    verdict(
        b,
        ["narrative-%02d" % i for i in range(1, count + 1)],
        "uncertain",
        stages=("first_reviews",),
    )
    result = experiment.evaluate(m, b)["runs"][0]
    assert result["gates"]["G5"] is allowed
    assert result["first_review_rate"] == count / 40
    assert result["quality_total"] == 40 and result["quality_passes"] == 40


@pytest.mark.parametrize(
    "change", ["missing_review", "unresolved_critical", "erased_violation", "time_travel"]
)
def test_review_completeness_and_history(package, change):
    m, b = package
    run = b["runs"][0]
    if change == "missing_review":
        run["first_reviews"].pop()
    elif change == "unresolved_critical":
        verdict(b, ["critical-01"], "uncertain")
    elif change == "erased_violation":
        verdict(b, ["narrative-01"], criterion="safe", stages=("first_reviews",))
    else:
        run["first_reviewed_at"] = "2026-10-21T11:00:00Z"
    assert not experiment.evaluate(m, b)["runs"][0]["gates"]["G5"]


@pytest.mark.parametrize(
    "change",
    [
        "fixture",
        "hash",
        "source",
        "configuration",
        "stale",
        "write",
        "checks",
        "reuse",
        "missing",
        "pre_freeze",
    ],
)
def test_runtime_evidence_cannot_be_replaced_by_good_prose(package, change):
    m, b = package
    e = b["runs"][0]["evidence"][0]
    if change == "fixture":
        e["mode"] = "engineering_fixture"
    elif change == "source":
        e["evidence_sha256"] = "0" * 64
    elif change == "configuration":
        e["configuration"] = {"route": "different"}
    elif change == "stale":
        e["fresh_run"] = False
    elif change == "write":
        e["business_after_sha256"] = "0" * 64
    elif change == "checks":
        e["checks"]["scope_current"] = False
    elif change == "reuse":
        b["runs"][1]["evidence"][0]["run_id"] = e["run_id"]
        signed(b["runs"][1]["evidence"][0])
    elif change == "missing":
        b["runs"][0]["evidence"].pop()
    elif change == "pre_freeze":
        e["started_at"] = "2026-10-20T13:00:00Z"
    signed(e)
    if change == "hash":
        e["sha256"] = "0" * 64
    result = experiment.evaluate(m, b)
    assert not result["gate_checks_passed"]
    assert not all(r["gates"]["G6"] for r in result["runs"])


@pytest.mark.parametrize(
    "change",
    [
        "public_family",
        "repeat_family",
        "repeat_prompt",
        "author",
        "reviewer",
        "unfrozen",
        "exposure_drift",
        "count",
    ],
)
def test_holdout_readiness_rejects_leakage_and_missing_independence(package, change):
    m, _ = package
    c = m["cases"][0]
    if change == "public_family":
        c["family"] = experiment.exposure_registry()["families"][0]
    elif change == "repeat_family":
        c["family"] = m["cases"][1]["family"]
    elif change == "repeat_prompt":
        c["prompt"] = "  " + m["cases"][1]["prompt"].upper() + "  "
    elif change == "author":
        c["provenance"]["author_kind"] = "model"
    elif change == "reviewer":
        c["provenance"]["reviewer"] = c["provenance"]["author"]
    elif change == "unfrozen":
        m["frozen"] = False
    elif change == "exposure_drift":
        m["public_exposure_sha256"] = "0" * 64
    elif change == "count":
        m["cases"].pop()
    assert not experiment.readiness(m)["ready"]


def test_preparation_is_exactly_64_empty_unapproved_slots():
    m = experiment.scaffold()
    assert len(m["cases"]) == 64 and not experiment.readiness(m)["ready"]
    assert all(not c["prompt"] and not c["provenance"]["answer_approved"] for c in m["cases"])


@pytest.mark.parametrize("change", ["baseline", "manifest", "iterations", "duplicate"])
def test_bundle_contract_drift_rejected(package, change):
    m, b = package
    if change == "baseline":
        b["baseline"]["configuration_sha256"] = "0" * 64
    elif change == "manifest":
        b["manifest_sha256"] = "0" * 64
    elif change == "iterations":
        b["runs"].pop()
    else:
        b["runs"][0]["evidence"].append(deepcopy(b["runs"][0]["evidence"][0]))
    with pytest.raises(ValueError):
        experiment.evaluate(m, b)


def test_cli_exit_and_prompt_projection(tmp_path, monkeypatch, capsys):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(experiment.scaffold()))
    monkeypatch.setattr(sys, "argv", ["r2_experiment", "check", "--manifest", str(path)])
    with pytest.raises(SystemExit) as exc:
        experiment.main()
    assert exc.value.code == 2
    capsys.readouterr()
    monkeypatch.setattr(sys, "argv", ["r2_experiment", "prompts", "--manifest", str(path)])
    experiment.main()
    assert all(set(r) == {"case_id", "prompt"} for r in json.loads(capsys.readouterr().out))


def test_first_review_must_explicitly_cover_all_criteria(package):
    m, b = package
    del b["runs"][0]["first_reviews"][0]["criteria"]["safe"]
    assert not experiment.evaluate(m, b)["runs"][0]["gates"]["G5"]


def test_relabelled_public_prompt_and_missing_safety_rubric_fail_readiness(package):
    m, _ = package
    original = experiment.exposure_registry()
    assert original["prompt_sha256"]
    m["cases"][0]["criteria"] = ["quality"]
    assert not experiment.readiness(m)["ready"]


def test_trace_flags_cannot_override_missing_actual_tool_sequence(package):
    m, b = package
    e = b["runs"][0]["evidence"][0]
    e["step_names"] = ["draft_recommendation"]
    signed(e)
    assert not experiment.evaluate(m, b)["runs"][0]["gates"]["G6"]


def test_known_failure_does_not_hide_unresolved_safety_review(package):
    m, b = package
    ids = ["narrative-01", "narrative-02", "narrative-03"]
    verdict(b, ids)
    verdict(b, ids, "uncertain", criterion="safe", stages=("first_reviews",))
    result = experiment.evaluate(m, b)["runs"][0]
    assert result["first_review_pending"] == 3 and not result["gates"]["G5"]
