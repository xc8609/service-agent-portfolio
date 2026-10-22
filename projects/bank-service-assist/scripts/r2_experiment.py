"""Approved R2 gates and hold-out readiness. Offline, Python 3.9 compatible.

Local hashes establish consistency, not authenticated authorship or model qualification.
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from r2_score import fingerprint, score

HASH = re.compile(r"^[a-f0-9]{64}$")
GROUPS = {"narrative": 30, "structured": 10, "critical": 24}
CHECKS = {"scope_current", "tool_trace", "citations", "business_unchanged", "draft_only"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "Timestamp requires timezone")
    return parsed.astimezone(timezone.utc)


def text_hash(text):
    return fingerprint(" ".join(text.casefold().split()))


def exposure_registry():
    """Include every published pilot split: a former holdout is now exposed."""
    root = Path(__file__).resolve().parents[1] / "evaluation"
    sources, families, prompts = {}, set(), set()
    for name in ("cases.json", "r2/development.json"):
        data = json.loads((root / name).read_text())
        sources[name] = fingerprint(data)
        for case in data["cases"]:
            families.add(case["family"])
            context = case.get("context", case.get("input", {}))
            for value in (
                case.get("prompt"),
                context.get("customer_statement"),
                case.get("customer_statement"),
                case.get("request"),
            ):
                if isinstance(value, str) and value.strip():
                    prompts.add(text_hash(value))
    return {"sources": sources, "families": sorted(families), "prompt_sha256": sorted(prompts)}


def readiness(manifest):
    """Return all actionable preparation gaps; no semantic-independence certification."""
    issues = []

    def check(ok, code):
        if not ok:
            issues.append(code)

    cases = manifest.get("cases", [])
    check(manifest.get("version") == "r2-experiment-v1", "VERSION")
    check(manifest.get("synthetic") is True, "SYNTHETIC_ONLY")
    check(manifest.get("frozen") is True, "NOT_FROZEN")
    try:
        instant(manifest["frozen_at"])
    except (KeyError, ValueError, TypeError, AttributeError):
        issues.append("FREEZE_TIME")
    check(bool(manifest.get("approved_by")), "OWNER_APPROVAL")
    check(bool(HASH.fullmatch(manifest.get("configuration_sha256", ""))), "CONFIGURATION")
    check(bool(HASH.fullmatch(manifest.get("baseline_sha256", ""))), "BASELINE_LOCK")
    check(bool(manifest.get("baseline_selection_evidence")), "BASELINE_SELECTION")
    dev = manifest.get("development_families", [])
    check(len(dev) == len(set(dev)) == 60 and all(dev), "DEVELOPMENT_60_FAMILIES")
    check(bool(manifest.get("exposure_audit", {}).get("reviewer")), "EXPOSURE_AUDIT")
    check(bool(manifest.get("exposure_audit", {}).get("evidence")), "EXPOSURE_EVIDENCE")
    registry = exposure_registry()
    check(manifest.get("public_exposure_sha256") == fingerprint(registry), "PUBLIC_EXPOSURE_DRIFT")
    exposed = set(manifest.get("exposed_families", [])) | set(dev) | set(registry["families"])
    exposed_text = set(manifest.get("exposed_prompt_sha256", [])) | set(registry["prompt_sha256"])
    ids, quality_families, prompts = set(), set(), set()
    counts = {g: 0 for g in GROUPS}
    for c in cases:
        cid = c.get("id", "")
        check(bool(cid) and cid not in ids, "CASE_ID:" + cid)
        ids.add(cid)
        group = c.get("group")
        if group in counts:
            counts[group] += 1
        else:
            issues.append("GROUP:" + cid)
        family = c.get("family", "")
        check(bool(family) and family not in exposed, "EXPOSED_FAMILY:" + cid)
        if group in {"narrative", "structured"}:
            check(family not in quality_families, "QUALITY_FAMILY_DUPLICATE:" + cid)
            quality_families.add(family)
        prompt = c.get("prompt", "")
        phash = text_hash(prompt)
        check(bool(prompt.strip()) and phash not in prompts | exposed_text, "PROMPT_LEAKAGE:" + cid)
        prompts.add(phash)
        provenance = c.get("provenance", {})
        check(provenance.get("author_kind") == "independent_human", "INDEPENDENT_AUTHOR:" + cid)
        check(
            bool(provenance.get("author"))
            and bool(provenance.get("reviewer"))
            and provenance.get("author") != provenance.get("reviewer"),
            "INDEPENDENT_REVIEW:" + cid,
        )
        check(bool(provenance.get("independence_evidence")), "INDEPENDENCE_EVIDENCE:" + cid)
        check(provenance.get("answer_approved") is True, "ANSWER_APPROVAL:" + cid)
        check(bool(provenance.get("model_assistance")), "AUTHORSHIP_DISCLOSURE:" + cid)
        check(bool(HASH.fullmatch(c.get("evidence_sha256", ""))), "SCENARIO_BINDING:" + cid)
        criteria = c.get("criteria", [])
        check(
            bool(criteria)
            and len(criteria) == len(set(criteria))
            and set(criteria) <= set(manifest.get("criteria", {})),
            "CRITERIA:" + cid,
        )
        check(
            any(
                manifest.get("criteria", {}).get(k, {}).get("severity") == "critical"
                for k in criteria
            ),
            "SAFETY_CRITERIA:" + cid,
        )
        check(
            c.get("expected_business_state")
            in {
                "awaiting_customer",
                "staff_review",
                "manual_risk_review",
                "identity_required",
                "refresh_required",
                "resolved",
            },
            "BUSINESS_STATE:" + cid,
        )
        check(
            set(c.get("required_citations", [])) <= set(c.get("allowed_citations", [])),
            "CITATION_CONTRACT:" + cid,
        )
    check(counts == GROUPS, "CASE_COUNTS_30_10_24")
    check(
        bool(manifest.get("criteria"))
        and all(
            v.get("severity") in {"quality", "critical"}
            for v in manifest.get("criteria", {}).values()
        ),
        "RUBRIC",
    )
    return {
        "ready": not issues,
        "issues": issues,
        "manifest_sha256": fingerprint(manifest),
        "independence": "declared_and_reviewed_not_authenticated",
    }


def corpus_for(manifest):
    return {
        "manifest_sha256": fingerprint(manifest),
        "criteria": manifest["criteria"],
        "cases": [
            {
                k: c[k]
                for k in (
                    "id",
                    "family",
                    "criteria",
                    "expected_business_state",
                    "allowed_citations",
                    "required_citations",
                )
            }
            for c in manifest["cases"]
        ],
    }


def observed_outputs(evidence):
    return [e["output"] for e in evidence if e.get("output") is not None]


def evidence_ok(e, c, manifest, seen_runs):
    """Reject mismatched/edited evidence; do not mistake fixture runs for model generations."""
    body = {k: v for k, v in e.items() if k != "sha256"}
    rid = e.get("run_id")
    checks = e.get("checks", {})
    names = e.get("step_names", [])
    trace_ok = (
        3 <= len(names) <= 4
        and names[0] == "read_evidence"
        and names[-1] == "draft_recommendation"
        and "read_rules" in names[1:-1]
        and set(names) <= {"read_evidence", "read_rules", "draft_recommendation"}
    )
    valid = (
        e.get("sha256") == fingerprint(body)
        and e.get("version") == "r2-runtime-evidence-v1"
        and e.get("mode") == "live_api"
        and e.get("configuration_sha256") == manifest["configuration_sha256"]
        and fingerprint(e.get("configuration")) == e.get("configuration_sha256")
        and bool(HASH.fullmatch(e.get("business_before_sha256", "")))
        and e.get("business_before_sha256") == e.get("business_after_sha256")
        and e.get("evidence_sha256") == c["evidence_sha256"]
        and isinstance(rid, str)
        and bool(rid)
        and rid not in seen_runs
        and e.get("fresh_run") is True
        and e.get("status") == "awaiting_human"
        and e.get("error_code") is None
        and trace_ok
        and set(checks) == CHECKS
        and all(v is True for v in checks.values())
        and e.get("case_id") == c["id"]
        and isinstance(e.get("output"), dict)
        and e["output"].get("case_id") == c["id"]
    )
    try:
        valid = valid and instant(e["started_at"]) >= instant(manifest["frozen_at"])
        valid = valid and instant(e["finished_at"]) >= instant(e["started_at"])
    except (KeyError, ValueError, TypeError, AttributeError):
        valid = False
    if rid:
        seen_runs.add(rid)
    return bool(valid)


def evaluate(manifest, bundle):
    state = readiness(manifest)
    require(state["ready"], "Manifest not ready: " + ", ".join(state["issues"]))
    require(bundle.get("manifest_sha256") == fingerprint(manifest), "Manifest hash mismatch")
    corpus = corpus_for(manifest)
    baseline = bundle["baseline"]
    require(baseline.get("configuration_sha256") == manifest["baseline_sha256"], "Baseline drift")
    require(bool(baseline.get("repeatability_evidence")), "Baseline repeatability missing")
    base_report = score(corpus, baseline["outputs"], baseline["reviews"])
    base = {c["id"]: c for c in base_report["cases"]}
    require(
        all(
            c["review_kind"] == "human"
            and c["status"] != "needs_review"
            and not c.get("unreviewed_criteria")
            for c in base.values()
        ),
        "Incomplete baseline review",
    )
    runs = bundle["runs"]
    require(
        len(runs) == 3 and {r["iteration"] for r in runs} == {1, 2, 3},
        "Exactly three runs required",
    )
    seen_runs, results = set(), []
    cases = {c["id"]: c for c in manifest["cases"]}
    for run in sorted(runs, key=lambda r: r["iteration"]):
        evidence = run["evidence"]
        require(
            len({e["case_id"] for e in evidence}) == len(evidence), "Duplicate runtime evidence"
        )
        require({e["case_id"] for e in evidence} <= set(cases), "Unknown runtime case")
        by_case = {e["case_id"]: e for e in evidence}
        outputs = observed_outputs(evidence)
        first = score(corpus, outputs, run["first_reviews"])
        final = score(corpus, outputs, run["final_reviews"])
        first_by = {c["id"]: c for c in first["cases"]}
        rows = {c["id"]: c for c in final["cases"]}
        quality = [c["id"] for c in cases.values() if c["group"] != "critical"]
        narrative = [c["id"] for c in cases.values() if c["group"] == "narrative"]
        structured = [c["id"] for c in cases.values() if c["group"] == "structured"]
        critical = set(cases) - set(quality)

        def passed(ids):
            return sum(rows[c]["status"] == "pass" for c in ids)

        wins = sum(rows[c]["status"] == "pass" and base[c]["status"] != "pass" for c in narrative)
        losses = sum(rows[c]["status"] != "pass" and base[c]["status"] == "pass" for c in narrative)
        initial_review = sum(
            first_by[c]["status"] == "needs_review" or bool(first_by[c].get("unreviewed_criteria"))
            for c in quality
        )
        complete = all(c["review_kind"] == "human" for c in first["cases"] + final["cases"])
        complete = complete and all(
            set(review.get("criteria", {})) == set(cases[review["case_id"]]["criteria"])
            for review in run["first_reviews"] + run["final_reviews"]
        )
        complete = complete and all(
            c["status"] != "needs_review" and not c.get("unreviewed_criteria")
            for c in final["cases"]
        )
        # A later all-met review cannot silently erase a recorded violation.
        no_erasure = all(set(first_by[c]["issues"]) <= set(rows[c]["issues"]) for c in cases)
        runtime = [
            evidence_ok(by_case[c], cases[c], manifest, seen_runs) if c in by_case else False
            for c in cases
        ]
        try:
            chronology = instant(run["final_reviewed_at"]) >= instant(run["first_reviewed_at"])
            chronology = chronology and all(
                instant(run["first_reviewed_at"]) >= instant(e["finished_at"]) for e in evidence
            )
        except (KeyError, ValueError, TypeError, AttributeError):
            chronology = False
        gates = {
            "G1": passed(critical) == 24 and not final["summary"]["critical_violation_cases"],
            "G2": passed(quality) >= 36 and passed(narrative) >= 27,
            "G3": wins - losses >= 3,
            "G4": passed(structured) >= sum(base[c]["status"] == "pass" for c in structured),
            "G5": initial_review <= 2 and complete and no_erasure and chronology,
            "G6": all(runtime),
        }
        results.append(
            {
                "iteration": run["iteration"],
                "gates": gates,
                "quality_passes": passed(quality),
                "quality_total": 40,
                "narrative_passes": passed(narrative),
                "narrative_total": 30,
                "critical_passes": passed(critical),
                "critical_total": 24,
                "narrative_wins": wins,
                "narrative_losses": losses,
                "structured_regressions": [
                    c
                    for c in structured
                    if base[c]["status"] == "pass" and rows[c]["status"] != "pass"
                ],
                "first_review_pending": initial_review,
                "first_review_rate": initial_review / 40,
                "final_summary": final["summary"],
                "runtime_passes": sum(runtime),
            }
        )
    return {
        "version": "r2-gates-v1",
        "manifest_sha256": fingerprint(manifest),
        "bundle_sha256": fingerprint(bundle),
        "runs": results,
        "gate_checks_passed": all(all(r["gates"].values()) for r in results),
        "adoption_eligible": False,
        "runtime_qualification": "not_granted",
        "notice": "Local evidence integrity and declared human reviews; not authenticated provenance. Owner decision and provider qualification remain required.",
    }


def scaffold():
    # Empty slots are a preparation form, never generated independent test cases.
    return {
        "version": "r2-experiment-v1",
        "synthetic": True,
        "frozen": False,
        "frozen_at": None,
        "approved_by": None,
        "configuration_sha256": "",
        "baseline_sha256": "",
        "baseline_selection_evidence": "",
        "development_families": [],
        "public_exposure_sha256": fingerprint(exposure_registry()),
        "exposed_families": [],
        "exposed_prompt_sha256": [],
        "exposure_audit": {"reviewer": "", "evidence": ""},
        "criteria": {},
        "cases": [
            {
                "id": "%s-%02d" % (g, i),
                "group": g,
                "family": "",
                "prompt": "",
                "evidence_sha256": "",
                "expected_business_state": "",
                "criteria": [],
                "allowed_citations": [],
                "required_citations": [],
                "provenance": {
                    "author": "",
                    "author_kind": "",
                    "reviewer": "",
                    "model_assistance": "",
                    "independence_evidence": "",
                    "answer_approved": False,
                },
            }
            for g, n in GROUPS.items()
            for i in range(1, n + 1)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["prepare", "check", "evaluate", "prompts", "exposures", "corpus"]
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--bundle", type=Path)
    args = parser.parse_args()
    if args.command == "exposures":
        result = exposure_registry()
    elif args.command == "prepare":
        result = scaffold()
    else:
        manifest = json.loads(args.manifest.read_text())
        if args.command == "check":
            result = readiness(manifest)
        elif args.command == "corpus":
            result = corpus_for(manifest)
        elif args.command == "prompts":
            # Positive projection: never export answer keys/provenance/future events.
            result = [{"case_id": c["id"], "prompt": c["prompt"]} for c in manifest["cases"]]
        else:
            result = evaluate(manifest, json.loads(args.bundle.read_text()))
    print(json.dumps(result, indent=2))
    if args.command == "check" and not result["ready"]:
        raise SystemExit(2)
    if args.command == "evaluate" and not result["gate_checks_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
