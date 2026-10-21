CREATE TABLE service_routes (
  concern_code text PRIMARY KEY, queue_id uuid NOT NULL REFERENCES service_queues(id),
  feedback_queue_id uuid NOT NULL REFERENCES service_queues(id),
  lead_id uuid NOT NULL REFERENCES staff_principals(id), version bigint NOT NULL CHECK(version>0), active boolean NOT NULL
);
CREATE TABLE customer_contact_methods (
  id uuid PRIMARY KEY, customer_id uuid NOT NULL REFERENCES customers(id), masked_ref text NOT NULL,
  active boolean NOT NULL, version bigint NOT NULL CHECK(version>0)
);
CREATE TABLE referral_pair_guards (pair_key text PRIMARY KEY, revision bigint NOT NULL);
CREATE TABLE referral_intakes (
  id uuid PRIMARY KEY, proposal_id uuid NOT NULL UNIQUE REFERENCES proposals(id),
  case_id uuid NOT NULL REFERENCES cases(id), work_item_id uuid NOT NULL REFERENCES work_items(id),
  contact_id uuid NOT NULL REFERENCES contacts(id), payload jsonb NOT NULL,
  source_versions jsonb NOT NULL, committed_by uuid NOT NULL REFERENCES staff_principals(id),
  committed_at timestamptz NOT NULL, operation_id uuid NOT NULL REFERENCES operations(id) DEFERRABLE INITIALLY DEFERRED,
  disposition text NOT NULL CHECK(disposition IN ('queued','linked_existing'))
);
ALTER TABLE work_items ADD COLUMN acceptance_due_at timestamptz;
