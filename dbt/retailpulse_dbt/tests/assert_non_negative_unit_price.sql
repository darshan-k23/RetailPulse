-- ==============================================================================
-- Singular Data Test: assert_non_negative_unit_price.sql
-- Fails if any order in staging has a negative unit price (unit_price < 0)
-- ==============================================================================

SELECT
    order_id,
    unit_price
FROM
    {{ ref('stg_orders') }}
WHERE
    unit_price < 0

