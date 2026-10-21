"""Reconciled aggregate exports: no customer narrative, staff or transaction identifiers."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .db import ROOT, runtime_connection

PROJECT = ROOT / "projects/bank-service-assist"
FIELDS = ("metric_group", "metric", "segment", "value", "availability", "cutoff", "data_kind")


def snapshot(conn, cutoff):
    marts = {
        name: conn.execute(
            (PROJECT / "sql" / f"{name}_mart.sql").read_text(), {"cutoff": cutoff}
        ).fetchall()
        for name in ("run", "proposal", "contact_plan")
    }
    # Independent base-table oracle checks; no joins to steps/revisions/attempt details.
    oracle = {
        "runs": conn.execute(
            "SELECT count(*) AS n FROM agent_runs WHERE started_at<=%s", (cutoff,)
        ).fetchone()["n"],
        "proposals": conn.execute(
            "SELECT count(DISTINCT proposal_id) AS n FROM proposal_revisions WHERE recorded_at<=%s",
            (cutoff,),
        ).fetchone()["n"],
        "attempts": conn.execute(
            "SELECT count(*) AS n FROM callback_attempts WHERE occurred_at<=%s", (cutoff,)
        ).fetchone()["n"],
    }
    if (
        len(marts["run"]),
        len(marts["proposal"]),
        sum(r["actual_calls"] for r in marts["contact_plan"]),
    ) != (oracle["runs"], oracle["proposals"], oracle["attempts"]):
        raise ValueError("Source totals do not reconcile")
    rows = []

    def add(group, metric, segment, value, availability="observed_synthetic"):
        rows.append(
            dict(
                zip(
                    FIELDS,
                    (
                        group,
                        metric,
                        segment,
                        value,
                        availability,
                        cutoff.isoformat(),
                        "synthetic_operational",
                    ),
                )
            )
        )

    runs = marts["run"]
    proposals = marts["proposal"]
    plans = marts["contact_plan"]
    add("Agent runs", "All started runs", "all", len(runs))
    for state in ("awaiting_human", "failed", "cancelled", "interrupted", "running"):
        add("Agent runs", "Run outcome", state, sum(r["status"] == state for r in runs))
    for profile, n in sorted(Counter(r["provider_profile"] for r in runs).items()):
        add("Agent runs", "Provider profile", profile, n)
    latencies = [float(r["latency_ms"]) for r in runs if r["latency_ms"] is not None]
    add("Agent runs", "Missing terminal latency", "all", len(runs) - len(latencies))
    add(
        "Agent runs",
        "Mean terminal latency (ms)",
        "completed timing only",
        sum(latencies) / len(latencies) if latencies else None,
        "observed_synthetic" if latencies else "unavailable",
    )
    add("Agent runs", "Missing usage", "all", sum(r["usage_unknown"] for r in runs))
    add("Agent runs", "Model cost", "all", None, "unavailable_not_qualified")
    add("Proposals", "All proposals", "all", len(proposals))
    for state in ("accepted_unchanged", "accepted_edited", "rejected", "pending"):
        add("Proposals", "Disposition", state, sum(r["disposition"] == state for r in proposals))
    for segment, subset in (
        ("all", proposals),
        ("agent", [r for r in proposals if r["origin"] == "agent"]),
        ("staff", [r for r in proposals if r["origin"] == "staff"]),
    ):
        decided = sum(r["disposition"] != "pending" for r in subset)
        accepted = sum(r["status"] == "committed" for r in subset)
        if segment != "all":
            add("Proposals", "Origin", segment, len(subset))
        add("Proposals", "Decided denominator", segment, decided)
        add(
            "Proposals",
            "Accepted proportion",
            "decided only" if segment == "all" else segment + " drafts, decided only",
            accepted / decided if decided else None,
            "observed_synthetic" if decided else "unavailable",
        )
    add("Contact history", "Lifetime recorded outcomes", "all", oracle["attempts"])
    for kind in ("initial", "lead_approved"):
        subset = [r for r in plans if r["kind"] == kind]
        for field, label in [
            ("actual_calls", "Recorded outcomes"),
            ("counted_calls", "Quota-counted calls"),
            ("never_dialed_faults", "Never-dialed faults"),
            ("window_missed", "Retained window misses"),
        ]:
            add("Contact history", label, kind, sum(int(r[field] or 0) for r in subset))
    add(
        "Contact history",
        "Original first-contact target misses",
        "initial",
        sum(bool(r["first_contact_missed"]) for r in plans),
    )
    add(
        "Evaluation",
        "Measured human time saved",
        "not studied",
        None,
        "unavailable_no_effort_study",
    )
    add("Evaluation", "Measured ROI", "not studied", None, "unavailable_no_effort_study")
    rows.sort(key=lambda r: (r["metric_group"], r["metric"], r["segment"]))
    fingerprint = hashlib.sha256(
        json.dumps(marts, sort_keys=True, default=str).encode()
    ).hexdigest()
    return rows, oracle, fingerprint


def export(settings, output, cutoff):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with runtime_connection(settings.database_url) as conn:
        rows, oracle, fingerprint = snapshot(conn, cutoff)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue()
    delivered = list(csv.DictReader(io.StringIO(data)))

    def value(metric):
        return sum(float(r["value"]) for r in delivered if r["metric"] == metric and r["value"])

    if (value("All started runs"), value("All proposals"), value("Lifetime recorded outcomes")) != (
        oracle["runs"],
        oracle["proposals"],
        oracle["attempts"],
    ):
        raise ValueError("CSV reconciliation failed")
    path = output / "workflow_metrics.csv"
    manifest = output / "manifest.json"
    old = json.loads(manifest.read_text()) if manifest.exists() else None
    report = {
        "status": "reconciled",
        "cutoff": cutoff.isoformat(),
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "data_kind": "synthetic_operational",
        "source_totals": oracle,
        "aggregate_rows": len(rows),
        "source_fingerprint": fingerprint,
        "csv_sha256": hashlib.sha256(data.encode()).hexdigest(),
        "previous_source_fingerprint": old["source_fingerprint"] if old else None,
        "source_changed_since_previous_export": old["source_fingerprint"] != fingerprint
        if old
        else None,
        "snapshot_semantics": "Current state at extraction for records started/occurred by cutoff; not historical time travel. Late corrections can change repeated-cutoff exports.",
        "contains_customer_content": False,
        "cost": "unavailable",
        "human_effort_study": "not_executed",
    }
    path.write_text(data)
    manifest.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PROJECT / "data/processed/tableau")
    parser.add_argument("--cutoff")
    args = parser.parse_args()
    cutoff = (
        datetime.fromisoformat(args.cutoff.replace("Z", "+00:00"))
        if args.cutoff
        else datetime.now(timezone.utc)
    )
    if cutoff.tzinfo is None:
        parser.error("cutoff requires timezone")
    print(json.dumps(export(Settings.from_env(), args.output, cutoff), indent=2))


if __name__ == "__main__":
    main()
