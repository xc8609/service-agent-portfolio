"""Rebuild local tables and a factual report; never publish complaint narratives."""
import json
import os
import sys
from pathlib import Path

import duckdb

from download_archive import sha256

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
REVIEW_PER_PRODUCT = 10  # balanced discovery worksheet size per in-scope product


def rows(connection, sql):
    result = connection.execute(sql)
    return [dict(zip([col[0] for col in result.description], row)) for row in result.fetchall()]


def main():
    os.chdir(ROOT)  # SQL input paths are rooted at the repository, not the caller's cwd.
    raw, processed = PROJECT / "data/raw", PROJECT / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((raw / "source-manifest.json").read_text())
    if sha256(raw / manifest["csv_file"]) != manifest["csv_sha256"]:
        raise ValueError("CSV checksum does not match the source manifest")
    with duckdb.connect(str(processed / "cfpb.duckdb")) as con:
        con.execute("BEGIN")
        try:
            for filename in ("01_load.sql", "02_staging.sql", "03_routing_scope.sql"):
                con.execute((PROJECT / "sql" / filename).read_text())
            summary = rows(con, """
                SELECT count(*) AS records, count(DISTINCT complaint_id) AS distinct_ids,
                    count(*) FILTER (WHERE has_narrative) AS with_narrative,
                    min(date_received) AS first_received, max(date_received) AS last_received,
                    count(*) FILTER (WHERE complaint_id IS NULL) AS invalid_ids,
                    count(*) FILTER (WHERE date_received IS NULL) AS invalid_received_dates,
                    count(*) FILTER (WHERE date_sent_to_company IS NULL) AS invalid_sent_dates,
                    count(*) FILTER (WHERE date_sent_to_company < date_received) AS reversed_dates,
                    count(*) FILTER (WHERE nullif(trim(product), '') IS NULL) AS missing_products,
                    count(*) FILTER (WHERE is_timely IS NULL) AS unknown_timely_response
                FROM stg_complaints""")[0]
            products = rows(con, """SELECT product, count(*) AS records,
                count(*) FILTER (WHERE has_narrative) AS narratives
                FROM stg_complaints GROUP BY product ORDER BY records DESC""")
            con.execute("""CREATE OR REPLACE TABLE banking_discovery AS
                SELECT s.*, r.routing_team FROM stg_complaints AS s
                JOIN ref_product_team AS r USING (product) WHERE s.has_narrative""")
            scope = rows(con, """SELECT r.routing_team, r.product,
                count(s.complaint_id) AS records,
                count(s.complaint_id) FILTER (WHERE s.has_narrative) AS narratives
                FROM ref_product_team AS r LEFT JOIN stg_complaints AS s USING (product)
                GROUP BY ALL ORDER BY r.routing_team, r.product""")
            bank_count = con.execute("SELECT count(*) FROM banking_discovery").fetchone()[0]
            duplicates = con.execute("""SELECT count(*) - count(DISTINCT
                lower(regexp_replace(trim(narrative), '\\s+', ' ', 'g')))
                FROM banking_discovery""").fetchone()[0]
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        con.execute("COPY banking_discovery TO ? (FORMAT PARQUET)", [str(processed / "banking_discovery.parquet")])
        # Fixed hash order is reproducible. This is a balanced discovery selection,
        # not a prevalence estimate or a held-out model evaluation set.
        sample_sql = f"""SELECT complaint_id, routing_team, product, issue, narrative,
            date_received, '' AS reviewer_observation, '' AS ambiguous_product,
            '' AS missing_context
            FROM (SELECT *, row_number() OVER (PARTITION BY product
                ORDER BY md5(CAST(complaint_id AS VARCHAR)), complaint_id) AS rn
                FROM banking_discovery) WHERE rn <= {REVIEW_PER_PRODUCT}
            ORDER BY routing_team, product, rn"""
        con.execute("COPY (" + sample_sql + ") TO ? (HEADER, DELIMITER ',')", [str(processed / "discovery_review.csv")])
        review_rows = con.execute("SELECT count(*) FROM (" + sample_sql + ")").fetchone()[0]
        con.execute("""COPY (SELECT product, count(*) AS records,
            count(*) FILTER (WHERE has_narrative) AS narratives FROM stg_complaints
            GROUP BY product ORDER BY records DESC) TO ? (HEADER, DELIMITER ',')""",
            [str(processed / "product_summary.csv")])
    payload = {"source": manifest, "summary": summary, "products": products,
               "routing_scope": scope, "banking_narratives": bank_count,
               "discovery_review_rows": review_rows,
               "banking_normalized_duplicate_excess": duplicates,
               "duckdb_version": duckdb.__version__, "python_version": sys.version.split()[0]}
    (processed / "profile.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")
    # The shareable manifest contains provenance only, no complaint records.
    (PROJECT / "data/source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    coverage = 100 * summary["with_narrative"] / summary["records"]
    lines = ["# Initial Real-Data Quality Report", "",
             "<!-- Generated by scripts/profile_data.py; manual edits are overwritten. -->", "",
             "Generated from the complete official July 2026 archive; no model has been trained.", "",
             "## Provenance", "",
             f"- Downloaded: {manifest['retrieved_at_utc']}",
             f"- Source: [{manifest['csv_file']}]({manifest['url']})",
             f"- Archive SHA-256: `{manifest['archive_sha256']}`",
             f"- Environment: Python {payload['python_version']}, DuckDB {duckdb.__version__}", "",
             "## Observed quality checks", "", "| Check | Result |", "|---|---:|"]
    lines += [f"| {key.replace('_', ' ')} | {value} |" for key, value in summary.items()]
    lines += [f"| narrative coverage | {coverage:.2f}% |", "",
              "## Product coverage", "", "| Product | Records | Narratives | Text coverage |", "|---|---:|---:|---:|"]
    lines += [f"| {p['product']} | {p['records']:,} | {p['narratives']:,} | {100*p['narratives']/p['records']:.2f}% |" for p in products]
    lines += ["", "## Simulated routing scope", "",
              "The simulated user is a bank complaint intake analyst reviewing an initial",
              "product suggestion. Scope and the simulated product-to-team mapping are defined",
              "in `sql/03_routing_scope.sql`; other products are explicitly out of scope.", "",
              "| Simulated team | Product | Records | Narratives |", "|---|---|---:|---:|"]
    lines += [f"| {s['routing_team']} | {s['product']} | {s['records']:,} | {s['narratives']:,} |" for s in scope]
    lines += ["", f"This selection contains **{bank_count:,} nonblank narratives**.",
              f"Normalized repeated-text excess within this selection: **{duplicates:,}**",
              "(lowercase and collapsed whitespace; excess rows, not duplicate groups).",
              "Keep original rows for discovery; resolve repeated/near-duplicate text before",
              "splitting model data. No train/test split has been made.", "",
              "Text availability varies greatly by product. Counts describe this published",
              "archive, not all bank customers or verified incidents. Do not extrapolate the",
              "text subset's product mix to all complaints or infer why text is missing.",
              "One month cannot establish seasonality or taxonomy stability across time.",
              "Sent-to-company dates and timely-response flags do not measure final resolution",
              "time, internal queue duration or actual routing accuracy.", "",
              "## Local outputs and next review", "",
              "- `data/processed/cfpb.duckdb`: raw/staging tables and banking discovery table.",
              "- `data/processed/banking_discovery.parquet`: scoped source records, git-ignored.",
              f"- `data/processed/discovery_review.csv`: {review_rows} rows, up to {REVIEW_PER_PRODUCT} per scoped product,",
              "  selected by fixed complaint-ID hash; review columns are blank, not completed annotations.",
              "- `data/processed/product_summary.csv` and `profile.json`: reproducible summaries.", "",
              f"Review the {review_rows} records for multi-product cases, missing context and ambiguous labels",
              "before finalizing requirements. Discovery-reviewed records must be excluded from",
              "a later untouched evaluation set. The CSV selection is not a random population sample.",
              "No paid API, LLM submission, dashboard, automated routing or measured savings is claimed.", ""]
    (PROJECT / "docs/03_data_quality_report.md").write_text("\n".join(lines))
    print(json.dumps({"summary": summary, "banking_narratives": bank_count,
                      "duplicate_text_excess": duplicates}, default=str, indent=2))


if __name__ == "__main__":
    main()
