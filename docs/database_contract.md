# RetailPulse Database Contract & Data Dictionary

## 1. PostgreSQL Source
- **Database**: `retail_source`
- **Schema**: `public`
- **Table**: `orders`

### Schema Definition:
| Column Name | Data Type | Constraint | Description |
|:---|:---|:---|:---|
| `order_id` | INT / BIGINT | PRIMARY KEY | Unique order transaction ID |
| `order_date` | TIMESTAMP | NOT NULL | Timestamp of purchase |
| `customer_id` | INT | NOT NULL | Foreign/reference customer ID |
| `customer_name` | VARCHAR(100) | NOT NULL | Name of customer |
| `product_id` | VARCHAR(50) | NOT NULL | Product SKU code |
| `product_name` | VARCHAR(150) | NOT NULL | Product catalog description |
| `product_category`| VARCHAR(50) | NOT NULL | Category (e.g., Electronics, Fashion) |
| `quantity` | INT | NOT NULL, > 0 | Units purchased |
| `unit_price` | NUMERIC(10, 2) | NOT NULL, > 0 | Price per single unit |
| `discount_amount` | NUMERIC(10, 2) | NOT NULL, >= 0 | Discount applied |
| `total_amount` | NUMERIC(10, 2) | NOT NULL | Final transaction amount |
| `payment_method` | VARCHAR(50) | NOT NULL | Method (Credit Card, Debit Card, UPI, Cash) |
| `store_region` | VARCHAR(50) | NOT NULL | Region (North, South, East, West, Central) |
| `order_status` | VARCHAR(30) | NOT NULL | Status (Completed, Cancelled, Returned) |

---

## 2. Google BigQuery Data Warehouse
- **Raw Dataset**: `raw_retail`
  - **Raw Table**: `orders` (Ingested 1:1 via Airbyte sync)
- **Analytics Dataset**: `analytics_retail` (Transformed models produced by dbt)

---

## 3. dbt Model Transformations

### Staging Model: `stg_orders`
- **Target Location**: `analytics_retail.stg_orders` (view or ephemeral)
- **Role**: Standardize column naming, validate datatypes, filter corrupted records.

### Mart Model 1: `sales_by_product`
- **Target Location**: `analytics_retail.sales_by_product` (table)
- **Metrics**: Total units sold, Gross sales, Total discounts, Net revenue, Average order size by category and product.

### Mart Model 2: `sales_by_region`
- **Target Location**: `analytics_retail.sales_by_region` (table)
- **Metrics**: Total orders, Total revenue, Regional percentage share, Average revenue per order.

### Mart Model 3: `monthly_sales`
- **Target Location**: `analytics_retail.monthly_sales` (table)
- **Metrics**: Year, Month, Monthly transaction count, Monthly total revenue, Month-over-Month (MoM) revenue growth.

