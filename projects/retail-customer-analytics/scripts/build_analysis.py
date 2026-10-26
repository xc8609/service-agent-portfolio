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
    for name in ("01_staging.sql", "03_model.sql"):
        con.execute((ROOT / "sql" / name).read_text())
    conflicts = con.execute(
        "SELECT count(*) FROM fact_invoice WHERE source_customer_count>1 "
        "OR source_date_count>1 OR source_country_count>1"
    ).fetchone()[0]
    if conflicts:
        raise ValueError("Invoice customer/date/country conflict: " + str(conflicts))
    if con.execute("SELECT count(*)<>count(DISTINCT line_key) FROM fact_invoice_line").fetchone()[
        0
    ]:
        raise ValueError("Source lineage key is not unique")
    for name in ("02_marts.sql", "04_diagnostics.sql"):
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


def write_csv(con, query, path):
    cursor = con.execute(query)
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow([item[0] for item in cursor.description])
        while True:
            batch = cursor.fetchmany(10000)
            if not batch:
                break
            writer.writerows(batch)


def model_checks(con):
    """Independent arithmetic controls at fact, order, product and cohort grains."""
    checks = {}
    for table, key in (
        ("dim_date", "date_key"),
        ("dim_country", "country_key"),
        ("dim_product", "product_key"),
        ("dim_customer", "customer_key"),
        ("fact_invoice", "invoice_key"),
        ("fact_invoice_line", "line_key"),
    ):
        checks[table + "_unique_key"] = con.execute(
            "SELECT count(*)=count(DISTINCT " + key + ") FROM " + table
        ).fetchone()[0]
    fact_control = con.execute(
        "SELECT count(*),coalesce(sum(recorded_value),0) FROM fact_invoice_line"
    ).fetchone()
    checks["fact_source_reconciliation"] = (
        fact_control
        == con.execute(
            "SELECT count(*),coalesce(sum(recorded_value),0) FROM analysis_lines"
        ).fetchone()
    )
    checks["dimension_join_preserves_grain_and_value"] = (
        fact_control
        == con.execute(
            "SELECT count(*),coalesce(sum(f.recorded_value),0) FROM fact_invoice_line f "
            "JOIN dim_date d ON f.date_key=d.date_key "
            "JOIN dim_country g ON f.country_key=g.country_key "
            "JOIN dim_product p ON f.product_key=p.product_key "
            "LEFT JOIN dim_customer c ON f.customer_key=c.customer_key"
        ).fetchone()
    )
    checks["identified_customer_foreign_keys"] = con.execute(
        "SELECT count(*)=0 FROM fact_invoice_line f LEFT JOIN dim_customer c "
        "ON f.customer_key=c.customer_key WHERE f.customer_key IS NOT NULL "
        "AND c.customer_key IS NULL"
    ).fetchone()[0]
    sales_value, sales_orders = con.execute(
        "SELECT coalesce(sum(recorded_value),0),count(DISTINCT invoice_key) FROM sales"
    ).fetchone()
    checks["invoice_fact_reconciles"] = (sales_value, sales_orders) == con.execute(
        "SELECT coalesce(sum(recorded_value),0),count(*) FROM fact_invoice"
    ).fetchone()
    checks["tableau_sales_reconciles"] = (sales_value, sales_orders) == con.execute(
        "SELECT coalesce(sum(recorded_value),0),count(DISTINCT invoice_key) FROM tableau_sales"
    ).fetchone()
    checks["merchandise_and_service_reconcile"] = (
        sales_value
        == con.execute(
            "SELECT coalesce(sum(recorded_value),0) FROM tableau_sales "
            "WHERE is_merchandise IN ('Merchandise','Service')"
        ).fetchone()[0]
    )
    checks["country_date_filter_reconciles"] = (
        con.execute(
            "SELECT coalesce(sum(recorded_value),0),count(DISTINCT invoice_key) FROM tableau_sales "
            "WHERE country='France' AND occurred_date>=DATE '2011-01-01' "
            "AND occurred_date<DATE '2011-12-01'"
        ).fetchone()
        == con.execute(
            "SELECT coalesce(sum(recorded_value),0),count(DISTINCT invoice_key) FROM sales "
            "WHERE country_name='France' AND occurred_at>=TIMESTAMP '2011-01-01' "
            "AND occurred_at<TIMESTAMP '2011-12-01'"
        ).fetchone()
    )
    checks["tableau_customers_reconciles"] = (
        con.execute(
            "SELECT count(*),coalesce(sum(sales_value_12m),0) FROM tableau_customers"
        ).fetchone()
        == con.execute("SELECT count(*),coalesce(sum(sales_value_12m),0) FROM customers").fetchone()
    )
    checks["order_bridge_reconciles"] = (
        con.execute("SELECT sum(prior_orders),sum(current_orders) FROM order_bridge").fetchone()
        == con.execute(
            "SELECT count(*) FILTER (WHERE year(occurred_date)=2010),"
            "count(*) FILTER (WHERE year(occurred_date)=2011) FROM fact_invoice "
            "WHERE year(occurred_date) IN (2010,2011) AND month(occurred_date)<=11"
        ).fetchone()
    )
    checks["product_value_bridge_reconciles"] = (
        con.execute(
            "SELECT coalesce(sum(prior_value),0),coalesce(sum(current_value),0) FROM product_changes"
        ).fetchone()
        == con.execute(
            "SELECT coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2010),0),"
            "coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2011),0) "
            "FROM tableau_sales WHERE is_merchandise='Merchandise' "
            "AND year(occurred_date) IN (2010,2011) AND month(occurred_date)<=11"
        ).fetchone()
    )
    checks["product_penetration_bounds"] = con.execute(
        "SELECT count(*)=0 FROM product_changes WHERE current_penetration<0 "
        "OR current_penetration>1"
    ).fetchone()[0]
    checks["cohorts_by_segment_reconcile"] = con.execute(
        "WITH grouped AS (SELECT cohort_month,month_index,sum(cohort_customers) AS n,"
        "sum(active_customers) AS active FROM cohorts_by_segment GROUP BY 1,2) "
        "SELECT count(*)=0 FROM grouped g FULL JOIN cohorts c "
        "USING (cohort_month,month_index) WHERE g.n IS DISTINCT FROM c.cohort_customers "
        "OR g.active IS DISTINCT FROM c.active_customers"
    ).fetchone()[0]
    return checks


