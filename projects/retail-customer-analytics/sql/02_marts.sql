CREATE OR REPLACE TABLE monthly AS
SELECT date_trunc('month', occurred_at)::DATE AS month,
  sum(CASE WHEN record_class = 'sale' THEN recorded_value ELSE 0 END) AS sales_value,
  count(DISTINCT CASE WHEN record_class = 'sale' THEN invoice_key END) AS sales_orders,
  sum(CASE WHEN record_class = 'cancellation' THEN -recorded_value ELSE 0 END) AS cancellation_value,
  count(DISTINCT CASE WHEN record_class = 'cancellation' THEN invoice_key END) AS cancellation_documents,
  sum(CASE WHEN record_class = 'sale' AND customer_key IS NOT NULL THEN recorded_value ELSE 0 END) AS known_sales_value,
  count(DISTINCT CASE WHEN record_class = 'sale' AND customer_key IS NOT NULL THEN invoice_key END) AS known_sales_orders
FROM analysis_lines GROUP BY 1 ORDER BY 1;

CREATE OR REPLACE TABLE countries AS
SELECT country_name AS country,
  sum(CASE WHEN record_class = 'sale' THEN recorded_value ELSE 0 END) AS sales_value,
  count(DISTINCT CASE WHEN record_class = 'sale' THEN invoice_key END) AS sales_orders,
  sum(CASE WHEN record_class = 'cancellation' THEN -recorded_value ELSE 0 END) AS cancellation_value
FROM analysis_lines GROUP BY 1 ORDER BY sales_value DESC, country;

CREATE OR REPLACE TABLE customers AS
SELECT customer_key, min(order_date) AS first_observed_order,
  max(order_date) AS last_observed_order,
  date_diff('day', max(order_date), DATE '2011-12-01') AS recency_days,
  count(*) AS orders_24m,
  count(*) FILTER (WHERE order_date >= DATE '2010-12-01') AS orders_12m,
  coalesce(sum(sales_value) FILTER (WHERE order_date >= DATE '2010-12-01'), 0) AS sales_value_12m,
  CASE
    WHEN recency_days <= 90 AND orders_12m >= 2 THEN 'Active repeat'
    WHEN recency_days <= 90 THEN 'Recent single-order'
    WHEN orders_12m >= 2 THEN 'Lapsed repeat'
    WHEN orders_12m = 1 THEN 'Lapsed single-order'
    ELSE 'No orders in last 12 months'
  END AS segment
FROM customer_orders GROUP BY customer_key;

CREATE OR REPLACE TABLE segments AS
SELECT segment, count(*) AS customers, sum(sales_value_12m) AS sales_value_12m,
  sum(orders_12m) AS orders_12m, median(recency_days) AS median_recency_days
FROM customers GROUP BY segment ORDER BY sales_value_12m DESC, segment;

CREATE OR REPLACE TABLE cohorts AS
WITH membership AS (
  SELECT customer_key, date_trunc('month', first_observed_order)::DATE AS cohort_month FROM customers
), sizes AS (
  SELECT cohort_month, count(*) AS cohort_customers FROM membership GROUP BY 1
), activity AS (
  SELECT m.cohort_month,
    date_diff('month', m.cohort_month, o.order_date) AS month_index,
    count(DISTINCT o.customer_key) AS active_customers
  FROM customer_orders o JOIN membership m USING (customer_key) GROUP BY 1,2
), matured AS (
SELECT s.cohort_month, r.range AS month_index, s.cohort_customers,
  CASE WHEN s.cohort_month + r.range * INTERVAL '1 month' < DATE '2011-12-01'
    THEN coalesce(a.active_customers, 0) END AS active_customers
FROM sizes s CROSS JOIN range(12) r
LEFT JOIN activity a ON s.cohort_month = a.cohort_month AND r.range = a.month_index
)
SELECT *, active_customers::DOUBLE / cohort_customers AS repeat_rate FROM matured
ORDER BY 1,2;

CREATE OR REPLACE TABLE repeat_90d AS
WITH sequenced AS (
  SELECT *, row_number() OVER (PARTITION BY customer_key ORDER BY order_date, invoice_key) AS n
  FROM customer_orders
), dates AS (
  SELECT customer_key, min(order_date) AS first_order,
    min(order_date) FILTER (WHERE n = 2) AS second_order
  FROM sequenced GROUP BY customer_key
)
SELECT *, first_order + INTERVAL '90 days' < DATE '2011-12-01' AS eligible,
  second_order IS NOT NULL AND date_diff('day', first_order, second_order) <= 90 AS repeated
FROM dates;
