# RetailPulse: Google BigQuery Warehouse Setup Guide

This guide walks you through setting up **Google BigQuery** as the cloud data warehouse for the **RetailPulse** project. It is designed to be beginner-friendly while adhering strictly to enterprise security and least-privilege standards.

---

## 1. Google Cloud Free Tier & BigQuery Sandbox

You **do not** need to enter credit card details or enable paid billing to complete this microproject.

### BigQuery Sandbox Capabilities:
- **10 GB** of free active storage every month.
- **1 TB** of free query data processing every month.
- **Cost:** \$0.00.
- **Limitation:** Tables in sandbox mode have a default expiration of **60 days** (which is more than enough for a college microproject).
- **Billing Warning:** Do **NOT** upgrade to a paid billing account unless explicitly required. The sandbox provides all features needed by Airbyte and dbt for this project.

---

## 2. Step 1: Create or Select a Google Cloud Project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. At the top navigation bar, click the **Project Dropdown** (next to the "Google Cloud" logo).
4. Click **New Project** (top right of the modal window).
5. Enter a project name, e.g., `retailpulse-de-project`.
6. Notice the generated **Project ID** underneath the project name (e.g., `retailpulse-de-project-456789`).
   > [!IMPORTANT]
   > The **Project ID** is globally unique and immutable. Note this down — this is what Airbyte, dbt, and BigQuery SQL queries will reference, **not** the project name.
7. Click **Create** and wait a few seconds for the notification confirming project creation.
8. Switch to the newly created project using the project dropdown.

---

## 3. Step 2: Verify BigQuery API is Enabled

For modern Google Cloud projects, the BigQuery API is enabled by default. To verify:
1. In the search bar at the top, type `BigQuery API`.
2. Click **BigQuery API** from the Marketplace / API results.
3. If the button displays **API Enabled**, no action is needed.
4. If it shows **Enable**, click **Enable**.

---

## 4. Step 3: Open BigQuery Studio

1. In the navigation menu (left hamburger menu) or top search bar, navigate to **BigQuery** &rarr; **BigQuery Studio**.
2. If prompted with a welcome or "Sandbox" banner, dismiss it.
3. In the left panel labeled **Explorer**, you will see your project ID pinned.

---

## 5. Step 4: The 3-Tier Naming Hierarchy

BigQuery organizes data in a strict 3-tier hierarchy:
```
[Google Cloud Project ID] . [Dataset ID] . [Table ID]
      e.g. retailpulse-de-12345.raw_retail.orders
```

| Hierarchy Level | Analogy in Relational DB | Purpose in RetailPulse |
| :--- | :--- | :--- |
| **Project ID** | Server / Cluster Instance | The overall GCP container housing all cloud resources. |
| **Dataset ID** | Database Schema / Database | Logical groupings of tables with shared region and access control. |
| **Table ID** | Table / View | The actual physical storage of transactional or analytical records. |

---

## 6. Step 5: Create the Two Required Datasets

You need two distinct datasets to maintain a clean separation between raw ingested data and modeled analytics:

1. `raw_retail`: Receives the raw sync from PostgreSQL via Airbyte.
2. `analytics_retail`: Stores the clean staging and mart models created by dbt.

### CRITICAL: Dataset Region / Location Rule
> [!CAUTION]
> **Both datasets MUST reside in the exact same region** (e.g., Multi-region `US` or Single-region `asia-south1 (Mumbai)`).
> BigQuery **cannot** join or query across tables located in different regions!

---

### Option A: Create Datasets via BigQuery Studio UI (Manual)

#### Creating `raw_retail`:
1. In the **Explorer** panel, locate your Project ID.
2. Click the three vertical dots (**Actions**) next to your project ID and select **Create dataset**.
3. Fill in the modal form:
   - **Dataset ID:** `raw_retail`
   - **Location type:** Multi-region &rarr; `US (multiple regions in United States)` (or your preferred region).
   - **Default table expiration:** Leave unchecked (or default if Sandbox).
   - **Encryption:** Google-managed encryption key (default).
4. Click **Create dataset**.

#### Creating `analytics_retail`:
1. Click the three dots next to your project ID again &rarr; **Create dataset**.
2. Fill in:
   - **Dataset ID:** `analytics_retail`
   - **Location type:** Select the **exact same location** chosen for `raw_retail` (e.g., `US`).
3. Click **Create dataset**.

---

### Option B: Create Datasets via SQL in BigQuery Studio

Open an SQL query tab in BigQuery Studio and run:

```sql
-- Replace 'US' with your chosen region if different
CREATE SCHEMA IF NOT EXISTS `raw_retail`
OPTIONS (
  location = 'US',
  description = 'Raw retail sales data ingested from PostgreSQL via Airbyte'
);

CREATE SCHEMA IF NOT EXISTS `analytics_retail`
OPTIONS (
  location = 'US',
  description = 'Analytics-ready data marts transformed via dbt Core'
);
```

---

## 7. Step 6: Security & IAM Authentication

To allow Airbyte and dbt to communicate with BigQuery securely without using your personal Google credentials:
- We create dedicated **Service Accounts**.
- We download a **JSON Key File** to a secure, git-ignored local directory (`keys/`).
- We assign **Least-Privilege Roles** so each tool only accesses what it needs.

For complete, step-by-step instructions on setting up service accounts and exact permissions, consult:
&rarr; [bigquery_permissions.md](file:///c:/Users/Swapnaja/OneDrive/Desktop/RetailPulse/docs/bigquery_permissions.md)

---

## 8. Step 7: Verification SQL

Once your datasets are created, use the query script in [verify_bigquery.sql](file:///c:/Users/Swapnaja/OneDrive/Desktop/RetailPulse/sql/verify_bigquery.sql) to check schema existence and inspect data at each stage of the pipeline.

