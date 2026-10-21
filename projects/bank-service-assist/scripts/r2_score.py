"""Offline R2 development scoring. Human observations, never model self-certification.

Python 3.9 compatible. No API, runtime imports or modifications to frozen pilot data.
"""

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

DEFAULT_CASES = Path(__file__).resolve().parents[1] / "evaluation/r2/development.json"


def obj(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


TEXT = {"type": "string", "minLength": 1, "maxLength": 4000}
OUTPUT = obj(
    {
        "case_id": TEXT,
        "summary": TEXT,
        "citations": {"type": "array", "items": TEXT, "uniqueItems": True, "maxItems": 30},
        "gaps": {"type": "array", "items": TEXT, "maxItems": 10},
    }
)
REVIEW = obj(
    {
        "case_id": TEXT,
        "output_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "corpus_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "reviewer": TEXT,
        "kind": {"enum": ["human", "engineering_fixture"]},
        "business_state": {
            "enum": [
                "awaiting_customer",
                "staff_review",
                "manual_risk_review",
                "identity_required",
                "refresh_required",
                "resolved",
                "unknown",
            ]
        },
        "criteria": {
            "type": "object",
            "additionalProperties": obj(
                {
                    "verdict": {"enum": ["met", "not_met", "uncertain"]},
                    "evidence": TEXT,
                }
            ),
        },
    }
)


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def index(records, known, label):
    result = {}
    for record in records:
        if not isinstance(record, dict) or record.get("case_id") not in known:
            raise ValueError("Unknown or missing case ID in " + label)
        cid = record["case_id"]
        if cid in result:
            raise ValueError("Duplicate case ID in " + label)
        result[cid] = record
    return result


def load_corpus(path=DEFAULT_CASES):
    corpus = json.loads(Path(path).read_text())
    cases = corpus["cases"]
    if (
        corpus["version"] != "r2-development-v1"
        or corpus["frozen"] is not False
        or not cases
        or len({c["id"] for c in cases}) != len(cases)
    ):
        raise ValueError("Invalid R2 development corpus")
    for case in cases:
        criteria = case["criteria"]
        if (
            case["split"] != "development"
            or not case["family"]
            or not criteria
            or len(set(criteria)) != len(criteria)
            or not set(criteria) <= set(corpus["criteria"])
            or not set(case["required_citations"]) <= set(case["allowed_citations"])
        ):
            raise ValueError("Invalid case contract")
    if any(
        c["severity"] not in {"quality", "critical", "pending_owner"}
        for c in corpus["criteria"].values()
    ):
        raise ValueError("Invalid criterion severity")
    return corpus


def score(corpus, outputs, reviews=()):
    """Outputs contain prose only. Reviews are separate, hash-bound observations.

    Reviewer identity/provenance is declared, not authenticated by this local tool.
    Automatic checks never establish arbitrary prose safety or semantic correctness.
    """
    cases = corpus["cases"]
    known = {c["id"] for c in cases}
    if len(known) != len(cases):
        raise ValueError("Duplicate case ID in corpus")
    by_id = index(outputs, known, "outputs")
    reviewed = index(reviews, known, "reviews")
    corpus_hash = fingerprint(corpus)
    rows = []
    for case in cases:
        row = {
            "id": case["id"],
            "family": case["family"],
            "status": "fail",
            "business_state": "unknown",
            "issues": [],
            "critical_violations": [],
            "pending_severity_violations": [],
            "review_kind": None,
        }
        rows.append(row)
        output = by_id.get(case["id"])
        if output is None:
            row["issues"].append("MISSING_OUTPUT")
            continue
        if not Draft202012Validator(OUTPUT).is_valid(output):
            row["issues"].append("INVALID_OUTPUT")
            continue
        row["output_sha256"] = fingerprint(output)
        if not set(output["citations"]) <= set(case["allowed_citations"]):
            row["issues"].append("UNSUPPORTED_CITATION")
        if not set(case["required_citations"]) <= set(output["citations"]):
            row["issues"].append("MISSING_REQUIRED_CITATION")
        review = reviewed.get(case["id"])
        review_valid = review is not None and Draft202012Validator(REVIEW).is_valid(review)
        review_matches = (
            review_valid
            and review["output_sha256"] == row["output_sha256"]
            and review["corpus_sha256"] == corpus_hash
        )
        if not review_matches:
            if not row["issues"]:
                row["status"] = "needs_review"
            row["issues"].append("MISSING_INVALID_OR_STALE_REVIEW")
            continue
        row["review_kind"] = review["kind"]
        row["business_state"] = review["business_state"]
        observed = review["criteria"]
        if set(observed) - set(case["criteria"]):
            raise ValueError("Unknown review criterion")
        uncertain = set(case["criteria"]) - set(observed)
        for criterion, finding in observed.items():
            if finding["verdict"] == "uncertain":
                uncertain.add(criterion)
            elif finding["verdict"] == "not_met":
                row["issues"].append(criterion)
                severity = corpus["criteria"][criterion]["severity"]
                if severity == "critical":
                    row["critical_violations"].append(criterion)
                elif severity == "pending_owner":
                    row["pending_severity_violations"].append(criterion)
        if review["business_state"] == "unknown":
            uncertain.add("business_state")
        elif review["business_state"] != case["expected_business_state"]:
            row["issues"].append("WRONG_BUSINESS_STATE")
        row["unreviewed_criteria"] = sorted(uncertain)
        # A known violation wins over incomplete review; no averaging or overrides.
        if row["issues"]:
            row["status"] = "fail"
        elif uncertain:
            row["status"] = "needs_review"
        else:
            row["status"] = "pass"
    total = len(rows)
    summary = {
        status: sum(r["status"] == status for r in rows)
        for status in ("pass", "fail", "needs_review")
    }
    summary.update(
        {
            "total": total,
            "turn_pass_rate": summary["pass"] / total if total else None,
            "scoring_review_rate": summary["needs_review"] / total if total else None,
            "reviewed_cases": sum(r["review_kind"] is not None for r in rows),
            "human_review_cases": sum(r["review_kind"] == "human" for r in rows),
            "awaiting_customer": sum(r["business_state"] == "awaiting_customer" for r in rows),
            "resolved": sum(r["business_state"] == "resolved" for r in rows),
            "critical_violation_cases": sum(bool(r["critical_violations"]) for r in rows),
            "pending_severity_cases": sum(bool(r["pending_severity_violations"]) for r in rows),
            "engineering_review_cases": sum(
                r["review_kind"] == "engineering_fixture" for r in rows
            ),
        }
    )
    return {
        "rubric": "r2-development-v1",
        "corpus_sha256": corpus_hash,
        "purpose": "development_regression_only",
        "adoption_eligible": False,
        "runtime_qualification": "not_assessed",
        "summary": summary,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--reviews", type=Path)
    args = parser.parse_args()
    reviews = json.loads(args.reviews.read_text()) if args.reviews else []
    result = score(load_corpus(args.cases), json.loads(args.outputs.read_text()), reviews)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
