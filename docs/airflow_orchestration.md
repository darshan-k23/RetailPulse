# RetailPulse: Airflow Orchestration Deep-Dive
### Member 2 — Orchestration & BI Lead Guide

This document details the architecture, configuration, operator dependency chain, and troubleshooting steps for the Apache Airflow orchestration layer in RetailPulse.

---

## 1. Pipeline Overview

- **DAG Identifier:** `retail_sales_pipeline`
- **Schedule Interval:** `@daily` (or on-demand manual trigger)
- **Catchup:** `False`
- **DAG Source File:** `airflow/dags/retail_sales_pipeline.py`
- **Runtime Environment:** Docker Compose (`airflow/docker-compose.yaml`) or Local Virtual Environment

---

## 2. Airflow Task Dependency Flow

```
                      +-----------------------------+
                      |            start            |
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |   check_airbyte_sync_mode   | (BranchPythonOperator)
                      +-----------------------------+
                             /               \
              (Automated)   /                 \  (Simplified / Manual Mode)
                           ▼                   ▼
            +----------------------+     +--------------------------+
            | trigger_airbyte_sync |     | manual_ingestion_notice  |
            +----------------------+     +--------------------------+
                           │                           │
                           ▼                           │
            +----------------------+                   │
            | wait_for_sync_success|                   │
            +----------------------+                   │
                           \                           /
                            \                         /
                             ▼                       ▼
                      +-----------------------------+
                      |   validate_raw_ingestion    | (Asserts orders in raw_retail)
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |           dbt_run           | (Executes stg + 3 marts)
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |          dbt_test           | (Executes 32 data tests)
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |  validate_bigquery_output   | (Checksum & mart verification)
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |             end             |
                      +-----------------------------+
```

---

## 3. Operator Specifications & Implementation

### Task 1: `start`
- **Operator:** `EmptyOperator` (or `DummyOperator` fallback)
- **Purpose:** Acts as pipeline entry anchor and execution timestamp marker.

### Task 2: `check_airbyte_sync_mode`
- **Operator:** `BranchPythonOperator`
- **Purpose:** Inspects environment variable `AIRBYTE_CONNECTION_ID`.
  - If a valid UUID exists: routes execution to `trigger_airbyte_sync`.
  - If unset or placeholder: routes to `manual_ingestion_notice` (implementing the department-approved Simplified Mode).

### Task 3a: `trigger_airbyte_sync` & `wait_for_sync_success`
- **Operator:** `PythonOperator` / REST API Hook
- **Purpose:** Dispatches `POST /api/v1/connections/sync` to the Airbyte service (`http://localhost:8000` or `http://host.docker.internal:8000`), monitors the job polling endpoint `/api/v1/jobs/get` until reaching `SUCCEEDED` status.

### Task 3b: `manual_ingestion_notice`
- **Operator:** `PythonOperator`
- **Purpose:** Logs formal notification of manual sync execution in the Airbyte Web UI as permitted by Experiment 9 guidelines.

### Task 4: `validate_raw_ingestion`
- **Operator:** `PythonOperator` (`trigger_rule="none_failed_min_one_success"`)
- **Purpose:** Validates that BigQuery table `raw_retail.orders` exists and contains at least one record (expected: 500 records). Prevents running dbt transformations on empty or un-replicated datasets.

### Task 5: `dbt_run`
- **Operator:** `BashOperator`
- **Command:** `dbt run --project-dir <DBT_PROJECT_DIR> --profiles-dir <DBT_PROFILES_DIR>`
- **Purpose:** Builds the staging view `stg_orders` and materializes analytical tables `sales_by_product`, `sales_by_region`, and `monthly_sales` in the `analytics_retail` BigQuery dataset.

### Task 6: `dbt_test`
- **Operator:** `BashOperator`
- **Command:** `dbt test --project-dir <DBT_PROJECT_DIR> --profiles-dir <DBT_PROFILES_DIR>`
- **Purpose:** Executes the complete test suite (32 tests across staging and marts). If any test fails, Airflow immediately halts the pipeline and alerts the team before erroneous data reaches the BI layer.

### Task 7: `validate_bigquery_output`
- **Operator:** `PythonOperator`
- **Purpose:** Reconciles the output tables in `analytics_retail`. Asserts:
  1. `sales_by_product` contains 7 distinct catalog products.
  2. `sales_by_region` covers all 5 territories (South, West, North, East, Central).
  3. `monthly_sales` spans 12 continuous months.
  4. Cross-mart financial checksum: `SUM(monthly_sales.total_revenue) == SUM(sales_by_product.total_revenue) == ₹17,379,476.00 INR`.

### Task 8: `end`
- **Operator:** `EmptyOperator`
- **Purpose:** Terminal pipeline state confirming complete end-to-end data freshness.

---

## 4. How to Run & Verify Airflow

### Starting Airflow via Docker Compose:
```powershell
cd airflow
docker compose up -d --build
```

### Accessing Airflow UI:
- Open browser at `http://localhost:8080`
- Log in with `admin` / `admin`
- Unpause `retail_sales_pipeline` and click the **Trigger DAG** button
- Open the **Graph View** or **Grid View** to observe real-time task progression.
