CREATE TABLE callback_contexts (
  contact_id uuid PRIMARY KEY REFERENCES contacts(id), work_item_id uuid NOT NULL REFERENCES work_items(id),
  plan_id uuid NOT NULL REFERENCES contact_plans(id)
);
CREATE TABLE feedback_reviews (
  id uuid PRIMARY KEY, contact_id uuid NOT NULL REFERENCES callback_contexts(contact_id),
  work_item_id uuid NOT NULL REFERENCES work_items(id), result_id uuid NOT NULL REFERENCES investigation_results(id),
  result_version bigint NOT NULL, explanation text NOT NULL, status text NOT NULL CHECK(status IN ('draft','approved')),
  version bigint NOT NULL, actor_id uuid NOT NULL REFERENCES staff_principals(id), created_at timestamptz NOT NULL
);
CREATE TABLE callback_details (
  attempt_id uuid PRIMARY KEY REFERENCES callback_attempts(id), result_id uuid REFERENCES investigation_results(id),
  review_id uuid REFERENCES feedback_reviews(id), customer_response text, proof_id uuid REFERENCES verification_assertions(id)
);
CREATE TABLE evidence_requests (
  id uuid PRIMARY KEY, case_id uuid NOT NULL REFERENCES cases(id), specialist_work_id uuid NOT NULL REFERENCES work_items(id),
  followup_work_id uuid NOT NULL UNIQUE REFERENCES work_items(id), question text NOT NULL,
  requested_by uuid NOT NULL REFERENCES staff_principals(id), requested_at timestamptz NOT NULL
);
CREATE TABLE followup_entries (
  id uuid PRIMARY KEY, work_item_id uuid NOT NULL REFERENCES work_items(id), actor_id uuid NOT NULL REFERENCES staff_principals(id),
  recorded_at timestamptz NOT NULL, state text NOT NULL, statement text NOT NULL,
  evidence_refs jsonb NOT NULL, method_ref uuid REFERENCES customer_contact_methods(id), operation_id uuid NOT NULL REFERENCES operations(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE UNIQUE INDEX one_attempt_per_callback_contact ON callback_attempts(contact_id);
CREATE UNIQUE INDEX feedback_review_revision ON feedback_reviews(contact_id,version);
