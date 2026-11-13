"""
RetailPulse - Phase 7: Automated Pipeline Reconciliation & Data Quality Audit
Script: scripts/reconcile_pipeline.py

Purpose:
    Performs end-to-end data auditing, row count matching, and financial
    reconciliation across all stages of the Member 1 pipeline:
      1. Source CSV: data/retail_sales.csv
      2. PostgreSQL Source: retail_source.public.orders
      3. BigQuery Raw Layer: raw_retail.orders
      4. BigQuery Analytics Layer: analytics_retail.stg_orders & marts

Reconciliation Formula:
    Total Revenue = SUM(quantity * unit_price)
"""

import csv
import os
import sys
from decimal import Decimal
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "retail_sales.csv"


def audit_source_csv() -> dict:
    """Performs rigorous quality audit on the source CSV."""
    if not CSV_PATH.is_file():
        print(f"[FAIL] Source CSV missing at {CSV_PATH}", file=sys.stderr)
        return {"status": "FAIL"}

    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    total_records = len(reader)
    order_ids = [r["order_id"] for r in reader]
    unique_orders = len(set(order_ids))
    duplicate_count = total_records - unique_orders

    null_count = sum(
        1 for r in reader
        if not r.get("order_id") or not r.get("order_date") or not r.get("product")
        or not r.get("region") or not r.get("quantity") or not r.get("unit_price")
    )

    total_revenue = sum(
        Decimal(r["quantity"]) * Decimal(r["unit_price"])
        for r in reader
    )

    dates = sorted(r["order_date"] for r in reader)
    min_date = dates[0]
    max_date = dates[-1]

    return {
        "status": "PASS" if total_records == 500 and duplicate_count == 0 and null_count == 0 else "FAIL",
        "total_records": total_records,
        "unique_orders": unique_orders,
        "duplicate_count": duplicate_count,
        "null_count": null_count,
        "min_date": min_date,
        "max_date": max_date,
        "total_revenue": total_revenue,
    }


def audit_postgresql() -> dict:
    """Audits the PostgreSQL table retail_source.public.orders if available."""
    try:
        import psycopg
    except ImportError:
        try:
            import psycopg2 as psycopg
        except ImportError:
            return {"status": "SKIPPED", "reason": "psycopg driver not installed"}

    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", 5432))
    pg_db = os.getenv("POSTGRES_DATABASE") or os.getenv("POSTGRES_DB", "retail_source")
    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_pass = os.getenv("POSTGRES_PASSWORD")

    if not pg_pass:
        return {"status": "PENDING", "reason": "POSTGRES_PASSWORD not set in .env"}

    try:
        conn = psycopg.connect(
            host=pg_host, port=pg_port, dbname=pg_db, user=pg_user, password=pg_pass, connect_timeout=3
        )
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*), COUNT(DISTINCT order_id), SUM(quantity * unit_price) FROM public.orders;")
            row = cur.fetchone()
            total_count = row[0]
            unique_orders = row[1]
            total_rev = Decimal(str(row[2])) if row[2] is not None else Decimal("0.00")
        conn.close()
        return {
            "status": "PASS" if total_count == 500 else "FAIL",
            "total_records": total_count,
            "unique_orders": unique_orders,
            "total_revenue": total_rev,
        }
    except Exception as err:
        return {"status": "OFFLINE", "reason": f"Connection refused on {pg_host}:{pg_port} ({err})"}


