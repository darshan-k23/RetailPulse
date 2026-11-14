# RetailPulse Architecture & Viva Defense Reference
### Automated Retail Sales Analytics & Conversational BI Pipeline

RetailPulse models an end-to-end modern cloud retail analytics platform combining transactional OLTP systems, ELT data replication, cloud data warehousing, in-warehouse dimensional modeling, automated workflow orchestration, and conversational business intelligence.

---

## 🏛️ 1. End-to-End Pipeline Architecture Diagram

![RetailPulse Architecture Diagram](file:///docs/architecture.png)

```
+-----------------------------------------------------------------------------------------+
|                               MEMBER 1: DATA ENGINEERING                                |
|                                                                                         |
|   +--------------------------+              +---------------------------------------+   |
|   |  data/retail_sales.csv   |              |          PostgreSQL Source            |   |
|   |  500 records, 12 months  |  --------->  | Database: retail_source               |   |
|   |  Total: INR 17.38M       |  scripts/    | Table: public.orders                  |   |
|   +--------------------------+  load_postgres.py  Constraint: qty > 0, price > 0    |   |
|                                             +---------------------------------------+   |
|                                                                 │                       |
|                                                                 │ Airbyte OSS (abctl)   |
|                                                                 │ Full Refresh Sync     |
|                                                                 ▼                       |
|   +---------------------------------------+         +-------------------------------+   |
|   |          dbt Core Project             |         |     Google BigQuery (Raw)     |   |
|   |  Location: dbt/retailpulse_dbt/       |         | Dataset: raw_retail           |   |
|   |  - stg_orders (View, revenue calc)    | <------ | Table: orders                 |   |
|   |  - sales_by_product (Table Mart)      | BigQuery| Metadata: _airbyte_extracted_at|   |
|   |  - sales_by_region (Table Mart)       | SQL     +-------------------------------+   |
|   |  - monthly_sales (Table Mart)         |                                             |
|   |  - 32 automated schema & data tests   |                                             |
|   +---------------------------------------+                                             |
|                       │                                                                 |
|                       ▼                                                                 |
|   +---------------------------------------+                                             |
|   |       BigQuery Analytics Marts        |                                             |
|   | Dataset: analytics_retail             |                                             |
|   | Checksum: INR 17,379,476.00 (Match)   |                                             |
+---|---------------------------------------+---------------------------------------------+
                        │
                        │ Reads analytics marts
                        ▼
+-----------------------------------------------------------------------------------------+
|                         MEMBER 2: ORCHESTRATION & BI INTERFACE                          |
|                                                                                         |
|   +--------------------------------------+   +--------------------------------------+   |
|   |         Apache Airflow DAGs          |   |     Streamlit Conversational BI      |   |
|   | Automated scheduled pipeline runs:   |   | Predefined SQL & Conversational UI:  |   |
|   | [start -> airbyte -> validate_raw    |   | - Q1: Top Product (Laptop: ₹6.89M)   |   |
|   |  -> dbt_run -> dbt_test              |   | - Q2: Top Region (South: ₹4.82M)     |   |
|   |  -> validate_output -> end]          |   | - Q3: Monthly Trend (12 Months)      |   |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Component Breakdown & Responsibilities

### Stage 1: Data Generation & Source Storage (Member 1)
- **Dataset:** `data/retail_sales.csv` (500 deterministic orders, 12 months, ₹17,379,476.00 INR gross sales).
- **OLTP Source:** PostgreSQL `retail_source.public.orders` with schema integrity (`order_id` PK, `quantity > 0`, `unit_price > 0`).

### Stage 2: ELT Ingestion (Member 1)
- **Tool:** Airbyte Open Source (`abctl`).
- **Pipeline:** Replicates `retail_source.public.orders` into BigQuery `raw_retail.orders`.
- **Sync Mode:** `Full Refresh | Overwrite` ensuring idempotent replication without duplicate records.

### Stage 3: In-Warehouse Cloud Modeling (Member 1)
- **Tool:** dbt Core (`dbt-bigquery`).
- **Layers:**
  - **Staging View (`stg_orders`):** Standardizes types, trims text, deduplicates using `ROW_NUMBER()`, and calculates `revenue = ROUND(quantity * unit_price, 2)`.
  - **Marts (`sales_by_product`, `sales_by_region`, `monthly_sales`):** Dimensional aggregations optimized for business queries.
  - **Test Suite:** 32 automated tests verifying primary key uniqueness, not-null constraints, and positive business values.

### Stage 4: Orchestration & Dependency Enforcement (Member 2)
- **Tool:** Apache Airflow (`retail_sales_pipeline` DAG).
- **Execution Architecture:**
  - Branching decision between automated REST API Airbyte sync and acceptable simplified manual ingestion notice.
  - BigQuery raw table pre-validation.
  - `dbt_run` BashOperator: compiles and executes SQL transformations in `analytics_retail`.
  - `dbt_test` BashOperator: executes all 32 data quality checks before marking models healthy.
  - `validate_bigquery_output` PythonOperator: validates table existence, non-zero rows, and cross-mart financial checksums (`SUM(monthly_sales.total_revenue) == SUM(sales_by_product.total_revenue) == ₹17.38M`).

### Stage 5: Conversational Business Intelligence (Member 2)
- **Tool:** Streamlit (`app/streamlit_app.py`) + Plotly.
- **Consumption Principle:** Strictly queries dbt-transformed models in `analytics_retail`, never touching raw staging or PostgreSQL directly.
- **Safety & Scope:** Maps plain-English questions to strictly vetted predefined SQL templates, eliminating SQL injection vulnerability.
- **Resilience:** Live BigQuery connectivity with automatic fallback to a reconciled local analytics engine for offline viva demonstrations.

---

## 3. Core Viva Defense Concepts

| Concept | Explanation for Viva Defense |
| :--- | :--- |
| **What is ETL vs. ELT?** | In traditional ETL, data is transformed by an external server before reaching the warehouse. In ELT (used here), raw data is extracted and loaded into BigQuery first (via Airbyte), and transformed inside BigQuery using the warehouse's compute power (via dbt). |
| **Why Airbyte?** | Eliminates custom extraction scripts; provides reliable connectors, error handling, metadata enrichment (`_airbyte_raw_id`), and idempotent loading. |
| **Why dbt Core?** | Brings software engineering best practices to SQL: version control, modular refs (`ref('stg_orders')`), automated testing, and automatic dependency DAG creation. |
| **Why Apache Airflow?** | Airbyte and dbt run independently. Airflow orchestrates their execution sequence, guarantees dbt runs only after ingestion succeeds, and halts the pipeline if tests fail. |
| **What is Conversational BI here?** | Predefined parameterized SQL queries mapped to natural language intents, allowing business managers to ask questions like *"Which product generated the highest revenue?"* without writing SQL. |
