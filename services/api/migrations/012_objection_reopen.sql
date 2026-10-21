-- ST-13: a closed case reopens only through a captured customer objection.
-- Closures stay append-only history; a later closure must cite a newer result.
ALTER TABLE case_closures DROP CONSTRAINT case_closures_case_id_key;
ALTER TABLE case_closures ADD UNIQUE (case_id, result_id);
CREATE TABLE case_reopenings (
 id uuid PRIMARY KEY, case_id uuid NOT NULL REFERENCES cases(id),
 closure_id uuid NOT NULL UNIQUE REFERENCES case_closures(id),
 objection_id uuid NOT NULL UNIQUE REFERENCES customer_objections(id),
 actor_id uuid NOT NULL REFERENCES staff_principals(id),
 reopened_at timestamptz NOT NULL
);
