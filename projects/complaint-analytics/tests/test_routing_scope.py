"""The routing scope table is the single definition of in-scope products and teams."""
from pathlib import Path

import pytest

duckdb = pytest.importorskip("duckdb", reason="Install projects/complaint-analytics/requirements.txt for SQL checks")
SQL = Path(__file__).resolve().parents[1] / "sql"


def test_each_product_maps_to_exactly_one_team():
    with duckdb.connect() as con:
        con.execute((SQL / "03_routing_scope.sql").read_text())
        products, distinct_products, teams = con.execute(
            "SELECT count(*), count(DISTINCT product), count(DISTINCT routing_team) FROM ref_product_team"
        ).fetchone()
    assert products == distinct_products == 7
    assert teams == 5


def test_mart_keeps_only_scoped_products_and_adds_team():
    with duckdb.connect() as con:
        con.execute("""CREATE TABLE stg_complaints AS SELECT * FROM (VALUES
            (DATE '2026-07-01', 'Prepaid card', 'Fees', 'Web', 'Closed', TRUE, TRUE),
            (DATE '2026-07-01', 'Debt collection', 'Fees', 'Web', 'Closed', FALSE, TRUE)
        ) AS t(date_received, product, issue, submitted_via, company_response, has_narrative, is_timely)""")
        con.execute((SQL / "03_routing_scope.sql").read_text())
        con.execute((SQL / "04_complaint_mart.sql").read_text())
        assert con.execute(
            "SELECT routing_team, product, complaint_count FROM mart_complaint_daily"
        ).fetchall() == [("Cards", "Prepaid card", 1)]
