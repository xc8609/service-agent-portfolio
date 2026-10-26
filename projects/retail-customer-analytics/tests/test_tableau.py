"""Protect BI grain/filter contracts; native rendering is a separate UAT check."""

import importlib.util
import re
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "retail_tableau", PROJECT / "scripts/build_tableau.py"
)
tableau = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tableau)


def views(root, source):
    return [
        view
        for view in root.findall("./worksheets/worksheet/table/view")
        if view.find("./datasources/datasource").get("name") == "federated." + source
    ]


def test_native_structure_regression_and_relative_local_connections(tmp_path):
    destination = tmp_path / "retail.twb"
    tableau.build(destination)
    initial = destination.read_bytes()
    tableau.build(destination)
    assert destination.read_bytes() == initial
    root = ET.parse(destination).getroot()
    assert root.get("source-build")
    # Native 2026 rejected legacy computed-sort and the non-existent font-color format.
    for view in root.findall("./worksheets/worksheet/table/view"):
        assert {child.tag for child in view} <= {
            "datasources",
            "datasource-dependencies",
            "filter",
            "sort",
            "slices",
            "aggregation",
        }
    assert not root.findall(".//format[@attr='font-color']")
    for window in root.findall("./windows/window"):
        tags = [child.tag for child in window]
        assert tags == (
            ["cards", "viewpoint", "simple-id"]
            if window.get("class") == "worksheet"
            else ["viewpoints", "active", "device-preview", "simple-id"]
        )
    sources = root.findall("./datasources/datasource")
    assert len(root.findall("./dashboards/dashboard")) == 3
    worksheet_names = {sheet.get("name") for sheet in root.findall("./worksheets/worksheet")}
    for zone in root.findall("./dashboards/dashboard/zones//zone[@name]"):
        assert zone.get("name") in worksheet_names
    for viewpoint in root.findall("./windows/window/viewpoints/viewpoint"):
        assert viewpoint.get("name") in worksheet_names
    for source in sources:
        connection = source.find("./connection/named-connections/named-connection/connection")
        assert connection.get("directory") in ("../results", "../data/processed")
        assert connection.get("password") == ""
    assert b"machine-id" not in initial and b"author-id" not in initial


def test_page_scopes_do_not_leak_and_every_trading_sheet_receives_controls():
    root = tableau.build_tree()
    groups = {}
    for source in ("trading", "products"):
        source_views = views(root, source)
        assert len(source_views) == 5
        groups[source] = set()
        for view in source_views:
            filters = view.findall("filter")
            shared = {f.get("column").split(":")[1]: f for f in filters if f.get("filter-group")}
            assert {"country", "occurred_date"} <= set(shared)
            assert shared["occurred_date"].findtext("min") == "#2011-01-01#"
            assert shared["occurred_date"].findtext("max") == "#2011-11-30#"
            groups[source].update(f.get("filter-group") for f in shared.values())
    assert groups["trading"].isdisjoint(groups["products"])
    for view in views(root, "customers") + views(root, "cohorts"):
        assert not any(
            "occurred_date" in f.get("column", "") or "country" in f.get("column", "")
            for f in view.findall("filter")
        )
    market = root.find("./worksheets/worksheet[@name='Markets']")
    assert market.findtext("./table/rows").endswith("[none:country:nk]")
    assert market.find(".//groupfilter[@function='end']") is None
    zoom = root.find(
        "./windows/window[@name='01 Trading performance']/viewpoints/viewpoint[@name='Markets']/zoom"
    )
    assert zoom.get("type") == "fit-width"


def test_product_penetration_keeps_full_scope_before_product_selection():
    root = tableau.build_tree()
    product_source = root.find("./datasources/datasource[@name='federated.products']")
    denominator = product_source.find("./column[@name='[scope_invoices]']/calculation").get(
        "formula"
    )
    assert denominator == "{ FIXED : COUNTD([invoice_key]) }"
    for view in views(root, "products"):
        context = {
            f.get("column").split(":")[1]
            for f in view.findall("filter")
            if f.get("context") == "true"
        }
        assert context == {"country", "occurred_date", "segment", "is_merchandise"}
        service_filter = next(
            f for f in view.findall("filter") if "is_merchandise" in f.get("column")
        )
        assert service_filter.find("groupfilter").get("member") == '"Merchandise"'
        assert not any(
            "product_key" in f.get("column", "") and f.get("context")
            for f in view.findall("filter")
        )
    # Top-N is a chart limit only, never a KPI or denominator limit.
    top_limited = [
        sheet.get("name")
        for sheet in root.findall("./worksheets/worksheet")
        if sheet.find(".//groupfilter[@function='end']") is not None
    ]
    assert set(top_limited) == {
        "Leading products · top 15",
        "Comparable product changes · all markets",
    }


def test_count_distinct_orders_and_weighted_cohort_rates():
    root = tableau.build_tree()
    for name in ("Purchase invoices", "Merchandise invoices"):
        sheet = root.find("./worksheets/worksheet[@name='" + name + "']")
        assert sheet.find(".//encodings/text").get("column").endswith("[ctd:invoice_key:qk]")
    cohort = root.find(
        "./datasources/datasource[@name='federated.cohorts']/column[@name='[cohort_rate]']/calculation"
    )
    assert cohort.get("formula") == "SUM([active_customers]) / SUM([cohort_customers])"
    sheet = root.find("./worksheets/worksheet[@name='Cohort purchasing']")
    month_members = {x.get("member") for x in sheet.findall(".//filter/groupfilter/groupfilter")}
    assert month_members == {str(n) for n in range(1, 12)}


def test_actions_reference_real_sheets_clear_selection_and_map_cohort_segment():
    root = tableau.build_tree()
    dashboard_names = {x.get("name") for x in root.findall("./dashboards/dashboard")}
    sheet_names = {x.get("name") for x in root.findall("./worksheets/worksheet")}
    actions = root.findall("./actions/action")
    assert len(actions) == 4
    for action in actions:
        activation = action.find("activation")
        assert activation.get("auto-clear") == "true" and activation.get("type") == "on-select"
        source = action.find("source")
        assert source.get("dashboard") in dashboard_names and source.get("worksheet") in sheet_names
        command = action.find("command")
        assert command.get("command") == "tsc:tsl-filter"
        assert command.find("param[@name='target']").get("value") == source.get("dashboard")
        assert set(command.find("param[@name='exclude']").get("value").split(",")) <= sheet_names
    cohort = next(a for a in actions if a.get("caption") == "Select cohort group")
    assert "federated.cohorts" in cohort.find("link").get("expression")
    assert "<[segment]~na>" in cohort.find("link").get("expression")


def test_all_visual_field_instances_resolve_to_defined_columns():
    root = tableau.build_tree()
    for view in root.findall("./worksheets/worksheet/table/view"):
        dependency = view.find("datasource-dependencies")
        names = {c.get("name") for c in dependency.findall("column")}
        for inst in dependency.findall("column-instance"):
            assert inst.get("column") in names
        for column in dependency.findall("column"):
            calculation = column.find("calculation")
            if calculation is not None:
                assert {
                    "[" + n + "]" for n in re.findall(r"\[([^\]]+)\]", calculation.get("formula"))
                } <= names
