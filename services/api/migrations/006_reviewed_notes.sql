CREATE TABLE proposal_revisions (
  proposal_id uuid NOT NULL REFERENCES proposals(id),
  version bigint NOT NULL,
  payload jsonb NOT NULL,
  actor_id uuid NOT NULL REFERENCES staff_principals(id),
  recorded_at timestamptz NOT NULL,
  PRIMARY KEY (proposal_id, version)
);
ALTER TABLE operations ADD COLUMN contact_id uuid REFERENCES contacts(id);
CREATE UNIQUE INDEX one_actor_operation_key ON operations(actor_id, operation_key);
