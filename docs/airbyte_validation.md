# RetailPulse: Airbyte Synchronization Validation & Member 2 Handoff

This document details the post-sync data verification procedures in Google BigQuery and provides the formal integration contract for **Member 2** (Airflow Orchestration).

---

## PART E — BigQuery Data Ingestion Verification

After Airbyte finishes the sync with status **Succeeded**, execute these verification steps in BigQuery Studio to confirm ingestion integrity.

### 1. Verification SQL Queries

Run the following queries in BigQuery Studio (from [verify_bigquery.sql](file:///c:/Users/Swapnaja/OneDrive/Desktop/RetailPulse/sql/verify_bigquery.sql)):

#### Check 1: Record Count Audit (Must equal exactly 500)
```sql
SELECT
    COUNT(*) AS total_raw_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_records
FROM
    `raw_retail.orders`;
```
**Expected Output:**
- `total_raw_records`: **500**
- `unique_orders`: **500**
- `duplicate_records`: **0**

---

#### Check 2: Null Value Audit
```sql
SELECT
    COUNTIF(order_id IS NULL) AS null_order_ids,
    COUNTIF(order_date IS NULL) AS null_order_dates,
    COUNTIF(product IS NULL) AS null_products,
    COUNTIF(region IS NULL) AS null_regions,
    COUNTIF(quantity IS NULL) AS null_quantities,
    COUNTIF(unit_price IS NULL) AS null_unit_prices
FROM
    `raw_retail.orders`;
```
**Expected Output:** All null counts must be **0**.

---

#### Check 3: Schema & Airbyte Metadata Columns
Airbyte automatically enriches ingested tables with internal lineage metadata:
```sql
SELECT
    order_id,
    order_date,
    product,
    region,
    quantity,
    unit_price,
    _airbyte_raw_id,
    _airbyte_extracted_at
FROM
    `raw_retail.orders`
ORDER BY
    order_id ASC
LIMIT 5;
```

| Column | Type | Origin | Purpose in Viva |
| :--- | :--- | :--- | :--- |
| `order_id` | INT64 | PostgreSQL | Primary transaction identifier |
| `order_date` | DATE / STRING | PostgreSQL | Transaction timestamp |
| `product` | STRING | PostgreSQL | Product name |
| `region` | STRING | PostgreSQL | Geographic sales territory |
| `quantity` | INT64 | PostgreSQL | Units sold |
| `unit_price` | NUMERIC / FLOAT | PostgreSQL | Price per unit (INR) |
| `_airbyte_raw_id` | STRING | Airbyte | Unique UUID assigned to the ingestion event |
| `_airbyte_extracted_at`| TIMESTAMP | Airbyte | Exact timestamp when Airbyte read the record from PostgreSQL |

---

## PART F — Member 2 Handoff (Airflow Orchestration Contract)

This section contains all non-secret integration metadata for **Member 2** to integrate the Airbyte sync into the scheduled Apache Airflow DAG.

### 1. Connection Metadata Checklist

Fill in these identifiers from your Airbyte web console:

| Parameter | Member 1 Value | Where to Find in Airbyte UI |
| :--- | :--- | :--- |
| **Airbyte Host URL** | `http://localhost:8000` | Local Airbyte web service |
| **Source Name** | `Postgres_RetailSource` | Sources tab |
| **Destination Name** | `BigQuery_RawRetail` | Destinations tab |
| **Connection Name** | `Postgres_to_BigQuery_Orders` | Connections tab |
| **Connection ID (UUID)**| `<YOUR_CONNECTION_UUID>` | Inspect browser URL on the Connection page: `http://localhost:8000/workspaces/.../connections/<UUID>` |
| **Target Stream** | `orders` | Table selected in connection |
| **Sync Mode** | `Full Refresh \| Overwrite` | Connection configuration |
| **Target BigQuery Table** | `raw_retail.orders` | BigQuery destination |

---

### 2. Airflow Provider Integration Guide (For Member 2)

Member 2 will use the official Airbyte provider package:
```bash
pip install apache-airflow-providers-airbyte
```

#### Airflow Connection Setup (`Admin` &rarr; `Connections`):
- **Conn Id:** `airbyte_default`
- **Conn Type:** `Airbyte`
- **Host:** `localhost` (or `host.docker.internal` if Airflow runs in Docker)
- **Port:** `8000`
- **Login:** `admin` (or configured Airbyte username)
- **Password:** `<Airbyte-Admin-Password>`

#### DAG Implementation Pattern:
```python
from airflow import DAG
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "member_2",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="retailpulse_pipeline_dag",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    # Trigger Airbyte ingestion from PostgreSQL to BigQuery
    sync_postgres_to_bigquery = AirbyteTriggerSyncOperator(
        task_id="sync_postgres_to_bigquery",
        airbyte_conn_id="airbyte_default",
        connection_id="<YOUR_CONNECTION_UUID>",  # Member 1 provides this UUID
        asynchronous=False,                     # Waits for sync completion before proceeding to dbt
        timeout=3600,
    )
```

---

### 3. API & Security Guidelines

- **Supported Airbyte API Version:** Airbyte v1 API.
- **Trigger Endpoint:** `POST /api/v1/connections/sync` with payload `{"connectionId": "<YOUR_CONNECTION_UUID>"}`.
- **Security Rule:** Never commit the Airbyte admin password, API keys, or connection tokens to the GitHub repository. Airflow should manage credentials strictly inside Airflow Connections or environment variables.

