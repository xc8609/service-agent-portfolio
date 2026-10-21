-- Append-only customer reports. These never change ledger facts.
CREATE TABLE investigation_revisions (
  contact_id uuid NOT NULL REFERENCES contacts(id),
  revision integer NOT NULL CHECK (revision > 0),
  operation_key uuid NOT NULL,
  input_hash text NOT NULL,
  statement text NOT NULL CHECK (length(trim(statement)) BETWEEN 1 AND 2000),
  recognition text NOT NULL CHECK (recognition IN
    ('not_recorded','specific_entry','one_purchase_unresolved','both','neither')),
  transaction_versions jsonb NOT NULL,
  recognized_transaction_id uuid REFERENCES card_transactions(id),
  actor_id uuid NOT NULL REFERENCES staff_principals(id),
  recorded_at timestamptz NOT NULL,
  PRIMARY KEY(contact_id, revision),
  UNIQUE(contact_id, operation_key),
  CHECK ((recognition = 'specific_entry') = (recognized_transaction_id IS NOT NULL))
);
