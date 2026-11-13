{{ config(materialized='table') }}

/*
==============================================================================
Model: monthly_sales.sql
Layer: Marts / Analytical Layer (Table)
Source: ref('stg_orders')
Target: analytics_retail.monthly_sales

Purpose:
  Computes month-by-month sales performance trends across the 12-month period.
  Truncates order dates to the first day of each month.

Output Metrics:
  - month_start: The first calendar day of the sales month (e.g., 2025-11-01)
  - total_orders: Total unique orders placed in the month
  - total_quantity: Total volume of units sold in the month
  - total_revenue: Total monthly gross sales in INR
==============================================================================
*/

WITH staging_orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
)

SELECT
    DATE_TRUNC(order_date, MONTH) AS month_start,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM staging_orders
GROUP BY
    month_start
ORDER BY
    month_start ASC

