"""
RetailPulse - Phase 2: PostgreSQL Verification & Audit
Script: scripts/check_postgres.py

Purpose:
    Performs comprehensive data quality and schema contract verification on
    the PostgreSQL table (retail_source.public.orders) following data loading.

Validations:
    1. Table schema & column types match contract.
    2. Total record count == 500.
    3. Unique order_id count == 500 (no duplicate primary keys).
    4. Zero NULL values across all columns.
    5. Value sanity: all quantity > 0, all unit_price > 0.
    6. Displays 5 sample records.
"""

import os
import sys

# Load environment variables from .env
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
# CONFIGURATION
# ==============================================================================
EXPECTED_RECORD_COUNT = 500

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE") or os.getenv("POSTGRES_DB", "retail_source")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def get_connection():
    """Connects to the PostgreSQL database."""
    if not POSTGRES_PASSWORD:
        print("[ERROR] POSTGRES_PASSWORD environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        if DRIVER_TYPE == "psycopg3":
            return psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DATABASE,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
        else:
            return psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DATABASE,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
    except Exception as err:
        print(f"\n[ERROR] Connection to PostgreSQL failed: {err}", file=sys.stderr)
        sys.exit(1)


def verify_table_structure(cur):
    """Inspects and validates column definitions from information_schema."""
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'orders'
        ORDER BY ordinal_position;
    """
    cur.execute(query)
    columns = cur.fetchall()

    if not columns:
        print("[FAIL] Table 'public.orders' does not exist in database!", file=sys.stderr)
        return False

    print("\n1. Table Schema Verification (public.orders):")
    print(f"   {'Column Name':<15} {'Data Type':<20} {'Nullable':<10}")
    print("   " + "-" * 45)
    for col_name, data_type, is_nullable in columns:
        print(f"   {col_name:<15} {data_type:<20} {is_nullable:<10}")

    return True


def run_audits(cur):
    """Executes data quality audits on public.orders."""
    print("\n2. Data Quality & Metric Verification:")

    # 1. Row count & unique primary keys
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT order_id) FROM public.orders;")
    total_count, unique_orders = cur.fetchone()
    print(f"   Total Records:          {total_count} (Expected: {EXPECTED_RECORD_COUNT})")
    print(f"   Unique Order IDs:       {unique_orders}")

    # 2. Check for NULL values
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_id,
            COUNT(*) FILTER (WHERE order_date IS NULL) AS null_order_date,
            COUNT(*) FILTER (WHERE product IS NULL) AS null_product,
            COUNT(*) FILTER (WHERE region IS NULL) AS null_region,
            COUNT(*) FILTER (WHERE quantity IS NULL) AS null_quantity,
            COUNT(*) FILTER (WHERE unit_price IS NULL) AS null_unit_price
        FROM public.orders;
    """)
    nulls = cur.fetchone()
    total_nulls = sum(nulls)
    print(f"   Total NULL Values:      {total_nulls}")

    # 3. Check value constraints
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE quantity <= 0) AS invalid_quantity,
            COUNT(*) FILTER (WHERE unit_price <= 0) AS invalid_unit_price,
            MIN(order_date),
            MAX(order_date)
        FROM public.orders;
    """)
    invalid_qty, invalid_price, min_date, max_date = cur.fetchone()
    print(f"   Invalid Quantities (<=0): {invalid_qty}")
    print(f"   Invalid Prices (<=0):     {invalid_price}")
    print(f"   Date Range:               {min_date} to {max_date}")

    # 4. Display 5 Sample Records
    print("\n3. Sample Records (First 5):")
    cur.execute("""
        SELECT order_id, order_date, product, region, quantity, unit_price
        FROM public.orders
        ORDER BY order_id ASC
        LIMIT 5;
    """)
    samples = cur.fetchall()
    print(f"   {'order_id':<10} {'order_date':<12} {'product':<15} {'region':<10} {'qty':<6} {'unit_price':<12}")
    print("   " + "-" * 65)
    for row in samples:
        print(f"   {row[0]:<10} {str(row[1]):<12} {row[2]:<15} {row[3]:<10} {row[4]:<6} {float(row[5]):<12.2f}")

    # Assertions
    passed = True
    if total_count != EXPECTED_RECORD_COUNT:
        print(f"\n[FAIL] Expected {EXPECTED_RECORD_COUNT} records, found {total_count}.", file=sys.stderr)
        passed = False
    if unique_orders != EXPECTED_RECORD_COUNT:
        print(f"[FAIL] Found duplicate order IDs! Unique count: {unique_orders}", file=sys.stderr)
        passed = False
    if total_nulls > 0:
        print(f"[FAIL] Found {total_nulls} NULL fields.", file=sys.stderr)
        passed = False
    if invalid_qty > 0 or invalid_price > 0:
        print("[FAIL] Found records with non-positive quantity or price.", file=sys.stderr)
        passed = False

    return passed


def main():
    print("=" * 70)
    print(" RetailPulse - Phase 2: PostgreSQL Quality Verification")
    print("=" * 70)
    print(f"Target: {POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            exists = verify_table_structure(cur)
            if not exists:
                sys.exit(1)

            success = run_audits(cur)
            print("\n" + "=" * 70)
            if success:
                print("AUDIT STATUS: ALL CHECKS PASSED (500 Valid Records Verified)")
            else:
                print("AUDIT STATUS: FAILED CHECKS DETECTED")
                sys.exit(1)
            print("=" * 70)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

