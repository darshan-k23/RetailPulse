# retailpulse_dbt: dbt Core Project

This directory contains the dbt Core data transformation project for **RetailPulse**.

## Architecture & Layers

```
Raw Ingested Data              Staging Layer                     Analytics Marts
(BigQuery)                     (Views)                           (Tables)

raw_retail.orders  ──>  models/staging/stg_orders.sql  ──>  models/marts/sales_by_product.sql
                                                       ──>  models/marts/sales_by_region.sql
                                                       ──>  models/marts/monthly_sales.sql
```

## Directory Structure
- `dbt_project.yml`: Core dbt configuration and materialization rules.
- `models/sources.yml`: Declares upstream raw BigQuery sources ingested by Airbyte.
- `models/staging/`: Initial cleaning, typing, and standardizing layer (`stg_orders.sql`).
- `models/marts/`: Business-level aggregations (`sales_by_product`, `sales_by_region`, `monthly_sales`).

## Running dbt Commands
All commands should be executed from this folder (`dbt/retailpulse_dbt/`):

```powershell
# Check configuration and BigQuery connection
dbt debug

# Compile SQL models and verify Jinja syntax
dbt compile

# Run all transformations
dbt run

# Run schema and data quality tests
dbt test

# Generate and view interactive documentation
dbt docs generate
dbt docs serve
```
