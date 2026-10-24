-- Every source row stays present, including exact repeats; no unique source line ID exists.
CREATE OR REPLACE TABLE staged AS
WITH typed AS (
  SELECT *, upper(trim(invoice)) AS invoice_key,
    try_cast(quantity AS DECIMAL(18,4)) AS units,
    try_cast(price AS DECIMAL(18,4)) AS unit_price,
    try_cast(invoice_date AS TIMESTAMP) AS occurred_at,
    CASE WHEN regexp_full_match(trim(customer_id), '[0-9]+(\.0)?')
      THEN cast(try_cast(customer_id AS BIGINT) AS VARCHAR) END AS customer_key,
    coalesce(nullif(trim(country), ''), 'Unknown') AS country_name
  FROM raw_lines
)
SELECT *, units * unit_price AS recorded_value,
  NOT (source_sheet = 'Year 2009-2010' AND occurred_at >= DATE '2010-12-01') AS source_selected,
  CASE
    WHEN occurred_at IS NULL OR nullif(invoice_key, '') IS NULL
      OR units IS NULL OR unit_price IS NULL THEN 'invalid_required_field'
    WHEN starts_with(invoice_key, 'A') OR upper(trim(stock_code)) IN
      ('B', 'M', 'ADJUST', 'ADJUST2', 'BANK CHARGES', 'AMAZONFEE', 'D', 'CRUK')
      THEN 'manual_or_accounting_entry'
    WHEN unit_price <= 0 OR units = 0 THEN 'zero_or_negative_price_or_zero_quantity'
    WHEN starts_with(invoice_key, 'C') AND units < 0 THEN 'cancellation'
    WHEN NOT starts_with(invoice_key, 'C') AND units > 0 THEN 'sale'
    ELSE 'sign_or_cancellation_conflict'
  END AS record_class
FROM typed;

CREATE OR REPLACE VIEW analysis_lines AS
SELECT * FROM staged
WHERE source_selected AND occurred_at >= TIMESTAMP '2009-12-01' AND occurred_at < TIMESTAMP '2011-12-01';

CREATE OR REPLACE VIEW sales AS SELECT * FROM analysis_lines WHERE record_class = 'sale';
CREATE OR REPLACE VIEW cancellations AS SELECT * FROM analysis_lines WHERE record_class = 'cancellation';

-- One invoice can contain multiple products; frequency counts invoices, not lines.
CREATE OR REPLACE TABLE customer_orders AS
SELECT customer_key, invoice_key, min(occurred_at)::DATE AS order_date,
  sum(recorded_value) AS sales_value
FROM sales WHERE customer_key IS NOT NULL
GROUP BY customer_key, invoice_key;
