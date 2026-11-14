# RetailPulse: Streamlit Conversational BI Technical Reference
### Member 2 — Orchestration & Business Intelligence Lead

This document describes the design, query mapping, conversational intent parsing, and visualization engine of the RetailPulse Conversational BI application (`app/streamlit_app.py`).

---

## 1. Application Architecture

```
   User Natural Language Prompt / One-Click Button
                         │
                         ▼
             Conversational Intent Parser
       (Pattern Matcher & Parameter Extractor)
                         │
                         ▼
        Predefined Parameterized SQL Catalog
          (Zero Raw User SQL / Zero Injection)
                         │
                         ▼
           Warehouse Connection Engine
         (Live BigQuery <---> Local Reconciled Engine)
                         │
                         ▼
          Tabular DataFrame & Plotly Visualizations
```

---

## 2. Approved Business Questions & Exact SQL Mappings

The department guidelines strictly forbid executing arbitrary, un-sanitized SQL strings from users. The application maps every supported inquiry to deterministic, reviewed SQL templates:

### Question 1: Highest-Revenue Product
- **Business Inquiry:** *"Which product generated the highest revenue?"*
- **Target Mart:** `analytics_retail.sales_by_product`
- **SQL Template:**
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
- **Ground Truth Result:**
  - Product: **Laptop**
  - Total Orders: **60**
  - Total Quantity: **106 units**
  - Total Gross Revenue: **₹6,890,000.00 INR**

---

### Question 2: Highest-Sales Region
- **Business Inquiry:** *"Which region recorded the highest sales?"*
- **Target Mart:** `analytics_retail.sales_by_region`
- **SQL Template:**
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
- **Ground Truth Result:**
  - Region: **South**
  - Total Orders: **123**
  - Total Quantity: **260 units**
  - Total Gross Revenue: **₹4,823,494.00 INR**

---

### Question 3: Monthly Revenue Trend
- **Business Inquiry:** *"How does revenue change month by month?"*
- **Target Mart:** `analytics_retail.monthly_sales`
- **SQL Template:**
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
- **Ground Truth Result:**
  - 12 consecutive months (2025-11-01 to 2026-10-01)
  - Peak Month: **May 2026** (₹1,972,778.00 INR)
  - Cumulative Annual Total: **₹17,379,476.00 INR**

---

### Question 4 (Dynamic Conversational Filter): Specific Transactions
- **Business Inquiry:** *"Show all laptop transactions in South region"*
- **Target Mart:** `analytics_retail.stg_orders`
- **SQL Template:**
  ```sql
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

## 3. High-Reliability Fallback Engine

In college lab presentations, cloud networks or BigQuery trial credits may periodically drop or expire. RetailPulse addresses this with a dual-mode engine:
1. **Live BigQuery Mode:** If valid GCP service account credentials exist in `.env`, the app queries Google Cloud BigQuery directly using `google-cloud-bigquery`.
2. **Reconciled Local Mode:** If cloud credentials are not supplied or network fails, the application uses an in-memory SQL execution engine over `data/retail_sales.csv` applying the exact same SQL logic and transformations as dbt.
3. **Parity Guarantee:** Both modes return identical row counts, currency sums, and order numbers down to the exact paisa (₹17,379,476.00 INR).
