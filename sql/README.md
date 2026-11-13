# SQL Directory

This folder holds DDL (Data Definition Language) and DML (Data Manipulation Language) scripts for the source and destination databases.

## Subdirectories:
- `postgres/`:
  - `01_create_database.sql`: Commands to create `retail_source`.
  - `02_create_orders_table.sql`: DDL for `public.orders`.
  - `03_load_seed_data.sql`: Scripts to populate `orders` from CSV.
- `bigquery/`:
  - `01_create_datasets.sql`: DDL to create `raw_retail` and `analytics_retail` datasets.
  - `02_inspect_raw_orders.sql`: Sanity check queries for ingested data.

