# RetailPulse: Member 2 Technical Handover Document
### Data Engineering Pipeline Handoff for Airflow Orchestration & Streamlit Conversational BI

**Prepared by:** Member 1 (Data Engineering & Warehousing)  
**Target Recipient:** Member 2 (Airflow Orchestration & Streamlit BI Interface)  
**Project:** RetailPulse: Automated Retail Sales Analytics & Conversational BI Pipeline  
**Pipeline Flow:** `CSV -> PostgreSQL -> Airbyte -> Google BigQuery -> dbt Core`

---

## 1. Project & Cloud Warehouse Configuration

| Configuration Parameter | Value / Variable Reference | Notes |
| :--- | :--- | :--- |
| **GCP Project ID** | `{{ env_var('GCP_PROJECT_ID') }}` | Configured in root `.env` |
| **BigQuery Location / Region** | `US` (or region defined in `.env`) | Both raw and analytics datasets share this location |
| **Raw Warehouse Dataset** | `raw_retail` | Ingested directly from PostgreSQL via Airbyte |
| **Analytics Warehouse Dataset**| `analytics_retail` | Transformed data marts created by dbt Core |
| **GCP Credentials Path** | `keys/gcp_service_account.json` | Local service account JSON key (gitignored) |

---

## 2. PostgreSQL Source Database Specification

The source database models an operational OLTP e-commerce system.

- **Database Name:** `retail_source`
- **Schema Name:** `public`
- **Table Name:** `orders`
- **DDL Initializer:** `database/init.sql`
- **Seeder Script:** `scripts/load_postgres.py`

### Schema Definition:
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | `INTEGER` | `PRIMARY KEY` | Unique transaction ID (Values: 1001 to 1500) |
| `order_date` | `DATE` | `NOT NULL` | Calendar date of purchase (2025-11-01 to 2026-10-29) |
| `product` | `VARCHAR(100)`| `NOT NULL` | Product name (Laptop, Smartphone, Tablet, etc.) |
| `region` | `VARCHAR(50)` | `NOT NULL` | Territory (North, South, East, West, Central) |
| `quantity` | `INTEGER` | `NOT NULL, CHECK (quantity > 0)` | Units ordered (1 to 5) |
| `unit_price` | `NUMERIC(12,2)`| `NOT NULL, CHECK (unit_price > 0)`| Price per unit in INR (₹699.00 to ₹65,000.00) |

*Total Baseline Records:* Exactly **500 rows** (Total Gross Value: **₹17,379,476.00 INR**).

---

## 3. Airbyte Ingestion Pipeline Specification

Airbyte Open Source (managed via `abctl`) replicates raw transactions from PostgreSQL into BigQuery.

- **Airbyte Web UI URL:** `http://localhost:8000`
- **Source Connector:** `Postgres`
  - Name: `Postgres_RetailSource`
  - Host from Airbyte runtime: `host.docker.internal` (Resolves to host port `5432`)
  - Database: `retail_source`, Schema: `public`
- **Destination Connector:** `BigQuery`
  - Name: `BigQuery_RawRetail`
  - Target Dataset: `raw_retail`
  - Loading Method: `Standard (Batched Inserts)`
- **Connection Name:** `Postgres_to_BigQuery_Orders`
- **Selected Stream:** `orders`
- **Sync Mode:** `Full Refresh | Overwrite`
  - Drops/replaces the raw table atomically on each sync to guarantee zero duplicate records during reruns.
- **Connection UUID:**  
  Member 2 can obtain the Connection UUID from the browser URL when viewing the connection in the Airbyte UI:
  `http://localhost:8000/workspaces/<WORKSPACE_ID>/connections/<CONNECTION_UUID>`
- **Output Table:** `raw_retail.orders` (includes Airbyte metadata columns `_airbyte_raw_id` and `_airbyte_extracted_at`).

---

## 4. dbt Transformation Project Details

All transformation models are housed in the `dbt/retailpulse_dbt/` directory.

