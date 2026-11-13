-- ==============================================================================
-- RetailPulse: BigQuery Verification & Pipeline Validation Queries
-- File: sql/verify_bigquery.sql
--
-- Instructions:
--   Run these queries in BigQuery Studio to audit datasets, raw ingestion,
--   dbt transformations, and perform financial reconciliation.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DATASET EXISTENCE VERIFICATION
-- Checks that both raw_retail and analytics_retail exist in the project
-- ------------------------------------------------------------------------------
SELECT
    schema_name AS dataset_name,
    location,
    creation_time,
    last_modified_time
FROM
    `INFORMATION_SCHEMA.SCHEMATA`
WHERE
    schema_name IN ('raw_retail', 'analytics_retail')
ORDER BY
    schema_name;


-- ------------------------------------------------------------------------------
-- 2. RAW DATA INGESTION VERIFICATION (Post-Airbyte Sync)
-- Checks that orders were ingested from PostgreSQL into raw_retail.orders
-- ------------------------------------------------------------------------------

-- 2a. Confirm total row count and uniqueness (Expected: 500 records)
SELECT
    COUNT(*) AS total_raw_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_records
FROM
    `raw_retail.orders`;

-- 2b. Check for null values in critical columns
SELECT
    COUNTIF(order_id IS NULL) AS null_order_ids,
    COUNTIF(order_date IS NULL) AS null_order_dates,
    COUNTIF(product IS NULL) AS null_products,
    COUNTIF(region IS NULL) AS null_regions,
    COUNTIF(quantity IS NULL) AS null_quantities,
    COUNTIF(unit_price IS NULL) AS null_unit_prices
FROM
    `raw_retail.orders`;

-- 2c. Preview first 10 raw records
SELECT
    order_id,
    order_date,
    product,
    region,
    quantity,
    unit_price,
    _airbyte_raw_id,
    _airbyte_extracted_at
FROM
    `raw_retail.orders`
ORDER BY
    order_id ASC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- 3. ANALYTICS MART VERIFICATION (Post-dbt Transformation)
-- Run these checks after 'dbt run' or 'dbt build'
-- ------------------------------------------------------------------------------

-- 3a. Verify Staging Model: analytics_retail.stg_orders
SELECT
    COUNT(*) AS staging_row_count,
    COUNT(DISTINCT order_id) AS staging_unique_orders,
    ROUND(SUM(revenue), 2) AS staging_total_revenue
FROM
    `analytics_retail.stg_orders`;

-- 3b. Verify Mart 1: analytics_retail.sales_by_product
SELECT
    product,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.sales_by_product`
ORDER BY
    total_revenue DESC;

-- 3c. Verify Mart 2: analytics_retail.sales_by_region
SELECT
    region,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.sales_by_region`
ORDER BY
    total_revenue DESC;

-- 3d. Verify Mart 3: analytics_retail.monthly_sales
SELECT
    month_start,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.monthly_sales`
ORDER BY
    month_start ASC;


-- ------------------------------------------------------------------------------
-- 4. FINANCIAL & RECONCILIATION AUDIT (Cross-Mart Checksum)
-- Asserts that total revenue matches across all layers: Expected = 17,379,476.00 INR
-- ------------------------------------------------------------------------------
WITH raw_calc AS (
    SELECT ROUND(SUM(CAST(quantity AS NUMERIC) * CAST(unit_price AS NUMERIC)), 2) AS raw_revenue
    FROM `raw_retail.orders`
),

staging_calc AS (
    SELECT ROUND(SUM(revenue), 2) AS staging_revenue
    FROM `analytics_retail.stg_orders`
),

product_calc AS (
    SELECT ROUND(SUM(total_revenue), 2) AS product_mart_revenue
    FROM `analytics_retail.sales_by_product`
),

region_calc AS (
    SELECT ROUND(SUM(total_revenue), 2) AS region_mart_revenue
    FROM `analytics_retail.sales_by_region`
),

monthly_calc AS (
    SELECT ROUND(SUM(total_revenue), 2) AS monthly_mart_revenue
    FROM `analytics_retail.monthly_sales`
)

SELECT
    raw_calc.raw_revenue,
    staging_calc.staging_revenue,
    product_calc.product_mart_revenue,
    region_calc.region_mart_revenue,
    monthly_calc.monthly_mart_revenue,
    -- Discrepancy checks (must all be 0.00)
    staging_calc.staging_revenue - raw_calc.raw_revenue AS staging_discrepancy,
    product_calc.product_mart_revenue - raw_calc.raw_revenue AS product_discrepancy,
    region_calc.region_mart_revenue - raw_calc.raw_revenue AS region_discrepancy,
    monthly_calc.monthly_mart_revenue - raw_calc.raw_revenue AS monthly_discrepancy
FROM
    raw_calc
CROSS JOIN staging_calc
CROSS JOIN product_calc
CROSS JOIN region_calc
CROSS JOIN monthly_calc;
