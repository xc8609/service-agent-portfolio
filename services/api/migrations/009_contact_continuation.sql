-- Synthetic operational controls; immutable attempt/decision history.
CREATE TABLE callback_anomalies (
 id uuid PRIMARY KEY, attempt_id uuid NOT NULL REFERENCES callback_attempts(id),
 reasons jsonb NOT NULL, recorded_at timestamptz NOT NULL
);
CREATE TABLE case_closures (
 id uuid PRIMARY KEY, case_id uuid NOT NULL UNIQUE REFERENCES cases(id),
 result_id uuid NOT NULL REFERENCES investigation_results(id),
 attempt_id uuid NOT NULL REFERENCES callback_attempts(id),
 actor_id uuid NOT NULL REFERENCES staff_principals(id), reason text NOT NULL,
 closed_at timestamptz NOT NULL, operation_id uuid NOT NULL REFERENCES operations(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX one_reserved_date ON contact_reservations(case_id,service_date) WHERE state='reserved';
