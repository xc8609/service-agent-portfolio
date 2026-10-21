"""Build the Tableau aggregate source and reconcile it against complaint records."""
import json
from pathlib import Path

import duckdb

PROJECT = Path(__file__).resolve().parents[1]
IN_SCOPE = "product IN (SELECT product FROM ref_product_team)"


def main():
    processed = PROJECT / "data/processed"
    output = processed / "tableau"
    output.mkdir(parents=True, exist_ok=True)
    database = processed / "cfpb.duckdb"
    if not database.exists():
        raise FileNotFoundError("Run profile_data.py before exporting Tableau data")
    with duckdb.connect(str(database)) as con:
        con.execute((PROJECT / "sql/03_routing_scope.sql").read_text())
        quality = con.execute("""SELECT count(*), count(DISTINCT complaint_id),
            count(*) FILTER (WHERE date_received IS NULL)
            FROM stg_complaints WHERE """ + IN_SCOPE).fetchone()
        if quality[0] != quality[1] or quality[2]:
            raise ValueError("Missing/duplicate IDs or invalid dates; fix before aggregating")
        con.execute((PROJECT / "sql/04_complaint_mart.sql").read_text())
        fields = ["complaint_count", "narrative_count", "timely_yes_count",
                  "timely_no_count", "timely_unknown_count"]
        actual = con.execute("SELECT " + ",".join("sum(" + name + ")" for name in fields)
                             + " FROM mart_complaint_daily").fetchone()
        expected = con.execute("""SELECT count(*),
            count(*) FILTER (WHERE has_narrative),
            count(*) FILTER (WHERE is_timely = TRUE),
            count(*) FILTER (WHERE is_timely = FALSE),
            count(*) FILTER (WHERE is_timely IS NULL)
            FROM stg_complaints WHERE """ + IN_SCOPE).fetchone()
        if actual != expected or sum(actual[2:]) != actual[0]:
            raise ValueError("Tableau measures do not reconcile with staging")
        csv_path = output / "complaint_daily.csv"
        con.execute("""COPY (SELECT * FROM mart_complaint_daily
            ORDER BY date_received, routing_team, product, issue, channel, company_response)
            TO ? (HEADER, DELIMITER ',')""", [str(csv_path)])
        # Read the delivered file as well as the database view.
        delivered = con.execute("SELECT " + ",".join("sum(" + name + ")" for name in fields)
                                + " FROM read_csv_auto(?)", [str(csv_path)]).fetchone()
        if delivered != expected:
            raise ValueError("Exported CSV totals differ from staging")
        row_count = con.execute("SELECT count(*) FROM mart_complaint_daily").fetchone()[0]
        products = con.execute("""SELECT routing_team, product, sum(complaint_count),
            sum(narrative_count) FROM mart_complaint_daily
            GROUP BY routing_team, product ORDER BY routing_team, product""").fetchall()
    result = {"status": "reconciled", "aggregate_rows": row_count,
              "totals": dict(zip(fields, actual)),
              "by_product": [{"routing_team": row[0], "product": row[1],
                              "complaints": row[2], "narratives": row[3]} for row in products],
              "source_manifest": "data/source-manifest.json",
              "source_window": "2026-07-01 through 2026-07-31",
              "scope": "sql/03_routing_scope.sql", "contains_narratives_or_complaint_ids": False}
    (processed / "tableau_export_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
