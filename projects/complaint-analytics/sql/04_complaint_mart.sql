-- One row per received date / product / issue / channel / company response.
-- All in-scope records (see 03_routing_scope.sql), including complaints without text.
-- routing_team is determined by product, so it does not change the grain.
-- Measures are additive; compute weighted rates from sums in Tableau.
CREATE OR REPLACE VIEW mart_complaint_daily AS
SELECT
    s.date_received,
    r.routing_team,
    s.product,
    COALESCE(NULLIF(TRIM(s.issue), ''), 'Unknown') AS issue,
    COALESCE(NULLIF(TRIM(s.submitted_via), ''), 'Unknown') AS channel,
    COALESCE(NULLIF(TRIM(s.company_response), ''), 'Unknown') AS company_response,
    COUNT(*) AS complaint_count,
    SUM(CASE WHEN s.has_narrative THEN 1 ELSE 0 END) AS narrative_count,
    SUM(CASE WHEN s.is_timely = TRUE THEN 1 ELSE 0 END) AS timely_yes_count,
    SUM(CASE WHEN s.is_timely = FALSE THEN 1 ELSE 0 END) AS timely_no_count,
    SUM(CASE WHEN s.is_timely IS NULL THEN 1 ELSE 0 END) AS timely_unknown_count
FROM stg_complaints AS s
JOIN ref_product_team AS r USING (product)
GROUP BY s.date_received, r.routing_team, s.product,
    COALESCE(NULLIF(TRIM(s.issue), ''), 'Unknown'),
    COALESCE(NULLIF(TRIM(s.submitted_via), ''), 'Unknown'),
    COALESCE(NULLIF(TRIM(s.company_response), ''), 'Unknown');
