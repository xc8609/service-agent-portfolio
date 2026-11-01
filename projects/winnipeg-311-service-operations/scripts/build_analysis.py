"""Build the case model and publish aggregate results; keep request records local."""

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW_COLUMNS = [
    "case_id",
    "interaction_id",
    "channel_type",
    "subject",
    "reason",
    "type",
    "open_date",
    "closed_date",
    "case_status",
    "neighbourhood",
    "ward",
]
WINDOW_START = "2023-01-01 00:00:00"
WINDOW_END = "2026-10-01 00:00:00"
# The source holds complete days to 30 October 2026 at the recorded retrieval.
SNAPSHOT_AT = "2026-10-31 00:00:00"


def create_raw(con):
    con.execute(
        "CREATE TABLE raw_requests (" + ", ".join(name + " VARCHAR" for name in RAW_COLUMNS) + ")"
    )
    con.execute("CREATE TABLE raw_follow_up (month VARCHAR, type VARCHAR, rows BIGINT)")
    con.execute(
        "CREATE TABLE request_type_map AS SELECT * FROM read_csv(?, header=true, all_varchar=true)",
        [str(ROOT / "reference/request_type_map.csv")],
    )


def build(con, snapshot_at=SNAPSHOT_AT, window_start=WINDOW_START, window_end=WINDOW_END):
    con.execute(
        "CREATE OR REPLACE TABLE settings AS SELECT ?::TIMESTAMP AS snapshot_at, "
        "?::TIMESTAMP AS window_start, ?::TIMESTAMP AS window_end",
        [snapshot_at, window_start, window_end],
    )
    con.execute((ROOT / "sql/01_staging.sql").read_text())
    invalid = con.execute(
        "SELECT count(*) FROM staged WHERE case_id IS NULL OR case_id='' OR opened_at IS NULL "
        "OR interaction_id IS NULL"
    ).fetchone()[0]
    if invalid:
        raise ValueError("Rows missing case, interaction or open date: " + str(invalid))
    con.execute((ROOT / "sql/02_cases.sql").read_text())
    conflicts = con.execute(
        "SELECT count(*) FROM case_rollup WHERE type_values>1 OR open_values>1 "
        "OR close_values>1 OR status_values>1"
    ).fetchone()[0]
    if conflicts:
        raise ValueError("Case attributes differ across interactions: " + str(conflicts))
    negative = con.execute("SELECT count(*) FROM fact_case WHERE days_to_close<0").fetchone()[0]
    if negative:
        raise ValueError("Cases closed before they opened: " + str(negative))
    con.execute((ROOT / "sql/03_marts.sql").read_text())


def load_local(con):
    con.execute(
        "INSERT INTO raw_requests SELECT * FROM read_csv(?, header=true, all_varchar=true)",
        [str(ROOT / "data/raw/water_waste_service_requests.csv")],
    )
    follow_ups = json.loads((ROOT / "data/raw/follow_up_calls_monthly.json").read_text())
    con.executemany(
        "INSERT INTO raw_follow_up VALUES (?, ?, ?)",
        [(item["month"][:10], item["type"], int(item["rows"])) for item in follow_ups],
    )


def scalar(con, query):
    return con.execute(query).fetchone()[0]


def checks(con, manifest):
    result = {
        "extract_rows_match_manifest": scalar(con, "SELECT count(*) FROM raw_requests")
        == manifest["rows"],
        "extract_rows_by_type_match_api": dict(
            con.execute("SELECT type, count(*) FROM raw_requests GROUP BY type").fetchall()
        )
        == manifest["api_rows_by_type"],
        "staging_keeps_every_row": scalar(con, "SELECT count(*) FROM staged")
        == scalar(con, "SELECT count(*) FROM raw_requests"),
        "case_key_unique": scalar(con, "SELECT count(*)=count(DISTINCT case_id) FROM fact_case"),
        "mapped_types_all_present": scalar(
            con,
            "SELECT count(*)=0 FROM request_type_map m WHERE m.request_type NOT IN "
            "(SELECT request_type FROM staged)",
        ),
        "interactions_reconcile_to_rows": scalar(
            con, "SELECT sum(interactions) FROM fact_case"
        )
        == scalar(
            con,
            "SELECT count(*) FROM staged s JOIN request_type_map m USING (request_type) "
            "WHERE opened_at >= (SELECT window_start FROM settings) "
            "AND opened_at < (SELECT snapshot_at FROM settings)",
        ),
        "monthly_mart_reconciles_to_cases": scalar(
            con, "SELECT sum(cases) FROM monthly_requests"
        )
        == scalar(con, "SELECT count(*) FROM fact_case WHERE in_monthly_window"),
        "open_ageing_reconciles_to_open_cases": scalar(
            con, "SELECT sum(open_cases) FROM open_ageing"
        )
        == scalar(con, "SELECT count(*) FROM fact_case WHERE open_at_snapshot"),
        "closed_within_bands_are_monotonic": scalar(
            con,
            "SELECT count(*)=0 FROM monthly_requests WHERE NOT (closed_within_1_day <= "
            "closed_within_3_days AND closed_within_3_days <= closed_within_7_days AND "
            "closed_within_7_days <= closed_within_14_days AND closed_within_14_days <= "
            "closed_within_30_days AND closed_within_30_days <= closed_cases)",
        ),
        "follow_up_rows_match_manifest": scalar(con, "SELECT sum(rows) FROM raw_follow_up")
        == manifest["follow_up_rows"],
    }
    return result


