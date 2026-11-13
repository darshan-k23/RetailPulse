# Airbyte Ingestion Directory

This folder documents the Airbyte pipeline syncing retail transactions from PostgreSQL to Google BigQuery.

## Pipeline Flow:
```
PostgreSQL (Source: retail_source.public.orders)
                      │
                      ▼
             Airbyte ELT Pipeline
  (CDC / Incremental Sync or Full Refresh Sync)
                      │
                      ▼
Google BigQuery (Destination: raw_retail.orders)
```

## Folder Contents:
- `configs/`: Contains exported connection configuration templates, source/destination definitions, and schema normalization mappings.
- `README.md`: Step-by-step setup guide for configuring the Airbyte connector via UI or Docker Compose.

