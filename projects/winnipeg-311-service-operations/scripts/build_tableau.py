"""Build the two-page Tableau workbook from the published aggregate results.

The workbook reads only ../results CSVs; request records are never needed. XML
structure follows the natively verified retail workbook. Native opening and
interaction are checked separately and recorded in dashboard/verification.md.
"""

import uuid
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

PROJECT = Path(__file__).resolve().parents[1]
INK, PAPER, TEAL = "#242424", "#f5f1e8", "#245f58"
COUNTS = [
    "cases",
    "interactions",
    "repeat_contact_cases",
    "closed_cases",
    "closed_within_1_day",
    "closed_within_3_days",
    "closed_within_7_days",
    "closed_within_14_days",
    "closed_within_30_days",
    "open_at_snapshot",
    "cases_with_ward",
]
SCHEMAS = {
    "requests": [
        ("month", "date"),
        ("analysis_group", "string"),
        ("waste_stream", "string"),
        ("request_type", "string"),
    ]
    + [(name, "integer") for name in COUNTS],
    "turnaround": [
        ("open_year", "string"),
        ("analysis_group", "string"),
        ("cases", "integer"),
        ("open_at_snapshot", "integer"),
        ("median_days", "real"),
        ("p90_days", "real"),
    ],
    "ageing": [
        ("analysis_group", "string"),
        ("waste_stream", "string"),
        ("request_type", "string"),
        ("age_band", "string"),
        ("open_cases", "integer"),
    ],
    "followups": [
        ("month", "date"),
        ("breached_calls", "integer"),
        ("not_breached_calls", "integer"),
        ("follow_up_calls", "integer"),
    ],
}
FILES = {
    "requests": "monthly_requests.csv",
    "turnaround": "turnaround_by_year.csv",
    "ageing": "open_ageing.csv",
    "followups": "follow_up_monthly.csv",
}
CALCULATIONS = {
    "requests": {
        "within_7_share": ("real", "SUM([closed_within_7_days]) / SUM([cases])"),
        "within_30_share": ("real", "SUM([closed_within_30_days]) / SUM([cases])"),
    },
    "turnaround": {},
    "ageing": {
        "year_or_more_share": (
            "real",
            "SUM(IF [age_band] = '5. 365 days or more' THEN [open_cases] ELSE 0 END)"
            " / SUM([open_cases])",
        ),
    },
    "followups": {
        "breached_share": ("real", "SUM([breached_calls]) / SUM([follow_up_calls])"),
    },
}
CAPTIONS = {
    "month": "Month opened",
    "analysis_group": "Request group",
    "waste_stream": "Waste stream",
    "request_type": "Request type",
    "cases": "Cases",
    "within_7_share": "Closed within 7 days",
    "within_30_share": "Closed within 30 days",
    "open_year": "Year opened",
    "median_days": "Median days to close",
    "p90_days": "90th percentile days to close",
    "age_band": "Age at 31 Oct 2026",
    "open_cases": "Open records",
    "year_or_more_share": "Open a year or more",
    "follow_up_calls": "Follow-up calls",
    "breached_calls": "Recorded as SLA breached",
    "breached_share": "Share recorded as SLA breached",
}
PERCENT_FIELDS = {"within_7_share", "within_30_share", "year_or_more_share", "breached_share"}
DAY_FIELDS = {"median_days", "p90_days"}
MONTH_RANGE = ("2023-01-01", "2026-09-01")
CONTROLS = {
    "requests": [("month", 11, MONTH_RANGE), ("waste_stream", 12, None)],
    "ageing": [("waste_stream", 21, None)],
}
PAGE_1 = "01 Demand and turnaround"
PAGE_2 = "02 Open records and follow-ups"


def node(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, tag, {k.replace("_", "-"): str(v) for k, v in attributes.items()})
    child.text = text
    return child


def simple_id(parent, name):
    node(
        parent,
        "simple-id",
        uuid="{" + str(uuid.uuid5(uuid.NAMESPACE_URL, "winnipeg-311/" + name)).upper() + "}",
    )


