"""Regression cases for invoice attribution and non-additive product measures."""

import importlib.util
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "retail_model_build", PROJECT / "scripts/build_analysis.py"
)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def item(
    invoice,
    customer="1",
    date="2011-10-01",
    code="10001",
    label="First item",
    price="10",
    units="1",
    country="United Kingdom",
):
    return (invoice, code, label, units, date, price, customer, country)


@pytest.fixture
def database():
    connections = []

    def load(records):
        con = duckdb.connect(":memory:")
        connections.append(con)
        analysis.create_raw(con)
        con.executemany(
            "INSERT INTO raw_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [("Synthetic", str(index + 2)) + row for index, row in enumerate(records)],
        )
        analysis.build(con)
        return con

    yield load
    for con in connections:
        con.close()


def test_dimension_joins_keep_source_grain_and_exact_repeated_lines(database):
    repeat = item("1", units="3", price="0.123")
    con = database([repeat, repeat, item("C2", units="-1"), item("3", customer=None)])
    assert con.execute("SELECT count(*) FROM fact_invoice_line").fetchone()[0] == 4
    assert con.execute("SELECT count(*) FROM fact_invoice").fetchone()[0] == 2
    # The calendar includes days with no transactions rather than omitting them.
    assert con.execute("SELECT count(*) FROM dim_date").fetchone()[0] == 730
    assert con.execute("SELECT sum(recorded_value) FROM tableau_sales").fetchone()[0] == Decimal(
        "10.738"
    )
    assert all(analysis.model_checks(con).values())


def test_product_label_uses_latest_sale_and_deterministic_row_tie_break(database):
    con = database(
        [
            item("1", code="10001 ", label="OLD LABEL", date="2010-01-01"),
            item("2", label="Updated label", date="2011-01-01"),
            item("3", label="Latest label", date="2011-01-01"),
            item("4", label=" ", date="2011-02-01"),
            item("C5", label="Not a sale label", date="2011-03-01", units="-1"),
        ]
    )
    assert con.execute(
        "SELECT product_label,sale_description_variants FROM dim_product"
    ).fetchone() == (
        "Latest label",
        3,
    )
    assert con.execute("SELECT count(*) FROM dim_product").fetchone()[0] == 1
    assert (
        con.execute(
            "SELECT source_description FROM fact_invoice_line WHERE invoice_key='1'"
        ).fetchone()[0]
        == "OLD LABEL"
    )


def test_partial_missing_customer_is_resolved_once_for_full_invoice(database):
    con = database(
        [
            item("1", customer="1", price="10"),
            item("1", customer=None, price="30", code="10002"),
            item("2", customer=None, price="20"),
        ]
    )
    assert con.execute(
        "SELECT customer_key,recorded_value FROM fact_invoice ORDER BY invoice_key"
    ).fetchall() == [
        ("1", Decimal("40")),
        (None, Decimal("20")),
    ]
    assert con.execute("SELECT orders_12m,sales_value_12m FROM tableau_customers").fetchone() == (
        1,
        Decimal("40"),
    )
    assert con.execute(
        "SELECT count(*),sum(recorded_value) FROM tableau_sales WHERE customer_key='1'"
    ).fetchone() == (2, Decimal("40"))
    assert con.execute(
        "SELECT prior_orders,current_orders FROM order_bridge WHERE customer_group='Unidentified customer'"
    ).fetchone() == (0, 1)
    # Raw ID coverage is deliberately still source-row coverage, not imputed coverage.
    assert con.execute("SELECT known_sales_value FROM monthly").fetchone()[0] == Decimal("10")


@pytest.mark.parametrize(
    "change",
    [
        {"customer": "2"},
        {"date": "2011-10-02"},
        {"country": "France"},
    ],
)
def test_ambiguous_invoice_ownership_date_or_country_fails_build(database, change):
    with pytest.raises(ValueError, match="Invoice customer/date/country conflict"):
        database([item("1"), item("1", **change)])


def test_order_bridge_counts_four_disjoint_customer_groups(database):
    con = database(
        [
            item("1", customer="1", date="2010-01-01"),
            item("2", customer="1", date="2011-01-01"),
            item("3", customer="1", date="2011-02-01"),
            item("4", customer="2", date="2011-01-01"),
            item("5", customer="3", date="2010-01-01"),
            item("6", customer=None, date="2010-01-01"),
            item("7", customer=None, date="2011-01-01"),
            item("8", customer=None, date="2011-02-01"),
            item("9", customer="4", date="2010-12-01"),  # Outside both comparison periods.
        ]
    )
    assert con.execute(
        "SELECT customer_group,prior_orders,current_orders,order_change FROM order_bridge ORDER BY sort_order"
    ).fetchall() == [
        ("Both periods", 1, 2, 1),
        ("Current period only", 0, 1, 1),
        ("Prior period only", 1, 0, -1),
        ("Unidentified customer", 1, 2, 1),
    ]
    assert analysis.model_checks(con)["order_bridge_reconciles"]


