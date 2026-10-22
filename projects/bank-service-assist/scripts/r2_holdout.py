"""Private R2 authoring, batch answer review and explicit freeze. No model calls.

Declarations are not authenticated signatures. Never use generated approval records
as evidence that a human reviewed answers. Python 3.9 compatible.
"""

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from r2_experiment import fingerprint, instant, readiness, require, scaffold

AUTHOR_FIELDS = (
    "source_facts",
    "customer_statement",
    "staff_request",
    "authorization_state",
    "knowledge_rules",
    "setup_recipe",
    "family_novelty",
    "answer_intent",
    "must_ask",
    "must_not_assert",
    "next_step",
    "citation_rationale",
    "allowed_variation",
)
BATCHES = {
    "A-narrative": ["narrative-%02d" % i for i in range(1, 16)],
    "B-narrative": ["narrative-%02d" % i for i in range(16, 31)],
    "C-structured": ["structured-%02d" % i for i in range(1, 11)],
    "D-critical": ["critical-%02d" % i for i in range(1, 25)],
}


def authoring_template():
    result = scaffold()
    for case in result["cases"]:
        case["authoring"] = {k: "" for k in AUTHOR_FIELDS}
        case["provenance"]["reviewer_kind"] = ""
    return result


def review_template(manifest):
    require(
        {c["id"] for c in manifest["cases"]} == {c for ids in BATCHES.values() for c in ids},
        "Use the 64 stable authoring slot IDs",
    )
    return {
        "version": "r2-answer-review-v1",
        "manifest_sha256": fingerprint(manifest),
        "reviewer": "",
        "reviewer_kind": "",
        "reviewed_at": None,
        "batches": [
            {
                "id": batch,
                "case_ids": list(ids),
                "decision": "pending",
                "rationale": "",
                "exceptions": [],
            }
            for batch, ids in BATCHES.items()
        ],
        "freeze_authorized": False,
    }


def review_markdown(manifest):
    cases = {c["id"]: c for c in manifest["cases"]}
    lines = [
        "# PRIVATE — R2 answer review",
        "",
        "Not model input. Not a model result.",
        "Manifest SHA-256: " + fingerprint(manifest),
        "",
        "Review four batches; record exceptions by case ID. All decisions default to pending.",
        "",
    ]
    for batch, ids in BATCHES.items():
        lines += ["## " + batch, ""]
        for cid in ids:
            case = cases[cid]
            lines += [
                "### " + cid,
                "",
                "Family: " + case.get("family", ""),
                "Expected state: " + case.get("expected_business_state", ""),
                "",
            ]
            # Render as literal fenced JSON so untrusted case text cannot masquerade as instructions.
            visible = {
                "prompt": case.get("prompt", ""),
                "authoring": case.get("authoring", {}),
                "criteria": {k: manifest["criteria"].get(k) for k in case["criteria"]},
                "allowed_citations": case["allowed_citations"],
                "required_citations": case["required_citations"],
                "provenance": case["provenance"],
            }
            serialized = json.dumps(visible, ensure_ascii=True, indent=2).replace("`", "\\u0060")
            lines += ["```json", serialized, "```", ""]
    return "\n".join(lines)


def freeze(manifest, review, *, now=None):
    """Return a new frozen document only after an explicit, current, complete human review."""
    require(manifest.get("frozen") is False, "Already frozen; preserve the original")
    require(review.get("version") == "r2-answer-review-v1", "Review version")
    require(review.get("manifest_sha256") == fingerprint(manifest), "Stale answer review")
    require(
        review.get("reviewer_kind") == "human" and bool(review.get("reviewer")),
        "Human owner review required",
    )
    require(
        review.get("freeze_authorized") is True, "Separate explicit freeze authorization required"
    )
    now = now or datetime.now(timezone.utc)
    require(
        now.tzinfo is not None and instant(review["reviewed_at"]) <= now,
        "Review time must precede freeze",
    )
    expected = review_template(manifest)
    batches = review.get("batches", [])
    require(
        len(batches) == 4 and {b["id"] for b in batches} == set(BATCHES),
        "Four unique batches required",
    )
    for batch in batches:
        require(batch["case_ids"] == BATCHES[batch["id"]], "Changed batch membership")
        require(
            batch.get("decision") == "approve" and bool(batch.get("rationale", "").strip()),
            "Unapproved batch",
        )
        require(
            batch.get("exceptions") == [],
            "Resolve exceptions in a new reviewed revision before freeze",
        )
    require(expected["manifest_sha256"] == review["manifest_sha256"], "Review mismatch")
    result = deepcopy(manifest)
    for case in result["cases"]:
        require(
            all(
                isinstance(case.get("authoring", {}).get(k), str) and case["authoring"][k].strip()
                for k in AUTHOR_FIELDS
            ),
            "Incomplete authoring: " + case["id"],
        )
        require(
            case["provenance"].get("reviewer_kind") == "human",
            "Independent human answer reviewer required",
        )
        case["provenance"]["answer_approved"] = True
    result.update(
        frozen=True,
        frozen_at=now.isoformat(),
        approved_by=review["reviewer"],
        freeze_record={
            "source_manifest_sha256": fingerprint(manifest),
            "answer_review_sha256": fingerprint(review),
            "notice": "Declared human review; not authenticated provenance or model qualification",
        },
    )
    state = readiness(result)
    require(state["ready"], "Freeze blocked: " + ", ".join(state["issues"]))
    return result


def write_new(path, text):
    # Exclusive creation prevents accidental overwriting of reviewed/frozen records.
    with path.open("x", encoding="utf-8") as target:
        target.write(text + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "review", "freeze"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = authoring_template()
    else:
        manifest = json.loads(args.manifest.read_text())
        if args.command == "review":
            result = review_template(manifest)
            if args.markdown:
                require(args.markdown.resolve() != args.out.resolve(), "Output paths must differ")
                require(
                    not args.out.exists() and not args.markdown.exists(), "Outputs already exist"
                )
                write_new(args.markdown, review_markdown(manifest))
        else:
            result = freeze(manifest, json.loads(args.review.read_text()))
    write_new(args.out, json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
