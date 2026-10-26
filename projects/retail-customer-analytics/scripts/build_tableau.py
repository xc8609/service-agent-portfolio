"""Build three interactive Tableau dashboards from the SQL export contracts.

Detailed Tableau inputs stay in ignored data/processed; only definitions and
aggregate diagnostics are published. Native opening/interaction is verified
separately from the structural checks in tests/test_tableau.py.
"""

import argparse
import os
import uuid
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

PROJECT = Path(__file__).resolve().parents[1]
INK, PAPER, TEAL, BRONZE = "#242424", "#f5f1e8", "#245f58", "#8b6f47"
SALES_SCHEMA = [
    ("invoice_key", "string"),
    ("occurred_date", "date"),
    ("country", "string"),
    ("product_key", "string"),
    ("product_label", "string"),
    ("customer_key", "string"),
    ("segment", "string"),
    ("units", "real"),
    ("recorded_value", "real"),
    ("is_merchandise", "string"),
]
SCHEMAS = {
    "trading": SALES_SCHEMA,
    "products": SALES_SCHEMA,
    "customers": [
        ("customer_key", "string"),
        ("segment", "string"),
        ("recency_days", "integer"),
        ("orders_12m", "integer"),
        ("sales_value_12m", "real"),
        ("orders_24m", "integer"),
        ("cohort_month", "date"),
        ("eligible_90d", "integer"),
        ("repeated_90d", "integer"),
    ],
    "cohorts": [
        ("cohort_month", "date"),
        ("month_index", "integer"),
        ("segment", "string"),
        ("cohort_customers", "integer"),
        ("active_customers", "integer"),
        ("repeat_rate", "real"),
    ],
    "changes": [
        ("product_key", "string"),
        ("product_label", "string"),
        ("prior_value", "real"),
        ("current_value", "real"),
        ("value_change", "real"),
        ("prior_orders", "integer"),
        ("current_orders", "integer"),
        ("current_penetration", "real"),
    ],
}
CONNECTIONS = {
    "trading": ("../data/processed", "tableau_sales.csv"),
    "products": ("../data/processed", "tableau_sales.csv"),
    "customers": ("../data/processed", "tableau_customers.csv"),
    "cohorts": ("../results", "cohorts_by_segment.csv"),
    "changes": ("../results", "product_changes.csv"),
}
CALCULATIONS = {
    "trading": {
        "month": ("date", "DATETRUNC('month', [occurred_date])"),
        "average_invoice": ("real", "SUM([recorded_value]) / COUNTD([invoice_key])"),
    },
    "products": {
        "month": ("date", "DATETRUNC('month', [occurred_date])"),
        "product_display": ("string", "[product_key] + ' — ' + [product_label]"),
        "scope_invoices": ("integer", "{ FIXED : COUNTD([invoice_key]) }"),
        "penetration": ("real", "COUNTD([invoice_key]) / MIN([scope_invoices])"),
    },
    "customers": {
        "repeat_90d": (
            "real",
            "IF SUM([eligible_90d]) > 0 THEN SUM(IF [eligible_90d] = 1 THEN [repeated_90d] ELSE 0 END) / SUM([eligible_90d]) END",
        ),
    },
    "cohorts": {
        "cohort_label": (
            "string",
            "STR(DATEPART('year', [cohort_month])) + '-' + RIGHT('0' + STR(DATEPART('month', [cohort_month])), 2)",
        ),
        "cohort_rate": ("real", "SUM([active_customers]) / SUM([cohort_customers])"),
    },
    "changes": {
        "product_display": ("string", "[product_key] + ' — ' + [product_label]"),
        "absolute_change": ("real", "ABS([value_change])"),
    },
}
CAPTIONS = {
    "recorded_value": "Recorded sales · GBP",
    "sales_value_12m": "Last 12 months · GBP",
    "invoice_key": "Purchase invoice",
    "customer_key": "Identified customer",
    "average_invoice": "Average invoice · GBP",
    "country": "Recorded country",
    "occurred_date": "Purchase date",
    "segment": "Customer group · 1 Dec 2011",
    "is_merchandise": "Record type",
    "product_display": "Product code and description",
    "scope_invoices": "All merchandise invoices in filter scope",
    "penetration": "Order penetration",
    "repeat_90d": "Repeat within 90 days · eligible customers",
    "cohort_rate": "Monthly purchasing share",
    "cohort_label": "First observed purchase month",
    "month_index": "Months after first observed purchase",
    "value_change": "Jan–Nov 2011 less Jan–Nov 2010 · GBP",
}
PERCENT_FIELDS = {"penetration", "repeat_90d", "repeat_rate", "cohort_rate", "current_penetration"}
CURRENCY_FIELDS = {
    "recorded_value",
    "sales_value_12m",
    "average_invoice",
    "value_change",
    "current_value",
    "prior_value",
}


