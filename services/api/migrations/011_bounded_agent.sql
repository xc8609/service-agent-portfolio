ALTER TABLE agent_runs ADD COLUMN actor_id uuid REFERENCES staff_principals(id);
ALTER TABLE agent_runs ADD COLUMN request_hash text;
ALTER TABLE agent_runs ADD COLUMN evidence_hash text;
ALTER TABLE agent_runs ADD COLUMN output jsonb;
ALTER TABLE agent_runs ADD COLUMN error_code text;
ALTER TABLE agent_runs ADD COLUMN usage jsonb;
ALTER TABLE agent_runs ADD COLUMN cancelled boolean NOT NULL DEFAULT false;
ALTER TABLE agent_runs ADD COLUMN lease_until timestamptz;
