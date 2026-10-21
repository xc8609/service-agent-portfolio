-- Migration 001: immutable snapshot of the v0.4 reference domain schema.

-- API/service predicates enforce cross-record authorization and state semantics.


CREATE TABLE staff_principals (
  id uuid PRIMARY KEY NOT NULL,
  subject_ref text NOT NULL,
  active boolean NOT NULL,
  UNIQUE (subject_ref)
);

CREATE TABLE service_queues (
  id uuid PRIMARY KEY NOT NULL,
  name text NOT NULL,
  kind text NOT NULL,
  active boolean NOT NULL,
  UNIQUE (name)
);

CREATE TABLE queue_memberships (
  id uuid PRIMARY KEY NOT NULL,
  principal_id uuid NOT NULL,
  queue_id uuid NOT NULL,
  role text NOT NULL,
  active boolean NOT NULL,
  UNIQUE (principal_id, queue_id, role)
);

CREATE TABLE customers (
  id uuid PRIMARY KEY NOT NULL,
  external_ref text NOT NULL,
  display_alias text NOT NULL,
  data_origin text NOT NULL,
  UNIQUE (external_ref)
);

CREATE TABLE card_accounts (
  id uuid PRIMARY KEY NOT NULL,
  customer_id uuid NOT NULL,
  masked_ref text NOT NULL,
  product text NOT NULL,
  currency char(3) NOT NULL,
  version bigint NOT NULL,
  UNIQUE (masked_ref)
);

CREATE TABLE card_transactions (
  id uuid PRIMARY KEY NOT NULL,
  account_id uuid NOT NULL,
  amount_minor bigint NOT NULL,
  currency char(3) NOT NULL,
  merchant_description text NOT NULL,
  status text NOT NULL,
  occurred_at timestamptz NOT NULL,
  posted_at timestamptz,
  source_ref text NOT NULL,
  version bigint NOT NULL
);

CREATE TABLE transaction_relationships (
  id uuid PRIMARY KEY NOT NULL,
  left_transaction_id uuid NOT NULL,
  right_transaction_id uuid NOT NULL,
  relation text NOT NULL,
  evidence_ref text NOT NULL,
  version bigint NOT NULL,
  UNIQUE (left_transaction_id, right_transaction_id, relation)
);

CREATE TABLE contacts (
  id uuid PRIMARY KEY NOT NULL,
  customer_id uuid NOT NULL,
  actor_id uuid NOT NULL,
  kind text NOT NULL,
  status text NOT NULL,
  opened_at timestamptz NOT NULL,
  closed_at timestamptz,
  version bigint NOT NULL
);

CREATE TABLE verification_assertions (
  id uuid PRIMARY KEY NOT NULL,
  contact_id uuid NOT NULL,
  issuer_ref text NOT NULL,
  state text NOT NULL,
  verified_at timestamptz,
  expires_at timestamptz,
  scope_json jsonb NOT NULL
);

CREATE TABLE cases (
  id uuid PRIMARY KEY NOT NULL,
  customer_id uuid NOT NULL,
  origin_contact_id uuid NOT NULL,
  owner_queue_id uuid NOT NULL,
  status text NOT NULL,
  concern text NOT NULL,
  created_at timestamptz NOT NULL,
  closed_at timestamptz,
  disposition text,
  version bigint NOT NULL
);

CREATE TABLE case_transactions (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  transaction_id uuid NOT NULL,
  UNIQUE (case_id, transaction_id)
);

CREATE TABLE work_items (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  kind text NOT NULL,
  queue_id uuid NOT NULL,
  assignee_id uuid,
  status text NOT NULL,
  due_at timestamptz,
  original_due_at timestamptz,
  calendar_ref text NOT NULL,
  source_event_key text NOT NULL,
  version bigint NOT NULL,
  parent_work_id uuid,
  UNIQUE (source_event_key)
);

CREATE TABLE investigation_results (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  author_id uuid NOT NULL,
  version bigint NOT NULL,
  finding_code text NOT NULL,
  evidence_refs jsonb NOT NULL,
  approved_customer_explanation text NOT NULL,
  published_at timestamptz NOT NULL,
  UNIQUE (case_id, version)
);

CREATE TABLE result_private_notes (
  id uuid PRIMARY KEY NOT NULL,
  result_id uuid NOT NULL,
  body text NOT NULL,
  UNIQUE (result_id)
);

CREATE TABLE required_actions (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  action_kind text NOT NULL,
  status text NOT NULL,
  external_ref text NOT NULL,
  receipt_ref text,
  updated_at timestamptz NOT NULL,
  version bigint NOT NULL,
  UNIQUE (external_ref)
);