- **dbt Project Name:** `retailpulse_dbt`
- **Project Directory:** `c:\Users\Swapnaja\OneDrive\Desktop\RetailPulse\dbt\retailpulse_dbt\`
- **Profile Name:** `retailpulse` (Configured in `$HOME/.dbt/profiles.yml`)
- **Source Declaration:** `models/sources.yml` (`source('raw_retail', 'orders')`)
- **Staging Model:** `models/staging/stg_orders.sql` (Materialized as `VIEW`)
- **Analytical Mart Models:**
  - `models/marts/sales_by_product.sql` (Materialized as `TABLE`)
  - `models/marts/sales_by_region.sql` (Materialized as `TABLE`)
  - `models/marts/monthly_sales.sql` (Materialized as `TABLE`)
- **Test Suite:** 32 automated tests in `models/staging/schema.yml`, `models/marts/schema.yml`, and `tests/`.

### Commands to Run dbt:
```powershell
cd dbt/retailpulse_dbt

# Check connection
dbt debug

# Run transformations
dbt run

# Run quality test suite
dbt test

# Or execute run + test in one command
dbt build
```

---

## 5. Final BigQuery Data Contract (Analytics Layer)

Member 2's Streamlit application should query the tables in `analytics_retail`:

### Table 1: `analytics_retail.stg_orders` (View)
Cleansed, validated, and deduplicated transactional records.
| Column Name | BigQuery Data Type | Description |
| :--- | :--- | :--- |
| `order_id` | `INT64` | Unique transaction ID (Primary Key) |
| `order_date` | `DATE` | Calendar transaction date (`YYYY-MM-DD`) |
| `product` | `STRING` | Standardized, whitespace-trimmed product name |
| `region` | `STRING` | Standardized geographic region |
| `quantity` | `INT64` | Units ordered (1 to 5) |
| `unit_price` | `NUMERIC` | Unit list price in INR |
| `revenue` | `NUMERIC` | Line total calculated as `ROUND(quantity * unit_price, 2)` |

---

### Table 2: `analytics_retail.sales_by_product` (Table)
Aggregated product-level performance mart.
| Column Name | BigQuery Data Type | Description |
| :--- | :--- | :--- |
| `product` | `STRING` | Unique product name (Laptop, Smartphone, etc.) |
| `total_orders` | `INT64` | Count of distinct orders containing this product |
| `total_quantity` | `INT64` | Total cumulative units sold |
| `total_revenue` | `NUMERIC` | Total gross sales revenue in INR |

---

### Table 3: `analytics_retail.sales_by_region` (Table)
Aggregated geographic performance mart.
| Column Name | BigQuery Data Type | Description |
| :--- | :--- | :--- |
| `region` | `STRING` | Sales territory (North, South, East, West, Central) |
| `total_orders` | `INT64` | Count of distinct customer orders in this region |
| `total_quantity` | `INT64` | Total volume of units shipped to this region |
| `total_revenue` | `NUMERIC` | Cumulative gross revenue in INR for this region |

---

### Table 4: `analytics_retail.monthly_sales` (Table)
Aggregated time-series trend mart.
| Column Name | BigQuery Data Type | Description |
| :--- | :--- | :--- |
| `month_start` | `DATE` | First calendar day of the sales month (`YYYY-MM-01`) |
| `total_orders` | `INT64` | Count of distinct orders placed during the month |
| `total_quantity` | `INT64` | Total volume of units sold during the month |
| `total_revenue` | `NUMERIC` | Cumulative gross sales revenue in INR for the month |

---

## 6. Sample BigQuery Queries for Streamlit & Conversational BI

Member 2 can use these tested SQL templates in the Streamlit application or as prompt templates for the Conversational LLM:

### Query A: Highest Revenue Product
```sql
SELECT
    product,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.sales_by_product`
ORDER BY
    total_revenue DESC
LIMIT 1;
```

### Query B: Highest Revenue Region
```sql
SELECT
    region,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.sales_by_region`
ORDER BY
    total_revenue DESC
LIMIT 1;
```

### Query C: Month-wise Revenue Trends (Time-Series)
```sql
SELECT
    month_start,
    total_orders,
    total_quantity,
    total_revenue
FROM
    `analytics_retail.monthly_sales`
ORDER BY
    month_start ASC;
```

### Query D: Dynamic Natural Language Query Filtering Example
```sql
-- E.g., User asks: "Show me all Laptop transactions in the South region"
SELECT
    order_id,
    order_date,
    product,
    region,
    quantity,
    unit_price,
    revenue
FROM
    `analytics_retail.stg_orders`
WHERE
    LOWER(product) = 'laptop'
    AND LOWER(region) = 'south'
ORDER BY
    order_date DESC;
