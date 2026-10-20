-- Grain: one retained plan, aggregate calls before joining to prevent fanout.
SELECT p.id,p.work_item_id,p.kind,p.status,p.max_attempts,p.valid_until,w.original_due_at,
       coalesce(a.actual_calls,0) AS actual_calls,coalesce(a.counted_calls,0) AS counted_calls,
       coalesce(a.never_dialed_faults,0) AS never_dialed_faults,
       (p.valid_until<=%(cutoff)s AND NOT EXISTS(SELECT 1 FROM callback_attempts success WHERE success.contact_plan_id=p.id AND success.outcome='connected_verified' AND success.occurred_at<=p.valid_until AND NOT EXISTS(SELECT 1 FROM callback_anomalies anomaly WHERE anomaly.attempt_id=success.id))) AS window_missed,
       (p.kind='initial' AND w.original_due_at<=%(cutoff)s AND (p.first_placed_at IS NULL OR p.first_placed_at>w.original_due_at)) AS first_contact_missed
FROM contact_plans p JOIN work_items w ON w.id=p.work_item_id
LEFT JOIN (SELECT contact_plan_id,count(*) AS actual_calls,
 count(*) FILTER(WHERE counts_toward_limit) AS counted_calls,
 count(*) FILTER(WHERE dial_state='not_placed' AND outcome='technical_failure') AS never_dialed_faults
 FROM callback_attempts WHERE occurred_at<=%(cutoff)s GROUP BY contact_plan_id) a ON a.contact_plan_id=p.id
WHERE p.created_at<=%(cutoff)s ORDER BY p.id;
