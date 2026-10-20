-- Runtime additions for the authorized inbound lookup slice.
CREATE TABLE demo_environment (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  marker text NOT NULL CHECK (marker = 'service-agent-disposable-v1'),
  database_name text NOT NULL,
  fixture_version text NOT NULL
);
CREATE TABLE demo_sessions (
  token_hash text PRIMARY KEY,
  principal_id uuid NOT NULL REFERENCES staff_principals(id),
  contact_id uuid NOT NULL REFERENCES contacts(id),
  expires_at timestamptz NOT NULL
);
ALTER TABLE card_transactions ADD CHECK (status IN ('pending','posted','reversed','refunded'));
ALTER TABLE card_transactions ADD CHECK (version > 0);
ALTER TABLE card_accounts ADD CHECK (version > 0);
ALTER TABLE customers ADD CHECK (data_origin = 'synthetic');
CREATE INDEX transactions_lookup ON card_transactions(account_id, occurred_at, id);
CREATE INDEX proof_by_contact ON verification_assertions(contact_id, verified_at DESC);