def column_definition(field, dtype, formula=None):
    dimension = dtype in ("string", "date")
    column = ET.Element(
        "column",
        {
            "name": "[" + field + "]",
            "caption": CAPTIONS.get(field, field.replace("_", " ").capitalize()),
            "datatype": dtype,
            "role": "dimension" if dimension else "measure",
            "type": "ordinal" if dtype == "date" else "nominal" if dimension else "quantitative",
        },
    )
    if not dimension:
        column.set(
            "default-format",
            "p0.0%" if field in PERCENT_FIELDS else "n#,##0.0;-#,##0.0" if field in DAY_FIELDS else "#,##0",
        )
    if formula:
        node(column, "calculation", **{"class": "tableau", "formula": formula})
    return column


def relation(parent, name):
    filename = FILES[name]
    rel = node(
        parent,
        "relation",
        connection="textscan." + name,
        name=filename,
        table="[" + filename.replace(".", "#") + "]",
        type="table",
    )
    cols = node(rel, "columns", character_set="UTF-8", header="yes", locale="en_CA", separator=",")
    for ordinal, (field, dtype) in enumerate(SCHEMAS[name]):
        node(cols, "column", datatype=dtype, name=field, ordinal=ordinal)


def datasource(parent, name):
    filename = FILES[name]
    ds = node(
        parent,
        "datasource",
        caption=name.title(),
        inline="true",
        name="federated." + name,
        version="18.1",
    )
    connection = node(ds, "connection", **{"class": "federated"})
    named = node(
        node(connection, "named-connections"),
        "named-connection",
        caption=name,
        name="textscan." + name,
    )
    node(
        named,
        "connection",
        **{
            "class": "textscan",
            "directory": "../results",
            "filename": filename,
            "password": "",
            "server": "",
        },
    )
    relation(connection, name)
    records = node(connection, "metadata-records")
    object_id = filename + "_" + name.upper()
    for ordinal, (field, dtype) in enumerate(SCHEMAS[name]):
        record = node(records, "metadata-record", **{"class": "column"})
        for key, val in {
            "remote-name": field,
            "remote-type": {"string": 129, "date": 133, "real": 5, "integer": 20}[dtype],
            "local-name": "[" + field + "]",
            "parent-name": "[" + filename + "]",
            "remote-alias": field,
            "ordinal": ordinal,
            "local-type": dtype,
            "aggregation": "Year" if dtype == "date" else "Count" if dtype == "string" else "Sum",
            "contains-null": "true",
            "object-id": "[" + object_id + "]",
        }.items():
            node(record, key, str(val))
        ds.append(column_definition(field, dtype))
    for field, (dtype, formula) in CALCULATIONS[name].items():
        ds.append(column_definition(field, dtype, formula))
    node(
        ds,
        "layout",
        dim_ordering="alphabetic",
        measure_ordering="alphabetic",
        show_structure="true",
    )
    obj = node(node(node(ds, "object-graph"), "objects"), "object", caption=filename, id=object_id)
    relation(node(obj, "properties", context=""), name)
    return ds


def instance(field, derivation="None", kind="nominal"):
    prefix = {"None": "none", "Sum": "sum", "Avg": "avg", "User": "usr"}[derivation]
    return "[" + prefix + ":" + field + ":" + ("nk" if kind == "nominal" else "qk") + "]"


def reference(source, field, derivation="None", kind="nominal"):
    return "[federated." + source + "]." + instance(field, derivation, kind)


def add_filter(view, source, field, group, selection):
    date_range = isinstance(selection, tuple)
    filt = node(
        view,
        "filter",
        **{
            "class": "quantitative" if date_range else "categorical",
            "column": reference(source, field, kind="quantitative" if date_range else "nominal"),
            "filter-group": str(group),
            **({"included-values": "in-range"} if date_range else {}),
        },
    )
    if date_range:
        node(filt, "min", "#" + selection[0] + "#")
        node(filt, "max", "#" + selection[1] + "#")
    else:
        node(filt, "groupfilter", function="level-members", level=instance(field))


