"""Regression cases for case-level deduplication, snapshot status and censored turnaround."""

import importlib.util
from pathlib import Path

import duckdb
import pytest

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "winnipeg_311_build", PROJECT / "scripts/build_analysis.py"
)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)

MISSED = "Missed Garbage Collection Deficiency"
BULKY = "Request for Bulky Pick Up - 10 Items"
SNAPSHOT = "2026-10-31 00:00:00"


def row(
    case,
    opened,
    closed=None,
    request_type=MISSED,
    interaction="1",
    channel="Voice In",
    status=None,
    ward=None,
):
    status = status or ("Closed" if closed else "Open")
    return (
        case,
        interaction,
        channel,
        "Service Request",
        "Water and Waste",
        request_type,
        opened,
        closed,
        status,
        None,
        ward,
    )


@pytest.fixture
def database():
    connections = []

    def load(records, follow_ups=()):
        con = duckdb.connect(":memory:")
        connections.append(con)
        analysis.create_raw(con)
        con.executemany(
            "INSERT INTO raw_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records
        )
        if follow_ups:
            con.executemany("INSERT INTO raw_follow_up VALUES (?, ?, ?)", list(follow_ups))
        analysis.build(con, snapshot_at=SNAPSHOT)
        return con

    yield load
    for con in connections:
        con.close()


def test_repeat_interactions_form_one_case_with_first_channel(database):
    con = database(
        [
            row("a", "2026-03-02T09:00:00", "2026-03-04T09:00:00", interaction="20", channel="e-mail In"),
            row("a", "2026-03-02T09:00:00", "2026-03-04T09:00:00", interaction="10"),
        ]
    )
    assert con.execute(
        "SELECT interactions, first_channel, days_to_close FROM fact_case"
    ).fetchall() == [(2, "Voice In", 2.0)]
    assert con.execute(
        "SELECT cases, interactions, repeat_contact_cases, closed_within_3_days FROM monthly_requests"
    ).fetchall() == [(1, 2, 1, 1)]


def test_conflicting_case_attributes_stop_the_build(database):
    with pytest.raises(ValueError, match="Case attributes differ"):
        database(
            [
                row("a", "2026-03-02T09:00:00", "2026-03-04T09:00:00", interaction="1"),
                row("a", "2026-03-02T09:00:00", "2026-03-09T09:00:00", interaction="2"),
            ]
        )


def test_case_closed_after_snapshot_is_open_and_aged_to_snapshot(database):
    con = database([row("a", "2026-10-21T00:00:00", "2026-11-03T00:00:00")])
    assert con.execute(
        "SELECT open_at_snapshot, closed_at, days_to_close, age_days FROM fact_case"
    ).fetchall() == [(True, None, None, 10.0)]
    assert con.execute("SELECT age_band, open_cases FROM open_ageing").fetchall() == [
        ("2. 7-29 days", 1)
    ]


def test_scope_excludes_unmapped_types_and_cases_after_snapshot(database):
    con = database(
        [
            row("a", "2026-09-01T08:00:00", "2026-09-02T08:00:00"),
            row("b", "2026-09-01T08:00:00", "2026-09-02T08:00:00", request_type="No Water"),
            row("c", "2026-10-31T08:00:00"),
            row("d", "2026-10-05T08:00:00"),
            row("e", "2022-12-31T23:00:00"),
        ]
    )
    assert con.execute("SELECT case_id FROM fact_case ORDER BY 1").fetchall() == [("a",), ("d",)]
    # October opens are aged in the snapshot but are outside the complete-month mart.
    assert con.execute("SELECT sum(cases) FROM monthly_requests").fetchone()[0] == 1
    assert con.execute("SELECT sum(open_cases) FROM open_ageing").fetchone()[0] == 1


def test_quantile_is_withheld_until_open_cases_cannot_change_it(database):
    closed = [
        row(str(index), "2025-01-01T00:00:00", f"2025-01-0{index + 2}T00:00:00", request_type=BULKY)
        for index in range(4)
    ]
    con = database(closed + [row("open", "2025-01-01T00:00:00", request_type=BULKY)])
    median, p90 = con.execute(
        "SELECT median_days, p90_days FROM turnaround_by_year"
    ).fetchone()
    assert median == 3.0
    assert p90 is None


def test_quantile_is_withheld_when_open_cases_are_younger(database):
    con = database(
        [
            row("a", "2026-09-29T00:00:00", "2026-10-30T00:00:00"),
            row("b", "2026-09-29T00:00:00", "2026-10-30T12:00:00"),
            row("c", "2026-09-30T00:00:00"),
        ]
    )
    assert con.execute("SELECT median_days FROM turnaround_by_year").fetchone()[0] is None


def test_follow_up_calls_stop_at_monthly_window(database):
    con = database(
        [row("a", "2026-03-02T09:00:00", "2026-03-04T09:00:00")],
        follow_ups=[
            ("2026-09-01", "Follow up- SLA breached", 4),
            ("2026-09-01", "Follow Up Call- SLA not breached", 6),
            ("2026-10-01", "Follow up- SLA breached", 9),
        ],
    )
    assert con.execute("SELECT * FROM follow_up_monthly").fetchall()[0][1:] == (4, 6, 10)
    assert con.execute("SELECT count(*) FROM follow_up_monthly").fetchone()[0] == 1


def test_published_results_reconcile():
    import json

    results = PROJECT / "results"
    checks = json.loads((results / "checks.json").read_text())
    assert checks and all(checks.values())
    summary = json.loads((results / "summary.json").read_text())
    assert sum(summary["cases_by_group"].values()) == summary["cases"]
