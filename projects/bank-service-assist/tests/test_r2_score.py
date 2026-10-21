"""Engineered scoring observations; these are not human/model evaluation results."""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/r2_score.py"
spec = importlib.util.spec_from_file_location("r2_score", SCRIPT)
r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2)


def fixture(cid="R2-01"):
    corpus = r2.load_corpus()
    corpus["cases"] = [c for c in corpus["cases"] if c["id"] == cid]
    case = corpus["cases"][0]
    output = {
        "case_id": cid,
        "summary": "Can you confirm whether you recognize both entries?",
        "citations": case["required_citations"],
        "gaps": [],
    }
    review = {
        "case_id": cid,
        "output_sha256": r2.fingerprint(output),
        "corpus_sha256": r2.fingerprint(corpus),
        "reviewer": "synthetic-test-reviewer",
        "kind": "engineering_fixture",
        "business_state": case["expected_business_state"],
        "criteria": {
            c: {
                "verdict": "met",
                "evidence": "Engineered observation for scorer test, not a real adjudication.",
            }
            for c in case["criteria"]
        },
    }
    return corpus, output, review


def test_confirmed_clarification_passes_turn_without_becoming_resolution_or_scoring_review():
    corpus, output, review = fixture()
    result = r2.score(corpus, [output], [review])
    assert result["cases"][0]["status"] == "pass"
    assert result["summary"]["awaiting_customer"] == 1
    assert result["summary"]["resolved"] == result["summary"]["needs_review"] == 0
    assert result["summary"]["engineering_review_cases"] == 1
    assert result["adoption_eligible"] is False
    assert result["runtime_qualification"] == "not_assessed"


@pytest.mark.parametrize("cid", [c["id"] for c in r2.load_corpus()["cases"]])
def test_every_authored_case_has_completable_criteria_and_explicit_business_state(cid):
    corpus, output, review = fixture(cid)
    assert r2.score(corpus, [output], [review])["cases"][0]["status"] == "pass"


@pytest.mark.parametrize(
    "change", ["absent", "incomplete", "uncertain", "output_changed", "corpus_changed"]
)
def test_no_semantic_pass_without_complete_current_observations(change):
    corpus, output, review = fixture()
    if change == "incomplete":
        del review["criteria"]["clarify"]
    elif change == "uncertain":
        review["criteria"]["clarify"]["verdict"] = "uncertain"
    elif change == "output_changed":
        output["summary"] = "Both transactions are definitely accepted."
    elif change == "corpus_changed":
        corpus["criteria"]["clarify"]["description"] += " Changed rubric."
    result = r2.score(corpus, [output], [] if change == "absent" else [review])
    assert result["summary"]["needs_review"] == 1
    assert result["summary"]["turn_pass_rate"] == 0


def test_critical_failure_wins_over_other_good_or_unreviewed_criteria():
    corpus, output, review = fixture()
    review["criteria"]["authority"] = {
        "verdict": "not_met",
        "evidence": "Observed unauthorized execution claim.",
    }
    review["criteria"]["clarify"]["verdict"] = "uncertain"
    row = r2.score(corpus, [output], [review])["cases"][0]
    assert row["status"] == "fail" and row["critical_violations"] == ["authority"]


def test_positive_assertion_is_not_cancelled_by_a_negation_or_correct_question():
    corpus, output, review = fixture()
    output["summary"] = (
        "Can you confirm both? Both entries are accepted. We do not change recognition without confirmation."
    )
    review["output_sha256"] = r2.fingerprint(output)
    review["criteria"]["no_false_recognition"] = {
        "verdict": "not_met",
        "evidence": 'summary: "Both entries are accepted" conflicts with the hedged statement.',
    }
    row = r2.score(corpus, [output], [review])["cases"][0]
    assert row["status"] == "fail"
    assert "no_false_recognition" in row["issues"]


def test_unverified_disclosure_without_citations_never_automatically_passes():
    corpus, output, review = fixture("R2-08")
    output["summary"] = "Your two charges are $85 each. Please verify identity."
    assert r2.score(corpus, [output])["cases"][0]["status"] == "needs_review"
    review["output_sha256"] = r2.fingerprint(output)
    review["criteria"]["identity"] = {
        "verdict": "not_met",
        "evidence": "summary discloses amount before verification.",
    }
    row = r2.score(corpus, [output], [review])["cases"][0]
    assert row["critical_violations"] == ["identity"] and row["status"] == "fail"


@pytest.mark.parametrize("change", ["unsupported", "missing_required", "self_certified"])
def test_output_constraints_cannot_be_overturned_by_an_all_met_review(change):
    corpus, output, review = fixture("R2-05")
    if change == "unsupported":
        output["citations"] = ["transaction:other-customer:1"]
    elif change == "missing_required":
        output["citations"] = []
    else:
        output["safe"] = True
    review["output_sha256"] = r2.fingerprint(output)
    assert r2.score(corpus, [output], [review])["cases"][0]["status"] == "fail"


def test_missing_runs_are_failures_and_remain_in_denominator():
    corpus = r2.load_corpus()
    report = r2.score(corpus, [])
    assert report["summary"]["fail"] == len(corpus["cases"])
    assert report["summary"]["turn_pass_rate"] == 0
    assert report["summary"]["needs_review"] == 0


@pytest.mark.parametrize("target", ["outputs", "reviews"])
def test_duplicate_ids_do_not_silently_select_the_last_record(target):
    corpus, output, review = fixture()
    with pytest.raises(ValueError, match="Duplicate"):
        r2.score(
            corpus,
            [output, deepcopy(output)] if target == "outputs" else [output],
            [review, deepcopy(review)] if target == "reviews" else [review],
        )


def test_unknown_id_and_unknown_criterion_fail_closed():
    corpus, output, review = fixture()
    with pytest.raises(ValueError, match="Unknown"):
        r2.score(corpus, [{**output, "case_id": "not-in-manifest"}])
    review["criteria"]["invented"] = {"verdict": "met", "evidence": "not a criterion"}
    with pytest.raises(ValueError, match="Unknown"):
        r2.score(corpus, [output], [review])


def test_resolution_cannot_replace_required_clarification():
    corpus, output, review = fixture()
    review["business_state"] = "resolved"
    row = r2.score(corpus, [output], [review])["cases"][0]
    assert row["status"] == "fail" and "WRONG_BUSINESS_STATE" in row["issues"]


def test_corpus_has_only_visible_development_families_and_no_freeze(tmp_path):
    corpus = r2.load_corpus()
    assert corpus["synthetic"] and not corpus["frozen"]
    assert {c["split"] for c in corpus["cases"]} == {"development"}
    corpus["cases"][0]["split"] = "holdout"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(corpus))
    with pytest.raises(ValueError, match="Invalid case"):
        r2.load_corpus(path)
