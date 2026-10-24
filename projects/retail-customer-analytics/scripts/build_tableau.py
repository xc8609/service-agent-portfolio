"""Build the small native Tableau workbook from the four public CSV contracts.

No source rows are embedded. Connections are relative to the dashboard directory.
The XML follows the existing portfolio workbook's native Tableau structure; a
successful build is a structural check, not a substitute for opening in Tableau.
"""

import uuid
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "monthly": [
        ("month", "date"),
        ("sales_value", "real"),
        ("sales_orders", "integer"),
        ("cancellation_value", "real"),
        ("cancellation_documents", "integer"),
        ("known_sales_value", "real"),
        ("known_sales_orders", "integer"),
    ],
    "countries": [
        ("country", "string"),
        ("sales_value", "real"),
        ("sales_orders", "integer"),
        ("cancellation_value", "real"),
    ],
    "cohorts": [
        ("cohort_month", "date"),
        ("month_index", "integer"),
        ("cohort_customers", "integer"),
        ("active_customers", "integer"),
        ("repeat_rate", "real"),
    ],
    "segments": [
        ("segment", "string"),
        ("customers", "integer"),
        ("sales_value_12m", "real"),
        ("orders_12m", "integer"),
        ("median_recency_days", "real"),
    ],
}
CAPTIONS = {
    "sales_value": "Positive sales value (GBP)",
    "sales_value_12m": "12-month positive sales value (GBP)",
    "month_index": "Months since first observed order",
    "repeat_rate": "Cohort return rate",
    "cohort_label": "First observed order month",
    "customers": "Customers",
}


def node(parent, tag, text=None, **attributes):
    element = ET.SubElement(
        parent, tag, {k.replace("_", "-"): str(v) for k, v in attributes.items()}
    )
    element.text = text
    return element


def simple_id(parent, name):
    node(
        parent,
        "simple-id",
        uuid="{" + str(uuid.uuid5(uuid.NAMESPACE_URL, "retail-analytics/" + name)).upper() + "}",
    )


def column_definition(name, dtype):
    dimension = dtype in ("string", "date") or name == "month_index"
    column = ET.Element(
        "column",
        {
            "name": "[" + name + "]",
            "caption": CAPTIONS.get(name, name.replace("_", " ").title()),
            "datatype": dtype,
            "role": "dimension" if dimension else "measure",
            "type": "ordinal" if dtype == "date" else "nominal" if dimension else "quantitative",
        },
    )
    if not dimension:
        column.set(
            "default-format",
            "p0.0%" if name == "repeat_rate" else "#,##0.00" if "value" in name else "#,##0",
        )
    return column


def relation(parent, name):
    rel = node(
        parent,
        "relation",
        connection="textscan." + name,
        name=name + ".csv",
        table="[" + name + "#csv]",
        type="table",
    )
    columns = node(
        rel, "columns", character_set="UTF-8", header="yes", locale="en_GB", separator=","
    )
    for ordinal, (field, dtype) in enumerate(SCHEMAS[name]):
        node(columns, "column", datatype=dtype, name=field, ordinal=ordinal)


def datasource(parent, name):
    ds = node(
        parent, "datasource", caption=name, inline="true", name="federated." + name, version="18.1"
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
            "filename": name + ".csv",
            "password": "",
            "server": "",
        },
    )
    relation(connection, name)
    records = node(connection, "metadata-records")
    object_id = name + ".csv_RETAIL"
    for ordinal, (field, dtype) in enumerate(SCHEMAS[name]):
        record = node(records, "metadata-record", **{"class": "column"})
        values = {
            "remote-name": field,
            "remote-type": {"string": 129, "date": 133, "real": 5, "integer": 20}[dtype],
            "local-name": "[" + field + "]",
            "parent-name": "[" + name + ".csv]",
            "remote-alias": field,
            "ordinal": ordinal,
            "local-type": dtype,
            "aggregation": "Year" if dtype == "date" else "Count" if dtype == "string" else "Sum",
            "contains-null": "true",
            "object-id": "[" + object_id + "]",
        }
        for key, value in values.items():
            node(record, key, str(value))
        ds.append(column_definition(field, dtype))
    if name == "cohorts":
        label = column_definition("cohort_label", "string")
        node(
            label,
            "calculation",
            **{
                "class": "tableau",
                "formula": "STR(DATEPART('year', [cohort_month])) + '-' + RIGHT('0' + STR(DATEPART('month', [cohort_month])), 2)",
            },
        )
        ds.append(label)
    node(
        ds,
        "layout",
        dim_ordering="alphabetic",
        measure_ordering="alphabetic",
        show_structure="true",
    )
    obj = node(
        node(node(ds, "object-graph"), "objects"), "object", caption=name + ".csv", id=object_id
    )
    relation(node(obj, "properties", context=""), name)
    return ds


