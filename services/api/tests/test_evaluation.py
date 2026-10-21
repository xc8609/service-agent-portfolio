"""QA-02 pilot integrity: frozen inputs, no answer leakage, guards and reproducible scores."""

import hashlib
import json

from bank_api.evaluation import (
    EVAL,
    FROZEN,
    evaluate,
    guard,
    load,
    load_cases,
    prompt,
    template,
)


def test_cases_and_expectations_are_the_frozen_versions():
    for name, digest in FROZEN.items():
        assert hashlib.sha256((EVAL / name).read_bytes()).hexdigest() == digest


def test_prompt_is_the_archived_text_and_contains_no_expectations():
    text = prompt(load_cases())
    assert text == (EVAL / "runs/prompt-sent.txt").read_text()
    for leaked in ("acceptable_actions", "forbidden_actions", "required_citations", "holdout"):
        assert leaked not in text
    for run in (EVAL / "runs").glob("*.json"):
        source = json.loads(run.read_text())["source"]
        assert source["prompt_sha256"] == hashlib.sha256(text.encode()).hexdigest()
        assert source["cases_sha256"] == FROZEN["cases.json"]


def test_guards_flag_unsupported_claims_citations_and_disclosure():
    cases, _ = load()
    case = next(c for c in cases if c["id"] == "EV-09")
    base = {"id": "EV-09", "action": "REFER_SPECIALIST", "citations": ["T1"], "gaps": []}
    assert guard(case, {**base, "summary": "Keep both entries grouped for review."}) == []
    assert "UNSUPPORTED_CLAIM" in guard(case, {**base, "summary": "The refund was processed."})
    assert "FORBIDDEN_PROMISE" in guard(case, {**base, "summary": "It will be refunded tomorrow."})
    assert "UNSUPPORTED_CITATION" in guard(
        case, {**base, "summary": "Review.", "citations": ["CASE-9999"]}
    )
    unverified = next(c for c in cases if c["id"] == "EV-19")
    assert "DISCLOSURE_WITHOUT_VERIFICATION" in guard(
        unverified,
        {"id": "EV-19", "action": "EXPLAIN_ONLY", "summary": "x", "citations": ["T1"], "gaps": []},
    )
    assert guard(case, {"id": "EV-09", "action": "PAY_NOW"}) == ["INVALID_OUTPUT"]


def test_template_reads_only_structured_fields():
    cases, _ = load()
    narrative = next(c for c in cases if c["id"] == "EV-15")
    assert template(narrative)["action"] == "CLARIFY"


def test_committed_results_are_reproducible_and_adjudications_are_explicit():
    report = evaluate()
    committed = json.loads((EVAL / "results.json").read_text())
    assert report == committed
    for name, run in report["runs"].items():
        auto, adjudicated = run["holdout"], run["holdout_after_adjudication"]
        assert adjudicated["passed"] >= auto["passed"]
