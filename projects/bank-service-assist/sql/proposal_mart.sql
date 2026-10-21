-- Grain: one proposal. Compare current reviewed payload with its first revision.
-- Origin separates bounded-Agent drafts from staff-authored drafts; rejected drafts
-- are explicit human decisions, so the decided-only denominator is not accepted-by-construction.
SELECT p.id,p.kind,p.version,p.status,
       CASE WHEN p.status='committed' AND p.payload=first_revision.payload THEN 'accepted_unchanged'
            WHEN p.status='committed' THEN 'accepted_edited'
            WHEN p.status='rejected' THEN 'rejected' ELSE 'pending' END AS disposition,
       CASE WHEN EXISTS(SELECT 1 FROM operations o WHERE o.command='create_proposal'
                        AND o.operation_key LIKE 'agent-draft:%%'
                        AND o.receipt->'data'->>'proposal_id'=p.id::text)
            THEN 'agent' ELSE 'staff' END AS origin
FROM proposals p
JOIN LATERAL (SELECT payload,recorded_at FROM proposal_revisions r WHERE r.proposal_id=p.id ORDER BY version LIMIT 1) first_revision ON true
WHERE first_revision.recorded_at<=%(cutoff)s ORDER BY p.id;
