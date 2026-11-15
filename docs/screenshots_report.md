# RetailPulse: Implementation & Verification Screenshots Report
### Experiment 9: Data Engineering Microproject

This document provides visual evidence of the successful execution of the complete RetailPulse pipeline across all stages: Data Generation, PostgreSQL OLTP, Airflow Orchestration, dbt Modeling, and Streamlit Conversational BI.

---

## 1. End-to-End Architecture Diagram
![Architecture Diagram](file:///docs/architecture.png)

---

## 2. Apache Airflow DAG Orchestration (`retail_sales_pipeline`)
![Airflow DAG Execution](file:///docs/screenshots/15_airflow_dag_pipeline_execution.png)
*Airflow DAG showing task dependency chain: `start -> check_airbyte_sync_mode -> validate_raw_ingestion -> dbt_run -> dbt_test -> validate_bigquery_output -> end`.*

---

## 3. Streamlit Conversational BI Dashboard
### Overview & High-Level KPIs
![Streamlit Overview](file:///docs/screenshots/01_streamlit_overview_kpis.png)
*Summary KPI cards displaying ₹17.38M Total Revenue, Laptop as Top Product (₹6.89M), South as Top Territory (₹4.82M), and 12-month span.*

### Question 1: Highest-Revenue Product
![Q1 Highest Product](file:///docs/screenshots/02_streamlit_q1_highest_product.png)
*Result: Laptop generated ₹6,890,000.00 INR across 60 orders (106 units sold).*

### Question 2: Highest-Sales Region
![Q2 Highest Region](file:///docs/screenshots/03_streamlit_q2_highest_region.png)
*Result: South territory recorded ₹4,823,494.00 INR across 123 customer orders (260 units).*

### Question 3: Monthly Revenue Trend
![Q3 Monthly Trend](file:///docs/screenshots/04_streamlit_q3_monthly_trend.png)
*Result: 12 continuous months peaking in May 2026 at ₹1.97M INR with Plotly spline visualization.*

### Dynamic Conversational Query: Filtered Orders
![Filtered Orders](file:///docs/screenshots/05_streamlit_conversational_filter.png)
*Query: "Show all laptop transactions in South region" securely parameterized to `analytics_retail.stg_orders`.*

---

## 4. Analytical Mart Explorers
### Product Performance Mart (`sales_by_product`)
![Product Mart](file:///docs/screenshots/06_streamlit_product_mart.png)

### Regional Sales Mart (`sales_by_region`)
![Regional Mart](file:///docs/screenshots/07_streamlit_regional_mart.png)

### Monthly Sales Trends Mart (`monthly_sales`)
![Monthly Trends](file:///docs/screenshots/08_streamlit_monthly_trends.png)

### Staging Transactions Explorer (`stg_orders`)
![Staging Explorer](file:///docs/screenshots/09_streamlit_staging_orders.png)

---

## 5. Terminal Execution Proof
### Member 2 Automated Unit Tests (5/5 Passing)
![Unit Tests](file:///docs/screenshots/12_terminal_member2_unit_tests.png)

### Cross-Mart Financial Reconciliation Audit (₹0.00 Discrepancy)
![Reconciliation Audit](file:///docs/screenshots/13_terminal_reconciliation_audit.png)

### Dataset Generation & Quality Audit
![Dataset Generation](file:///docs/screenshots/11_terminal_generate_dataset.png)

### dbt Core Manifest Compilation (`dbt parse`)
![dbt Parse](file:///docs/screenshots/14_terminal_dbt_parse.png)
