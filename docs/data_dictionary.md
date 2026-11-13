# RetailPulse: Data Dictionary & Dataset Specification

## 1. Overview
- **Dataset File**: `data/retail_sales.csv`
- **Total Records**: 500
- **Time Coverage**: Continuous 12-month period (November 1, 2025 to October 31, 2026)
- **Currency**: Indian Rupee (INR - ₹)
- **Generation Method**: Deterministic, reproducible pseudo-random generation using Python standard library (`random.seed(42)`).

---

## 2. Column Specifications

| Column Name | Data Type | Nullable | Constraints / Domain | Description & Viva Context |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | Integer | No | `1001` - `1500`, Unique | Primary key identifying each individual transaction. No duplicates permitted. |
| `order_date` | Date (ISO 8601) | No | `2025-11-01` to `2026-10-31` | Date on which the sale was recorded (`YYYY-MM-DD`). |
| `product` | String / Text | No | Discrete product catalog | High-demand consumer technology products sold by the retailer. |
| `region` | String / Text | No | `West`, `North`, `South`, `East`, `Central` | Operational retail territory/zone where transaction took place. |
| `quantity` | Integer | No | Integer in range `[1, 5]` | Number of units purchased in the transaction. |
| `unit_price` | Decimal(10,2) | No | Positive Numeric value (INR) | List price per single unit of the product at transaction time. |

---

## 3. Product Catalog & Baseline Pricing (INR)

| Product | Standard Unit Price (INR) | Market Weight (%) | Target Category |
| :--- | :--- | :--- | :--- |
| **Laptop** | ₹65,000.00 | 12% | Computing & Workstations |
| **Smartphone** | ₹28,000.00 | 22% | Mobile Devices |
| **Tablet** | ₹22,000.00 | 10% | Handheld Computing |
| **Monitor** | ₹14,500.00 | 14% | Displays & Peripherals |
| **Headphones** | ₹2,499.00 | 18% | Audio Accessories |
| **Keyboard** | ₹1,299.00 | 12% | Input Peripherals |
| **Mouse** | ₹699.00 | 12% | Input Peripherals |

---

## 4. Geographic Regions

- **West**: High-density urban retail zone (Mumbai, Pune, Ahmedabad).
- **North**: High-volume commercial zone (Delhi NCR, Chandigarh, Jaipur).
- **South**: Technology enterprise retail zone (Bengaluru, Hyderabad, Chennai).
- **East**: Emerging retail zone (Kolkata, Bhubaneswar, Guwahati).
- **Central**: Distributed logistics hub (Bhopal, Indore, Nagpur).

---

## 5. Architectural Rationale: Why No `revenue` Column?

In modern **ELT (Extract, Load, Transform)** data architecture:
1. **Raw Ingestion Integrity**: Operational source systems capture factual transaction events (`quantity`, `unit_price`). Storing calculated fields at the source introduces redundant storage and risks data drift if calculation logic changes.
2. **Separation of Concerns**: Ingestion tools like Airbyte should extract the raw, untouched truth from the source without business logic or schema mutations.
3. **dbt Transformation Responsibility**: Calculating metrics such as `revenue = quantity * unit_price`, profit margins, or discount adjustments is the explicit domain of the modeling layer in dbt. This ensures business metrics remain centralized, version-controlled, and testable.

---

## 6. Downstream Pipeline Flow

```
+------------------------------------+
|        data/retail_sales.csv       |
+------------------------------------+
                  |
                  | Loaded via SQL / Python Seeder
                  v
+------------------------------------+
|         PostgreSQL Database        |
|    retail_source.public.orders     |
+------------------------------------+
                  |
                  | Ingested via Airbyte Connection
                  v
+------------------------------------+
|       Google BigQuery (Raw)        |
|          raw_retail.orders         |
+------------------------------------+
                  |
                  | Transformed via dbt Core
                  v
+------------------------------------+
|    BigQuery Analytics Marts        |
|  - stg_orders (calculates revenue) |
|  - sales_by_product                |
|  - sales_by_region                 |
|  - monthly_sales                   |
+------------------------------------+
```

