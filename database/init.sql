-- ==============================================================================
-- RetailPulse - PostgreSQL Database Initialization Script
-- File: database/init.sql
--
-- Target Contract:
--   Database: retail_source
--   Schema:   public
--   Table:    orders
-- ==============================================================================

-- 1. Ensure schema exists
CREATE SCHEMA IF NOT EXISTS public;

-- 2. Create orders table with explicit constraints matching data contract
CREATE TABLE IF NOT EXISTS public.orders (
    order_id    INTEGER PRIMARY KEY,
    order_date  DATE NOT NULL,
    product     VARCHAR(100) NOT NULL,
    region      VARCHAR(50) NOT NULL,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(12, 2) NOT NULL CHECK (unit_price > 0)
);

-- 3. Create index on order_date to optimize range queries and Airbyte incremental syncs
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);

-- 4. Create index on product & region for downstream OLTP query performance
CREATE INDEX IF NOT EXISTS idx_orders_product ON public.orders(product);
CREATE INDEX IF NOT EXISTS idx_orders_region ON public.orders(region);