CREATE TABLE callback_attempts (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  contact_id uuid NOT NULL,
  actor_id uuid NOT NULL,
  occurred_at timestamptz NOT NULL,
  service_date date NOT NULL,
  dial_state text NOT NULL,
  outcome text NOT NULL,
  counts_toward_limit boolean NOT NULL,
  rule_version text NOT NULL,
  operation_key text NOT NULL,
  contact_plan_id uuid NOT NULL,
  reservation_id uuid,
  UNIQUE (operation_key)
);

CREATE TABLE contact_reservations (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  service_date date NOT NULL,
  scheduled_at timestamptz NOT NULL,
  state text NOT NULL,
  version bigint NOT NULL,
  contact_plan_id uuid NOT NULL
);

CREATE TABLE customer_objections (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  contact_id uuid NOT NULL,
  statement text NOT NULL,
  evidence_refs jsonb NOT NULL,
  complaint_requested boolean NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE policy_versions (
  id uuid PRIMARY KEY NOT NULL,
  policy_key text NOT NULL,
  version text NOT NULL,
  product text NOT NULL,
  jurisdiction text NOT NULL,
  audience text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  body text NOT NULL,
  source_label text NOT NULL,
  UNIQUE (policy_key, version)
);

CREATE TABLE service_calendars (
  id uuid PRIMARY KEY NOT NULL,
  calendar_key text NOT NULL,
  version text NOT NULL,
  timezone text NOT NULL,
  open_windows jsonb NOT NULL,
  holidays jsonb NOT NULL,
  UNIQUE (calendar_key, version)
);

CREATE TABLE proposals (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid,
  contact_id uuid NOT NULL,
  kind text NOT NULL,
  payload jsonb NOT NULL,
  source_versions jsonb NOT NULL,
  status text NOT NULL,
  version bigint NOT NULL,
  author_ref text NOT NULL,
  rendered_source_hash text NOT NULL
);

CREATE TABLE operations (
  id uuid PRIMARY KEY NOT NULL,
  actor_id uuid NOT NULL,
  operation_key text NOT NULL,
  command text NOT NULL,
  request_hash text NOT NULL,
  status text NOT NULL,
  receipt jsonb,
  created_at timestamptz NOT NULL,
  UNIQUE (actor_id, command, operation_key)
);

CREATE TABLE audit_events (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid,
  actor_ref text NOT NULL,
  event_type text NOT NULL,
  occurred_at timestamptz NOT NULL,
  safe_details jsonb NOT NULL,
  operation_id uuid,
  aggregate_sequence bigint NOT NULL,
  UNIQUE (case_id, aggregate_sequence)
);

CREATE TABLE outbox_events (
  id uuid PRIMARY KEY NOT NULL,
  event_key text NOT NULL,
  aggregate_ref text NOT NULL,
  aggregate_version bigint NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  status text NOT NULL,
  lease_expires_at timestamptz,
  attempt_count integer NOT NULL,
  UNIQUE (event_key)
);

CREATE TABLE agent_runs (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid,
  contact_id uuid NOT NULL,
  scope_snapshot jsonb NOT NULL,
  provider_profile text NOT NULL,
  trigger_key text NOT NULL,
  status text NOT NULL,
  started_at timestamptz NOT NULL,
  finished_at timestamptz,
  UNIQUE (trigger_key)
);

CREATE TABLE agent_steps (
  id uuid PRIMARY KEY NOT NULL,
  run_id uuid NOT NULL,
  sequence integer NOT NULL,
  tool_name text NOT NULL,
  source_refs jsonb NOT NULL,
  safe_result jsonb NOT NULL,
  duration_ms integer NOT NULL,
  UNIQUE (run_id, sequence)
);

CREATE TABLE update_commitments (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  proposed_by uuid NOT NULL,
  proposed_at timestamptz NOT NULL,
  proposed_update_at timestamptz NOT NULL,
  customer_safe_progress text NOT NULL,
  reason text NOT NULL,
  status text NOT NULL,
  version bigint NOT NULL,
  decided_by uuid,
  decided_at timestamptz,
  decision_reason text,
  supersedes_id uuid,
  operation_key text NOT NULL,
  CHECK (status IN ('pending_approval','approved','rejected','superseded','missed')),
  CHECK (status NOT IN ('approved','rejected','superseded','missed') OR (decided_by IS NOT NULL AND decided_at IS NOT NULL)),
  CHECK (proposed_update_at > proposed_at)
);

CREATE TABLE complaint_intakes (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  objection_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  queue_id uuid NOT NULL,
  recorded_by uuid NOT NULL,
  recorded_at timestamptz NOT NULL,
  status text NOT NULL,
  external_receipt_ref text,
  acknowledged_at timestamptz,
  version bigint NOT NULL,
  UNIQUE (objection_id),
  UNIQUE (work_item_id),
  CHECK (status IN ('recorded','pending_delivery','delivery_failed','acknowledged')),
  CHECK (status <> 'acknowledged' OR (external_receipt_ref IS NOT NULL AND acknowledged_at IS NOT NULL))
);

CREATE TABLE objection_work_links (
  id uuid PRIMARY KEY NOT NULL,
  objection_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  kind text NOT NULL,
  created_at timestamptz NOT NULL,
  UNIQUE (objection_id, kind),
  CHECK (kind IN ('specialist_rereview','complaint_intake'))
);

CREATE TABLE lead_review_decisions (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  exhausted_plan_id uuid NOT NULL,
  actor_id uuid NOT NULL,
  decided_at timestamptz NOT NULL,
  reason text NOT NULL,
  kind text NOT NULL,
  owner_id uuid NOT NULL,
  review_at timestamptz,
  operation_key text NOT NULL,
  expected_work_version bigint NOT NULL,
  CHECK (kind IN ('new_plan','review_hold')),
  CHECK ((kind = 'review_hold' AND review_at > decided_at) OR (kind = 'new_plan' AND review_at IS NULL))
);

CREATE TABLE contact_plans (
  id uuid PRIMARY KEY NOT NULL,
  case_id uuid NOT NULL,
  work_item_id uuid NOT NULL,
  kind text NOT NULL,
  status text NOT NULL,
  version bigint NOT NULL,
  previous_plan_id uuid,
  approval_decision_id uuid,
  owner_id uuid,
  max_attempts integer NOT NULL,
  valid_from timestamptz,
  valid_until timestamptz,
  approved_slots jsonb NOT NULL,
  calendar_ref text NOT NULL,
  first_placed_at timestamptz,
  created_at timestamptz NOT NULL,
  UNIQUE (approval_decision_id),
  CHECK (kind IN ('initial','lead_approved')),
  CHECK (max_attempts > 0),
  CHECK (valid_until IS NULL OR valid_until > valid_from),
  CHECK (kind <> 'lead_approved' OR (approval_decision_id IS NOT NULL AND previous_plan_id IS NOT NULL AND owner_id IS NOT NULL AND valid_from IS NOT NULL AND valid_until IS NOT NULL)),
  CHECK (kind <> 'initial' OR (previous_plan_id IS NULL AND approval_decision_id IS NULL AND max_attempts = 3))
);

CREATE TABLE contact_notes (
  id uuid PRIMARY KEY NOT NULL,
  contact_id uuid NOT NULL,
  case_id uuid,
  proposal_id uuid NOT NULL,
  reviewed_proposal_version bigint NOT NULL,
  body text NOT NULL,
  customer_allegations jsonb NOT NULL,
  source_versions jsonb NOT NULL,
  committed_by uuid NOT NULL,
  committed_at timestamptz NOT NULL,
  operation_id uuid NOT NULL,
  UNIQUE (proposal_id, reviewed_proposal_version),
  UNIQUE (operation_id)
);

ALTER TABLE queue_memberships ADD FOREIGN KEY (principal_id) REFERENCES staff_principals(id);

ALTER TABLE queue_memberships ADD FOREIGN KEY (queue_id) REFERENCES service_queues(id);

ALTER TABLE card_accounts ADD FOREIGN KEY (customer_id) REFERENCES customers(id);

ALTER TABLE card_transactions ADD FOREIGN KEY (account_id) REFERENCES card_accounts(id);

ALTER TABLE transaction_relationships ADD FOREIGN KEY (left_transaction_id) REFERENCES card_transactions(id);

ALTER TABLE transaction_relationships ADD FOREIGN KEY (right_transaction_id) REFERENCES card_transactions(id);

ALTER TABLE contacts ADD FOREIGN KEY (customer_id) REFERENCES customers(id);

ALTER TABLE contacts ADD FOREIGN KEY (actor_id) REFERENCES staff_principals(id);

ALTER TABLE verification_assertions ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE cases ADD FOREIGN KEY (customer_id) REFERENCES customers(id);

ALTER TABLE cases ADD FOREIGN KEY (origin_contact_id) REFERENCES contacts(id);

ALTER TABLE cases ADD FOREIGN KEY (owner_queue_id) REFERENCES service_queues(id);

ALTER TABLE case_transactions ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE case_transactions ADD FOREIGN KEY (transaction_id) REFERENCES card_transactions(id);

ALTER TABLE work_items ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE work_items ADD FOREIGN KEY (queue_id) REFERENCES service_queues(id);

ALTER TABLE work_items ADD FOREIGN KEY (assignee_id) REFERENCES staff_principals(id);

ALTER TABLE work_items ADD FOREIGN KEY (parent_work_id) REFERENCES work_items(id);

ALTER TABLE investigation_results ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE investigation_results ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE investigation_results ADD FOREIGN KEY (author_id) REFERENCES staff_principals(id);

ALTER TABLE result_private_notes ADD FOREIGN KEY (result_id) REFERENCES investigation_results(id);

ALTER TABLE required_actions ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (actor_id) REFERENCES staff_principals(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (contact_plan_id) REFERENCES contact_plans(id);

ALTER TABLE callback_attempts ADD FOREIGN KEY (reservation_id) REFERENCES contact_reservations(id);

ALTER TABLE contact_reservations ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE contact_reservations ADD FOREIGN KEY (contact_plan_id) REFERENCES contact_plans(id);

ALTER TABLE customer_objections ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE customer_objections ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE proposals ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE proposals ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE operations ADD FOREIGN KEY (actor_id) REFERENCES staff_principals(id);

ALTER TABLE audit_events ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE audit_events ADD FOREIGN KEY (operation_id) REFERENCES operations(id);

ALTER TABLE agent_runs ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE agent_runs ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE agent_steps ADD FOREIGN KEY (run_id) REFERENCES agent_runs(id);

ALTER TABLE update_commitments ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE update_commitments ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE update_commitments ADD FOREIGN KEY (proposed_by) REFERENCES staff_principals(id);

ALTER TABLE update_commitments ADD FOREIGN KEY (decided_by) REFERENCES staff_principals(id);

ALTER TABLE update_commitments ADD FOREIGN KEY (supersedes_id) REFERENCES update_commitments(id);

ALTER TABLE complaint_intakes ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE complaint_intakes ADD FOREIGN KEY (objection_id) REFERENCES customer_objections(id);

ALTER TABLE complaint_intakes ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE complaint_intakes ADD FOREIGN KEY (queue_id) REFERENCES service_queues(id);

ALTER TABLE complaint_intakes ADD FOREIGN KEY (recorded_by) REFERENCES staff_principals(id);

ALTER TABLE objection_work_links ADD FOREIGN KEY (objection_id) REFERENCES customer_objections(id);

ALTER TABLE objection_work_links ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE lead_review_decisions ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE lead_review_decisions ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE lead_review_decisions ADD FOREIGN KEY (exhausted_plan_id) REFERENCES contact_plans(id);

ALTER TABLE lead_review_decisions ADD FOREIGN KEY (actor_id) REFERENCES staff_principals(id);

ALTER TABLE lead_review_decisions ADD FOREIGN KEY (owner_id) REFERENCES staff_principals(id);

ALTER TABLE contact_plans ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE contact_plans ADD FOREIGN KEY (work_item_id) REFERENCES work_items(id);

ALTER TABLE contact_plans ADD FOREIGN KEY (previous_plan_id) REFERENCES contact_plans(id);

ALTER TABLE contact_plans ADD FOREIGN KEY (approval_decision_id) REFERENCES lead_review_decisions(id);

ALTER TABLE contact_plans ADD FOREIGN KEY (owner_id) REFERENCES staff_principals(id);

ALTER TABLE contact_notes ADD FOREIGN KEY (contact_id) REFERENCES contacts(id);

ALTER TABLE contact_notes ADD FOREIGN KEY (case_id) REFERENCES cases(id);

ALTER TABLE contact_notes ADD FOREIGN KEY (proposal_id) REFERENCES proposals(id);

ALTER TABLE contact_notes ADD FOREIGN KEY (committed_by) REFERENCES staff_principals(id);

ALTER TABLE contact_notes ADD FOREIGN KEY (operation_id) REFERENCES operations(id);

CREATE UNIQUE INDEX one_active_contact_slot ON contact_reservations(case_id, service_date) WHERE state = 'reserved';

CREATE UNIQUE INDEX one_active_contact_plan ON contact_plans(work_item_id) WHERE status = 'active';

CREATE UNIQUE INDEX one_approved_commitment ON update_commitments(work_item_id) WHERE status = 'approved';

CREATE INDEX work_by_queue_due ON work_items(queue_id, status, due_at);

CREATE INDEX case_by_customer ON cases(customer_id, created_at);
