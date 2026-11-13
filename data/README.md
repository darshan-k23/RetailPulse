# Data Directory

This folder is dedicated to data assets and dataset generation scripts.

## Subdirectories:
- `raw/`: Stores the generated retail sales CSV dataset (`orders.csv` or `orders_raw.csv`).
- `scripts/`: Contains Python scripts used to synthesize realistic transactional retail data (using `faker` and `pandas`).

## Data Contract Schema (`orders`):
The dataset will contain transactional sales records with the following fields:
- `order_id`: Unique transaction identifier (Integer / UUID)
- `order_date`: Date/timestamp of order placement (Timestamp)
- `customer_id`: Unique customer identifier (Integer)
- `product_id`: Product SKU identifier (String)
- `product_name`: Descriptive product name (String)
- `product_category`: High-level merchandise category (e.g., Electronics, Fashion, Home)
- `quantity`: Number of items ordered (Integer >= 1)
- `unit_price`: Base price per unit in USD/INR (Numeric / Float > 0)
- `discount_amount`: Discount applied per line (Numeric / Float >= 0)
- `total_amount`: Final line total `(quantity * unit_price) - discount_amount`
- `payment_method`: Credit Card, Debit Card, UPI, Cash on Delivery, etc.
- `store_region`: North, South, East, West, Central
- `order_status`: Completed, Cancelled, Returned, Shipped

