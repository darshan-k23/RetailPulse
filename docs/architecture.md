# RetailPulse Architecture & Viva Defense Reference

## 1. System Components & Flow

### Component 1: Data Generation (Python)
- Generates realistic synthetic sales data reflecting e-commerce and retail transactions.
- Introduces business logic: order amounts calculated via `(quantity * unit_price) - discount_amount`, realistic dates, regional distributions, and categorical taxonomy.

### Component 2: Source Storage (PostgreSQL)
- Database: `retail_source`
- Schema: `public`
- Table: `orders`
- Represents an OLTP (Online Transaction Processing) operational retail database with strict indexing on `order_id` and `order_date`.

### Component 3: Data Ingestion (Airbyte)
- Connects PostgreSQL to Google BigQuery.
- Mode: Replicates data from `retail_source.public.orders` to BigQuery `raw_retail.orders`.
- Highlights ELT philosophy: raw data is landed in BigQuery before any transformations are applied, maintaining auditability and raw history.

### Component 4: Cloud Data Warehousing (Google BigQuery)
- Multi-dataset separation:
  - `raw_retail`: Houses raw, unmanipulated tables loaded by Airbyte.
  - `analytics_retail`: Houses sanitized staging tables and analytical dimensional/mart tables built by dbt.
- Serverless, highly scalable, columnar query execution engine.

### Component 5: Data Transformation & Modeling (dbt Core)
- SQL-first modeling using Jinja templating.
- Separation into:
  - **Staging (`stg_orders`)**: Cleanses raw ingestion artifacts, standardizes types, and filters anomalies.
  - **Marts (`sales_by_product`, `sales_by_region`, `monthly_sales`)**: Business-oriented dimensional aggregates ready for analytical consumption.

### Component 6: Quality Validation & Testing
- Automated dbt schema tests (Unique, Not Null, Accepted Values, Relationships).
- Python reconciliation audits verifying row count integrity from PostgreSQL to BigQuery.

---

## 2. Integration with Member 2
- **Airflow DAGs (Member 2)**: Triggers the Airbyte sync job, waits for completion, triggers `dbt run` and `dbt test`, and verifies table freshness.
- **Conversational BI (Member 2)**: Connects to `analytics_retail` tables via Streamlit to allow users to ask conversational business questions in plain English (e.g. "Which region generated the highest revenue last month?").