def worksheet(
    parent,
    name,
    source,
    definitions,
    measure,
    derivation="Sum",
    mark="Text",
    dimension=None,
    col_dimension=None,
    tooltips=(),
):
    """mark: Text (KPI), Bar (rows=dimension), Line (x=dimension), Table (rows × cols)."""
    ds = definitions[source]
    sheet = node(parent, "worksheet", name=name)
    title = node(node(node(sheet, "layout-options"), "title"), "formatted-text")
    node(title, "run", name, bold="true", fontcolor=INK, fontsize="12")
    table = node(sheet, "table")
    view = node(table, "view")
    node(
        node(view, "datasources"),
        "datasource",
        caption=ds.attrib["caption"],
        name=ds.attrib["name"],
    )
    deps = node(view, "datasource-dependencies", datasource=ds.attrib["name"])
    for column in ds.findall("column"):
        deps.append(deepcopy(column))
    line = mark == "Line"
    used = {(measure, derivation, "quantitative")}
    if dimension:
        used.add((dimension, "None", "quantitative" if line else "nominal"))
    if col_dimension:
        used.add((col_dimension, "None", "nominal"))
    for field, aggregation in tooltips:
        used.add((field, aggregation, "quantitative"))
    controls = CONTROLS.get(source, [])
    for field, _, selection in controls:
        used.add((field, "None", "quantitative" if isinstance(selection, tuple) else "nominal"))
    if source in ("turnaround", "ageing") or (source == "requests" and dimension != "analysis_group"):
        used.add(("analysis_group", "None", "nominal"))
    for field, aggregation, kind in sorted(used):
        node(
            deps,
            "column-instance",
            column="[" + field + "]",
            derivation=aggregation,
            name=instance(field, aggregation, kind),
            pivot="key",
            type=kind,
        )
    for field, group, selection in controls:
        add_filter(view, source, field, group, selection)
    if controls:
        slices = node(view, "slices")
        for field, _, selection in controls:
            kind = "quantitative" if isinstance(selection, tuple) else "nominal"
            node(slices, "column", reference(source, field, kind=kind))
    node(view, "aggregation", value="true")
    style = node(table, "style")
    for element, formats in [
        ("cell", {"font-family": "Arial", "font-size": "10"}),
        ("worksheet", {"display-field-labels": "false", "background-color": PAPER}),
        ("gridline", {"line-visibility": "off"}),
    ]:
        rule = node(style, "style-rule", element=element)
        for attr, value in formats.items():
            node(rule, "format", attr=attr, value=value)
    if dimension and not line:
        header = node(style, "style-rule", element="header")
        node(header, "format", attr="width", field=reference(source, dimension), value="200")
    if mark == "Table":
        cell = node(style, "style-rule", element="cell")
        field = reference(source, measure, derivation, "quantitative")
        node(cell, "format", attr="text-format", field=field, value="n#,##0.0;-#,##0.0")
    pane = node(
        node(table, "panes"), "pane", selection_relaxation_option="selection-relaxation-allow"
    )
    node(node(pane, "view"), "breakdown", value="auto")
    node(pane, "mark", **{"class": "Text" if mark == "Table" else mark})
    enc = node(pane, "encodings")
    metric = reference(source, measure, derivation, "quantitative")
    node(enc, "tooltip", column=metric)
    if mark in ("Bar", "Text", "Table"):
        node(enc, "text", column=metric)
    for field, aggregation in tooltips:
        node(enc, "tooltip", column=reference(source, field, aggregation, "quantitative"))
    tooltip = node(node(pane, "customized-tooltip"), "formatted-text")
    if dimension:
        dim_kind = "quantitative" if line else "nominal"
        node(tooltip, "run", "<" + reference(source, dimension, kind=dim_kind) + ">\n", bold="true")
    if col_dimension:
        node(tooltip, "run", "<" + reference(source, col_dimension) + ">\n")
    node(tooltip, "run", CAPTIONS.get(measure, name) + ": <" + metric + ">\n")
    for field, aggregation in tooltips:
        node(
            tooltip,
            "run",
            CAPTIONS.get(field, field)
            + ": <"
            + reference(source, field, aggregation, "quantitative")
            + ">\n",
        )
    if mark in ("Text", "Table"):
        label = node(node(pane, "customized-label"), "formatted-text")
        size = "26" if mark == "Text" else "11"
        node(label, "run", "<" + metric + ">", bold="true", fontcolor=INK, fontsize=size)
    mark_style = node(node(pane, "style"), "style-rule", element="mark")
    node(mark_style, "format", attr="mark-color", value=TEAL)
    node(mark_style, "format", attr="mark-labels-show", value="false" if line else "true")
    node(mark_style, "format", attr="size", value="0.65")
    dim_ref = (
        reference(source, dimension, kind="quantitative" if line else "nominal") if dimension else ""
    )
    if line:
        rows, cols = metric, dim_ref
    elif mark == "Bar":
        rows, cols = dim_ref, metric
    elif mark == "Table":
        rows, cols = dim_ref, reference(source, col_dimension)
    else:
        rows, cols = "", ""
    node(table, "rows", rows)
    node(table, "cols", cols)
    simple_id(sheet, "worksheet/" + name)
    return sheet


