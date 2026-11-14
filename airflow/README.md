# RetailPulse: Apache Airflow Orchestration Engine
### Member 2 — Orchestration & Workflow Scheduling

This module houses the Apache Airflow DAG (`retail_sales_pipeline`), Docker Compose environment, and execution configurations for RetailPulse.

---

## 1. DAG Architecture & Dependency Graph

The DAG implements the exact task chain mandated by the department guidelines:

```
           +-----------------------------+
           |            start            |
           +-----------------------------+
                          │
                          ▼
           +-----------------------------+
           |   check_airbyte_sync_mode   | (BranchPythonOperator)
           +-----------------------------+
                 │                      │
   (Automated)   │                      │ (Simplified / Manual)
                 ▼                      ▼
  +----------------------+    +--------------------------+
  | trigger_airbyte_sync |    | manual_ingestion_notice  |
  +----------------------+    +--------------------------+
                 │                      │
                 ▼                      │
  +----------------------+              │
  | wait_for_sync_success|              │
  +----------------------+              │
                 │                      │
                 └──────────┬───────────┘
                            ▼
           +-----------------------------+
           |   validate_raw_ingestion    | (BigQuery check: orders_raw count)
           +-----------------------------+
                          │
                          ▼
           +-----------------------------+
           |           dbt_run           | (BashOperator: staging + marts)
           +-----------------------------+
                          │
                          ▼
           +-----------------------------+
           |          dbt_test           | (BashOperator: 32 data tests)
           +-----------------------------+
                          │
                          ▼
           +-----------------------------+
           |  validate_bigquery_output   | (Checksum & mart parity checks)
           +-----------------------------+
                          │
                          ▼
           +-----------------------------+
           |             end             |
           +-----------------------------+
```

---

## 2. Quickstart: Running Airflow via Docker Compose

### Prerequisites
- Docker Desktop installed and running
- `.env` configured at the project root with `GCP_PROJECT_ID` and GCP service account key in `keys/gcp_service_account.json`

### Commands (Windows PowerShell or Linux):
```powershell
# Navigate to airflow directory
cd airflow

# Start Airflow containers (Webserver, Scheduler, Postgres metadata DB)
docker compose up -d --build

# Inspect running containers
docker compose ps
```

### Accessing the Web UI:
- **URL:** [http://localhost:8080](http://localhost:8080)
- **Username:** `admin`
- **Password:** `admin`

---

## 3. Supported Modes of Operation

1. **Fully Automated Ingestion Mode:**
   - Set `AIRBYTE_CONNECTION_ID` in `.env`.
   - The DAG triggers `POST /api/v1/connections/sync` on `AIRBYTE_HOST:8000` and monitors execution until status equals `SUCCEEDED`.
2. **Acceptable Simplified Mode (Department Approved Fallback):**
   - If `AIRBYTE_CONNECTION_ID` is blank or Airbyte API is offline, the DAG branches to `manual_ingestion_notice`.
   - Ingestion is triggered once in the Airbyte UI, and Airflow immediately takes over to validate BigQuery raw tables, run dbt models, run dbt tests, and audit the output marts.

---

## 4. Teardown & Maintenance
```powershell
# Stop Airflow services
docker compose down

# Stop and wipe metadata volumes
docker compose down -v
```
