-- Load the raw CFPB export into DuckDB as-is.
-- Run from repo root:
--   duckdb projects/cfpb-complaint-triage/data/processed/cfpb.duckdb < projects/cfpb-complaint-triage/sql/01_load.sql

CREATE OR REPLACE TABLE raw_complaints AS
SELECT *
FROM read_csv(
    'projects/cfpb-complaint-triage/data/raw/CCDB_Export_20_July_2026.csv',
    header = true,
    all_varchar = true      -- load everything as text; type it in staging
);

SELECT count(*) AS row_count FROM raw_complaints;
