"""Protect the improvement baselines and the demand classification they rely on."""

import csv
import importlib.util
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "winnipeg_311_improvements", PROJECT / "scripts/build_improvement_baselines.py"
)
baselines = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(baselines)


def types(path):
    with (PROJECT / path).open(newline="") as stream:
        return [row["request_type"] for row in csv.DictReader(stream)]


def test_every_mapped_type_has_one_demand_type():
    demand = baselines.read(PROJECT / "reference/demand_type_map.csv")
    assert sorted(types("reference/demand_type_map.csv")) == sorted(
        types("reference/request_type_map.csv")
    )
    assert len({row["request_type"] for row in demand}) == len(demand)
    assert {row["demand_type"] for row in demand} == {"Collection failure", "Other request"}


def test_missed_collections_count_as_failures_and_third_party_damage_does_not():
    demand = {
        row["request_type"]: row["demand_type"]
        for row in baselines.read(PROJECT / "reference/demand_type_map.csv")
    }
    groups = {
        row["request_type"]: row["analysis_group"]
        for row in baselines.read(PROJECT / "reference/request_type_map.csv")
    }
    for request_type, group in groups.items():
        if group in ("Missed collection", "Escalated missed collection"):
            assert demand[request_type] == "Collection failure"
    assert demand["Carts Damaged By Third Party"] == "Other request"
    assert demand["Solid Waste Staff Complaint / Commendation"] == "Other request"


def test_published_baselines_match_a_rebuild():
    published = json.loads((PROJECT / "results/improvement_baselines.json").read_text())
    assert baselines.build() == published


def test_baselines_reconcile_to_the_summary():
    result = baselines.build()
    summary = json.loads((PROJECT / "results/summary.json").read_text())
    assert result["collection_failure"]["cases"] == summary["cases"]
    assert result["open_records"]["open"] == summary["open_at_snapshot"]
    assert result["open_records"]["open_365_days_or_more"] == summary["open_365_days_or_more"]
    calls = result["city_follow_up_calls"]
    assert sum(year["calls"] for year in calls.values()) == summary["city_follow_up_calls"]


def test_summer_illustration_uses_the_reference_rate():
    summer = baselines.build()["summer_missed_collections"]
    latest = summer["by_year"]["2026"]
    illustration = summer["illustration"]
    assert illustration["over_7_days_at_reference_rate"] < latest["summer_over_7_days"]
    assert (
        illustration["over_7_days_at_reference_rate"] + illustration["fewer_cases_over_7_days"]
        == latest["summer_over_7_days"]
    )
