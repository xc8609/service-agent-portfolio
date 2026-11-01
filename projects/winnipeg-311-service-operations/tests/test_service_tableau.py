"""Protect workbook structure and filter scopes; native rendering is checked separately."""

import importlib.util
import re
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "winnipeg_311_tableau", PROJECT / "scripts/build_tableau.py"
)
tableau = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tableau)


def views(root, source):
    return [
        view
        for view in root.findall("./worksheets/worksheet/table/view")
        if view.find("./datasources/datasource").get("name") == "federated." + source
    ]


def test_build_is_deterministic_and_reads_only_published_results(tmp_path):
    destination = tmp_path / "service.twb"
    tableau.build(destination)
    first = destination.read_bytes()
    tableau.build(destination)
    assert destination.read_bytes() == first
    assert (PROJECT / "dashboard/service_operations.twb").read_bytes() == first
    root = ET.parse(destination).getroot()
    for source in root.findall("./datasources/datasource"):
        connection = source.find("./connection/named-connections/named-connection/connection")
        assert connection.get("directory") == "../results"
        assert (PROJECT / "results" / connection.get("filename")).exists()
    assert b"machine-id" not in first and b"author-id" not in first


def test_dashboard_zones_and_windows_reference_real_sheets():
    root = tableau.build_tree()
    names = {sheet.get("name") for sheet in root.findall("./worksheets/worksheet")}
    assert len(names) == 14
    assert len(root.findall("./dashboards/dashboard")) == 2
    for zone in root.findall("./dashboards/dashboard/zones//zone[@name]"):
        assert zone.get("name") in names
    for viewpoint in root.findall("./windows/window/viewpoints/viewpoint"):
        assert viewpoint.get("name") in names
    for view in root.findall("./worksheets/worksheet/table/view"):
        assert {child.tag for child in view} <= {
            "datasources",
            "datasource-dependencies",
            "filter",
            "slices",
            "aggregation",
        }


def test_page_controls_are_shared_within_one_source_only():
    root = tableau.build_tree()
    for view in views(root, "requests"):
        shared = {
            f.get("column").split(":")[1]: f for f in view.findall("filter") if f.get("filter-group")
        }
        assert set(shared) == {"month", "waste_stream"}
        assert shared["month"].findtext("min") == "#2023-01-01#"
        assert shared["month"].findtext("max") == "#2026-09-01#"
    for view in views(root, "ageing"):
        assert [f.get("filter-group") for f in view.findall("filter")] == ["21"]
    for view in views(root, "turnaround") + views(root, "followups"):
        assert not view.findall("filter")


def test_rates_are_weighted_by_summed_counts():
    root = tableau.build_tree()
    formulas = {
        column.get("name"): column.find("calculation").get("formula")
        for column in root.findall("./datasources/datasource/column")
        if column.find("calculation") is not None
    }
    assert formulas["[within_7_share]"] == "SUM([closed_within_7_days]) / SUM([cases])"
    assert formulas["[breached_share]"] == "SUM([breached_calls]) / SUM([follow_up_calls])"
    assert "'5. 365 days or more'" in formulas["[year_or_more_share]"]


def test_actions_target_real_sheets_and_cross_source_turnaround():
    root = tableau.build_tree()
    names = {sheet.get("name") for sheet in root.findall("./worksheets/worksheet")}
    actions = root.findall("./actions/action")
    assert len(actions) == 3
    for action in actions:
        assert action.find("activation").get("auto-clear") == "true"
        assert action.find("source").get("worksheet") in names
        exclude = action.find("command/param[@name='exclude']").get("value").split(",")
        assert set(exclude) <= names
    turnaround = next(a for a in actions if a.get("caption").endswith("for turnaround"))
    assert "federated.turnaround" in turnaround.find("link").get("expression")


def test_visual_field_instances_resolve_to_defined_columns():
    root = tableau.build_tree()
    for view in root.findall("./worksheets/worksheet/table/view"):
        dependency = view.find("datasource-dependencies")
        names = {c.get("name") for c in dependency.findall("column")}
        for inst in dependency.findall("column-instance"):
            assert inst.get("column") in names
        for column in dependency.findall("column"):
            calculation = column.find("calculation")
            if calculation is not None:
                fields = re.findall(r"\[([^\]]+)\]", calculation.get("formula"))
                assert {"[" + n + "]" for n in fields} <= names
