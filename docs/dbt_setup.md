# RetailPulse: dbt Core & Google BigQuery Setup Guide

This guide explains how **dbt Core (data build tool)** is structured, configured, and connected to **Google BigQuery** for Phase 5 of the **RetailPulse** project.

---

## 1. Core dbt Concepts for College Viva

### What is dbt Core?
dbt Core is an open-source command-line transformation framework that operates on the **"T" (Transform)** in modern **ELT** architectures. 
- Instead of extracting data out of the warehouse to transform it using external servers (like legacy ETL), dbt compiles modular SQL and Jinja templates into raw SQL queries that execute **directly inside the cloud warehouse (BigQuery)**.
- dbt handles dependencies, generates data lineage DAGs, builds automated testing, and documents data definitions.

### What are dbt Adapters?
dbt Core itself is database-agnostic. To talk to specific data warehouses, it uses **adapters** (e.g., `dbt-bigquery`, `dbt-snowflake`, `dbt-postgres`).
- The `dbt-bigquery` adapter translates dbt commands into GoogleSQL, manages BigQuery API jobs, creates BigQuery tables/views, and handles GCP authentication.

---

## 2. Configuration Files: `dbt_project.yml` vs. `profiles.yml`

A common viva question is the architectural difference between these two files:

| Characteristic | `dbt_project.yml` | `profiles.yml` |
| :--- | :--- | :--- |
| **Location** | Project repository root (`dbt/retailpulse_dbt/`) | User home directory (`~/.dbt/profiles.yml`) |
| **Committed to Git?** | **YES** (Public, shared across team) | **NO** (Strictly private & gitignored) |
| **Purpose** | Defines model paths, naming, materialization strategies (`view` vs `table`), and project configurations. | Contains connection targets, credentials, private keys, database hosts, and tokens. |
| **Why Separate?** | Code portability: anyone can clone the repo and run it using their own environment without exposing credentials. | Security: prevents leaking database passwords or cloud service account keys into GitHub. |

---

## 3. Configuring `profiles.yml` on Windows

On Windows, dbt searches for the profile file at:
```text
%USERPROFILE%\.dbt\profiles.yml
(e.g., C:\Users\Swapnaja\.dbt\profiles.yml)
```

### Step 1: Create the `.dbt` Directory in User Home
Open Windows PowerShell:
```powershell
New-Item -ItemType Directory -Path "$HOME\.dbt" -Force
```

### Step 2: Create and Configure `profiles.yml`
Create or edit `$HOME\.dbt\profiles.yml`:

```yaml
retailpulse:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: YOUR_ACTUAL_GCP_PROJECT_ID    # Replace with your GCP project ID
      dataset: analytics_retail               # Target dataset for dbt models
      threads: 4
      keyfile: C:\Users\Swapnaja\OneDrive\Desktop\RetailPulse\keys\gcp_service_account.json
      timeout_seconds: 300
      location: US                            # Must match raw_retail dataset region
      priority: interactive
```

> [!TIP]
> **Alternative: OAuth via `gcloud` (Application Default Credentials)**
> If you have the Google Cloud SDK (`gcloud`) installed on Windows, you can authenticate via browser without a keyfile:
> 1. Run: `gcloud auth application-default login`
> 2. Change `method: service-account` to `method: oauth` and remove the `keyfile` line.

---

## 4. Separation of Responsibilities: Member 1 vs. Member 2

To prevent dependency clashes:
- **Member 1 (Data Engineering):** Operates locally with `dbt-core` and `dbt-bigquery` installed in their isolated virtual environment. Member 1 creates, tests, and models the staging and mart SQL files.
- **Member 2 (Airflow Orchestration):** Runs Airflow in Docker or a separate virtual environment. Member 2 triggers dbt via the `BashOperator` (running `dbt run --project-dir ...`) or Cosmos/Airflow dbt provider. This keeps Airflow's strict dependency pins from breaking dbt's packages.

---

## 5. Verification Commands & Initial Diagnostic

To test your dbt installation and BigQuery connectivity:

```powershell
# Navigate into the dbt project folder
cd c:\Users\Swapnaja\OneDrive\Desktop\RetailPulse\dbt\retailpulse_dbt

# Check installed version
dbt --version

# Run diagnostic connection check
dbt debug
```

---

## 6. Troubleshooting Connection Errors (`dbt debug`)

### Error 1: `Could not find profile named 'retailpulse'`
- **Cause:** `profiles.yml` is missing in `$HOME\.dbt/` or the root key in `profiles.yml` does not match `profile: 'retailpulse'` defined in `dbt_project.yml`.
- **Fix:** Ensure `$HOME\.dbt\profiles.yml` exists and starts with `retailpulse:`.

### Error 2: `403 Access Denied / The caller does not have permission`
- **Cause:** The service account lacks permissions in GCP.
- **Fix:** Ensure the service account has `roles/bigquery.jobUser` on the project and `roles/bigquery.dataEditor` on the `analytics_retail` dataset.

### Error 3: `404 Not Found: Dataset analytics_retail was not found`
- **Cause:** The dataset has not been created yet in BigQuery Studio.
- **Fix:** Open BigQuery Studio and run:
  ```sql
  CREATE SCHEMA IF NOT EXISTS `analytics_retail` OPTIONS (location = 'US');
  ```

### Error 4: `Keyfile does not exist`
- **Cause:** The path specified in `keyfile:` does not point to a valid file.
- **Fix:** Verify that `keys/gcp_service_account.json` exists and that the absolute path in `profiles.yml` is formatted correctly with standard backslashes or forward slashes.

### Error 5: `Dataset was not found in location US`
- **Cause:** `raw_retail` was created in a different region (e.g. `asia-south1`) than the `location:` specified in `profiles.yml` (e.g. `US`).
- **Fix:** Align the `location:` parameter in `profiles.yml` to match the exact location of your BigQuery datasets.
