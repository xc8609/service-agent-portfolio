-- Typed, snake_case staging view over the raw export.
-- Column names follow the CFPB bulk CSV header; verify with DESCRIBE raw_complaints after loading.

CREATE OR REPLACE VIEW stg_complaints AS
SELECT
    TRY_CAST("Complaint ID" AS BIGINT)               AS complaint_id,
    TRY_CAST("Date received" AS DATE)                AS date_received,
    TRY_CAST("Date sent to company" AS DATE)         AS date_sent_to_company,
    "Product"                                        AS product,
    "Sub-product"                                    AS sub_product,
    "Issue"                                          AS issue,
    "Sub-issue"                                      AS sub_issue,
    "Consumer complaint narrative"                   AS narrative,
    "Company public response"                        AS company_public_response,
    "Company"                                        AS company,
    "State"                                          AS state,
    "Submitted via"                                  AS submitted_via,
    "Company response to consumer"                   AS company_response,
    CASE "Timely response?" WHEN 'Yes' THEN TRUE
         WHEN 'No' THEN FALSE ELSE NULL END           AS is_timely,
    "Tags"                                           AS tags,
    LENGTH(TRIM(COALESCE("Consumer complaint narrative", ''))) > 0 AS has_narrative
FROM raw_complaints;

-- Sanity checks
SELECT
    count(*)                                   AS total,
    count(*) FILTER (WHERE has_narrative)      AS with_narrative,
    min(date_received)                         AS first_date,
    max(date_received)                         AS last_date
FROM stg_complaints;
