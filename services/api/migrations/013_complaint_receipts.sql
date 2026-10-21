-- Append-only operational evidence; historical failures cannot be reconstructed.
CREATE TABLE complaint_delivery_receipts (
 id uuid PRIMARY KEY,
 intake_id uuid NOT NULL REFERENCES complaint_intakes(id),
 intake_version integer NOT NULL CHECK (intake_version > 0),
 outcome text NOT NULL CHECK (outcome IN ('acknowledged','delivery_failed')),
 reason text,
 external_receipt_ref text,
 recorded_at timestamptz NOT NULL,
 actor_id uuid NOT NULL REFERENCES staff_principals(id),
 operation_key text NOT NULL,
 UNIQUE (intake_id, intake_version),
 UNIQUE (actor_id, operation_key),
 CHECK ((outcome='delivery_failed' AND length(trim(reason)) > 0 AND reason IS NOT NULL
         AND external_receipt_ref IS NULL)
     OR (outcome='acknowledged' AND reason IS NULL AND external_receipt_ref IS NOT NULL
         AND external_receipt_ref ~ '^SYN-[A-Z0-9-]{4,40}$'))
);
