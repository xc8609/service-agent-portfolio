-- Supersession is not approval. Preserve explicit approval provenance separately.
ALTER TABLE update_commitments
 ADD COLUMN approved_by uuid REFERENCES staff_principals(id),
 ADD COLUMN approved_at timestamptz,
 ADD CONSTRAINT commitment_approval_pair CHECK ((approved_by IS NULL) = (approved_at IS NULL));
-- Only these legacy states prove approval in the existing state machine.
-- Ambiguous superseded rows remain internal; never invent approval history.
UPDATE update_commitments SET approved_by=decided_by, approved_at=decided_at
 WHERE status IN ('approved','missed') AND decided_by IS NOT NULL AND decided_at IS NOT NULL;
