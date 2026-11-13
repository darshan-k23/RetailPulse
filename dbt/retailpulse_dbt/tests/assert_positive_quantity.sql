-- ==============================================================================
-- Singular Data Test: assert_positive_quantity.sql
-- Fails if any order in staging has a non-positive quantity (quantity <= 0)
-- ==============================================================================

SELECT
    order_id,
    quantity
FROM
    {{ ref('stg_orders') }}
WHERE
    quantity <= 0