def node(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, tag, {k.replace("_", "-"): str(v) for k, v in attributes.items()})
    child.text = text
    return child


def simple_id(parent, name):
    node(
        parent,
        "simple-id",
        uuid="{" + str(uuid.uuid5(uuid.NAMESPACE_URL, "retail-analytics/" + name)).upper() + "}",
    )


def column_definition(field, dtype, formula=None):
    dimension = dtype in ("string", "date") or field == "month_index"
    column = ET.Element(
        "column",
        {
            "name": "[" + field + "]",
            "caption": CAPTIONS.get(field, field.replace("_", " ").title()),
            "datatype": dtype,
            "role": "dimension" if dimension else "measure",
            "type": "ordinal" if dtype == "date" else "nominal" if dimension else "quantitative",
        },
    )
    if not dimension:
        column.set(
            "default-format",
            "p0.0%"
            if field in PERCENT_FIELDS
            else "£#,##0.00"
            if field in CURRENCY_FIELDS
            else "#,##0",
        )
    if formula:
        node(column, "calculation", **{"class": "tableau", "formula": formula})
    return column


def relation(parent, name):
    filename = CONNECTIONS[name][1]
    rel = node(
        parent,
        "relation",
        connection="textscan." + name,
        name=filename,
        table="[" + filename.replace(".", "#") + "]",
        type="table",
    )
    cols = node(rel, "columns", character_set="UTF-8", header="yes", locale="en_GB", separator=",")
    for ordinal, (field, dtype) in enumerate(SCHEMAS[name]):
        node(cols, "column", datatype=dtype, name=field, ordinal=ordinal)


def datasource(parent, name):
    directory, filename = CONNECTIONS[name]
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
            "directory": directory,
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
    prefix = {
        "None": "none",
        "Sum": "sum",
        "Avg": "avg",
        "CountD": "ctd",
        "User": "usr",
        "Min": "min",
    }[derivation]
    return "[" + prefix + ":" + field + ":" + ("nk" if kind == "nominal" else "qk") + "]"


def reference(source, field, derivation="None", kind="nominal"):
    return "[federated." + source + "]." + instance(field, derivation, kind)


def filters_for(source):
    if source in ("trading", "products"):
        base = 10 if source == "trading" else 20
        controls = [
            ("country", base + 1, None),
            ("occurred_date", base + 2, ("2011-01-01", "2011-11-30")),
        ]
        if source == "products":
            controls += [("segment", 23, None), ("is_merchandise", None, "Merchandise")]
        return controls
    return []


def add_filter(view, source, field, group=None, selection=None, context=False, top=None):
    date_range = isinstance(selection, tuple)
    kind = "quantitative" if date_range else "nominal"
    attrs = {
        "class": "quantitative" if date_range else "categorical",
        "column": reference(source, field, kind=kind),
    }
    if group is not None:
        attrs["filter-group"] = str(group)
    if context:
        attrs["context"] = "true"
    if date_range:
        attrs["included-values"] = "in-range"
    filt = node(view, "filter", **attrs)
    if date_range:
        node(filt, "min", "#" + selection[0] + "#")
        node(filt, "max", "#" + selection[1] + "#")
    elif top:
        end = node(filt, "groupfilter", count=top[0], end="top", function="end", units="records")
        ordered = node(end, "groupfilter", direction="DESC", expression=top[1], function="order")
        node(ordered, "groupfilter", function="level-members", level=instance(field))
    elif selection is not None:
        node(
            filt,
            "groupfilter",
            function="member",
            level=instance(field),
            member='"' + selection + '"',
        )
    else:
        node(filt, "groupfilter", function="level-members", level=instance(field))