def quality(con):
    statuses = con.execute(
        "SELECT status, count(*) FROM case_rollup c JOIN request_type_map m USING (request_type) "
        "GROUP BY status ORDER BY status"
    ).fetchall()
    ward_by_year = con.execute(
        "SELECT year(open_month), round(100.0*count(ward)/count(*),1) FROM fact_case "
        "GROUP BY 1 ORDER BY 1"
    ).fetchall()
    return {
        "source_rows_all_water_and_waste": scalar(con, "SELECT count(*) FROM staged"),
        "source_rows_in_scope": scalar(
            con, "SELECT count(*) FROM staged JOIN request_type_map USING (request_type)"
        ),
        "cases_in_scope_before_snapshot": scalar(con, "SELECT count(*) FROM fact_case"),
        "cases_with_repeat_interactions": scalar(
            con, "SELECT count(*) FROM fact_case WHERE interactions>1"
        ),
        "case_status_values": {status: count for status, count in statuses},
        "cases_closed_after_snapshot_treated_as_open": scalar(
            con,
            "SELECT count(*) FROM case_rollup c JOIN fact_case f USING (case_id) "
            "WHERE c.closed_at >= (SELECT snapshot_at FROM settings)",
        ),
        "ward_present_percent_by_open_year": {str(year): pct for year, pct in ward_by_year},
        "mapped_request_types": scalar(con, "SELECT count(*) FROM request_type_map"),
    }


def summary(con):
    totals = con.execute(
        "SELECT count(*), sum(interactions), count(*) FILTER (WHERE interactions>1) "
        "FROM fact_case WHERE in_monthly_window"
    ).fetchone()
    by_group = con.execute(
        "SELECT analysis_group, sum(cases) FROM monthly_requests GROUP BY 1 ORDER BY 2 DESC"
    ).fetchall()
    seasonal = con.execute(
        "WITH m AS (SELECT month, sum(cases) AS cases FROM monthly_requests GROUP BY month) "
        "SELECT month(month) AS calendar_month, round(avg(cases)) FROM m GROUP BY 1 ORDER BY 1"
    ).fetchall()
    open_cases = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE age_days>=30), "
        "count(*) FILTER (WHERE age_days>=365) FROM fact_case WHERE open_at_snapshot"
    ).fetchone()
    follow = con.execute(
        "SELECT sum(follow_up_calls), sum(breached_calls) FROM follow_up_monthly"
    ).fetchone()
    return {
        "monthly_window": "January 2023 - September 2026 (opened)",
        "snapshot_at_local": SNAPSHOT_AT,
        "cases": totals[0],
        "interactions": totals[1],
        "cases_with_repeat_contact": totals[2],
        "cases_by_group": {group: count for group, count in by_group},
        "average_cases_by_calendar_month": {str(month): cases for month, cases in seasonal},
        "open_at_snapshot": open_cases[0],
        "open_30_days_or_more": open_cases[1],
        "open_365_days_or_more": open_cases[2],
        "city_follow_up_calls": follow[0],
        "city_follow_up_breached": follow[1],
    }


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
        writer.writerows(cursor.fetchall())


def main():
    manifest = json.loads((ROOT / "data/source-manifest.json").read_text())
    con = duckdb.connect(str(ROOT / "data/processed/311.duckdb"))
    for table in ("raw_requests", "raw_follow_up", "request_type_map"):
        con.execute("DROP TABLE IF EXISTS " + table)
    create_raw(con)
    load_local(con)
    build(con)
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    result_checks = checks(con, manifest)
    write_json(results / "checks.json", result_checks)
    if not all(result_checks.values()):
        raise ValueError("Failed checks: " + str([k for k, v in result_checks.items() if not v]))
    write_json(results / "quality.json", quality(con))
    write_json(results / "summary.json", summary(con))
    for name in (
        "monthly_requests",
        "turnaround_by_year",
        "turnaround_by_type",
        "open_ageing",
        "follow_up_monthly",
    ):
        write_csv(con, "SELECT * FROM " + name, results / (name + ".csv"))
    con.close()


if __name__ == "__main__":
    main()
