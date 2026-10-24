"""Run SQL marts and publish aggregate results; keep individual records local."""

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = [
    "source_sheet",
    "source_row",
    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",
]


def create_raw(con):
    con.execute("CREATE TABLE raw_lines (" + ", ".join(name + " VARCHAR" for name in COLUMNS) + ")")


def build(con):
    for name in ("01_staging.sql", "02_marts.sql"):
        con.execute((ROOT / "sql" / name).read_text())


def rows(con, query):
    cursor = con.execute(query)
    keys = [item[0] for item in cursor.description]
    return [dict(zip(keys, row)) for row in cursor.fetchall()]


def json_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, default=json_value) + "\n")


def main():
    processed = ROOT / "data/processed"
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    con = duckdb.connect(str(processed / "retail.duckdb"))
    con.execute("DROP TABLE IF EXISTS raw_lines")
    create_raw(con)
    con.execute(
        "INSERT INTO raw_lines SELECT * FROM read_csv(?, all_varchar=true)",
        [str(processed / "lines.csv")],
    )
    build(con)
    source_columns = ",".join(COLUMNS[2:])
    overlap_unmatched = con.execute(
        "SELECT count(*) FROM (SELECT "
        + source_columns
        + " FROM staged WHERE source_sheet='Year 2009-2010' AND occurred_at >= DATE '2010-12-01' EXCEPT ALL SELECT "
        + source_columns
        + " FROM staged WHERE source_sheet='Year 2010-2011')"
    ).fetchone()[0]
    quality = {
        "source_rows": con.execute("SELECT count(*) FROM staged").fetchone()[0],
        "overlap_rows_excluded": con.execute(
            "SELECT count(*) FROM staged WHERE NOT source_selected"
        ).fetchone()[0],
        "overlap_rows_unmatched_in_later_sheet": overlap_unmatched,
        "record_classes": rows(
            con, "SELECT record_class, count(*) AS rows FROM staged GROUP BY 1 ORDER BY 1"
        ),
        "window_rows": con.execute("SELECT count(*) FROM analysis_lines").fetchone()[0],
        "partial_december_rows": con.execute(
            "SELECT count(*) FROM staged WHERE occurred_at >= DATE '2011-12-01'"
        ).fetchone()[0],
        "exact_repeated_rows": con.execute(
            "SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT "
            + ",".join(COLUMNS[2:])
            + " FROM raw_lines)) FROM raw_lines"
        ).fetchone()[0],
        "exact_repeated_rows_after_overlap_removal": con.execute(
            "SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT "
            + source_columns
            + " FROM staged WHERE source_selected)) FROM staged WHERE source_selected"
        ).fetchone()[0],
        "missing_customer_sales_rows": con.execute(
            "SELECT count(*) FROM sales WHERE customer_key IS NULL"
        ).fetchone()[0],
        "invoice_customer_conflicts": con.execute(
            "SELECT count(*) FROM (SELECT invoice_key FROM sales GROUP BY 1 HAVING count(DISTINCT customer_key)>1)"
        ).fetchone()[0],
        "invoice_month_conflicts": con.execute(
            "SELECT count(*) FROM (SELECT invoice_key FROM sales GROUP BY 1 HAVING count(DISTINCT date_trunc('month',occurred_at))>1)"
        ).fetchone()[0],
        "window_positive_duplicate_value": con.execute(
            "SELECT coalesce(sum(recorded_value),0) FROM (SELECT *, row_number() OVER (PARTITION BY "
            + ",".join(COLUMNS[2:])
            + " ORDER BY source_sheet,source_row) AS n FROM sales) WHERE n>1"
        ).fetchone()[0],
        "jan_nov_duplicate_sensitivity": rows(
            con,
            "WITH ranked AS (SELECT *, row_number() OVER (PARTITION BY "
            + source_columns
            + " ORDER BY source_sheet,source_row) AS n FROM sales) SELECT year(occurred_at) AS year, sum(recorded_value) AS retained_value, sum(CASE WHEN n=1 THEN recorded_value ELSE 0 END) AS deduplicated_value FROM ranked WHERE month(occurred_at)<=11 GROUP BY 1 ORDER BY 1",
        ),
    }
    summary = rows(
        con,
        """SELECT
      sum(sales_value) AS sales_value, sum(sales_orders) AS sales_orders,
      sum(cancellation_value) AS cancellation_value,
      sum(cancellation_documents) AS cancellation_documents,
      sum(known_sales_value)/nullif(sum(sales_value),0) AS known_customer_value_coverage,
      sum(known_sales_orders)::DOUBLE/nullif(sum(sales_orders),0) AS known_customer_order_coverage,
      sum(sales_value)/nullif(sum(sales_orders),0) AS average_order_value FROM monthly""",
    )[0]
    summary.update(
        rows(
            con,
            """SELECT count(*) AS customers,
      count(*) FILTER (WHERE orders_24m >= 2) AS repeat_customers,
      count(*) FILTER (WHERE orders_24m >= 2)::DOUBLE / nullif(count(*),0) AS repeat_customer_share
      FROM customers""",
        )[0]
    )
    summary.update(
        rows(
            con,
            """SELECT count(*) FILTER (WHERE eligible) AS eligible_90d,
      count(*) FILTER (WHERE eligible AND repeated) AS repeated_90d,
      count(*) FILTER (WHERE eligible AND repeated)::DOUBLE / nullif(count(*) FILTER (WHERE eligible),0) AS repeat_90d_rate
      FROM repeat_90d""",
        )[0]
    )
    summary["year_comparison"] = rows(
        con,
        """SELECT year(month) AS year,
      sum(sales_value) AS sales_value, sum(sales_orders) AS sales_orders,
      sum(sales_value)/sum(sales_orders) AS average_order_value
      FROM monthly WHERE month(month) <= 11 AND year(month) IN (2010,2011) GROUP BY 1 ORDER BY 1""",
    )
    summary.update(
        {
            "window_start": "2009-12-01",
            "window_end": "2011-11-30",
            "as_of": "2011-12-01",
            "currency": "GBP",
        }
    )
    # Independent source controls: grouped exports must reconcile to the selected detail.
    checks = {
        "row_classification": sum(item["rows"] for item in quality["record_classes"])
        == quality["source_rows"],
        "overlap_verified": overlap_unmatched == 0,
        "source_window_reconciliation": quality["window_rows"]
        + quality["partial_december_rows"]
        + quality["overlap_rows_excluded"]
        == quality["source_rows"],
        "monthly_sales_value": summary["sales_value"]
        == con.execute("SELECT sum(recorded_value) FROM sales").fetchone()[0],
        "monthly_sales_orders": summary["sales_orders"]
        == con.execute("SELECT count(DISTINCT invoice_key) FROM sales").fetchone()[0],
        "country_sales_value": con.execute("SELECT sum(sales_value) FROM countries").fetchone()[0]
        == summary["sales_value"],
        "cancellation_value": summary["cancellation_value"]
        == con.execute("SELECT -sum(recorded_value) FROM cancellations").fetchone()[0],
        "segment_customers": con.execute("SELECT sum(customers) FROM segments").fetchone()[0]
        == summary["customers"],
        "segment_value": con.execute("SELECT sum(sales_value_12m) FROM segments").fetchone()[0]
        == con.execute(
            "SELECT sum(recorded_value) FROM sales WHERE customer_key IS NOT NULL AND occurred_at >= DATE '2010-12-01'"
        ).fetchone()[0],
        "customer_orders_unambiguous": quality["invoice_customer_conflicts"] == 0,
        "monthly_orders_unambiguous": quality["invoice_month_conflicts"] == 0,
    }
    if not all(checks.values()):
        raise ValueError("Reconciliation failed: " + repr(checks))
    for table in ("monthly", "countries", "cohorts", "segments"):
        data = rows(con, "SELECT * FROM " + table)
        with (output / (table + ".csv")).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    write_json(output / "quality.json", quality)
    write_json(output / "summary.json", summary)
    write_json(output / "checks.json", checks)
    print(
        json.dumps({"summary": summary, "quality": quality, "checks": checks}, default=json_value)
    )
    con.close()


if __name__ == "__main__":
    main()
