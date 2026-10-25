"""Small synthetic business cases for the actual retail SQL pipeline."""

import importlib.util
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "retail_build_analysis", PROJECT / "scripts/build_analysis.py"
)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def line(
    invoice,
    customer="12345",
    when="2011-10-01 12:00:00",
    quantity="1",
    price="10.00",
    stock="10001",
):
    return (invoice, stock, "Synthetic item", quantity, when, price, customer, "United Kingdom")


@pytest.fixture
def database():
    connections = []

    def load(records):
        con = duckdb.connect(":memory:")
        connections.append(con)
        analysis.create_raw(con)
        con.executemany(
            "INSERT INTO raw_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [("Synthetic", str(i + 2)) + record for i, record in enumerate(records)],
        )
        analysis.build(con)
        return con

    yield load
    for con in connections:
        con.close()


def test_invoice_lines_and_exact_repeats_do_not_inflate_order_frequency(database):
    repeated = line("500001", quantity="3", price="0.10")
    con = database([repeated, repeated, line("500001", quantity="2", price="0.20", stock="10002")])

    assert con.execute("SELECT count(*) FROM staged").fetchone()[0] == 3
    assert con.execute("SELECT sales_orders, sales_value FROM monthly").fetchone() == (
        1,
        Decimal("1.00"),
    )
    assert con.execute("SELECT orders_24m, sales_value_12m FROM customers").fetchone() == (
        1,
        Decimal("1.00"),
    )


def test_missing_customer_sales_remain_in_totals_without_inventing_a_customer(database):
    con = database(
        [
            line("500001", customer="12345.0", price="10"),
            line("500002", customer=None, price="20"),
            line("500003", customer="", price="30"),
            line("500004", customer="not-an-id", price="40"),
        ]
    )

    assert con.execute(
        "SELECT sales_orders, sales_value, known_sales_orders, known_sales_value FROM monthly"
    ).fetchone() == (4, Decimal("100"), 1, Decimal("10"))
    assert con.execute("SELECT customer_key, orders_24m FROM customers").fetchall() == [
        ("12345", 1)
    ]


def test_cancellations_and_invalid_records_stay_separate_from_positive_sales(database):
    con = database(
        [
            line("500001", quantity="2", price="10"),
            line("c500002", quantity="-1", price="10"),
            line("C500003", quantity="1"),
            line("500004", quantity="-1"),
            line("500005", price="0"),
            line("500006", price="-2"),
            line("500007", quantity="0"),
            line("500008", when="not-a-date"),
            line("", price="3"),
        ]
    )
    classifications = dict(
        con.execute("SELECT record_class, count(*) FROM staged GROUP BY 1").fetchall()
    )

    assert classifications == {
        "sale": 1,
        "cancellation": 1,
        "sign_or_cancellation_conflict": 2,
        "zero_or_negative_price_or_zero_quantity": 3,
        "invalid_required_field": 2,
    }
    assert sum(classifications.values()) == 9
    assert con.execute(
        "SELECT sales_value, sales_orders, cancellation_value, cancellation_documents FROM monthly"
    ).fetchone() == (Decimal("20"), 1, Decimal("10"), 1)
    assert con.execute("SELECT orders_24m FROM customers").fetchone()[0] == 1


def test_complete_month_window_keeps_last_day_and_excludes_partial_december(database):
    con = database(
        [
            line("500001", when="2009-11-30 23:59:59"),
            line("500002", when="2009-12-01 00:00:00"),
            line("500003", when="2011-11-30 23:59:59"),
            line("500004", when="2011-12-01 00:00:00"),
            line("500005", when="2011-12-09 12:00:00"),
        ]
    )

    assert con.execute("SELECT invoice_key FROM sales ORDER BY invoice_key").fetchall() == [
        ("500002",),
        ("500003",),
    ]
    assert con.execute("SELECT month FROM monthly ORDER BY month").fetchall() == [
        (date(2009, 12, 1),),
        (date(2011, 11, 1),),
    ]
    assert con.execute("SELECT orders_24m, orders_12m FROM customers").fetchone() == (2, 1)


def test_cohort_distinguishes_observed_inactivity_from_unobserved_future(database):
    con = database(
        [
            line("500001", customer="1", when="2011-01-01"),
            line("500002", customer="2", when="2011-10-01"),
            line("500003", customer="2", when="2011-11-01"),
            line("500004", customer="3", when="2011-10-10"),
        ]
    )

    assert con.execute(
        "SELECT active_customers, repeat_rate FROM cohorts WHERE cohort_month='2011-01-01' AND month_index=1"
    ).fetchone() == (0, 0.0)
    assert con.execute(
        "SELECT cohort_customers, active_customers, repeat_rate FROM cohorts WHERE cohort_month='2011-10-01' AND month_index=1"
    ).fetchone() == (2, 1, 0.5)
    assert con.execute(
        "SELECT active_customers, repeat_rate FROM cohorts WHERE cohort_month='2011-10-01' AND month_index=2"
    ).fetchone() == (None, None)
    assert con.execute(
        "SELECT active_customers, repeat_rate FROM cohorts WHERE cohort_month='2011-10-01' AND month_index=0"
    ).fetchone() == (2, 1.0)