def diagnostics(con):
    counts = {
        table: con.execute("SELECT count(*) FROM " + table).fetchone()[0]
        for table in (
            "fact_invoice_line",
            "fact_invoice",
            "dim_date",
            "dim_product",
            "dim_customer",
            "dim_country",
            "tableau_sales",
            "tableau_customers",
        )
    }
    source_profile = rows(
        con,
        """SELECT
        count(DISTINCT product_key) AS sales_stock_codes,
        count(DISTINCT product_key) FILTER (WHERE sale_description_variants>1)
          AS sales_codes_with_multiple_labels
        FROM tableau_sales JOIN dim_product USING (product_key)""",
    )[0]
    source_profile["multiple_product_invoices"] = con.execute(
        "SELECT count(*) FROM (SELECT invoice_key FROM tableau_sales GROUP BY 1 "
        "HAVING count(DISTINCT product_key)>1)"
    ).fetchone()[0]
    source_profile["partially_missing_customer_invoices"] = con.execute(
        "SELECT count(*) FROM (SELECT invoice_key FROM sales GROUP BY 1 "
        "HAVING count(DISTINCT customer_key)=1 AND count(*) FILTER (WHERE customer_key IS NULL)>0)"
    ).fetchone()[0]
    full_window = rows(
        con,
        """SELECT
        coalesce(sum(recorded_value) FILTER (WHERE is_merchandise='Merchandise'),0) AS merchandise_value,
        coalesce(sum(recorded_value) FILTER (WHERE is_merchandise='Service'),0) AS service_value
        FROM tableau_sales""",
    )[0]
    comparison = rows(
        con,
        """SELECT
        coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2010),0) AS prior_merchandise_value,
        coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2011),0) AS current_merchandise_value,
        count(DISTINCT invoice_key) FILTER (WHERE year(occurred_date)=2010) AS prior_merchandise_orders,
        count(DISTINCT invoice_key) FILTER (WHERE year(occurred_date)=2011) AS current_merchandise_orders
        FROM tableau_sales WHERE is_merchandise='Merchandise'
        AND year(occurred_date) IN (2010,2011) AND month(occurred_date)<=11""",
    )[0]
    top10 = con.execute(
        "SELECT coalesce(sum(current_value),0) FROM (SELECT current_value FROM product_changes "
        "ORDER BY current_value DESC,product_key LIMIT 10)"
    ).fetchone()[0]
    comparison["top10_current_value"] = top10
    comparison["top10_current_share"] = (
        top10 / comparison["current_merchandise_value"]
        if comparison["current_merchandise_value"]
        else None
    )
    service_breakdown = rows(
        con,
        """SELECT p.product_scope,count(*) AS lines,
        sum(t.recorded_value) AS recorded_value FROM tableau_sales t
        JOIN dim_product p USING (product_key) WHERE t.is_merchandise='Service'
        GROUP BY 1 ORDER BY 1""",
    )
    return {
        "model_counts": counts,
        "source_profile": source_profile,
        "full_window": full_window,
        "comparison": comparison,
        "service_breakdown": service_breakdown,
    }


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
            "SELECT sum(recorded_value) FROM fact_invoice WHERE customer_key IS NOT NULL AND occurred_date >= DATE '2010-12-01'"
        ).fetchone()[0],
        "customer_orders_unambiguous": quality["invoice_customer_conflicts"] == 0,
        "monthly_orders_unambiguous": quality["invoice_month_conflicts"] == 0,
    }
    if not all(checks.values()):
        raise ValueError("Reconciliation failed: " + repr(checks))
    dimension_checks = model_checks(con)
    if not all(dimension_checks.values()):
        raise ValueError("Model reconciliation failed: " + repr(dimension_checks))
    for table in ("monthly", "countries", "cohorts", "segments"):
        data = rows(con, "SELECT * FROM " + table)
        with (output / (table + ".csv")).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    write_json(output / "quality.json", quality)
    write_json(output / "summary.json", summary)
    write_json(output / "checks.json", checks)
    for table, ordering in (
        ("order_bridge", "sort_order"),
        ("product_changes", "value_change DESC,product_key"),
        ("product_preferences", "segment,rank"),
        ("cohorts_by_segment", "cohort_month,month_index,segment"),
    ):
        write_csv(
            con, "SELECT * FROM " + table + " ORDER BY " + ordering, output / (table + ".csv")
        )
    for table, ordering in (
        ("tableau_sales", "invoice_key,occurred_date,product_key,recorded_value,units"),
        ("tableau_customers", "customer_key"),
    ):
        write_csv(
            con, "SELECT * FROM " + table + " ORDER BY " + ordering, processed / (table + ".csv")
        )
    write_json(output / "model_checks.json", dimension_checks)
    write_json(output / "diagnostic_summary.json", diagnostics(con))
    print(
        json.dumps({"summary": summary, "quality": quality, "checks": checks}, default=json_value)
    )
    con.close()


if __name__ == "__main__":
    main()
