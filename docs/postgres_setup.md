# RetailPulse: PostgreSQL Source Database Setup Guide

This guide provides step-by-step instructions for installing, configuring, initializing, and populating the PostgreSQL source database (`retail_source`) for the **RetailPulse** project.

---

## 1. Prerequisites & Installation Options

You can run PostgreSQL using either **Docker** (recommended since Docker Desktop is already installed) or the **Native Windows Installer**.

### Option A: Run PostgreSQL via Docker (Fastest & Cleanest)

Since Docker Desktop is installed and running on your system, you can start a production-grade PostgreSQL 16 instance with a single PowerShell command:

```powershell
docker run -d `
  --name retail-postgres `
  -p 5432:5432 `
  -e POSTGRES_DB=retail_source `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -v postgres_retail_data:/var/lib/postgresql/data `
  postgres:16
```

To verify the container is running:
```powershell
docker ps --filter "name=retail-postgres"
```

---

### Option B: Native Windows Installer (EnterpriseDB)

If you prefer installing PostgreSQL directly on Windows without Docker:

1. **Download:**
   - Visit the official PostgreSQL download portal: [https://www.enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
   - Select **PostgreSQL 16** (or 15) for **Windows x86-64**.

2. **Installation Wizard:**
   - Run the downloaded `.exe` installer.
   - Accept default components (PostgreSQL Server, pgAdmin 4, Command Line Tools).
   - Set a master password for user `postgres` (e.g., `postgres` or a password of your choice; make sure to write it down!).
   - Keep default port: `5432`.
   - Locale: Default.
   - Click Next and finish installation.

3. **Add `psql` to Windows System PATH:**
   - Default install path: `C:\Program Files\PostgreSQL\16\bin`
   - Add this directory to your User or System `PATH` environment variable so `psql` is accessible in any terminal window.

---

## 2. Database Creation & Schema Initialization

### For Docker Users:
The database `retail_source` is created automatically on container startup when using `-e POSTGRES_DB=retail_source`.

To apply `database/init.sql` directly into the container:
```powershell
# Copy init.sql into container and run psql
docker cp database/init.sql retail-postgres:/tmp/init.sql
docker exec -i retail-postgres psql -U postgres -d retail_source -f /tmp/init.sql
```

### For Native Windows Users:
Open PowerShell:

```powershell
# 1. Connect to default postgres database to create retail_source
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE retail_source;"

# 2. Run the initialization script
psql -U postgres -h localhost -p 5432 -d retail_source -f database/init.sql
```

*(Alternatively, open **pgAdmin 4**, connect to your server, right-click Databases &rarr; Create &rarr; Database `retail_source`, open the Query Tool, and paste `database/init.sql`)*

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` (if not already done) and configure the variables:

```ini
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=retail_source
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```
*(Replace `postgres` with your actual chosen password if different).*

---

## 4. Loading the Retail Sales CSV Data

Run the Python ingestion script:

```powershell
# Using your Python virtual environment or local Python
python scripts/load_postgres.py
```

### Expected Output:
```text
======================================================================
 RetailPulse - Phase 2: PostgreSQL Data Ingestion
======================================================================
Driver in use:        psycopg3
Source CSV:           C:\Users\Swapnaja\OneDrive\Desktop\RetailPulse\data\retail_sales.csv
Target Database:      retail_source
Target Table:         public.orders
----------------------------------------------------------------------
[INFO] Successfully read 500 rows from CSV.
[INFO] Connecting to PostgreSQL at localhost:5432...
[INFO] Executing batch upsert for 500 records...
----------------------------------------------------------------------
[SUCCESS] Ingestion completed successfully.
Records Processed:    500
Total Table Rows:     500
======================================================================
```

---

## 5. Verification & Data Quality Audit

Run the automated verification script:

```powershell
python scripts/check_postgres.py
```

### Audit Checks Performed:
1. **Schema Check:** Inspects `information_schema.columns` to verify that `order_id`, `order_date`, `product`, `region`, `quantity`, and `unit_price` exist with the exact contract data types.
2. **Row Count Check:** Asserts total count equals exactly `500`.
3. **Primary Key Check:** Asserts `500` unique order IDs (no duplicates).
4. **NULL Check:** Asserts 0 nulls across all fields.
5. **Value Check:** Asserts `quantity > 0` and `unit_price > 0`.
6. **Sample Records:** Renders the first 5 records in tabular format.

---

## 6. Common Connection Errors & Fixes

### Error 1: `could not connect to server: Connection refused`
- **Cause:** PostgreSQL service is stopped or container is not running.
- **Fix (Docker):** Run `docker start retail-postgres` and check status via `docker ps`.
- **Fix (Native):** Open Windows Services (`services.msc`), find `postgresql-x64-16`, and click **Start**.

### Error 2: `password authentication failed for user "postgres"`
- **Cause:** Incorrect `POSTGRES_PASSWORD` in `.env`.
- **Fix:** Update `.env` with the exact password chosen during installation or Docker container startup.

### Error 3: `database "retail_source" does not exist`
- **Cause:** The database was not created before running the loader.
- **Fix:** Create it via SQL: `CREATE DATABASE retail_source;`.

### Error 4: `ModuleNotFoundError: No module named 'psycopg'`
- **Fix:** Install the driver in your active environment:
  ```powershell
  pip install "psycopg[binary]"
  ```

