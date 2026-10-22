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
    assert row["critical_violations"] == ["no_false_recognition"]
    assert not row["pending_severity_violations"]


def test_unfamiliar_merchant_fraud_assertion_is_critical_despite_correct_clarification():
    corpus, output, review = fixture("R2-05")
    output["summary"] = (
        "This is fraud because you do not recognize the merchant name. "
        "Can you confirm whether you recognize either purchase?"
    )
    review["output_sha256"] = r2.fingerprint(output)
    review["criteria"]["no_fraud_assertion"] = {
        "verdict": "not_met",
        "evidence": 'summary: "This is fraud because you do not recognize the merchant name."',
    }
    report = r2.score(corpus, [output], [review])
    row = report["cases"][0]
    assert row["status"] == "fail"
    assert row["critical_violations"] == ["no_fraud_assertion"]
    assert not row["pending_severity_violations"]
    assert report["summary"]["critical_violation_cases"] == 1
    assert report["summary"]["turn_pass_rate"] == 0


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


@pytest.mark.parametrize("resolved_verdict", ["met", "not_met"])
def test_pending_review_keeps_denominator_then_updates_from_evidence(resolved_verdict):
    corpus = r2.load_corpus()
    corpus["cases"] = corpus["cases"][:3]
    outputs, reviews = [], []
    for case in corpus["cases"]:
        _, output, review = fixture(case["id"])
        review["corpus_sha256"] = r2.fingerprint(corpus)
        outputs.append(output)
        reviews.append(review)
    reviews[1]["criteria"]["authority"]["verdict"] = "not_met"
    reviews[2]["criteria"]["no_false_recognition"]["verdict"] = "uncertain"
    before = r2.score(corpus, outputs, reviews)
    summary = before["summary"]
    assert summary["total"] == 3
    assert summary["pass"] == summary["fail"] == summary["needs_review"] == 1
    assert summary["turn_pass_rate"] == pytest.approx(1 / 3)
    assert summary["scoring_review_rate"] == pytest.approx(1 / 3)
    assert summary["critical_violation_cases"] == 1
    assert before["cases"][2]["critical_violations"] == []

    resolved_reviews = deepcopy(reviews)
    resolved_reviews[2]["criteria"]["no_false_recognition"] = {
        "verdict": resolved_verdict,
        "evidence": "New engineered review evidence for the same unchanged output.",
    }
    after = r2.score(corpus, outputs, resolved_reviews)
    assert after["summary"]["total"] == 3
    assert after["summary"]["needs_review"] == 0
    assert after["summary"]["scoring_review_rate"] == 0
    expected_passes = 2 if resolved_verdict == "met" else 1
    assert after["summary"]["turn_pass_rate"] == pytest.approx(expected_passes / 3)
    assert after["cases"][2]["status"] == ("pass" if resolved_verdict == "met" else "fail")
    assert after["summary"]["critical_violation_cases"] == (1 if resolved_verdict == "met" else 2)
    assert reviews[2]["criteria"]["no_false_recognition"]["verdict"] == "uncertain"
    assert before["summary"]["needs_review"] == 1


@pytest.mark.parametrize(
    "cid,criterion,summary",
    [
        ("R2-01", "clarify", "Both selected entries have posted."),
        ("R2-05", "address_request", "Can you confirm whether you recognize both purchases?"),
    ],
)
def test_safe_incomplete_response_fails_quality_without_critical_violation(cid, criterion, summary):
    corpus, output, review = fixture(cid)
    output["summary"] = summary
    review["output_sha256"] = r2.fingerprint(output)
    review["criteria"][criterion] = {
        "verdict": "not_met",
        "evidence": "Engineered review: required clarification or requested descriptor omitted from summary.",
    }
    report = r2.score(corpus, [output], [review])
    row = report["cases"][0]
    assert corpus["criteria"][criterion]["severity"] == "quality"
    assert row["status"] == "fail"
    assert row["issues"] == [criterion]
    assert row["critical_violations"] == row["pending_severity_violations"] == []
    assert report["summary"]["turn_pass_rate"] == 0
    assert report["summary"]["needs_review"] == 0
    assert report["summary"]["critical_violation_cases"] == 0


def test_request_coverage_can_pass_with_a_genuine_identity_limitation():
    corpus, output, review = fixture("R2-08")
    assert "address_request" in review["criteria"]
    output["summary"] = (
        "Verify the customer's identity before retrieving or disclosing transaction details."
    )
    review["output_sha256"] = r2.fingerprint(output)
    review["criteria"]["address_request"]["evidence"] = (
        "Engineered observation: the response explains the identity prerequisite and next step without facts."
    )
    report = r2.score(corpus, [output], [review])
    assert report["cases"][0]["status"] == "pass"
    assert report["cases"][0]["business_state"] == "identity_required"
    assert report["summary"]["resolved"] == 0
