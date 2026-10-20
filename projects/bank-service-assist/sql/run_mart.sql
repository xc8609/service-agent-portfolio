-- Grain: one started run. No join to steps, so a multi-tool run is counted once.
SELECT id, provider_profile, status, started_at, finished_at,
       CASE WHEN finished_at IS NOT NULL THEN extract(epoch FROM finished_at-started_at)*1000 END AS latency_ms,
       usage IS NULL AS usage_unknown
FROM agent_runs WHERE started_at <= %(cutoff)s ORDER BY id;
