CREATE TABLE due_events (
 id uuid PRIMARY KEY, work_item_id uuid NOT NULL REFERENCES work_items(id),
 due_at timestamptz NOT NULL, kind text NOT NULL, recorded_at timestamptz NOT NULL,
 UNIQUE(work_item_id,due_at,kind)
);
CREATE TABLE local_notifications (
 event_id uuid PRIMARY KEY REFERENCES outbox_events(id), received_at timestamptz NOT NULL,
 payload jsonb NOT NULL
);
ALTER TABLE service_routes ADD COLUMN complaint_queue_id uuid REFERENCES service_queues(id);
DROP INDEX one_reserved_date; -- original one_active_contact_slot already enforces the same rule
ALTER TABLE callback_contexts ALTER COLUMN plan_id DROP NOT NULL;
CREATE TABLE progress_contacts (
 id uuid PRIMARY KEY, work_item_id uuid NOT NULL REFERENCES work_items(id),
 contact_id uuid NOT NULL UNIQUE REFERENCES callback_contexts(contact_id),
 commitment_id uuid REFERENCES update_commitments(id), actor_id uuid NOT NULL REFERENCES staff_principals(id),
 occurred_at timestamptz NOT NULL, operation_id uuid NOT NULL REFERENCES operations(id) DEFERRABLE INITIALLY DEFERRED
);