def worksheet(
    parent,
    name,
    source,
    definitions,
    measure,
    derivation="Sum",
    dimension=None,
    mark="Bar",
    col_dimension=None,
    extra_tooltips=(),
    top=None,
    context_scope=False,
):
    ds = definitions[source]
    sheet = node(parent, "worksheet", name=name)
    title = node(node(node(sheet, "layout-options"), "title"), "formatted-text")
    node(
        title,
        "run",
        "Markets · scroll to explore" if name == "Markets" else name,
        bold="true",
        fontcolor=INK,
        fontsize="12",
    )
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
    used = {(measure, derivation, "quantitative")}
    if dimension:
        used.add((dimension, "None", "quantitative" if mark == "Line" else "nominal"))
    if col_dimension:
        used.add((col_dimension, "None", "nominal"))
    for field, aggregation in extra_tooltips:
        used.add((field, aggregation, "nominal" if aggregation == "None" else "quantitative"))
    controls = filters_for(source)
    for field, _, selection in controls:
        used.add((field, "None", "quantitative" if isinstance(selection, tuple) else "nominal"))
    if source == "products":
        used.add(("product_key", "None", "nominal"))
    if source == "cohorts":
        used.add(("segment", "None", "nominal"))
        used.add(("month_index", "None", "nominal"))
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
        add_filter(view, source, field, group, selection, context_scope or source == "trading")
    if top:
        add_filter(view, source, dimension, top=top)
    if source == "cohorts":
        # Month 0 is 100% by construction; reserve colour scale for repeat months.
        filt = node(
            view, "filter", **{"class": "categorical", "column": reference(source, "month_index")}
        )
        union = node(filt, "groupfilter", function="union")
        for index in range(1, 12):
            node(
                union,
                "groupfilter",
                function="member",
                level=instance("month_index"),
                member=str(index),
            )
    if controls:
        slices = node(view, "slices")
        for field, _, selection in controls:
            node(
                slices,
                "column",
                reference(
                    source,
                    field,
                    kind="quantitative" if isinstance(selection, tuple) else "nominal",
                ),
            )
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
    if dimension and mark != "Line":
        header = node(style, "style-rule", element="header")
        node(
            header,
            "format",
            attr="width",
            field=reference(source, dimension),
            value="230" if "product" in dimension else "160",
        )
    pane = node(
        node(table, "panes"), "pane", selection_relaxation_option="selection-relaxation-allow"
    )
    node(node(pane, "view"), "breakdown", value="auto")
    node(pane, "mark", **{"class": mark})
    enc = node(pane, "encodings")
    metric = reference(source, measure, derivation, "quantitative")
    node(enc, "tooltip", column=metric)
    if mark in ("Bar", "Square", "Text"):
        node(enc, "text", column=metric)
    if mark == "Square":
        node(enc, "color", column=metric)
    if source == "products" and dimension == "product_display":
        node(enc, "lod", column=reference(source, "product_key"))
    for field, aggregation in extra_tooltips:
        node(
            enc,
            "tooltip",
            column=reference(
                source, field, aggregation, "nominal" if aggregation == "None" else "quantitative"
            ),
        )
    tooltip = node(node(pane, "customized-tooltip"), "formatted-text")
    if dimension:
        node(
            tooltip,
            "run",
            "<"
            + reference(source, dimension, kind="quantitative" if mark == "Line" else "nominal")
            + ">\n",
            bold="true",
        )
    node(tooltip, "run", CAPTIONS.get(measure, name) + ": <" + metric + ">\n")
    for field, aggregation in extra_tooltips:
        node(
            tooltip,
            "run",
            CAPTIONS.get(field, field.replace("_", " "))
            + ": <"
            + reference(
                source, field, aggregation, "nominal" if aggregation == "None" else "quantitative"
            )
            + ">\n",
        )
    if source == "cohorts":
        node(
            tooltip, "run", "First observed purchase cohort. Unobserved future months remain blank."
        )
    if mark == "Text":
        label = node(node(pane, "customized-label"), "formatted-text")
        node(label, "run", "<" + metric + ">", bold="true", fontcolor=INK, fontsize="26")
    mark_style = node(node(pane, "style"), "style-rule", element="mark")
    if mark != "Square":
        node(mark_style, "format", attr="mark-color", value=TEAL)
    else:
        encoding = node(
            node(style, "style-rule", element="mark"),
            "encoding",
            attr="color",
            field=metric,
            min="0",
            max="1",
            type="custom-interpolated",
        )
        palette = node(encoding, "color-palette", custom="true", name="", type="ordered-sequential")
        node(palette, "color", PAPER)
        node(palette, "color", TEAL)
    node(mark_style, "format", attr="mark-labels-show", value="false" if mark == "Line" else "true")
    node(mark_style, "format", attr="size", value="1" if mark == "Square" else "0.65")
    dim_ref = (
        reference(source, dimension, kind="quantitative" if mark == "Line" else "nominal")
        if dimension
        else ""
    )
    node(table, "rows", metric if mark == "Line" else dim_ref)
    node(
        table,
        "cols",
        dim_ref
        if mark == "Line"
        else reference(source, col_dimension)
        if col_dimension
        else metric
        if mark == "Bar"
        else "",
    )
    simple_id(sheet, "worksheet/" + name)
    return sheet


