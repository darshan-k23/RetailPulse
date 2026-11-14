# RetailPulse
### Automated Retail Sales Analytics & Conversational BI Pipeline

RetailPulse is an end-to-end Data Engineering and Conversational Business Intelligence microproject simulating a modern cloud retail analytics platform. It extracts raw transactional sales data, models an operational OLTP database, replicates data into Google BigQuery via Airbyte, transforms raw records into dimensional data marts using dbt Core, automates the lifecycle via Apache Airflow, and exposes analytical insights through an AI-powered conversational BI Streamlit application.

---

## 👥 Engineering Division of Responsibilities

| Responsibility Domain | Engineer | Scope & Delivered Artifacts | Implementation Status |
| :--- | :--- | :--- | :---: |
| **Data Engineering & Warehousing** | **Member 1** | 1. Synthetic transactional retail dataset (500 rows, ₹17.38M)<br>2. PostgreSQL source database setup & idempotent seeder<br>3. Google BigQuery cloud data warehouse provisioning (`raw_retail`, `analytics_retail`)<br>4. Airbyte Open Source ELT ingestion pipeline (PostgreSQL &rarr; BigQuery)<br>5. dbt Core transformation layer (`stg_orders`, `sales_by_product`, `sales_by_region`, `monthly_sales`)<br>6. Pipeline validation & cross-mart financial reconciliation | **COMPLETED** |
| **Orchestration & Conversational BI** | **Member 2** | 1. Apache Airflow DAG orchestration (`retail_sales_pipeline` in Docker Compose)<br>2. Upstream ingestion verification & dbt dependency enforcement<br>3. Streamlit Conversational BI web interface (`app/streamlit_app.py`)<br>4. Predefined SQL mappings for the 3 approved business questions<br>5. Automated test suite (`tests/test_member2_bi.py`) & offline fallback engine<br>6. Architecture diagram & final submission documentation | **COMPLETED** |

---

## 🏛️ End-to-End Pipeline Architecture

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
|   | Automated scheduled pipeline runs:   |   | Natural Language / Predefined SQL:   |   |
|   | [start -> airbyte -> validate_raw    |   | - Q1: Top Product (Laptop: ₹6.89M)   |   |
|   |  -> dbt_run -> dbt_test              |   | - Q2: Top Region (South: ₹4.82M)     |   |
|   |  -> validate_output -> end]          |   | - Q3: Monthly Trend (12 Months)      |   |
+-----------------------------------------------------------------------------------------+
```

---

## 🎯 Approved Core Business Questions & Answers

| Question | Target dbt Analytics Model | Executed SQL Query | Ground Truth Output |
| :--- | :--- | :--- | :--- |
| **Q1: Which product generated the highest revenue?** | `analytics_retail.sales_by_product` | `SELECT product, total_orders, total_quantity, total_revenue FROM analytics_retail.sales_by_product ORDER BY total_revenue DESC LIMIT 1;` | **Laptop** (₹6,890,000.00 INR, 106 units sold across 60 orders) |
| **Q2: Which region recorded the highest sales?** | `analytics_retail.sales_by_region` | `SELECT region, total_orders, total_quantity, total_revenue FROM analytics_retail.sales_by_region ORDER BY total_revenue DESC LIMIT 1;` | **South** (₹4,823,494.00 INR across 123 customer orders) |
| **Q3: How does revenue change month by month?** | `analytics_retail.monthly_sales` | `SELECT month_start, total_orders, total_quantity, total_revenue FROM analytics_retail.monthly_sales ORDER BY month_start ASC;` | 12 continuous months (Nov 2025 – Oct 2026), peaking in **May 2026** at **₹1.97M INR** (Total: ₹17.38M) |

---

## 📂 Complete Repository File Structure

```
RetailPulse/
│
├── .env.example                     # Environment variables template (GCP, Postgres, Airflow, Airbyte)
├── .gitignore                       # Protects secrets, .env, GCP keys, venv, and logs
├── README.md                        # Master project documentation
├── requirements.txt                 # Unified dependencies for both Member 1 & Member 2
│
├── data/
│   ├── README.md                    # Data description & schema notes
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
│   ├── reconcile_pipeline.py        # End-to-end data reconciliation engine
│   └── generate_architecture_diagram.py # Generates docs/architecture.png
│
├── dbt/
│   └── retailpulse_dbt/             # Complete dbt Core project
│       ├── dbt_project.yml          # dbt project configuration & materializations
│       ├── profiles.yml.example     # Template for ~/.dbt/profiles.yml
│       ├── README.md                # dbt operational guide
│       ├── models/
│       │   ├── sources.yml          # Upstream BigQuery source declaration
│       │   ├── staging/
│       │   │   ├── stg_orders.sql   # Staging view with deduplication & revenue calculation
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
├── airflow/                         # Member 2: Orchestration Stack
│   ├── dags/
│   │   └── retail_sales_pipeline.py # Master Airflow DAG (Task dependencies & validation)
│   ├── Dockerfile                   # Custom Airflow image with dbt-bigquery
│   ├── docker-compose.yaml          # Full Airflow 2.8+ container deployment
│   └── README.md                    # Airflow operation guide
│
├── app/                             # Member 2: Conversational BI Interface
│   ├── streamlit_app.py             # Streamlit BI application with Predefined SQL mapping
│   └── README.md                    # Streamlit usage guide
│
├── sql/
│   └── verify_bigquery.sql          # Validation queries & cross-mart checksums
│
├── tests/
│   ├── test_member2_bi.py           # Automated unit test suite (5 passing tests)
│   └── README.md                    # Testing documentation
│
└── docs/
    ├── architecture.png             # Publication-quality high-res architecture diagram
    ├── architecture.md              # Architectural specification & viva defense concepts
    ├── data_dictionary.md           # Dataset schema & catalog pricing
    ├── postgres_setup.md            # PostgreSQL installation & operational guide
    ├── bigquery_setup.md            # BigQuery dataset creation & Free Tier guide
    ├── bigquery_permissions.md      # IAM least-privilege matrix & key security
    ├── airbyte_setup.md             # Airbyte OSS (abctl) setup guide
    ├── airbyte_validation.md        # Post-sync verification & Airflow operator specs
    ├── dbt_setup.md                 # dbt Core concepts & profiles.yml guide
    ├── airflow_orchestration.md     # Airflow DAG deep-dive & task dependency flow
    ├── streamlit_bi.md              # Streamlit Conversational BI technical reference
    ├── member1_validation_report.md # Quality validation report for Member 1
    ├── member2_validation_report.md # Quality validation report for Member 2
    ├── member2_handover.md          # Technical handoff contract from Member 1 to Member 2
    ├── final_submission_report.md   # Final microproject report (Experiment 9)
    └── screenshots/
        └── README.md                # Submission screenshots checklist
