-- Rows sharing a case_id are repeat interactions about one case. Case attributes must
-- agree across those rows; the build script stops if they do not.
CREATE OR REPLACE TABLE case_rollup AS
SELECT
  case_id,
  count(*) AS interactions,
  count(DISTINCT request_type) AS type_values,
  count(DISTINCT opened_at) AS open_values,
  count(DISTINCT coalesce(cast(closed_at AS VARCHAR), '')) AS close_values,
  count(DISTINCT status) AS status_values,
  min(request_type) AS request_type,
  min(opened_at) AS opened_at,
  max(closed_at) AS closed_at,
  min(status) AS status,
  arg_min(channel, interaction_id) AS first_channel,
  min(ward) AS ward,
  min(neighbourhood) AS neighbourhood
FROM staged
GROUP BY case_id;

-- In-scope solid-waste cases opened before the snapshot. A case closed after the
-- snapshot is treated as open at the snapshot.
CREATE OR REPLACE TABLE fact_case AS
WITH s AS (SELECT * FROM settings)
SELECT
  c.case_id,
  c.request_type,
  m.analysis_group,
  m.waste_stream,
  c.opened_at,
  cast(date_trunc('month', c.opened_at) AS DATE) AS open_month,
  CASE WHEN c.closed_at < s.snapshot_at THEN c.closed_at END AS closed_at,
  c.closed_at IS NULL OR c.closed_at >= s.snapshot_at AS open_at_snapshot,
  CASE WHEN c.closed_at < s.snapshot_at
    THEN (epoch(c.closed_at) - epoch(c.opened_at)) / 86400.0 END AS days_to_close,
  CASE WHEN c.closed_at IS NULL OR c.closed_at >= s.snapshot_at
    THEN (epoch(s.snapshot_at) - epoch(c.opened_at)) / 86400.0 END AS age_days,
  c.interactions,
  c.first_channel,
  c.ward,
  c.neighbourhood,
  c.opened_at < s.window_end AS in_monthly_window
FROM case_rollup c
JOIN request_type_map m ON c.request_type = m.request_type
CROSS JOIN s
WHERE c.opened_at >= s.window_start AND c.opened_at < s.snapshot_at;