def action(parent, name, dashboard, source_sheet, field, source, target_source=None, excluded=()):
    a = node(parent, "action", caption=name, name="[" + name + "]")
    node(a, "activation", auto_clear="true", type="on-select")
    node(a, "source", dashboard=dashboard, type="sheet", worksheet=source_sheet)
    target = target_source or source
    query = quote("[federated." + target + "].[" + field + "]", safe="")
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
    zone(2, 1800, 7400, 96000, 6500, text=subtitle)
    for i, (source, field, mode, sheet, x, w) in enumerate(controls, 3):
        zone(i, x, 14300, w, 7000, sheet=sheet, control=(source, field, mode))
    for i, (sheet, x, y, w, h) in enumerate(sheets, 20):
        zone(i, x, y, w, h, sheet=sheet)
    zone(90, 1800, 92500, 96000, 6500, text=note, size=10)
    simple_id(dash, "dashboard/" + name)


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
    definitions = {
        name: datasource(node_sources, name)
        for node_sources in [node(root, "datasources")]
        for name in SCHEMAS
    }
    actions = node(root, "actions")
    sheets = node(root, "worksheets")
    worksheet(sheets, "Recorded sales", "trading", definitions, "recorded_value", mark="Text")
    worksheet(
        sheets, "Purchase invoices", "trading", definitions, "invoice_key", "CountD", mark="Text"
    )
    worksheet(
        sheets, "Average invoice", "trading", definitions, "average_invoice", "User", mark="Text"
    )
    worksheet(
        sheets,
        "Monthly trading",
        "trading",
        definitions,
        "recorded_value",
        dimension="month",
        mark="Line",
        extra_tooltips=(("invoice_key", "CountD"), ("average_invoice", "User")),
    )
    worksheet(
        sheets,
        "Markets",
        "trading",
        definitions,
        "recorded_value",
        dimension="country",
        extra_tooltips=(("invoice_key", "CountD"),),
    )
    worksheet(
        sheets,
        "Identified customers",
        "customers",
        definitions,
        "customer_key",
        "CountD",
        mark="Text",
    )
    worksheet(
        sheets, "Client sales · 12 months", "customers", definitions, "sales_value_12m", mark="Text"
    )
    worksheet(
        sheets,
        "Repeat within 90 days",
        "customers",
        definitions,
        "repeat_90d",
        "User",
        mark="Text",
        extra_tooltips=(("eligible_90d", "Sum"),),
    )
    worksheet(
        sheets,
        "Customer groups",
        "customers",
        definitions,
        "customer_key",
        "CountD",
        dimension="segment",
        extra_tooltips=(("sales_value_12m", "Sum"),),
    )
    worksheet(
        sheets,
        "Cohort purchasing",
        "cohorts",
        definitions,
        "cohort_rate",
        "User",
        dimension="cohort_label",
        mark="Square",
        col_dimension="month_index",
        extra_tooltips=(("cohort_customers", "Sum"), ("active_customers", "Sum")),
    )
    worksheet(
        sheets,
        "Merchandise sales",
        "products",
        definitions,
        "recorded_value",
        mark="Text",
        context_scope=True,
    )
    worksheet(
        sheets,
        "Merchandise invoices",
        "products",
        definitions,
        "invoice_key",
        "CountD",
        mark="Text",
        context_scope=True,
    )
    worksheet(
        sheets,
        "Selected order penetration",
        "products",
        definitions,
        "penetration",
        "User",
        mark="Text",
        context_scope=True,
        extra_tooltips=(("scope_invoices", "Min"),),
    )
    worksheet(
        sheets,
        "Leading products · top 15",
        "products",
        definitions,
        "recorded_value",
        dimension="product_display",
        context_scope=True,
        top=(15, "SUM([recorded_value])"),
        extra_tooltips=(("invoice_key", "CountD"), ("penetration", "User")),
    )
    worksheet(
        sheets,
        "Product purchasing trend",
        "products",
        definitions,
        "recorded_value",
        dimension="month",
        mark="Line",
        context_scope=True,
        extra_tooltips=(("invoice_key", "CountD"),),
    )
    worksheet(
        sheets,
        "Comparable product changes · all markets",
        "changes",
        definitions,
        "value_change",
        dimension="product_display",
        top=(20, "SUM([absolute_change])"),
        extra_tooltips=(
            ("prior_value", "Sum"),
            ("current_value", "Sum"),
            ("current_orders", "Sum"),
        ),
    )
    action(actions, "Select market", "01 Trading performance", "Markets", "country", "trading")
    action(
        actions,
        "Select customer group",
        "02 Client development",
        "Customer groups",
        "segment",
        "customers",
        excluded=("Cohort purchasing",),
    )
    action(
        actions,
        "Select cohort group",
        "02 Client development",
        "Customer groups",
        "segment",
        "customers",
        target_source="cohorts",
        excluded=("Identified customers", "Client sales · 12 months", "Repeat within 90 days"),
    )
    action(
        actions,
        "Select product",
        "03 Product preferences",
        "Leading products · top 15",
        "product_key",
        "products",
    )
    dashboards = node(root, "dashboards")
    layouts = {
        "01 Trading performance": [
            ("Recorded sales", 1800, 24000, 31000, 12000),
            ("Purchase invoices", 34500, 24000, 31000, 12000),
            ("Average invoice", 67200, 24000, 31000, 12000),
            ("Monthly trading", 1800, 39000, 59000, 51000),
            ("Markets", 62500, 39000, 35700, 51000),
        ],
        "02 Client development": [
            ("Identified customers", 1800, 24000, 31000, 12000),
            ("Client sales · 12 months", 34500, 24000, 31000, 12000),
            ("Repeat within 90 days", 67200, 24000, 31000, 12000),
            ("Customer groups", 1800, 39000, 37000, 51000),
            ("Cohort purchasing", 41000, 39000, 57200, 51000),
        ],
        "03 Product preferences": [
            ("Merchandise sales", 1800, 24000, 31000, 12000),
            ("Merchandise invoices", 34500, 24000, 31000, 12000),
            ("Selected order penetration", 67200, 24000, 31000, 12000),
            ("Leading products · top 15", 1800, 39000, 57000, 51000),
            ("Product purchasing trend", 60500, 39000, 37700, 51000),
        ],
    }
    dashboard(
        dashboards,
        "01 Trading performance",
        "RETAIL PERFORMANCE | GBP | Default: Jan–Nov 2011\nRead sales, distinct invoices and basket value together. Date and country controls apply to this page.",
        ["trading"],
        layouts["01 Trading performance"],
        [
            ("trading", "country", "checkdropdown", "Recorded sales", 1800, 45000),
            ("trading", "occurred_date", "range", "Recorded sales", 49000, 49200),
        ],
        "Scroll the market view; select a bar to focus the other views, click again to clear. Reset country to (All), date to 1 Jan–30 Nov 2011. Recorded sales include service entries.",
    )
    dashboard(
        dashboards,
        "02 Client development",
        "CLIENT DEVELOPMENT | Snapshot: 1 Dec 2011 | Known customers only\nGroup activity: Dec 2010–Nov 2011. Cohorts follow first observed purchase; M0 is omitted from the repeat-month scale.",
        ["customers", "cohorts"],
        layouts["02 Client development"],
        [],
        "Select a customer-group bar to update the measures and cohort; click again to reset. The 90-day rate uses eligible customers only. Future months are blank. Snapshot groups are independent of trading/product page filters.",
    )
    dashboard(
        dashboards,
        "03 Product preferences",
        "PRODUCT PREFERENCES | Merchandise only | GBP | Default: Jan–Nov 2011\nTop 15 responds to date, country and customer group. All merchandise remains in the order-penetration denominator.",
        ["products"],
        layouts["03 Product preferences"],
        [
            ("products", "country", "checkdropdown", "Merchandise sales", 1800, 30000),
            ("products", "segment", "checkdropdown", "Merchandise sales", 33500, 30000),
            ("products", "occurred_date", "range", "Merchandise sales", 65200, 33000),
        ],
        "Select a product bar to focus the measures and trend; click again to clear. Reset lists to (All), date to 1 Jan–30 Nov 2011. Top 15 is not the full total. Customer-group labels refer to the fixed 1 Dec 2011 snapshot.",
    )
    windows = node(root, "windows", source_height="30")
    for sheet in sheets:
        window = node(windows, "window", **{"class": "worksheet", "name": sheet.attrib["name"]})
        # Keep only the additional comparative diagnostic visible as a worksheet tab.
        if sheet.attrib["name"] != "Comparable product changes · all markets":
            window.set("hidden", "true")
        node(window, "cards")
        node(
            node(window, "viewpoint"),
            "zoom",
            type="fit-width" if sheet.attrib["name"] == "Markets" else "entire-view",
        )
        simple_id(window, "window/" + sheet.attrib["name"])
    # Native Tableau restores the final dashboard window; open with the overview.
    for name, placements in reversed(tuple(layouts.items())):
        window = node(
            windows, "window", **{"class": "dashboard", "name": name, "maximized": "true"}
        )
        viewpoints = node(window, "viewpoints")
        for sheet, *_ in placements:
            node(
                node(viewpoints, "viewpoint", name=sheet),
                "zoom",
                type="fit-width" if sheet == "Markets" else "entire-view",
            )
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
    destination = destination or PROJECT / "dashboard/retail_customers.twb"
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
    print(
        "Built retail_customers.twb: 3 interactive dashboards, isolated page scopes, 4 selection actions"
    )


