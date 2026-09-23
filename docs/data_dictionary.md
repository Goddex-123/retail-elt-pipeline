# Retail ELT Platform — Comprehensive Data Dictionary

This document details the schema definitions, grains, data types, and business logic for all layers of the Retail ELT Platform data warehouse.

---

## 1. Bronze & Staging Layer (13 Tables)

All tables in the `bronze` schema retain the raw source attributes along with audit metadata columns:
- `_loaded_at` (`TIMESTAMP WITH TIME ZONE`): UTC timestamp when the record was ingested into the warehouse.
- `_batch_id` (`VARCHAR`): Unique UUID assigned to the ingestion batch.

### `customers`
| Column | Type | Nullable | Description & Quality Rules |
|---|---|---|---|
| `customer_id` | INT | NO | Primary key. Unique customer identifier. |
| `first_name` | VARCHAR(50) | NO | Customer given name. |
| `last_name` | VARCHAR(50) | NO | Customer family name. |
| `email` | VARCHAR(100) | NO | Primary email address for notifications and loyalty communications. |
| `phone` | VARCHAR(30) | YES | Contact number. Cleaned and normalized in silver layer. |
| `city` | VARCHAR(50) | YES | Customer city. Raw layer contains intentional blanks and casing inconsistencies cleaned in silver. |
| `loyalty_tier` | VARCHAR(20) | NO | Loyalty tier: `Bronze`, `Silver`, `Gold`, `Platinum`. Enforced via accepted_values. |
| `signup_date` | DATE | NO | Account registration date. |
| `date_of_birth` | DATE | YES | Customer birthdate for demographic analysis. |

### `products`
| Column | Type | Nullable | Description & Quality Rules |
|---|---|---|---|
| `product_id` | INT | NO | Primary key. |
| `product_name` | VARCHAR(100) | NO | Commercial product title. |
| `category_id` | INT | NO | Foreign key references `categories(category_id)`. |
| `supplier_id` | INT | NO | Foreign key references `suppliers(supplier_id)`. |
| `unit_price` | NUMERIC(10,2) | NO | Listed retail selling price (INR). Must be > 0 (tested via `positive_value`). |
| `cost_price` | NUMERIC(10,2) | NO | Cost of goods sold (COGS) incurred to procure the item. |
| `weight_kg` | NUMERIC(6,2) | YES | Physical weight in kilograms for logistics routing. |
| `is_active` | BOOLEAN | NO | Catalog listing status flag. |
| `created_at` | DATE | NO | Timestamp product was onboarded to catalog. |

### `orders`
| Column | Type | Nullable | Description & Quality Rules |
|---|---|---|---|
| `order_id` | INT | NO | Primary key. Unique transaction header ID. |
| `customer_id` | INT | NO | Foreign key references `customers(customer_id)`. |
| `store_id` | INT | NO | Foreign key references `stores(store_id)`. |
| `order_date` | TIMESTAMP | NO | Transaction placement timestamp. High-water mark tracking key. |
| `status` | VARCHAR(20) | NO | Fulfillment status: `completed`, `pending`, `shipped`, `cancelled`, `returned`. |
| `total_amount` | NUMERIC(12,2) | NO | Gross order value before returns. |
| `discount_amount` | NUMERIC(10,2) | NO | Order-level promotional discount applied. |
| `shipping_cost` | NUMERIC(8,2) | NO | Shipping and handling fees billed. |

### `order_items`
| Column | Type | Nullable | Description & Quality Rules |
|---|---|---|---|
| `order_item_id` | INT | NO | Primary key. |
| `order_id` | INT | NO | Foreign key references `orders(order_id)`. |
| `product_id` | INT | NO | Foreign key references `products(product_id)`. |
| `quantity` | INT | NO | Units purchased. Negative values from source simulation are cleansed in silver to 0. |
| `unit_price` | NUMERIC(10,2) | NO | Price per unit at moment of checkout. Validated positive. |
| `discount_pct` | INT | NO | Percentage discount applied (0 to 20%). |

### Additional Operational Tables
- `categories`: `category_id` (PK), `category_name`, `parent_category_id`
- `suppliers`: `supplier_id` (PK), `supplier_name`, `contact_name`, `contact_email`, `city`
- `stores`: `store_id` (PK), `store_name`, `city`, `region` (`North`, `South`, `East`, `West`), `store_type`, `opening_date`, `is_active`
- `payments`: `payment_id` (PK), `order_id` (FK), `payment_method` (`credit_card`, `debit_card`, `upi`, `net_banking`, `cash_on_delivery`, `wallet`), `payment_status` (`success`, `failed`, `pending`, `refunded`), `amount`, `payment_date`
- `returns`: `return_id` (PK), `order_id` (FK), `return_date`, `reason` (`defective`, `wrong_item`, `not_as_described`, `buyer_remorse`), `refund_amount`, `refund_status`
- `shipments`: `shipment_id` (PK), `order_id` (FK), `carrier`, `tracking_number`, `shipped_date`, `actual_delivery`
- `reviews`: `review_id` (PK), `order_id` (FK), `customer_id` (FK), `product_id` (FK), `rating` (1–5), `review_text`
- `inventory`: `inventory_id` (PK), `product_id` (FK), `store_id` (FK), `quantity_on_hand`, `reorder_level`
- `promotions`: `promotion_id` (PK), `promotion_name`, `discount_type`, `discount_value`, `start_date`, `end_date`

---

## 2. Gold Layer (Dimensional Model & Business Marts)

### 2.1 Dimensional Core

#### `gold.fct_orders` (Fact Table)
- **Grain**: One row per order line item.
- **Materialization**: Incremental.

