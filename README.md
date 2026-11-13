# RetailPulse
### Automated Retail Sales Analytics & Conversational BI Pipeline

RetailPulse is an end-to-end Data Engineering and Conversational Business Intelligence microproject simulating a modern cloud retail analytics platform. It extracts raw transactional sales data, models an operational OLTP database, replicates data into Google BigQuery via Airbyte, transforms raw records into dimensional data marts using dbt Core, automates the lifecycle via Apache Airflow, and exposes analytical insights through an AI-powered conversational BI Streamlit application.

---

## 👥 Engineering Division of Responsibilities

| Responsibility Domain | Engineer | Scope & Delivered Artifacts | Implementation Status |
| :--- | :--- | :--- | :---: |
| **Data Engineering & Warehousing** | **Member 1** | 1. Synthetic transactional retail dataset (500 rows, ₹17.38M)<br>2. PostgreSQL source database setup & idempotent seeder<br>3. Google BigQuery cloud data warehouse provisioning (`raw_retail`, `analytics_retail`)<br>4. Airbyte Open Source ELT ingestion pipeline (PostgreSQL &rarr; BigQuery)<br>5. dbt Core transformation layer (`stg_orders`, `sales_by_product`, `sales_by_region`, `monthly_sales`)<br>6. Pipeline validation & cross-mart financial reconciliation | **COMPLETED** |
| **Orchestration & Conversational BI** | **Member 2** | 1. Apache Airflow DAG orchestration (triggering Airbyte + dbt)<br>2. Streamlit Conversational BI interface (Natural Language / LLM queries)<br>3. Final analytics dashboard integration | **READY FOR HANDOFF** |

---

## 🏛️ End-to-End Pipeline Architecture

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
|   | Automated scheduled pipeline runs:   |   | Natural Language / LLM queries over: |   |
|   | AirbyteTriggerSyncOperator -> dbt    |   | analytics_retail tables              |   |
+-----------------------------------------------------------------------------------------+
```

---

## 🗄️ Database Contract & Schemas

### 1. PostgreSQL (Source)
- **Database:** `retail_source` | **Schema:** `public` | **Table:** `orders`
- **Columns:** `order_id` (PK, INT), `order_date` (DATE), `product` (VARCHAR), `region` (VARCHAR), `quantity` (INT), `unit_price` (NUMERIC).

### 2. Google BigQuery (Warehouse)
- **Raw Layer:** `raw_retail.orders` (Ingested via Airbyte).
- **Analytics Layer:** `analytics_retail` (Modeled via dbt Core).

### 3. dbt Transformation Models
- `stg_orders`: Standardizes datatypes, trims strings, deduplicates by `order_id`, and calculates `revenue = ROUND(quantity * unit_price, 2)`.
- `sales_by_product`: Product-level sales volume, unit orders, and gross revenue.
- `sales_by_region`: Regional revenue distribution across South, West, North, East, and Central.
- `monthly_sales`: Continuous 12-month trend analysis (`DATE_TRUNC(order_date, MONTH)`).

---

## 📂 Repository File Structure

```
RetailPulse/
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Protects secrets, .env, GCP keys, venv, and logs
├── README.md                        # Master project documentation
├── requirements.txt                 # Pinned dependencies for Member 1
│
├── data/
│   └── retail_sales.csv             # Exactly 500 deterministic transactional records
│
├── database/
│   └── init.sql                     # PostgreSQL table DDL & indexing script
│
├── scripts/
│   ├── generate_dataset.py          # Synthetic dataset generator & validation audit
│   ├── load_postgres.py             # Idempotent PostgreSQL data loader
│   ├── check_postgres.py            # PostgreSQL table & constraint audit
│   ├── check_bigquery.py            # BigQuery connectivity & dataset health check
│   └── reconcile_pipeline.py        # End-to-end data reconciliation engine
│
├── dbt/
│   └── retailpulse_dbt/             # Complete dbt Core project
│       ├── dbt_project.yml          # dbt project configuration & materializations
│       ├── profiles.yml.example     # Template for ~/.dbt/profiles.yml
│       ├── README.md                # dbt operational guide
│       ├── models/
│       │   ├── sources.yml          # Upstream BigQuery source declaration
│       │   ├── staging/
│       │   │   ├── stg_orders.sql   # Staging view
│       │   │   └── schema.yml       # Column documentation & constraint tests
│       │   └── marts/
│       │       ├── sales_by_product.sql  # Product mart
│       │       ├── sales_by_region.sql   # Regional mart
│       │       ├── monthly_sales.sql     # Monthly time-series mart
│       │       └── schema.yml            # Mart tests & descriptions
│       └── tests/
│           ├── assert_positive_quantity.sql      # Singular data test
│           └── assert_non_negative_unit_price.sql # Singular data test
│
├── airbyte/
│   ├── configs/
│   │   └── connection_spec.json.example  # Airbyte pipeline specification
│   └── README.md                    # Airbyte setup summary
│
├── sql/
│   └── verify_bigquery.sql          # Validation queries & cross-mart checksums
│
└── docs/
    ├── data_dictionary.md           # Dataset schema & catalog pricing
    ├── postgres_setup.md            # PostgreSQL installation & operational guide
    ├── bigquery_setup.md            # BigQuery dataset creation & Free Tier guide
    ├── bigquery_permissions.md      # IAM least-privilege matrix & key security
    ├── airbyte_setup.md             # Airbyte OSS (abctl) setup guide
    ├── airbyte_validation.md        # Post-sync verification & Airflow operator specs
    ├── dbt_setup.md                 # dbt Core concepts & profiles.yml guide
    ├── member1_validation_report.md # Quality validation report & screenshot checklist
    └── member2_handover.md          # Complete technical handoff for Member 2
```

---

## ⚡ Quickstart: Running Member 1 Pipeline Components

### 1. Environment Setup (Windows PowerShell)
```powershell
cd c:\Users\Swapnaja\OneDrive\Desktop\RetailPulse
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 2. Generate Dataset & Seed PostgreSQL
```powershell
# Generate deterministic CSV (500 rows)
python scripts/generate_dataset.py

# Start PostgreSQL and seed
docker run -d --name retail-postgres -p 5432:5432 -e POSTGRES_DB=retail_source -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres:16
python scripts/load_postgres.py
python scripts/check_postgres.py
```

### 3. Replicate via Airbyte
- Launch Airbyte: `abctl local install --low-resource-mode`
- Access UI: `http://localhost:8000` (credentials via `abctl local credentials`)
- Sync: `Postgres_to_BigQuery_Orders` (Sync Mode: `Full Refresh | Overwrite`)

### 4. Execute dbt Transformations & Tests
```powershell
cd dbt/retailpulse_dbt
dbt parse     # Validate manifest (4 models, 32 data tests)
dbt run       # Execute transformations in analytics_retail
dbt test      # Execute all 32 tests
```

### 5. Run Financial Reconciliation Audit
```powershell
cd ../..
python scripts/reconcile_pipeline.py
```

---

## 🤝 Handover to Member 2
All pipeline integration endpoints, BigQuery schemas, SQL query samples, and Airflow operator code templates are documented in:
&rarr; [docs/member2_handover.md](file:///c:/Users/Swapnaja/OneDrive/Desktop/RetailPulse/docs/member2_handover.md)
