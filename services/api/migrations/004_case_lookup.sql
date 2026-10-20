-- Read-only customer-safe case projection; no case transition commands here.
ALTER TABLE cases ADD COLUMN public_reference text UNIQUE;
ALTER TABLE cases ADD COLUMN concern_code text;
ALTER TABLE cases ADD COLUMN status_recorded_at timestamptz;
ALTER TABLE cases ADD COLUMN timeline_sequence bigint NOT NULL DEFAULT 0 CHECK (timeline_sequence >= 0);
CREATE TABLE case_timeline_events (
  id uuid PRIMARY KEY,
  case_id uuid NOT NULL REFERENCES cases(id),
  aggregate_sequence bigint NOT NULL CHECK (aggregate_sequence > 0),
  case_version bigint NOT NULL CHECK (case_version > 0),
  case_status text NOT NULL,
  occurred_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL,
  event_type text NOT NULL,
  customer_safe_summary text NOT NULL,
  source_ref text NOT NULL,
  UNIQUE(case_id, aggregate_sequence)
);
CREATE INDEX case_transaction_lookup ON case_transactions(transaction_id, case_id);