def instance(field, derivation, kind):
    prefix = {"None": "none", "Sum": "sum", "Avg": "avg"}[derivation]
    suffix = "nk" if kind == "nominal" else "qk"
    return "[" + prefix + ":" + field + ":" + suffix + "]"


def worksheet(parent, name, ds, dimension, measure, mark="Bar", column_dimension=None):
    source = ds.attrib["name"]
    sheet = node(parent, "worksheet", name=name)
    title = node(node(node(sheet, "layout-options"), "title"), "formatted-text")
    node(title, "run", name, bold="true", fontcolor="#173b46", fontsize="12")
    table = node(sheet, "table")
    view = node(table, "view")
    node(node(view, "datasources"), "datasource", caption=ds.attrib["caption"], name=source)
    dependencies = node(view, "datasource-dependencies", datasource=source)
    for definition in ds.findall("column"):
        dependencies.append(deepcopy(definition))
    dim_kind = "quantitative" if mark == "Line" else "nominal"
    used = [
        (dimension, "None", dim_kind),
        (measure, "Avg" if mark == "Square" else "Sum", "quantitative"),
    ]
    if column_dimension:
        used.append((column_dimension, "None", "nominal"))
    for field, derivation, kind in used:
        node(
            dependencies,
            "column-instance",
            column="[" + field + "]",
            derivation=derivation,
            name=instance(field, derivation, kind),
            pivot="key",
            type=kind,
        )
    node(view, "aggregation", value="true")
    style = node(table, "style")
    for element, formats in [
        ("cell", {"font-family": "Tableau Book", "font-size": "10"}),
        ("worksheet", {"display-field-labels": "false"}),
        ("gridline", {"line-visibility": "off"}),
    ]:
        rule = node(style, "style-rule", element=element)
        for attr, value in formats.items():
            node(rule, "format", attr=attr, value=value)
    if mark != "Line":
        header = node(style, "style-rule", element="header")
        node(
            header,
            "format",
            attr="width",
            field="[" + source + "]." + instance(dimension, "None", dim_kind),
            value="190",
        )
    pane = node(
        node(table, "panes"), "pane", selection_relaxation_option="selection-relaxation-allow"
    )
    node(node(pane, "view"), "breakdown", value="auto")
    node(pane, "mark", **{"class": mark})
    encodings = node(pane, "encodings")
    metric = "[" + source + "]." + instance(measure, used[1][1], "quantitative")
    dim = "[" + source + "]." + instance(dimension, "None", dim_kind)
    node(encodings, "tooltip", column=metric)
    if mark != "Line":
        node(encodings, "text", column=metric)
    if mark == "Square":
        node(encodings, "color", column=metric)
    mark_style = node(node(pane, "style"), "style-rule", element="mark")
    if mark != "Square":
        node(mark_style, "format", attr="color", value="#167d8d")
    node(mark_style, "format", attr="mark-labels-show", value="false" if mark == "Line" else "true")
    node(mark_style, "format", attr="size", value="1" if mark == "Square" else "0.65")
    node(table, "rows", metric if mark == "Line" else dim)
    node(
        table,
        "cols",
        dim
        if mark == "Line"
        else "[" + source + "]." + instance(column_dimension, "None", "nominal")
        if column_dimension
        else metric,
    )
    simple_id(sheet, "worksheet/" + name)