def action(parent, name, dashboard, source_sheet, field, target_source, excluded=()):
    a = node(parent, "action", caption=name, name="[" + name + "]")
    node(a, "activation", auto_clear="true", type="on-select")
    node(a, "source", dashboard=dashboard, type="sheet", worksheet=source_sheet)
    query = quote("[federated." + target_source + "].[" + field + "]", safe="")
    expression = "tsl:" + quote(dashboard) + "?" + query + "~s0=<[" + field + "]~na>"
    node(
        a,
        "link",
        caption=name,
        delimiter=",",
        escape="\\",
        expression=expression,
        include_null="true",
        multi_select="true",
        url_escape="true",
    )
    command = node(a, "command", command="tsc:tsl-filter")
    node(command, "param", name="exclude", value=",".join((source_sheet,) + tuple(excluded)))
    node(command, "param", name="target", value=dashboard)


def dashboard(parent, name, subtitle, sources, sheets, controls, note):
    dash = node(parent, "dashboard", name=name)
    style = node(dash, "style")
    node(
        node(style, "style-rule", element="dashboard"),
        "format",
        attr="background-color",
        value=PAPER,
    )
    node(dash, "size", maxheight="820", maxwidth="1200", minheight="680", minwidth="960")
    ds_list = node(dash, "datasources")
    for source in sources:
        node(ds_list, "datasource", caption=source.title(), name="federated." + source)
    zones = node(
        node(dash, "zones"),
        "zone",
        h="100000",
        id="100",
        type_v2="layout-basic",
        w="100000",
        x="0",
        y="0",
    )

    def zone(i, x, y, w, h, text=None, sheet=None, control=None, size=11):
        attrs = dict(id=i, x=x, y=y, w=w, h=h)
        if control:
            source, field, mode = control
            attrs.update(
                type_v2="filter",
                name=sheet,
                param=reference(
                    source, field, kind="quantitative" if mode == "range" else "nominal"
                ),
                mode=mode,
            )
        elif sheet:
            attrs["name"] = sheet
        else:
            attrs["type_v2"] = "text"
        z = node(zones, "zone", **attrs)
        if text:
            node(
                node(z, "formatted-text"),
                "run",
                text,
                fontsize=size,
                bold="true" if size > 15 else "false",
                fontcolor=INK,
            )
        zs = node(z, "zone-style")
        for attr, value in {
            "border-style": "none",
            "border-width": "0",
            "margin": "8",
            "background-color": PAPER,
        }.items():
            node(zs, "format", attr=attr, value=value)

    zone(1, 1800, 1200, 96000, 6000, text=name, size=24)
    zone(2, 1800, 7400, 96000, 8200, text=subtitle)
    for i, (source, field, mode, sheet, x, w) in enumerate(controls, 3):
        zone(i, x, 16000, w, 7000, sheet=sheet, control=(source, field, mode))
    for i, (sheet, x, y, w, h) in enumerate(sheets, 20):
        zone(i, x, y, w, h, sheet=sheet)
    zone(90, 1800, 92500, 96000, 6500, text=note, size=10)
    simple_id(dash, "dashboard/" + name)


