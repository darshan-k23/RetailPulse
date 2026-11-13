{{ config(materialized='table') }}

/*
==============================================================================
Model: sales_by_product.sql
Layer: Marts / Analytical Layer (Table)
Source: ref('stg_orders')
Target: analytics_retail.sales_by_product

Purpose:
  Aggregates transactional performance metrics by product to determine
  product popularity, unit volume, and gross sales revenue.

Output Metrics:
  - product: Product catalog name
  - total_orders: Count of distinct transactions containing the product
  - total_quantity: Cumulative units purchased
  - total_revenue: Total revenue generated in INR
==============================================================================
*/

WITH staging_orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
)

SELECT
    product,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM staging_orders
GROUP BY
    product
ORDER BY
    total_revenue DESC

