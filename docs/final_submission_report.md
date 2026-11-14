# RetailPulse: End-to-End Microproject Submission Report
### Experiment 9: Data Engineering Microproject (Maximum 5 Marks)

---

## 1. Project Identification & Team Division

- **Project Title:** RetailPulse: Automated Retail Sales Analytics & Conversational BI Pipeline
- **Business Domain:** Retail Sales Analytics & Executive Decision Support
- **Dataset:** 500 deterministic transactional retail order records in CSV format (Total Gross: ₹17,379,476.00 INR)
- **Source Database:** PostgreSQL (`retail_source.public.orders`)
- **Ingestion / Warehouse:** Airbyte OSS (`abctl`) / Google Cloud BigQuery (`raw_retail`, `analytics_retail`)
- **Transformation / Orchestration:** dbt Core (`retailpulse_dbt`) / Apache Airflow (`retail_sales_pipeline`)
- **BI Interface:** Streamlit Conversational BI (`app/streamlit_app.py`) with Predefined SQL Mapping

### Team Member Division of Roles
| Role | Assigned Engineer | Responsibilities Owned & Delivered | Status |
| :--- | :--- | :--- | :---: |
| **Member 1 — Data Pipeline Lead** | Lead Engineer 1 | 1. Dataset generation, cleaning, and schema specification (500 records)<br>2. PostgreSQL OLTP database provisioning (`retail_source.public.orders`)<br>3. Google BigQuery datasets creation (`raw_retail`, `analytics_retail`)<br>4. Airbyte ELT pipeline setup (`Postgres_to_BigQuery_Orders`)<br>5. dbt Core project modeling (`stg_orders`, `sales_by_product`, `sales_by_region`, `monthly_sales`)<br>6. 32 automated dbt quality tests and cross-mart financial reconciliation | **COMPLETED** |
| **Member 2 — Orchestration & BI Lead** | Lead Engineer 2 | 1. Shared project repository setup, `.env.example`, `.gitignore`, `requirements.txt`<br>2. Apache Airflow DAG (`retail_sales_pipeline`) and Docker Compose runtime<br>3. Airbyte sync triggering, upstream raw table verification, and dbt execution sequencing<br>4. Streamlit Conversational BI web application (`app/streamlit_app.py`)<br>5. Predefined SQL query mapping for the 3 approved business questions<br>6. Architecture diagram (`docs/architecture.png`), test suites (`tests/test_member2_bi.py`), and documentation | **COMPLETED** |

---

## 2. Business Problem & Approved Analytical Questions

### 2.1 Problem Statement
Retail executives and sales managers need quick, accurate visibility into product popularity, regional sales contribution, and monthly financial momentum. Manually consolidating transactional CSV dumps or querying operational OLTP databases leads to report latency, query contention, and potential human calculation errors.

### 2.2 Approved Business Questions Answered
1. **Question 1:** *Which product generated the highest revenue?*
   - **Target Mart:** `analytics_retail.sales_by_product`
   - **Answer:** **Laptop** generated the highest gross revenue (**₹6,890,000.00 INR**) across **60 orders** (106 units sold).
2. **Question 2:** *Which region recorded the highest sales?*
   - **Target Mart:** `analytics_retail.sales_by_region`
   - **Answer:** The **South** sales territory recorded the highest gross revenue (**₹4,823,494.00 INR**) across **123 customer orders** (260 units shipped).
3. **Question 3:** *How does revenue change month by month?*
   - **Target Mart:** `analytics_retail.monthly_sales`
   - **Answer:** Across 12 consecutive months (Nov 2025 to Oct 2026), sales peaked in **May 2026** at **₹1,972,778.00 INR**, with an average monthly revenue of **₹1,448,289.67 INR**.

---

## 3. End-to-End Technical Architecture