LAYOUTS = {
    PAGE_1: [
        ("Cases", 1800, 24000, 31000, 12000),
        ("Closed within 7 days", 34500, 24000, 31000, 12000),
        ("Closed within 30 days", 67200, 24000, 31000, 12000),
        ("Cases by month", 1800, 38000, 59000, 27000),
        ("Cases by request group", 62500, 38000, 35700, 27000),
        ("Closed within 7 days by month", 1800, 66000, 47000, 26000),
        ("Median days to close by year opened", 50500, 66000, 47700, 26000),
    ],
    PAGE_2: [
        ("Open records", 1800, 24000, 31000, 12000),
        ("Open a year or more", 34500, 24000, 31000, 12000),
        ("Follow-ups recorded as breached", 67200, 24000, 31000, 12000),
        ("Open records by request group", 1800, 38000, 47000, 27000),
        ("Open records by age", 50500, 38000, 47700, 27000),
        ("Follow-up calls by month · city-wide", 1800, 66000, 47000, 26000),
        ("Share recorded as SLA breached · city-wide", 50500, 66000, 47700, 26000),
    ],
}


def build_tree():
    root = ET.Element(
        "workbook",
        {
            "original-version": "18.1",
            "source-build": "2026.2.3 (20262.26.0912.1023)",
            "source-platform": "mac",
            "version": "18.1",
        },
    )
    manifest = node(root, "document-format-change-manifest")
    for feature in (
        "ObjectModelEncapsulateLegacy",
        "ObjectModelTableType",
        "SchemaViewerObjectModel",
        "SheetIdentifierTracking",
        "WindowsPersistSimpleIdentifiers",
    ):
        node(manifest, feature)
    sources = node(root, "datasources")
    definitions = {name: datasource(sources, name) for name in SCHEMAS}
    actions = node(root, "actions")
    sheets = node(root, "worksheets")
    worksheet(sheets, "Cases", "requests", definitions, "cases")
    worksheet(sheets, "Closed within 7 days", "requests", definitions, "within_7_share", "User")
    worksheet(sheets, "Closed within 30 days", "requests", definitions, "within_30_share", "User")
    worksheet(
        sheets, "Cases by month", "requests", definitions, "cases", mark="Line", dimension="month"
    )
    worksheet(
        sheets,
        "Cases by request group",
        "requests",
        definitions,
        "cases",
        mark="Bar",
        dimension="analysis_group",
        tooltips=(("within_7_share", "User"),),
    )
    worksheet(
        sheets,
        "Closed within 7 days by month",
        "requests",
        definitions,
        "within_7_share",
        "User",
        mark="Line",
        dimension="month",
        tooltips=(("cases", "Sum"),),
    )
    worksheet(
        sheets,
        "Median days to close by year opened",
        "turnaround",
        definitions,
        "median_days",
        "Avg",
        mark="Table",
        dimension="analysis_group",
        col_dimension="open_year",
        tooltips=(("p90_days", "Avg"), ("cases", "Sum"), ("open_at_snapshot", "Sum")),
    )
    worksheet(sheets, "Open records", "ageing", definitions, "open_cases")
    worksheet(sheets, "Open a year or more", "ageing", definitions, "year_or_more_share", "User")
    worksheet(
        sheets, "Follow-ups recorded as breached", "followups", definitions, "breached_share", "User"
    )
    worksheet(
        sheets,
        "Open records by request group",
        "ageing",
        definitions,
        "open_cases",
        mark="Bar",
        dimension="analysis_group",
        tooltips=(("year_or_more_share", "User"),),
    )
    worksheet(
        sheets,
        "Open records by age",
        "ageing",
        definitions,
        "open_cases",
        mark="Bar",
        dimension="age_band",
    )
    worksheet(
        sheets,
        "Follow-up calls by month · city-wide",
        "followups",
        definitions,
        "follow_up_calls",
        mark="Line",
        dimension="month",
        tooltips=(("breached_calls", "Sum"),),
    )
    worksheet(
        sheets,
        "Share recorded as SLA breached · city-wide",
        "followups",
        definitions,
        "breached_share",
        "User",
        mark="Line",
        dimension="month",
        tooltips=(("follow_up_calls", "Sum"),),
    )
    action(
        actions,
        "Select request group",
        PAGE_1,
        "Cases by request group",
        "analysis_group",
        "requests",
        excluded=("Median days to close by year opened",),
    )
    action(
        actions,
        "Select request group for turnaround",
        PAGE_1,
        "Cases by request group",
        "analysis_group",
        "turnaround",
        excluded=(
            "Cases",
            "Closed within 7 days",
            "Closed within 30 days",
            "Cases by month",
            "Closed within 7 days by month",
        ),
    )
    action(
        actions,
        "Select open-record group",
        PAGE_2,
        "Open records by request group",
        "analysis_group",
        "ageing",
        excluded=(
            "Follow-ups recorded as breached",
            "Follow-up calls by month · city-wide",
            "Share recorded as SLA breached · city-wide",
        ),
    )
    dashboards = node(root, "dashboards")
    dashboard(
        dashboards,
        PAGE_1,
        "WINNIPEG 311 | Garbage and recycling service requests | Cases opened Jan 2023 – Sep 2026\n"
        "Demand by month and request group, and how quickly cases close. Bands are descriptive, not City service standards.",
        ["requests", "turnaround"],
        LAYOUTS[PAGE_1],
        [
            ("requests", "month", "range", "Cases", 1800, 45000),
            ("requests", "waste_stream", "checkdropdown", "Cases", 49000, 30000),
        ],
        "Select a request-group bar to focus the page; click again to clear. Month and stream controls do not change the median table "
        "(precomputed by year and group; blank = not yet determinable because open cases could still change it). "
        "Source: City of Winnipeg 311 Requests, retrieved 1 Nov 2026. Contains information licensed under the Open Government Licence – Winnipeg.",
    )
    dashboard(
        dashboards,
        PAGE_2,
        "WINNIPEG 311 | Open records at 31 Oct 2026 00:00 | City-wide follow-up calls Jan 2023 – Sep 2026\n"
        "Open records include many that are likely not live work. Follow-up calls cannot be linked to a request type.",
        ["ageing", "followups"],
        LAYOUTS[PAGE_2],
        [("ageing", "waste_stream", "checkdropdown", "Open records", 1800, 30000)],
        "Select a request-group bar to focus the open-record views; click again to clear. The stream control applies to open records only. "
        "Follow-up figures cover all City departments. Source: City of Winnipeg 311 Requests, retrieved 1 Nov 2026. "
        "Contains information licensed under the Open Government Licence – Winnipeg.",
    )
    windows = node(root, "windows", source_height="30")
    for sheet in sheets:
        window = node(
            windows,
            "window",
            **{"class": "worksheet", "name": sheet.attrib["name"], "hidden": "true"},
        )
        node(window, "cards")
        node(node(window, "viewpoint"), "zoom", type="entire-view")
        simple_id(window, "window/" + sheet.attrib["name"])
    # Native Tableau restores the final dashboard window; open with the first page.
    for name, placements in reversed(tuple(LAYOUTS.items())):
        window = node(windows, "window", **{"class": "dashboard", "name": name, "maximized": "true"})
        viewpoints = node(window, "viewpoints")
        for sheet, *_ in placements:
            node(node(viewpoints, "viewpoint", name=sheet), "zoom", type="entire-view")
        node(window, "active", id="-1")
        node(
            node(window, "device-preview"),
            "device",
            is_portrait="true",
            name="Generic Phone",
            type="Phone",
        )
        simple_id(window, "window/" + name)
    return root


def build(destination=None):
    root = build_tree()
    ET.indent(root, space="  ")
    destination = destination or PROJECT / "dashboard/service_operations.twb"
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
    print("Built " + destination.name + ": 2 dashboards, 14 worksheets, 3 selection actions")


if __name__ == "__main__":
    build()