```

---

## ⚡ Quickstart Guide

### 1. Environment Configuration
```powershell
# Clone and enter workspace
git clone https://github.com/darshan-k23/RetailPulse.git
cd RetailPulse

# Set up virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt

# Create your private environment file
Copy-Item .env.example .env
```

### 2. Member 1 Components (Database, Airbyte & dbt)
```powershell
# 1. Generate dataset and seed PostgreSQL
python scripts/generate_dataset.py
docker run -d --name retail-postgres -p 5432:5432 -e POSTGRES_DB=retail_source -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres:16
python scripts/load_postgres.py
python scripts/check_postgres.py

# 2. Trigger sync in Airbyte Web UI (http://localhost:8000)

# 3. Run dbt models and quality tests
cd dbt/retailpulse_dbt
dbt run
dbt test
cd ../..
```

### 3. Member 2 Components (Airflow & Streamlit BI)
```powershell
# Run Member 2 unit test suite (validates DAG, SQL logic, and Intent Parser)
python tests/test_member2_bi.py

# Launch the Conversational BI Streamlit Application
streamlit run app/streamlit_app.py
```
*(The Streamlit app will open at `http://localhost:8501`. It connects to live BigQuery if `.env` has credentials, or automatically uses the verified local replica engine if offline).*

### 4. Running Airflow via Docker Compose (Optional)
```powershell
cd airflow
docker compose up -d --build
# Open Airflow Web UI at http://localhost:8080 (admin / admin)
```

---

## 🎓 Viva Voce Preparation Guide (3–5 Minute Demo)

### Recommended Speaking Split
- **Member 1:** Explains dataset generation (500 rows, ₹17.38M), PostgreSQL OLTP structure, Airbyte ELT replication into BigQuery `raw_retail`, and dbt Core modeling (`stg_orders` and the 3 dimensional marts with 32 automated tests).
- **Member 2:** Explains the Airflow task dependency chain (`start -> airbyte -> validate_raw -> dbt_run -> dbt_test -> validate_output -> end`), shows the Streamlit Conversational BI interface, and demonstrates the answers to the 3 core business questions using predefined SQL.
- **Both:** Walk through the end-to-end architecture diagram (`docs/architecture.png`) and highlight the ₹0.00 discrepancy financial checksum match across the entire stack.

### Quick Viva Q&A
1. **What is ETL vs. ELT?**  
   *Answer:* In ETL, transformations happen before loading. In ELT (used in RetailPulse), raw data is loaded into Google BigQuery first via Airbyte, and transformed inside BigQuery using dbt SQL models, utilizing the cloud warehouse's scalability.
2. **Why use Airbyte?**  
   *Answer:* It automates data extraction from PostgreSQL to BigQuery without custom scripts, handles incremental or full-refresh syncs, and adds lineage metadata (`_airbyte_raw_id`).
3. **What does dbt do?**  
   *Answer:* dbt transforms raw data into clean views and analytical tables directly inside BigQuery, compiles modular SQL (`ref()`), and runs automated data quality tests.
4. **Why is Apache Airflow needed?**  
   *Answer:* Airflow coordinates the execution order, ensuring dbt transformations do not run before ingestion completes, and alerting if tests fail.
5. **How does Conversational BI work safely here?**  
   *Answer:* Plain-English inquiries are mapped to reviewed, parameterized SQL query templates, preventing arbitrary user SQL execution and SQL injection attacks.