```

---

## 7. Airflow Orchestration Integration Guide (For Member 2)

Member 2 will build an Apache Airflow DAG to automate the entire end-to-end pipeline.

### Step 1: Install Airflow Providers
```bash
pip install apache-airflow-providers-airbyte apache-airflow-providers-google
```

### Step 2: Configure Airflow Connections
1. In Airflow UI (`Admin` -> `Connections`), create connection `airbyte_default`:
   - **Conn Type:** `Airbyte`
   - **Host:** `localhost` (or `host.docker.internal` if Airflow runs in Docker)
   - **Port:** `8000`
   - **Login:** `admin` (or user from `abctl local credentials`)
   - **Password:** `<Airbyte-Password>`

### Step 3: Recommended DAG Task Flow Architecture

```
+---------------------------+
|  sync_postgres_to_bq      |  (AirbyteTriggerSyncOperator)
|  Triggers Airbyte Sync    |
+---------------------------+
              │
              ▼
+---------------------------+
|  run_dbt_transformations  |  (BashOperator: dbt run)
|  Builds analytics_retail  |
+---------------------------+
              │
              ▼
+---------------------------+
|  test_dbt_data_quality    |  (BashOperator: dbt test)
|  Validates 32 constraints |
+---------------------------+
              │
              ▼
+---------------------------+
|  validate_final_output    |  (BigQueryCheckOperator or Python)
|  Asserts 500 rows loaded  |
+---------------------------+
```

### DAG Template Code:
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.operators.bash import BashOperator

AIRBYTE_CONNECTION_UUID = "YOUR_AIRBYTE_CONNECTION_UUID"  # Insert from Airbyte UI
DBT_PROJECT_PATH = "/path/to/RetailPulse/dbt/retailpulse_dbt"

default_args = {
    "owner": "member_2",
    "depends_on_past": False,
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

    # 1. Trigger Airbyte sync and wait for completion
    trigger_airbyte_sync = AirbyteTriggerSyncOperator(
        task_id="trigger_airbyte_sync",
        airbyte_conn_id="airbyte_default",
        connection_id=AIRBYTE_CONNECTION_UUID,
        asynchronous=False,  # Synchronously blocks until sync reaches 'SUCCEEDED'
        timeout=1800,
    )

    # 2. Run dbt transformation models
    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command=f"cd {DBT_PROJECT_PATH} && dbt run",
    )

    # 3. Execute dbt quality tests
    test_dbt_models = BashOperator(
        task_id="test_dbt_models",
        bash_command=f"cd {DBT_PROJECT_PATH} && dbt test",
    )

    trigger_airbyte_sync >> run_dbt_models >> test_dbt_models
```

---

## 8. Exact Run Instructions for Member 1 Components

If Member 2 needs to re-run or test the data engineering components locally:

```powershell
# 1. Activate Python virtual environment
cd c:\Users\Swapnaja\OneDrive\Desktop\RetailPulse
.\venv\Scripts\Activate.ps1

# 2. Generate/re-validate synthetic CSV (500 records)
python scripts/generate_dataset.py

# 3. Start PostgreSQL and load data
docker start retail-postgres   # or start local service
python scripts/load_postgres.py
python scripts/check_postgres.py

# 4. Ingest via Airbyte
# Trigger sync manually in http://localhost:8000 or via Airflow DAG

# 5. Run dbt transformations & tests
cd dbt/retailpulse_dbt
dbt run
dbt test

# 6. Verify end-to-end pipeline reconciliation
cd ../..
python scripts/reconcile_pipeline.py
```

---

## 9. Known Limitations & Handoff Notes

1. **Airbyte Local Networking:**
   - Airbyte runs in a Docker container via `abctl`. When configuring PostgreSQL, always use `host.docker.internal` instead of `localhost`.
2. **BigQuery Sandbox Expiration:**
   - In Google Cloud BigQuery Sandbox mode, newly created tables carry a default expiration of 60 days. This has no effect on development, but is worth noting for production deployments.
3. **Credentials Management:**
   - GCP Service Account JSON keys must never be committed to git. Member 2 must maintain their own local `keys/gcp_service_account.json` and `.env` file based on `.env.example`.
4. **Airflow Environment Isolation:**
   - Member 2 should run Airflow in its own dedicated virtual environment or Docker containers to avoid package version conflicts with `dbt-core` or `dbt-bigquery`.

