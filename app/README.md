# RetailPulse: Streamlit Conversational BI Application
### Member 2 — Orchestration & Business Intelligence Lead

The RetailPulse BI application exposes transformed dimensional data marts in Google BigQuery through an intuitive Conversational Business Intelligence web interface built with **Streamlit** and **Plotly**.

---

## 1. Core Business Questions Answered

The application maps natural language questions and one-click quick actions to predefined, secure SQL queries over the `analytics_retail` BigQuery dataset:

| Question | Target dbt Mart | SQL Logic | Result Summary |
| :--- | :--- | :--- | :--- |
| **Q1: Highest-revenue product** | `analytics_retail.sales_by_product` | `SELECT product, total_orders, total_quantity, total_revenue FROM analytics_retail.sales_by_product ORDER BY total_revenue DESC LIMIT 1;` | **Laptop** (₹6,890,000.00 INR, 106 units sold across 60 orders) |
| **Q2: Highest-sales region** | `analytics_retail.sales_by_region` | `SELECT region, total_orders, total_quantity, total_revenue FROM analytics_retail.sales_by_region ORDER BY total_revenue DESC LIMIT 1;` | **South** (₹4,823,494.00 INR across 123 orders) |
| **Q3: Monthly revenue trend** | `analytics_retail.monthly_sales` | `SELECT month_start, total_orders, total_quantity, total_revenue FROM analytics_retail.monthly_sales ORDER BY month_start ASC;` | 12 continuous months (Nov 2025 – Oct 2026), peaking in May 2026 at ₹1.97M INR |

---

## 2. Advanced Conversational Capabilities

- **Dynamic Natural Language Filter:**
  - Query: *"Show all laptop transactions in South region"*
  - Target: `analytics_retail.stg_orders`
  - Safely extracts filter parameters (`product = Laptop`, `region = South`) without executing raw user-typed SQL.
- **Visual Analytics:**
  - Interactive Plotly horizontal and vertical bar charts.
  - Smooth spline time-series chart with markers for monthly revenue.
  - Interactive data tables with Indian Rupee (INR) currency formatting.

---

## 3. Resilient Multi-Mode Architecture

The Streamlit app includes an automatic fallback mechanism:
1. **Live Cloud Mode:** Connects to live Google Cloud BigQuery when `GCP_PROJECT_ID` and GCP service account key are configured in `.env`.
2. **Reconciled Local Mode:** Automatically activates if credentials are unavailable. Computes identical dimensional marts directly from `data/retail_sales.csv` using dbt-parity transformations, ensuring 100% reliable viva demonstration even during offline evaluations.

---

## 4. How to Launch Streamlit

```powershell
# Navigate to repository root
cd RetailPulse

# Ensure dependencies are installed
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app/streamlit_app.py
```

The web dashboard opens automatically at `http://localhost:8501`.