![Architecture Diagram](file:///docs/architecture.png)

### Key Architectural Principle:
- **Airflow coordinates the workflow; it does NOT transform data.** Airbyte extracts and loads data, BigQuery stores it, and dbt transforms it inside the warehouse using SQL.
- **Consumption Isolation:** Streamlit queries ONLY the transformed, validated data marts in `analytics_retail`, never querying the raw ingestion table or PostgreSQL source directly.

---

## 4. Pipeline Execution & Verification Summary

### 4.1 Data Integrity & Checksums
All 500 transactional records were reconciled across all layers of the stack:

| Pipeline Layer | Record Count | Total Gross Revenue (INR) | Discrepancy vs Baseline |
| :--- | :---: | :---: | :---: |
| **1. Source CSV (`data/retail_sales.csv`)** | 500 rows | ₹17,379,476.00 | BASELINE |
| **2. PostgreSQL (`retail_source.public.orders`)** | 500 rows | ₹17,379,476.00 | ₹0.00 (Match) |
| **3. BigQuery Raw (`raw_retail.orders`)** | 500 rows | ₹17,379,476.00 | ₹0.00 (Match) |
| **4. dbt Staging View (`analytics_retail.stg_orders`)** | 500 rows | ₹17,379,476.00 | ₹0.00 (Match) |
| **5. dbt Mart: `sales_by_product`** | 7 products | ₹17,379,476.00 | ₹0.00 (Match) |
| **6. dbt Mart: `sales_by_region`** | 5 regions | ₹17,379,476.00 | ₹0.00 (Match) |
| **7. dbt Mart: `monthly_sales`** | 12 months | ₹17,379,476.00 | ₹0.00 (Match) |

### 4.2 Apache Airflow DAG Flow
```
start -> check_airbyte_sync_mode -> [trigger_airbyte_sync -> wait_for_sync | manual_notice] 
      -> validate_raw_ingestion -> dbt_run -> dbt_test -> validate_bigquery_output -> end
```
- **Ingestion Mode:** Supports automated REST API triggering via Airbyte v1 API, as well as the department-approved Simplified Mode (manual Airbyte trigger followed by Airflow automated raw validation, dbt run, dbt test, and output reconciliation).
- **Quality Gate:** If any of the 32 dbt tests fail, the DAG terminates immediately, preventing bad data from entering the marts.

---

## 5. Issues Encountered, Root Causes & Remediation

1. **Airbyte Local Networking Isolation:**
   - *Problem:* Airbyte running in Docker could not reach `localhost:5432` for PostgreSQL.
   - *Resolution:* Configured connection host as `host.docker.internal:5432`, allowing the container to communicate through the Docker host gateway.
2. **Streamlit Execution Resilience during Viva:**
   - *Problem:* Cloud BigQuery trial credits or university Wi-Fi restrictions could disrupt live API calls during evaluation.
   - *Resolution:* Implemented a dual-mode `WarehouseService` in `app/streamlit_app.py` that queries live BigQuery when online, but automatically falls back to an exact in-memory dbt-replica engine when offline, guaranteeing zero downtime.
3. **Multi-Attribute Conversational Parsing:**
   - *Problem:* Prompt *"Show all laptop transactions in south region"* matched both regional overview and product filters.
   - *Resolution:* Implemented hierarchical entity extraction prioritizing multi-attribute queries (`product` + `region`) to route securely to parameterized `stg_orders` filters.

---

## 6. Demonstration Sequence for Final Viva (3–5 Minutes)

1. **Introduction (1 min — Both):**
   - Introduce RetailPulse, the business scenario, and show the architecture diagram (`docs/architecture.png`).
2. **Member 1 Demonstration (1.5 min):**
   - Show `data/retail_sales.csv` (500 records) and PostgreSQL table `retail_source.public.orders`.
   - Show Airbyte sync status (**Succeeded**) and BigQuery raw table `raw_retail.orders`.
   - Show dbt models (`stg_orders`, marts) and passing output of all 32 dbt tests.
3. **Member 2 Demonstration (1.5 min):**
   - Show the Airflow DAG graph (`retail_sales_pipeline`) and explain the task dependency chain.
   - Launch Streamlit (`streamlit run app/streamlit_app.py`) and demonstrate the 3 core questions:
     - Q1: Highest-revenue product (Laptop - ₹6.89M)
     - Q2: Highest-sales region (South - ₹4.82M)
     - Q3: Monthly revenue trend (12-month table & Plotly line chart)
   - Demonstrate the dynamic natural language filter: *"Show all laptop transactions in south region"*.
4. **Conclusion & Viva Defense (1 min — Both):**
   - Highlight the financial checksum match (₹17,379,476.00 across all 3 marts with ₹0.00 discrepancy).
   - Answer examiner questions on ETL vs ELT, role of dbt, and why Airflow coordinates rather than transforms.
