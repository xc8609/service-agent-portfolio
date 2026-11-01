-- One row per source interaction; nothing is dropped here.
CREATE OR REPLACE TABLE staged AS
SELECT
  trim(case_id) AS case_id,
  try_cast(interaction_id AS BIGINT) AS interaction_id,
  coalesce(nullif(trim(channel_type), ''), 'Unknown') AS channel,
  trim(type) AS request_type,
  try_cast(open_date AS TIMESTAMP) AS opened_at,
  try_cast(closed_date AS TIMESTAMP) AS closed_at,
  coalesce(nullif(trim(case_status), ''), 'Unknown') AS status,
  nullif(trim(ward), '') AS ward,
  nullif(trim(neighbourhood), '') AS neighbourhood
FROM raw_requests;
