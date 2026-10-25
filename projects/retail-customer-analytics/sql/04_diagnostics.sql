CREATE OR REPLACE VIEW tableau_sales AS
SELECT f.invoice_key, f.date_key AS occurred_date, g.country, p.product_key,
  p.product_label, f.customer_key, coalesce(c.segment, 'Unidentified customer') AS segment,
  f.units, f.recorded_value, p.is_merchandise
FROM fact_invoice_line f
JOIN dim_date d ON f.date_key=d.date_key
JOIN dim_country g ON f.country_key=g.country_key
JOIN dim_product p ON f.product_key=p.product_key
LEFT JOIN customers c ON f.customer_key=c.customer_key
WHERE f.record_class='sale';

CREATE OR REPLACE VIEW tableau_customers AS
SELECT c.customer_key, c.segment, c.recency_days, c.orders_12m, c.sales_value_12m,
  c.orders_24m, date_trunc('month', c.first_observed_order)::DATE AS cohort_month,
  r.eligible::INTEGER AS eligible_90d, (r.eligible AND r.repeated)::INTEGER AS repeated_90d
FROM customers c JOIN repeat_90d r USING (customer_key);

CREATE OR REPLACE TABLE order_bridge AS
WITH counts AS (
  SELECT customer_key,
    count(*) FILTER (WHERE year(occurred_date)=2010) AS prior_orders,
    count(*) FILTER (WHERE year(occurred_date)=2011) AS current_orders
  FROM fact_invoice WHERE year(occurred_date) IN (2010,2011) AND month(occurred_date)<=11
  GROUP BY customer_key
), categorized AS (
  SELECT *, CASE WHEN customer_key IS NULL THEN 'Unidentified customer'
    WHEN prior_orders>0 AND current_orders>0 THEN 'Both periods'
    WHEN current_orders>0 THEN 'Current period only' ELSE 'Prior period only' END AS customer_group
  FROM counts
), categories AS (
  SELECT * FROM (VALUES (1, 'Both periods'), (2, 'Current period only'),
    (3, 'Prior period only'), (4, 'Unidentified customer')) AS x(sort_order, customer_group)
)
SELECT x.sort_order, x.customer_group,
  count(c.customer_key) AS identified_customers,
  coalesce(sum(c.prior_orders),0)::BIGINT AS prior_orders,
  coalesce(sum(c.current_orders),0)::BIGINT AS current_orders,
  (coalesce(sum(c.current_orders),0)-coalesce(sum(c.prior_orders),0))::BIGINT AS order_change
FROM categories x LEFT JOIN categorized c USING (customer_group)
GROUP BY x.sort_order,x.customer_group ORDER BY x.sort_order;

CREATE OR REPLACE TABLE product_changes AS
WITH totals AS (
  SELECT product_key, product_label,
    coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2010),0) AS prior_value,
    coalesce(sum(recorded_value) FILTER (WHERE year(occurred_date)=2011),0) AS current_value,
    count(DISTINCT invoice_key) FILTER (WHERE year(occurred_date)=2010) AS prior_orders,
    count(DISTINCT invoice_key) FILTER (WHERE year(occurred_date)=2011) AS current_orders
  FROM tableau_sales WHERE is_merchandise='Merchandise'
    AND year(occurred_date) IN (2010,2011) AND month(occurred_date)<=11 GROUP BY 1,2
), population AS (
  SELECT count(DISTINCT invoice_key) AS merchandise_orders FROM tableau_sales
  WHERE is_merchandise='Merchandise' AND year(occurred_date)=2011 AND month(occurred_date)<=11
)
SELECT t.product_key,t.product_label,t.prior_value,t.current_value,
  t.current_value-t.prior_value AS value_change,t.prior_orders,t.current_orders,
  t.current_orders::DOUBLE / nullif(p.merchandise_orders,0) AS current_penetration
FROM totals t CROSS JOIN population p ORDER BY value_change DESC,product_key;

CREATE OR REPLACE TABLE product_preferences AS
WITH values_by_product AS (
  SELECT segment, product_key, product_label, sum(recorded_value) AS sales_value_12m,
    count(DISTINCT customer_key) AS purchasing_customers,
    count(DISTINCT invoice_key) AS purchase_invoices
  FROM tableau_sales WHERE is_merchandise='Merchandise' AND customer_key IS NOT NULL
    AND occurred_date >= DATE '2010-12-01' GROUP BY 1,2,3
), ranked AS (
  SELECT *, sum(sales_value_12m) OVER (PARTITION BY segment) AS segment_merchandise_value,
    row_number() OVER (PARTITION BY segment ORDER BY sales_value_12m DESC,product_key) AS rank
  FROM values_by_product
)
SELECT *, sales_value_12m/nullif(segment_merchandise_value,0) AS segment_value_share
FROM ranked WHERE rank<=20 ORDER BY segment,rank;

CREATE OR REPLACE TABLE cohorts_by_segment AS
WITH membership AS (
  SELECT customer_key, segment, date_trunc('month',first_observed_order)::DATE AS cohort_month
  FROM customers
), sizes AS (
  SELECT cohort_month,segment,count(*) AS cohort_customers FROM membership GROUP BY 1,2
), activity AS (
  SELECT m.cohort_month,m.segment,date_diff('month',m.cohort_month,o.order_date) AS month_index,
    count(DISTINCT o.customer_key) AS active_customers
  FROM customer_orders o JOIN membership m USING (customer_key) GROUP BY 1,2,3
), matured AS (
  SELECT s.cohort_month,r.range AS month_index,s.segment,s.cohort_customers,
    CASE WHEN s.cohort_month+r.range*INTERVAL '1 month'<DATE '2011-12-01'
      THEN coalesce(a.active_customers,0) END AS active_customers
  FROM sizes s CROSS JOIN range(12) r
  LEFT JOIN activity a ON s.cohort_month=a.cohort_month AND s.segment=a.segment
    AND r.range=a.month_index
)
SELECT *,active_customers::DOUBLE/cohort_customers AS repeat_rate
FROM matured ORDER BY cohort_month,month_index,segment;
