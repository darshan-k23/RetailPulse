import csv
from collections import defaultdict
from pathlib import Path

csv_path = Path("data/retail_sales.csv")
with open(csv_path, mode="r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

prod_sales = defaultdict(lambda: {"orders": set(), "qty": 0, "rev": 0.0})
region_sales = defaultdict(lambda: {"orders": set(), "qty": 0, "rev": 0.0})
monthly_sales = defaultdict(lambda: {"orders": set(), "qty": 0, "rev": 0.0})

for r in rows:
    oid = r["order_id"]
    dt = r["order_date"][:7] + "-01"
    p = r["product"]
    reg = r["region"]
    q = int(r["quantity"])
    pr = float(r["unit_price"])
    rev = round(q * pr, 2)

    prod_sales[p]["orders"].add(oid)
    prod_sales[p]["qty"] += q
    prod_sales[p]["rev"] += rev

    region_sales[reg]["orders"].add(oid)
    region_sales[reg]["qty"] += q
    region_sales[reg]["rev"] += rev

    monthly_sales[dt]["orders"].add(oid)
    monthly_sales[dt]["qty"] += q
    monthly_sales[dt]["rev"] += rev

print("=== SALES BY PRODUCT (Expected analytics_retail.sales_by_product) ===")
print(f"{'product':<15} {'total_orders':<14} {'total_quantity':<16} {'total_revenue (INR)':<20}")
print("-" * 65)
for p, s in sorted(prod_sales.items(), key=lambda x: x[1]["rev"], reverse=True):
    print(f"{p:<15} {len(s['orders']):<14} {s['qty']:<16} {s['rev']:<20.2f}")

print("\n=== SALES BY REGION (Expected analytics_retail.sales_by_region) ===")
print(f"{'region':<15} {'total_orders':<14} {'total_quantity':<16} {'total_revenue (INR)':<20}")
print("-" * 65)
for reg, s in sorted(region_sales.items(), key=lambda x: x[1]["rev"], reverse=True):
    print(f"{reg:<15} {len(s['orders']):<14} {s['qty']:<16} {s['rev']:<20.2f}")

print("\n=== MONTHLY SALES (Expected analytics_retail.monthly_sales) ===")
print(f"{'month_start':<15} {'total_orders':<14} {'total_quantity':<16} {'total_revenue (INR)':<20}")
print("-" * 65)
for dt, s in sorted(monthly_sales.items()):
    print(f"{dt:<15} {len(s['orders']):<14} {s['qty']:<16} {s['rev']:<20.2f}")

