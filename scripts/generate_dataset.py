"""
RetailPulse - Phase 1: Synthetic Retail Sales Dataset Generator
Script: scripts/generate_dataset.py

Purpose:
    Generates a deterministic, reproducible synthetic retail dataset of exactly
    500 transactional records for the RetailPulse Data Engineering pipeline.

Required Columns:
    1. order_id: Unique integer identifier
    2. order_date: ISO date (YYYY-MM-DD) between 2025-11-01 and 2026-10-31
    3. product: Realistic consumer electronic/accessory product name
    4. region: Geographical sales region
    5. quantity: Positive integer between 1 and 5
    6. unit_price: Realistic INR price based on product type

Note:
    Per project contract, NO revenue column is included in raw data.
    Revenue will be calculated downstream in dbt transformations.
"""

import csv
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


# ==============================================================================
# CONFIGURATION & REPRODUCIBILITY
# ==============================================================================
RANDOM_SEED = 42
TOTAL_RECORDS = 500
START_ORDER_ID = 1001

# Continuous 12-month period: November 1, 2025 to October 31, 2026
START_DATE = date(2025, 11, 1)
END_DATE = date(2026, 10, 31)

# Target output path
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "retail_sales.csv"

# Catalog definition: Products, typical INR prices, and relative market weights
PRODUCT_CATALOG = {
    "Laptop": {"price": 65000.00, "weight": 12},
    "Smartphone": {"price": 28000.00, "weight": 22},
    "Tablet": {"price": 22000.00, "weight": 10},
    "Monitor": {"price": 14500.00, "weight": 14},
    "Headphones": {"price": 2499.00, "weight": 18},
    "Keyboard": {"price": 1299.00, "weight": 12},
    "Mouse": {"price": 699.00, "weight": 12},
}

# Regional markets
REGIONS = ["West", "North", "South", "East", "Central"]
REGION_WEIGHTS = [25, 25, 20, 15, 15]

QUANTITIES = [1, 2, 3, 4, 5]
QUANTITY_WEIGHTS = [45, 30, 15, 7, 3]  # Real-world: smaller quantities are more frequent


def generate_dataset() -> list[dict]:
    """Generates 500 deterministic retail sales records."""
    random.seed(RANDOM_SEED)

    # Pre-calculate date range span (365 days)
    delta_days = (END_DATE - START_DATE).days

    products = list(PRODUCT_CATALOG.keys())
    product_weights = [PRODUCT_CATALOG[p]["weight"] for p in products]

    records = []
    # Generate dates across the span and sort them for realistic chronological ordering
    random_day_offsets = [random.randint(0, delta_days) for _ in range(TOTAL_RECORDS)]
    random_day_offsets.sort()

    for idx, day_offset in enumerate(random_day_offsets):
        order_id = START_ORDER_ID + idx
        order_date = START_DATE + timedelta(days=day_offset)

        # Choose product based on weighted market distribution
        chosen_product = random.choices(products, weights=product_weights, k=1)[0]
        unit_price = PRODUCT_CATALOG[chosen_product]["price"]

        # Choose region
        chosen_region = random.choices(REGIONS, weights=REGION_WEIGHTS, k=1)[0]

        # Choose quantity (1 to 5)
        chosen_quantity = random.choices(QUANTITIES, weights=QUANTITY_WEIGHTS, k=1)[0]

        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "product": chosen_product,
            "region": chosen_region,
            "quantity": chosen_quantity,
            "unit_price": f"{unit_price:.2f}",
        })

    return records


def save_dataset_to_csv(records: list[dict], file_path: Path) -> None:
    """Writes dataset records to a CSV file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["order_id", "order_date", "product", "region", "quantity", "unit_price"]

        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    except OSError as err:
        print(f"[ERROR] Failed to write CSV file at {file_path}: {err}", file=sys.stderr)
        sys.exit(1)


def validate_dataset(file_path: Path) -> None:
    """Validates the written CSV file according to data engineering rules."""
    if not file_path.is_file():
        print(f"[ERROR] CSV file does not exist at {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))

    total_records = len(reader)
    order_ids = [row["order_id"] for row in reader]
    unique_orders = set(order_ids)
    duplicate_count = total_records - len(unique_orders)

    # Check missing values
    missing_value_counts = {field: 0 for field in reader[0].keys()}
    for row in reader:
        for key, val in row.items():
            if val is None or str(val).strip() == "":
                missing_value_counts[key] += 1

    total_missing = sum(missing_value_counts.values())

    # Date range analysis
    dates = [datetime.strptime(row["order_date"], "%Y-%m-%d").date() for row in reader]
    min_date = min(dates)
    max_date = max(dates)

    # Display Validation Report
    print("=" * 70)
    print(" RetailPulse - Phase 1 Dataset Validation Report")
    print("=" * 70)
    print(f"File Path:            {file_path}")
    print(f"Total Records:        {total_records} (Expected: {TOTAL_RECORDS})")
    print(f"Unique Order IDs:     {len(unique_orders)}")
    print(f"Duplicate Order IDs:  {duplicate_count}")
    print(f"Total Missing Values: {total_missing}")
    print(f"Date Range:           {min_date} to {max_date}")
    print("-" * 70)
    print("Missing Values by Column:")
    for col, count in missing_value_counts.items():
        print(f"  - {col:<15}: {count}")

    # Integrity Assertions
    assert total_records == TOTAL_RECORDS, f"Expected {TOTAL_RECORDS} records, found {total_records}."
    assert duplicate_count == 0, f"Found {duplicate_count} duplicate order IDs."
    assert total_missing == 0, f"Found {total_missing} missing values."
    assert min_date >= START_DATE, f"Min date {min_date} before start date {START_DATE}."
    assert max_date <= END_DATE, f"Max date {max_date} after end date {END_DATE}."

    print("-" * 70)
    print("Sample Records (First 5):")
    print(f"{'order_id':<10} {'order_date':<12} {'product':<14} {'region':<10} {'quantity':<10} {'unit_price (INR)':<15}")
    for row in reader[:5]:
        print(f"{row['order_id']:<10} {row['order_date']:<12} {row['product']:<14} {row['region']:<10} {row['quantity']:<10} {row['unit_price']:<15}")

    print("-" * 70)
    print("Sample Records (Last 5):")
    for row in reader[-5:]:
        print(f"{row['order_id']:<10} {row['order_date']:<12} {row['product']:<14} {row['region']:<10} {row['quantity']:<10} {row['unit_price']:<15}")

    print("=" * 70)
    print("VALIDATION STATUS: SUCCESS - Dataset meets all specifications.")
    print("=" * 70)


def main():
    print(f"[INFO] Generating deterministic dataset (Seed={RANDOM_SEED})...")
    records = generate_dataset()
    save_dataset_to_csv(records, OUTPUT_FILE)
    print(f"[INFO] Successfully wrote {len(records)} records to {OUTPUT_FILE}")
    print("[INFO] Running data quality audit and validation...")
    validate_dataset(OUTPUT_FILE)


if __name__ == "__main__":
    main()

