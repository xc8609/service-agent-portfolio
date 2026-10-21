-- Unknown jurisdiction is deliberately not inferred from currency or location.
ALTER TABLE card_accounts ADD COLUMN jurisdiction text;
ALTER TABLE policy_versions ADD COLUMN published boolean NOT NULL DEFAULT false;
CREATE TABLE policy_sections (
  policy_version_id uuid NOT NULL REFERENCES policy_versions(id),
  section text NOT NULL,
  title text NOT NULL,
  decision_key text NOT NULL,
  transaction_pattern text NOT NULL CHECK (transaction_pattern IN ('two_posted','pending_posted')),
  conditions text[] NOT NULL,
  next_steps text[] NOT NULL,
  PRIMARY KEY (policy_version_id, section)
);
CREATE INDEX policy_applicability ON policy_versions (product,jurisdiction,audience,effective_from);