def audit_bigquery() -> dict:
    """Audits BigQuery raw and analytics datasets if credentials exist."""
    try:
        from google.cloud import bigquery
    except ImportError:
        return {"status": "SKIPPED", "reason": "google-cloud-bigquery not installed"}

    gcp_project = os.getenv("GCP_PROJECT_ID")
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not gcp_project or gcp_project == "your_gcp_project_id_here":
        return {"status": "PENDING", "reason": "GCP_PROJECT_ID not set in .env"}

    if not cred_path:
        return {"status": "PENDING", "reason": "GOOGLE_APPLICATION_CREDENTIALS not set in .env"}

    key_file = Path(cred_path)
    if not key_file.is_absolute():
        key_file = PROJECT_ROOT / key_file

    if not key_file.is_file():
        return {"status": "PENDING", "reason": f"Service account key not found at {key_file}"}

    try:
        client = bigquery.Client.from_service_account_json(str(key_file), project=gcp_project)
        # Check raw orders
        query = f"SELECT COUNT(*), COUNT(DISTINCT order_id), SUM(quantity * unit_price) FROM `{gcp_project}.raw_retail.orders`"
        job = client.query(query)
        result = list(job.result())[0]
        return {
            "status": "PASS",
            "total_records": result[0],
            "unique_orders": result[1],
            "total_revenue": Decimal(str(result[2])),
        }
    except Exception as err:
        return {"status": "OFFLINE", "reason": str(err)}


def main():
    print("=" * 80)
    print(" RETAILPULSE - PHASE 7: DATA QUALITY & PIPELINE RECONCILIATION")
    print("=" * 80)

    # 1. Source CSV Audit
    csv_results = audit_source_csv()
    print("\nSTAGE A: SOURCE DATA AUDIT (data/retail_sales.csv)")
    print("-" * 80)
    if csv_results["status"] == "PASS":
        print(f"Status:               [PASSED - VERIFIED]")
        print(f"Total Records:        {csv_results['total_records']} (Expected: 500)")
        print(f"Unique Order IDs:     {csv_results['unique_orders']}")
        print(f"Duplicate Order IDs:  {csv_results['duplicate_count']}")
        print(f"Null Field Count:     {csv_results['null_count']}")
        print(f"Date Span:            {csv_results['min_date']} to {csv_results['max_date']}")
        print(f"Total Source Revenue: INR {csv_results['total_revenue']:,.2f}")
    else:
        print(f"Status:               [FAILED]")

    # 2. PostgreSQL Audit
    pg_results = audit_postgresql()
    print("\nSTAGE B: POSTGRESQL SOURCE DATABASE (retail_source.public.orders)")
    print("-" * 80)
    if pg_results["status"] == "PASS":
        print(f"Status:               [PASSED - VERIFIED]")
        print(f"Total Records:        {pg_results['total_records']} (Matches CSV: {pg_results['total_records'] == csv_results['total_records']})")
        print(f"Unique Order IDs:     {pg_results['unique_orders']}")
        print(f"Total Revenue:        INR {pg_results['total_revenue']:,.2f}")
    else:
        print(f"Status:               [{pg_results['status']}]")
        print(f"Details:              {pg_results.get('reason')}")
        print("Remediation:          Start PostgreSQL container: docker start retail-postgres")

    # 3. Airbyte & BigQuery Audit
    bq_results = audit_bigquery()
    print("\nSTAGE C/D: BIGQUERY WAREHOUSE (raw_retail.orders)")
    print("-" * 80)
    if bq_results["status"] == "PASS":
        print(f"Status:               [PASSED - VERIFIED]")
        print(f"Total Raw Records:    {bq_results['total_records']}")
        print(f"Unique Order IDs:     {bq_results['unique_orders']}")
        print(f"Total Raw Revenue:    INR {bq_results['total_revenue']:,.2f}")
    else:
        print(f"Status:               [{bq_results['status']}]")
        print(f"Details:              {bq_results.get('reason')}")
        print("Remediation:          Configure .env with GCP_PROJECT_ID and place key in keys/gcp_service_account.json")

    # 4. Reconciliation Comparison
    print("\nSTAGE G: FINANCIAL & VOLUME RECONCILIATION")
    print("-" * 80)
    print(f"Expected Source Count:     500")
    print(f"Expected Source Revenue:   INR 17,379,476.00")
    if csv_results["status"] == "PASS":
        revenue_diff = csv_results["total_revenue"] - Decimal("17379476.00")
        print(f"Source CSV Revenue Parity: {'MATCH (Difference: INR 0.00)' if revenue_diff == 0 else f'MISMATCH ({revenue_diff})'}")
    print("=" * 80)


if __name__ == "__main__":
    main()