def write_smoke_variants():
    """Write local filter-state fixtures for native arithmetic checks.

    These states verify Tableau calculations and denominators. They do not prove
    mouse-driven action execution, which remains a distinct interaction check.
    """
    variants = {
        "france": [("trading", "country", "France")],
        "product-22423": [("products", "product_key", "22423")],
        "lapsed-repeat": [
            ("customers", "segment", "Lapsed repeat"),
            ("cohorts", "segment", "Lapsed repeat"),
        ],
    }
    output = PROJECT / "data/processed"
    output.mkdir(parents=True, exist_ok=True)
    for name, selections in variants.items():
        root = build_tree()
        for source, field, member in selections:
            for sheet in root.findall("./worksheets/worksheet"):
                view = sheet.find("./table/view")
                if view.find("./datasources/datasource").get("name") != "federated." + source:
                    continue
                # A product selection leaves the source bar chart unfiltered.
                if field == "product_key" and sheet.get("name") == "Leading products · top 15":
                    continue
                filt = next(
                    (
                        f
                        for f in view.findall("filter")
                        if f.get("column") == reference(source, field) and f.get("filter-group")
                    ),
                    None,
                )
                if filt is not None:
                    for child in list(filt):
                        filt.remove(child)
                    node(
                        filt,
                        "groupfilter",
                        function="member",
                        level=instance(field),
                        member='"' + member + '"',
                    )
                else:
                    deps = view.find("datasource-dependencies")
                    if deps.find("column-instance[@name='" + instance(field) + "']") is None:
                        node(
                            deps,
                            "column-instance",
                            column="[" + field + "]",
                            derivation="None",
                            name=instance(field),
                            pivot="key",
                            type="nominal",
                        )
                    # Add before sort/slices/aggregation, as required by native schema.
                    holder = ET.Element("holder")
                    add_filter(holder, source, field, selection=member)
                    index = next(
                        (
                            i
                            for i, child in enumerate(view)
                            if child.tag in ("sort", "slices", "aggregation")
                        ),
                        len(view),
                    )
                    view.insert(index, holder[0])
        for source in root.findall("./datasources/datasource"):
            connection = source.find("./connection/named-connections/named-connection/connection")
            original = PROJECT / "dashboard" / connection.get("directory")
            connection.set("directory", os.path.relpath(original.resolve(), output))
        # Restore the dashboard that owns the selected test state.
        target = (
            "01 Trading performance"
            if name == "france"
            else "03 Product preferences"
            if name == "product-22423"
            else "02 Client development"
        )
        windows = root.find("windows")
        active = windows.find("window[@name='" + target + "']")
        windows.remove(active)
        windows.append(active)
        ET.indent(root, space="  ")
        destination = output / ("tableau-smoke-" + name + ".twb")
        ET.ElementTree(root).write(destination, encoding="utf-8", xml_declaration=True)
        print(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke-variants",
        action="store_true",
        help="Also write ignored native filter-state fixtures",
    )
    args = parser.parse_args()
    build()
    if args.smoke_variants:
        write_smoke_variants()