| Column | Type | Business Logic / Formula |
|---|---|---|
| `order_item_id` | INT | Unique surrogate fact key. |
| `order_id` | INT | Order header identifier. |
| `customer_id` | INT | Customer dimension key. |
| `store_id` | INT | Store dimension key. |
| `product_id` | INT | Product dimension key. |
| `order_date` | TIMESTAMP | Full order timestamp. |
| `order_date_day` | DATE | Truncated date partition key. |
| `status` | VARCHAR | Order status. |
| `region` | VARCHAR | Store geographical region. |
| `category_id` | INT | Product category. |
| `quantity` | INT | Sold quantity (guaranteed non-negative). |
| `unit_price` | NUMERIC | Transactional unit price. |
| `line_total_gross` | NUMERIC | `quantity * unit_price` |
| `line_total_net` | NUMERIC | `quantity * unit_price * (1 - discount_pct / 100.0)` |
| `line_cost` | NUMERIC | `quantity * cost_price` |
| `line_profit` | NUMERIC | `line_total_net - line_cost` |
| `gross_margin_pct` | NUMERIC | `(line_profit / NULLIF(line_total_net, 0)) * 100.0` |

#### `gold.dim_customers_scd2` (SCD Type 2 Dimension)
- **Grain**: One row per customer historical state version.
- **Source**: dbt snapshot `snap_customers`.

| Column | Type | Business Logic / Formula |
|---|---|---|
| `dbt_scd_id` | VARCHAR | Unique surrogate key per SCD2 version. |
| `customer_id` | INT | Natural customer ID. |
| `full_name` | VARCHAR | Concatenated `first_name` + `last_name`. |
| `email` | VARCHAR | Email address. |
| `city` | VARCHAR | Normalized city. |
| `loyalty_tier` | VARCHAR | Active tier for the validity window. |
| `valid_from` | TIMESTAMP | Timestamp version became active (`dbt_valid_from`). |
| `valid_to` | TIMESTAMP | Timestamp version retired (`dbt_valid_to`). `NULL` if current. |
| `is_current` | BOOLEAN | `TRUE` if `valid_to IS NULL`, indicating latest profile state. |

---

### 2.2 Analytical Marts

#### `gold.customer_lifetime_value`
- **Grain**: One row per customer.
- **Business Purpose**: RFM (Recency, Frequency, Monetary) segmentation & CLV prediction.

| Column | Type | Business Logic |
|---|---|---|
| `customer_id` | INT | Customer identifier. |
| `recency_days` | INT | Days elapsed since customer's most recent completed order. |
| `frequency_orders` | INT | Count of distinct completed orders. |
| `monetary_total` | NUMERIC | Total lifetime net spend (INR). |
| `rfm_score` | INT | Composite score calculated as `R_score * 100 + F_score * 10 + M_score` (each scored 1–5). |
| `customer_segment` | VARCHAR | Categorized as: `Champions`, `Loyal Customers`, `Potential Loyalists`, `At Risk`, `Hibernating`. |
| `estimated_clv` | NUMERIC | Projected 12-month value: `(Average Order Value) * (Order Frequency) * (Gross Margin %)`. |

#### `gold.churn_risk`
- **Grain**: One row per at-risk customer.
- **Business Purpose**: Automated attrition detection and retention marketing dispatch.

| Column | Type | Business Logic |
|---|---|---|
| `customer_id` | INT | Customer identifier. |
| `days_inactive` | INT | Days since last engagement. |
| `churn_risk_score` | INT | Normalized risk index (0–100) combining recency decay, frequency drop, and return frequency. |
| `winback_priority` | VARCHAR | Priority tier: `CRITICAL` (High CLV + high churn risk), `HIGH`, `MEDIUM`, `LOW`. |

#### `gold.daily_sales`
- **Grain**: One row per calendar day.

| Column | Type | Business Logic |
|---|---|---|
| `order_date_day` | DATE | Calendar day. |
| `daily_revenue` | NUMERIC | Total net sales for the day. |
| `order_count` | INT | Total completed orders. |
| `avg_order_value` | NUMERIC | `daily_revenue / order_count`. |
| `running_total_revenue`| NUMERIC | Cumulative year-to-date or period sales. |
| `moving_avg_7d_revenue`| NUMERIC | 7-day trailing moving average to smooth seasonality. |
| `dod_growth_pct` | NUMERIC | Day-over-Day percentage change in net sales. |

#### `gold.stock_alerts`
- **Grain**: Product × Store.
- **Business Purpose**: Supply chain replenishment alerts.

| Column | Type | Business Logic |
|---|---|---|
| `product_id` | INT | Product reference. |
| `store_id` | INT | Retail branch reference. |
| `quantity_on_hand` | INT | Current physical units in store stock. |
| `reorder_level` | INT | Minimum safety threshold. |
| `alert_severity` | VARCHAR | `CRITICAL` (stock = 0), `HIGH` (stock < 50% reorder level), `MEDIUM` (stock <= reorder level). |
| `suggested_reorder_qty`| INT | Recommended procurement quantity to restore target stock. |

#### `gold.gross_margin`
- **Grain**: One row per product.

| Column | Type | Business Logic |
|---|---|---|
| `product_id` | INT | Product reference. |
| `total_revenue` | NUMERIC | Total net sales generated. |
| `total_cost` | NUMERIC | Total cost of units sold. |
| `gross_profit` | NUMERIC | `total_revenue - total_cost`. |
| `gross_margin_pct` | NUMERIC | `(gross_profit / NULLIF(total_revenue, 0)) * 100.0`. |
| `margin_tier` | VARCHAR | Classification: `High Margin (>40%)`, `Standard Margin (20-40%)`, `Low Margin (<20%)`. |
