-- Explicit grains: dimensions have one business key; fact rows retain source lineage.
CREATE OR REPLACE TABLE dim_date AS
SELECT day::DATE AS date_key, year(day) AS calendar_year,
  month(day) AS month_number, date_trunc('month', day)::DATE AS month_start
FROM generate_series(DATE '2009-12-01', DATE '2011-11-30', INTERVAL '1 day') AS calendar(day);

CREATE OR REPLACE TABLE dim_country AS
SELECT DISTINCT country_name AS country_key, country_name AS country FROM analysis_lines;

CREATE OR REPLACE TABLE dim_customer AS
SELECT DISTINCT customer_key FROM analysis_lines WHERE customer_key IS NOT NULL;

CREATE OR REPLACE TABLE dim_product AS
WITH candidates AS (
  SELECT coalesce(nullif(upper(trim(stock_code)), ''), '__UNKNOWN_PRODUCT__') AS product_key,
    nullif(trim(description), '') AS product_label, record_class, occurred_at,
    source_sheet, try_cast(source_row AS BIGINT) AS source_row,
    row_number() OVER (
      PARTITION BY coalesce(nullif(upper(trim(stock_code)), ''), '__UNKNOWN_PRODUCT__')
      ORDER BY (record_class = 'sale' AND nullif(trim(description), '') IS NOT NULL) DESC,
        (nullif(trim(description), '') IS NOT NULL) DESC, occurred_at DESC,
        source_sheet DESC, try_cast(source_row AS BIGINT) DESC
    ) AS rank
  FROM analysis_lines
), variants AS (
  SELECT product_key, count(DISTINCT upper(product_label)) FILTER (WHERE record_class='sale')
    AS sale_description_variants FROM candidates GROUP BY 1
)
SELECT c.product_key, coalesce(c.product_label, c.product_key) AS product_label,
  v.sale_description_variants,
  CASE WHEN c.product_key IN ('POST', 'DOT', 'C2', 'S', 'TEST001', 'TEST002')
    OR starts_with(c.product_key, 'GIFT_0001_') THEN 'Service' ELSE 'Merchandise' END
    AS is_merchandise,
  CASE WHEN c.product_key IN ('POST', 'DOT', 'C2') THEN 'Delivery'
    WHEN starts_with(c.product_key, 'GIFT_0001_') THEN 'Gift voucher'
    WHEN c.product_key = 'S' THEN 'Sample'
    WHEN c.product_key IN ('TEST001', 'TEST002') THEN 'Test item'
    ELSE 'Merchandise' END AS product_scope
FROM candidates c JOIN variants v USING (product_key) WHERE c.rank=1;

-- Invoices are a separate grain. Conflicts are checked before this model is used.
CREATE OR REPLACE TABLE fact_invoice AS
SELECT invoice_key, min(occurred_at)::DATE AS occurred_date,
  min(country_name) AS country_key, max(customer_key) AS customer_key,
  count(DISTINCT customer_key) AS source_customer_count,
  count(DISTINCT occurred_at::DATE) AS source_date_count,
  count(DISTINCT country_name) AS source_country_count,
  count(*) AS invoice_lines, sum(recorded_value) AS recorded_value
FROM sales GROUP BY invoice_key;

CREATE OR REPLACE TABLE fact_invoice_line AS
SELECT concat(s.source_sheet, ':', s.source_row) AS line_key,
  s.source_sheet, s.source_row, s.invoice_key, s.occurred_at::DATE AS date_key,
  s.country_name AS country_key,
  coalesce(nullif(upper(trim(s.stock_code)), ''), '__UNKNOWN_PRODUCT__') AS product_key,
  s.customer_key AS source_customer_key,
  CASE WHEN s.record_class='sale' THEN i.customer_key ELSE s.customer_key END AS customer_key,
  s.description AS source_description, s.units, s.unit_price, s.recorded_value, s.record_class
FROM analysis_lines s LEFT JOIN fact_invoice i USING (invoice_key);

-- Resolve a partially missing ID on an otherwise unambiguous invoice once.
-- No unknown invoices are combined into an invented customer.
CREATE OR REPLACE TABLE customer_orders AS
SELECT customer_key, invoice_key, occurred_date AS order_date, recorded_value AS sales_value
FROM fact_invoice WHERE customer_key IS NOT NULL;
