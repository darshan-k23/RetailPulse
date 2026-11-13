"""
RetailPulse - Phase 2: PostgreSQL Data Loader
Script: scripts/load_postgres.py

Purpose:
    Loads retail transaction records from data/retail_sales.csv into the
    PostgreSQL table (retail_source.public.orders) using parameterized SQL
    and transactional execution.

Design & Safety:
    - Reads connection credentials from environment variables (.env).
    - Uses upsert (ON CONFLICT DO UPDATE) to prevent duplicate key errors on rerun.
    - Employs transactions with rollback on failure.
    - Compatible with both psycopg (v3) and psycopg2 drivers.
"""

import csv
import os
import sys
from pathlib import Path

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Driver import: prefer psycopg v3, fallback to psycopg2
try:
    import psycopg
    DRIVER_TYPE = "psycopg3"
except ImportError:
    try:
        import psycopg2 as psycopg
        DRIVER_TYPE = "psycopg2"
    except ImportError:
        print("[ERROR] Neither 'psycopg' nor 'psycopg2' is installed.", file=sys.stderr)
        print("Please run: pip install 'psycopg[binary]'", file=sys.stderr)
        sys.exit(1)


# ==============================================================================
# CONFIGURATION & PATH RESOLUTION
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "retail_sales.csv"

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
# Support both POSTGRES_DATABASE and POSTGRES_DB
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE") or os.getenv("POSTGRES_DB", "retail_source")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    if not POSTGRES_PASSWORD:
        print("[ERROR] POSTGRES_PASSWORD environment variable is not set.", file=sys.stderr)
        print("Please configure your .env file with your PostgreSQL password.", file=sys.stderr)
        sys.exit(1)

    try:
        if DRIVER_TYPE == "psycopg3":
            conn = psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DATABASE,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
        else:
            conn = psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DATABASE,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
        return conn

    except Exception as err:
        print("\n" + "=" * 70, file=sys.stderr)
        print("[ERROR] Could not connect to PostgreSQL database.", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"Details:  {err}", file=sys.stderr)
        print(f"Target:   {POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}", file=sys.stderr)
        print("\nTroubleshooting tips:", file=sys.stderr)
        print("1. Ensure PostgreSQL is installed and the service is actively running.", file=sys.stderr)
        print("2. Verify that database 'retail_source' exists (run init.sql).", file=sys.stderr)
        print("3. Check credentials in your .env file.", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)


def read_csv_data(file_path: Path) -> list[tuple]:
    """Reads and validates the CSV rows prior to database loading."""
    if not file_path.is_file():
        print(f"[ERROR] CSV dataset not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        expected_cols = {"order_id", "order_date", "product", "region", "quantity", "unit_price"}
        if not expected_cols.issubset(reader.fieldnames):
            print(f"[ERROR] CSV header mismatch. Expected {expected_cols}, got {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)

        for line_no, row in enumerate(reader, start=2):
            try:
                order_id = int(row["order_id"])
                order_date = row["order_date"]
                product = row["product"].strip()
                region = row["region"].strip()
                quantity = int(row["quantity"])
                unit_price = float(row["unit_price"])

                rows.append((order_id, order_date, product, region, quantity, unit_price))
            except ValueError as err:
                print(f"[ERROR] Corrupted record at line {line_no}: {err}", file=sys.stderr)
                sys.exit(1)

    return rows


def load_data(conn, rows: list[tuple]) -> tuple[int, int]:
    """
    Inserts data into public.orders using safe parameterized SQL with UPSERT.
    Returns (processed_count, total_in_table).
    """
    insert_sql = """
        INSERT INTO public.orders (order_id, order_date, product, region, quantity, unit_price)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO UPDATE SET
            order_date  = EXCLUDED.order_date,
            product     = EXCLUDED.product,
            region      = EXCLUDED.region,
            quantity    = EXCLUDED.quantity,
            unit_price  = EXCLUDED.unit_price;
    """

    count_sql = "SELECT COUNT(*) FROM public.orders;"

    try:
        with conn.cursor() as cur:
            # First, ensure table exists as per init.sql
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.orders (
                    order_id    INTEGER PRIMARY KEY,
                    order_date  DATE NOT NULL,
                    product     VARCHAR(100) NOT NULL,
                    region      VARCHAR(50) NOT NULL,
                    quantity    INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price  NUMERIC(12, 2) NOT NULL CHECK (unit_price > 0)
                );
            """)

            print(f"[INFO] Executing batch upsert for {len(rows)} records...")
            cur.executemany(insert_sql, rows)

            # Query total records currently stored in the table
            cur.execute(count_sql)
            total_count = cur.fetchone()[0]

        # Commit the transaction
        conn.commit()
        return len(rows), total_count

    except Exception as err:
        conn.rollback()
        print(f"[ERROR] Transaction rolled back due to error: {err}", file=sys.stderr)
        sys.exit(1)


def main():
    print("=" * 70)
    print(" RetailPulse - Phase 2: PostgreSQL Data Ingestion")
    print("=" * 70)
    print(f"Driver in use:        {DRIVER_TYPE}")
    print(f"Source CSV:           {CSV_PATH}")
    print(f"Target Database:      {POSTGRES_DATABASE}")
    print(f"Target Table:         public.orders")
    print("-" * 70)

    rows = read_csv_data(CSV_PATH)
    print(f"[INFO] Successfully read {len(rows)} rows from CSV.")

    print(f"[INFO] Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...")
    conn = get_connection()

    try:
        processed, verified_count = load_data(conn, rows)
        print("-" * 70)
        print(f"[SUCCESS] Ingestion completed successfully.")
        print(f"Records Processed:    {processed}")
        print(f"Total Table Rows:     {verified_count}")
        print("=" * 70)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

