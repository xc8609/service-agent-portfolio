-- Additive monthly counts; shares are computed from these in Tableau or SQL.
CREATE OR REPLACE TABLE monthly_requests AS
SELECT
  open_month AS month,
  analysis_group,
  waste_stream,
  request_type,
  count(*) AS cases,
  sum(interactions) AS interactions,
  count(*) FILTER (WHERE interactions > 1) AS repeat_contact_cases,
  count(*) FILTER (WHERE NOT open_at_snapshot) AS closed_cases,
  count(*) FILTER (WHERE days_to_close <= 1) AS closed_within_1_day,
  count(*) FILTER (WHERE days_to_close <= 3) AS closed_within_3_days,
  count(*) FILTER (WHERE days_to_close <= 7) AS closed_within_7_days,
  count(*) FILTER (WHERE days_to_close <= 14) AS closed_within_14_days,
  count(*) FILTER (WHERE days_to_close <= 30) AS closed_within_30_days,
  count(*) FILTER (WHERE open_at_snapshot) AS open_at_snapshot,
  count(*) FILTER (WHERE ward IS NOT NULL) AS cases_with_ward
FROM fact_case
WHERE in_monthly_window
GROUP BY ALL
ORDER BY month, analysis_group, request_type;

-- Quantiles treat still-open cases as not yet closed. A quantile is reported only
-- when it is below the youngest open case's age, so later closures cannot change it.
CREATE OR REPLACE MACRO censored_quantile(days, open_age, q) AS
  CASE WHEN quantile_disc(coalesce(days, 1e9), q) < coalesce(min(open_age), 1e9)
    THEN round(quantile_disc(coalesce(days, 1e9), q), 1) END;

CREATE OR REPLACE TABLE turnaround_by_year AS
SELECT
  year(open_month) AS open_year,
  analysis_group,
  count(*) AS cases,
  count(*) FILTER (WHERE open_at_snapshot) AS open_at_snapshot,
  censored_quantile(days_to_close, age_days, 0.5) AS median_days,
  censored_quantile(days_to_close, age_days, 0.9) AS p90_days
FROM fact_case
WHERE in_monthly_window
GROUP BY ALL
ORDER BY open_year, analysis_group;

CREATE OR REPLACE TABLE turnaround_by_type AS
SELECT
  year(open_month) AS open_year,
  analysis_group,
  request_type,
  count(*) AS cases,
  count(*) FILTER (WHERE open_at_snapshot) AS open_at_snapshot,
  censored_quantile(days_to_close, age_days, 0.5) AS median_days,
  censored_quantile(days_to_close, age_days, 0.9) AS p90_days
FROM fact_case
WHERE in_monthly_window
GROUP BY ALL
HAVING count(*) >= 100
ORDER BY open_year, analysis_group, request_type;

CREATE OR REPLACE TABLE open_ageing AS
SELECT
  analysis_group,
  waste_stream,
  request_type,
  CASE
    WHEN age_days < 7 THEN '1. Under 7 days'
    WHEN age_days < 30 THEN '2. 7-29 days'
    WHEN age_days < 90 THEN '3. 30-89 days'
    WHEN age_days < 365 THEN '4. 90-364 days'
    ELSE '5. 365 days or more'
  END AS age_band,
  count(*) AS open_cases
FROM fact_case
WHERE open_at_snapshot
GROUP BY ALL
ORDER BY analysis_group, request_type, age_band;

CREATE OR REPLACE TABLE follow_up_monthly AS
SELECT
  cast(month AS DATE) AS month,
  sum(rows) FILTER (WHERE type = 'Follow up- SLA breached') AS breached_calls,
  sum(rows) FILTER (WHERE type = 'Follow Up Call- SLA not breached') AS not_breached_calls,
  sum(rows) AS follow_up_calls
FROM raw_follow_up
WHERE cast(month AS DATE) < (SELECT window_end FROM settings)
GROUP BY ALL
ORDER BY month;
