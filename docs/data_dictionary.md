# Data Dictionary

## Source / Bronze Layer (13 Tables)

### customers
| Column | Type | Description |
|--------|------|-------------|
| customer_id | INT | Primary key |
| first_name | VARCHAR | Customer first name |
| last_name | VARCHAR | Customer last name |
| email | VARCHAR | Email address |
| phone | VARCHAR | Phone number (nullable) |
| city | VARCHAR | City (may contain nulls, inconsistent casing) |
| loyalty_tier | VARCHAR | Bronze / Silver / Gold / Platinum |
| signup_date | DATE | Account creation date |
| date_of_birth | DATE | Customer DOB |

### products
| Column | Type | Description |
|--------|------|-------------|
| product_id | INT | Primary key |
| product_name | VARCHAR | Product display name |
| category_id | INT | FK → categories |
| supplier_id | INT | FK → suppliers |
| unit_price | DECIMAL | Selling price (INR) |
| cost_price | DECIMAL | Cost of goods (INR) |
| weight_kg | DECIMAL | Product weight |
| is_active | BOOLEAN | Active listing flag |
| created_at | DATE | Catalog entry date |

### orders
| Column | Type | Description |
|--------|------|-------------|
| order_id | INT | Primary key |
| customer_id | INT | FK → customers |
| store_id | INT | FK → stores |
| order_date | TIMESTAMP | Order placement time |
| status | VARCHAR | completed / pending / shipped / cancelled / returned |
| total_amount | DECIMAL | Order total (INR) |
| discount_amount | DECIMAL | Applied discount |
| shipping_cost | DECIMAL | Shipping charges |

### order_items
| Column | Type | Description |
|--------|------|-------------|
| order_item_id | INT | Primary key |
| order_id | INT | FK → orders |
| product_id | INT | FK → products |
| quantity | INT | Units ordered (may be negative — data quality issue) |
| unit_price | DECIMAL | Price at time of purchase |
| discount_pct | INT | Line-level discount percentage |

### payments
| Column | Type | Description |
|--------|------|-------------|
| payment_id | INT | Primary key |
| order_id | INT | FK → orders |
| payment_method | VARCHAR | credit_card / debit_card / upi / net_banking / cod / wallet |
| payment_status | VARCHAR | success / failed / pending / refunded |
| payment_date | TIMESTAMP | Transaction time |
| amount | DECIMAL | Payment amount (INR) |
| currency | VARCHAR | Currency code (INR) |

### returns
| Column | Type | Description |
|--------|------|-------------|
| return_id | INT | Primary key |
| order_id | INT | FK → orders |
| return_date | TIMESTAMP | Return initiation date |
| reason | VARCHAR | Return reason code |
| refund_amount | DECIMAL | Refund amount (INR) |
| refund_status | VARCHAR | processed / pending / rejected |

### Other Tables
- **categories**: category_id, category_name, parent_category_id
- **suppliers**: supplier_id, supplier_name, contact_name, contact_email, city
- **stores**: store_id, store_name, city, region, store_type, opening_date
- **shipments**: shipment_id, order_id, carrier, tracking_number, shipped_date, actual_delivery
- **reviews**: review_id, order_id, customer_id, product_id, rating (1-5), review_text
- **inventory**: inventory_id, product_id, store_id, quantity_on_hand, reorder_level
- **promotions**: promotion_id, promotion_name, discount_type, discount_value, start_date, end_date

---

## Gold Layer (Business Marts)

### Sales Mart
| Table | Grain | Key Metrics |
|-------|-------|-------------|
| fct_orders | Order line item | revenue, cost, profit, margin |
| daily_sales | Day | cumulative revenue, 7d moving avg, DoD growth |
| monthly_sales | Month | MoM growth %, revenue rank |
| revenue_by_region | Region | revenue share %, per-store revenue |
| top_products | Product | Pareto contribution %, product rank |

### Customer Mart
| Table | Grain | Key Metrics |
|-------|-------|-------------|
| customer_lifetime_value | Customer | RFM score, segment, estimated CLV |
| repeat_customer_rate | Monthly cohort | repeat rate %, frequent rate % |
| churn_risk | Customer | churn score (0-100), winback priority |
| dim_customers_scd2 | Customer (SCD2) | valid_from, valid_to, is_current |

### Inventory Mart
| Table | Grain | Key Metrics |
|-------|-------|-------------|
| stock_alerts | Product × Store | alert severity, suggested reorder qty |
| inventory_turnover | Product | turnover ratio, movement category |

### Finance Mart
| Table | Grain | Key Metrics |
|-------|-------|-------------|
| refund_analysis | Return reason | return rate %, reason share % |
| gross_margin | Product | margin %, profit per unit, margin tier |
| payment_success_rate | Payment method | success rate %, reliability tier |