def test_90_day_repeat_requires_mature_observation_and_counts_boundary_day(database):
    con = database(
        [
            line("500001", customer="1", when="2011-09-01"),
            line("500002", customer="1", when="2011-11-30"),  # Day 90, fully observed.
            line("500003", customer="2", when="2011-08-31"),
            line("500004", customer="2", when="2011-11-30"),  # Day 91, too late.
            line("500005", customer="3", when="2011-09-02"),
            line(
                "500006", customer="3", when="2011-11-01"
            ),  # Already repeated but window not mature.
            line("500007", customer="4", when="2011-08-01"),  # Mature, no repeat.
        ]
    )

    assert con.execute(
        "SELECT customer_key, eligible, repeated FROM repeat_90d ORDER BY customer_key"
    ).fetchall() == [("1", True, True), ("2", True, False), ("3", False, True), ("4", True, False)]
    assert con.execute(
        "SELECT count(*) FILTER (WHERE eligible), count(*) FILTER (WHERE eligible AND repeated) FROM repeat_90d"
    ).fetchone() == (3, 1)


def test_recency_and_frequency_segments_cover_each_customer_once(database):
    as_of = date(2011, 12, 1)
    day_90 = (as_of - timedelta(days=90)).isoformat()
    day_91 = (as_of - timedelta(days=91)).isoformat()
    con = database(
        [
            line("500001", customer="1", when="2011-07-01"),
            line("500002", customer="1", when=day_90),
            line("500003", customer="2", when=day_90),
            line("500004", customer="3", when="2011-07-01"),
            line("500005", customer="3", when=day_91),
            line("500006", customer="4", when=day_91),
            line("500007", customer="5", when="2010-11-30"),
        ]
    )

    assert con.execute(
        "SELECT customer_key, segment FROM customers ORDER BY customer_key"
    ).fetchall() == [
        ("1", "Active repeat"),
        ("2", "Recent single-order"),
        ("3", "Lapsed repeat"),
        ("4", "Lapsed single-order"),
        ("5", "No orders in last 12 months"),
    ]
    assert con.execute(
        "SELECT sum(customers), sum(orders_12m), sum(sales_value_12m) FROM segments"
    ).fetchone() == (5, 6, Decimal("60"))


def test_cohort_uses_first_observed_order_across_both_source_years(database):
    con = database(
        [
            line("500001", customer="1", when="2009-12-01", price="15"),
            line("500002", customer="1", when="2011-10-01", price="25"),
            line("500003", customer="2", when="2011-10-01", price="5"),
        ]
    )

    assert con.execute(
        "SELECT customer_key, first_observed_order FROM customers ORDER BY customer_key"
    ).fetchall() == [("1", date(2009, 12, 1)), ("2", date(2011, 10, 1))]
    assert (
        con.execute(
            "SELECT cohort_customers FROM cohorts WHERE cohort_month='2011-10-01' AND month_index=0"
        ).fetchone()[0]
        == 1
    )
    assert con.execute("SELECT sales_value_12m FROM customers WHERE customer_key='1'").fetchone()[
        0
    ] == Decimal("25")


def test_overlapping_source_sheets_choose_one_window_but_preserve_within_sheet_repeats():
    overlap = line("500001", when="2010-12-01 00:00:00", price="10")
    records = [
        ("Year 2009-2010", "2") + line("500000", when="2010-11-30 23:59:59", price="10"),
        ("Year 2009-2010", "3") + overlap,
        ("Year 2010-2011", "2") + overlap,
        ("Year 2010-2011", "3") + overlap,
    ]
    with duckdb.connect(":memory:") as con:
        analysis.create_raw(con)
        con.executemany("INSERT INTO raw_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
        analysis.build(con)

        assert con.execute("SELECT count(*) FROM staged").fetchone()[0] == 4
        assert con.execute(
            "SELECT source_sheet, count(*) FROM sales GROUP BY 1 ORDER BY 1"
        ).fetchall() == [("Year 2009-2010", 1), ("Year 2010-2011", 2)]
        assert con.execute(
            "SELECT month, sales_value, sales_orders FROM monthly ORDER BY month"
        ).fetchall() == [
            (date(2010, 11, 1), Decimal("10"), 1),
            (date(2010, 12, 1), Decimal("20"), 1),
        ]
        assert con.execute(
            "SELECT orders_24m, orders_12m, sales_value_12m FROM customers"
        ).fetchone() == (2, 1, Decimal("20"))


def test_manual_and_accounting_entries_do_not_become_purchases_or_cancellations(database):
    con = database(
        [
            line("A563185", price="11062.06", stock="B"),
            line("A563186", price="-11062.06", stock="B"),
            line("500001", price="9", stock="M"),
            line("C500002", quantity="-1", price="9", stock="M"),
            line("500003", price="7", stock="AMAZONFEE"),
            line("C500004", quantity="-1", price="7", stock="AMAZONFEE"),
            line("500005", quantity="2", price="10", stock="10001"),
            line("500005", price="3", stock="POST"),
            line("C500006", quantity="-1", price="10", stock="10001"),
        ]
    )

    assert con.execute("SELECT count(*) FROM staged").fetchone()[0] == 9
    assert (
        con.execute(
            "SELECT count(*) FROM staged WHERE record_class='manual_or_accounting_entry'"
        ).fetchone()[0]
        == 6
    )
    assert con.execute(
        "SELECT sales_value, sales_orders, cancellation_value, cancellation_documents FROM monthly"
    ).fetchone() == (Decimal("23"), 1, Decimal("10"), 1)
    assert con.execute(
        "SELECT orders_24m, sales_value_12m FROM customers"
    ).fetchone() == (1, Decimal("23"))
