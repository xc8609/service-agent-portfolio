-- Grain: one proposal. Compare current reviewed payload with its first revision.
SELECT p.id,p.kind,p.version,p.status,
       CASE WHEN p.status='committed' AND p.payload=first_revision.payload THEN 'accepted_unchanged'
            WHEN p.status='committed' THEN 'accepted_edited'
            WHEN p.status='rejected' THEN 'rejected' ELSE 'pending' END AS disposition
FROM proposals p
JOIN LATERAL (SELECT payload,recorded_at FROM proposal_revisions r WHERE r.proposal_id=p.id ORDER BY version LIMIT 1) first_revision ON true
WHERE first_revision.recorded_at<=%(cutoff)s ORDER BY p.id;