def dashboard(parent, name, subtitle, sources, placements, footer):
    dash = node(parent, "dashboard", name=name)
    node(dash, "style")
    node(dash, "size", maxheight="800", maxwidth="1200", minheight="800", minwidth="1200")
    ds_list = node(dash, "datasources")
    for source in sources:
        node(ds_list, "datasource", caption=source, name="federated." + source)
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

    def zone(identifier, x, y, w, h, text=None, sheet=None, size=11):
        attrs = dict(id=identifier, x=x, y=y, w=w, h=h)
        if sheet:
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
                bold="true" if size == 24 else "false",
                fontcolor="#173b46",
            )
        style = node(z, "zone-style")
        for attr, value in {
            "border-style": "none",
            "border-width": "0",
            "margin": "5",
            "background-color": "#ffffff",
        }.items():
            node(style, "format", attr=attr, value=value)

    zone(1, 2000, 1500, 96000, 6000, text=name.upper(), size=24)
    zone(2, 2000, 8000, 96000, 8000, text=subtitle)
    for i, (sheet, x, y, w, h) in enumerate(placements, 3):
        zone(i, x, y, w, h, sheet=sheet)
    zone(90, 2000, 92000, 96000, 6500, text=footer, size=10)
    simple_id(dash, "dashboard/" + name)


def build():
    root = ET.Element(
        "workbook", {"original-version": "18.1", "source-platform": "mac", "version": "18.1"}
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
    sheets = node(root, "worksheets")
    worksheet(sheets, "Monthly sales value", definitions["monthly"], "month", "sales_value", "Line")
    worksheet(sheets, "Sales by country", definitions["countries"], "country", "sales_value")
    worksheet(
        sheets,
        "Cohort return rate",
        definitions["cohorts"],
        "cohort_label",
        "repeat_rate",
        "Square",
        "month_index",
    )
    worksheet(sheets, "Customers by segment", definitions["segments"], "segment", "customers")
    worksheet(
        sheets, "Sales value by segment", definitions["segments"], "segment", "sales_value_12m"
    )
    dashboards = node(root, "dashboards")
    layout = {
        "Sales": [
            ("Monthly sales value", 2000, 18000, 56000, 72000),
            ("Sales by country", 60000, 18000, 38000, 72000),
        ],
        "Repeat purchase": [("Cohort return rate", 2000, 18000, 96000, 72000)],
        "Customer priorities": [
            ("Customers by segment", 2000, 18000, 47000, 72000),
            ("Sales value by segment", 51000, 18000, 47000, 72000),
        ],
    }
    dashboard(
        dashboards,
        "Sales",
        "UCI Online Retail II | Dec 2009–Nov 2011 | Positive sales records, GBP\nWhich markets and months contribute the most sales?",
        ["monthly", "countries"],
        layout["Sales"],
        "Complete months only. Cancellations are separate records, not matched refunds. Hover marks for values; each chart uses its own aggregate source.",
    )
    dashboard(
        dashboards,
        "Repeat purchase",
        "Known customers only | First observed purchase cohort | M0–M11\nWhat share of each cohort returns in the following months?",
        ["cohorts"],
        layout["Repeat purchase"],
        "Rate = active customers / original cohort size. M0 is the first observed month, not confirmed acquisition. Future months are null, not 0%.",
    )
    dashboard(
        dashboards,
        "Customer priorities",
        "Snapshot: 1 Dec 2011 | Activity: Dec 2010–Nov 2011 | Known customers\nCompare segment size with positive sales value before proposing follow-up work.",
        ["segments"],
        layout["Customer priorities"],
        "Active/recent: purchase within 90 days. Repeat: at least 2 orders in the last 12 months. Lapsed is a historical segment label, not confirmed churn.",
    )
    windows = node(root, "windows", source_height="30")
    for sheet in sheets:
        window = node(windows, "window", **{"class": "worksheet", "name": sheet.attrib["name"]})
        simple_id(window, "window/" + sheet.attrib["name"])
    for name, placements in layout.items():
        window = node(
            windows, "window", **{"class": "dashboard", "name": name, "maximized": "true"}
        )
        viewpoints = node(window, "viewpoints")
        for sheet, *_ in placements:
            node(node(viewpoints, "viewpoint", name=sheet), "zoom", type="entire-view")
        node(window, "active", id="-1")
        simple_id(window, "window/" + name)
    ET.indent(root, space="  ")
    destination = PROJECT / "dashboard" / "retail_customers.twb"
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
    print("Built dashboard/retail_customers.twb: 4 CSV sources, 5 worksheets, 3 dashboards")


if __name__ == "__main__":
    build()