def test_product_penetration_keeps_order_population_before_product_selection(database):
    con = database(
        [
            item("1", code="10001", price="20"),
            item("1", code="10002", price="30"),
            item("1", code="POST", price="5"),
            item("2", code="10001", price="40"),
            item("3", code="GIFT_0001_10", price="10"),
            item("4", code="S", price="1"),
            item("5", code="TEST001", price="1"),
        ]
    )
    assert con.execute(
        "SELECT product_key,current_value,current_orders,current_penetration FROM product_changes ORDER BY product_key"
    ).fetchall() == [
        ("10001", Decimal("60"), 2, 1.0),
        ("10002", Decimal("30"), 1, 0.5),
    ]
    result = analysis.diagnostics(con)
    assert result["comparison"]["current_merchandise_orders"] == 2
    assert result["full_window"] == {
        "merchandise_value": Decimal("90"),
        "service_value": Decimal("17"),
    }
    # Product counts sum to three, but there are only two merchandise invoices.
    assert con.execute("SELECT sum(current_orders) FROM product_changes").fetchone()[0] == 3


def test_product_changes_use_comparable_periods_and_preserve_zero_population(database):
    con = database(
        [
            item("1", date="2010-11-30", price="25"),
            item("2", date="2010-12-01", price="50"),
            item("3", date="2011-12-01", price="100"),
        ]
    )
    assert con.execute(
        "SELECT prior_value,current_value,value_change,current_penetration FROM product_changes"
    ).fetchone() == (
        Decimal("25"),
        Decimal("0"),
        Decimal("-25"),
        None,
    )
    assert analysis.diagnostics(con)["comparison"]["top10_current_share"] is None


def test_segment_cohorts_recombine_as_weighted_counts_and_keep_future_null(database):
    con = database(
        [
            item("1", customer="1", date="2011-10-01"),
            item("2", customer="1", date="2011-11-01"),
            item("3", customer="2", date="2011-10-01"),
            item("4", customer="3", date="2011-10-01"),
        ]
    )
    assert con.execute(
        "SELECT sum(active_customers)::DOUBLE/sum(cohort_customers) FROM cohorts_by_segment WHERE month_index=1"
    ).fetchone()[0] == pytest.approx(1 / 3)
    assert (
        con.execute(
            "SELECT count(*) FROM cohorts_by_segment WHERE month_index=2 AND active_customers IS NULL"
        ).fetchone()[0]
        == 2
    )
    assert analysis.model_checks(con)["cohorts_by_segment_reconcile"]


def test_tableau_flat_exports_have_declared_grains_and_headers(database):
    con = database([item("1"), item("1", code="10002"), item("2", customer=None)])
    assert [
        field[0] for field in con.execute("SELECT * FROM tableau_sales LIMIT 0").description
    ] == [
        "invoice_key",
        "occurred_date",
        "country",
        "product_key",
        "product_label",
        "customer_key",
        "segment",
        "units",
        "recorded_value",
        "is_merchandise",
    ]
    assert [
        field[0] for field in con.execute("SELECT * FROM tableau_customers LIMIT 0").description
    ] == [
        "customer_key",
        "segment",
        "recency_days",
        "orders_12m",
        "sales_value_12m",
        "orders_24m",
        "cohort_month",
        "eligible_90d",
        "repeated_90d",
    ]
    assert con.execute("SELECT count(*) FROM tableau_sales").fetchone()[0] == 3
    assert con.execute("SELECT count(*) FROM tableau_customers").fetchone()[0] == 1


def test_country_and_period_selection_counts_whole_invoices_without_product_inflation(database):
    con = database(
        [
            item("1", country="France", date="2011-01-01", price="20"),
            item("1", country="France", date="2011-01-01", price="30", code="10002"),
            item("2", country="France", date="2010-01-01", price="80"),
            item("3", country="United Kingdom", date="2011-01-01", price="100"),
        ]
    )
    assert con.execute(
        "SELECT sum(recorded_value),count(DISTINCT invoice_key) FROM tableau_sales "
        "WHERE country='France' AND occurred_date>='2011-01-01' AND occurred_date<'2011-12-01'"
    ).fetchone() == (Decimal("50"), 1)
    assert analysis.model_checks(con)["country_date_filter_reconciles"]
