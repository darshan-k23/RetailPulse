# RetailPulse: Project Verification Screenshots

This folder contains verification screenshots captured across all stages of the pipeline to serve as proof of successful execution for the final evaluation and viva demonstration.

---

## Required Submission Screenshots Checklist

### Stage 1: Source & PostgreSQL
- [ ] `01_postgresql_orders_count.png`: `SELECT COUNT(*) FROM public.orders;` verifying 500 rows.
- [ ] `02_postgresql_sample_data.png`: Sample 5 rows with non-null attributes in pgAdmin / terminal.

### Stage 2: Airbyte Ingestion
- [ ] `03_airbyte_connection_settings.png`: PostgreSQL source & BigQuery destination configuration in Airbyte UI.
- [ ] `04_airbyte_sync_succeeded.png`: Sync status showing **Succeeded** (500 records emitted, 500 records committed).

### Stage 3: Google BigQuery Raw Layer
- [ ] `05_bigquery_raw_table.png`: `raw_retail.orders` schema and row count audit in BigQuery Studio.

### Stage 4: dbt Core Transformations
- [ ] `06_dbt_run_terminal.png`: Terminal output of `dbt run` showing all 4 models created (`stg_orders`, `sales_by_product`, `sales_by_region`, `monthly_sales`).
- [ ] `07_dbt_test_terminal.png`: Terminal output of `dbt test` showing all 32 tests passing with 0 failures.

### Stage 5: Apache Airflow Orchestration
- [ ] `08_airflow_dag_graph_view.png`: `retail_sales_pipeline` DAG graph view in Airflow UI showing dependencies.
- [ ] `09_airflow_dag_run_success.png`: Successful execution run with all task boxes colored dark green (`success`).

### Stage 6: Streamlit Conversational BI
- [ ] `10_streamlit_q1_highest_product.png`: Answer to *"Which product generated the highest revenue?"* (Laptop, ₹6.89M).
- [ ] `11_streamlit_q2_highest_region.png`: Answer to *"Which region recorded the highest sales?"* (South, ₹4.82M).
- [ ] `12_streamlit_q3_monthly_trend.png`: Answer to *"How does revenue change month by month?"* (12-month table & line chart).
