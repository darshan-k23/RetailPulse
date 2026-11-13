{{ config(materialized='view') }}

/*
==============================================================================
Model: stg_orders.sql
Layer: Staging Layer (View)
Source: raw_retail.orders
Target: analytics_retail.stg_orders

Purpose:
  Cleans, casts, standardises, and validates raw transactional orders data
  ingested by Airbyte. Enforces deduplication and calculates line revenue.

Transformations Applied:
  1. CAST order_id to INT64.
  2. CAST order_date to DATE.
  3. Standardise product and region using TRIM().
  4. CAST quantity to INT64 and unit_price to NUMERIC.
  5. Compute revenue = ROUND(quantity * unit_price, 2).
  6. Deduplicate by order_id using ROW_NUMBER() window function.
  7. Filter invalid/corrupted records:
     - order_id IS NOT NULL (Primary key integrity)
     - quantity > 0 (Orders must contain at least 1 unit)
     - unit_price > 0 (List price must be positive)
==============================================================================
*/

WITH source_data AS (
    SELECT *
    FROM {{ source('raw_retail', 'orders') }}
),

standardized AS (
    SELECT
        CAST(order_id AS INT64) AS order_id,
        CAST(order_date AS DATE) AS order_date,
        TRIM(CAST(product AS STRING)) AS product,
        TRIM(CAST(region AS STRING)) AS region,
        CAST(quantity AS INT64) AS quantity,
        CAST(unit_price AS NUMERIC) AS unit_price,
        ROUND(CAST(quantity AS NUMERIC) * CAST(unit_price AS NUMERIC), 2) AS revenue,
        -- Window function to assign row numbers per order_id for deduplication
        ROW_NUMBER() OVER (
            PARTITION BY CAST(order_id AS INT64)
            ORDER BY CAST(order_date AS DATE) DESC
        ) AS dedup_rank
    FROM source_data
    -- Documented filtering rules: discard corrupt or unprocessable records
    WHERE order_id IS NOT NULL
      AND quantity > 0
      AND unit_price > 0
)

SELECT
    order_id,
    order_date,
    product,
    region,
    quantity,
    unit_price,
    revenue
FROM standardized
WHERE dedup_rank = 1

