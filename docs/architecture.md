# Architecture Guide

## Overview

The Retail ELT Platform follows a **Medallion Architecture** (Bronze → Silver → Gold) pattern, widely adopted by leading data teams at companies like Databricks, Netflix, and Airbnb.

## Design Principles

### 1. ELT Over ETL
Transformations happen **inside the warehouse** (PostgreSQL), not in transit. Raw data is loaded first (Extract + Load), then transformed using dbt SQL models (Transform). This enables:
- Full data lineage
- Replayable transformations
- Schema-on-read flexibility

### 2. Layered Architecture

| Layer | Schema | Purpose | Materialization |
|-------|--------|---------|-----------------|
| **Source** | `source` | Application database simulation | Tables (Pandas) |
| **Bronze** | `bronze` | Raw ingested data with metadata | Tables (Python) |
| **Silver** | `silver` | Cleaned, validated, deduplicated | Views (dbt) |
| **Gold** | `gold` | Business-ready aggregated marts | Tables (dbt) |

### 3. Star Schema
Gold layer follows a dimensional star schema:
- **Fact tables**: `fct_orders` (grain: one row per order line item)
- **Dimension tables**: `dim_customers_scd2`, products, stores, categories

### 4. SCD Type 2
Customer dimension tracks historical changes using dbt snapshots with `valid_from` / `valid_to` / `is_current` pattern.

## Data Flow

```
Source Systems → Python Generators → Source Schema
                                          ↓
                                    Bronze Schema (+ metadata columns)
                                          ↓
                                    Silver Schema (dbt staging models)
                                          ↓
                                    Gold Schema (dbt mart models)
                                          ↓
                                    Streamlit Dashboard
```

## Indexing Strategy

For production deployment, add these indexes:

```sql
-- Bronze layer: speed up extraction queries
CREATE INDEX idx_bronze_orders_date ON bronze.orders(order_date);
CREATE INDEX idx_bronze_customers_id ON bronze.customers(customer_id);

-- Gold layer: speed up dashboard queries
CREATE INDEX idx_fct_orders_date ON gold.fct_orders(order_date_day);
CREATE INDEX idx_fct_orders_customer ON gold.fct_orders(customer_id);
CREATE INDEX idx_fct_orders_product ON gold.fct_orders(product_id);
CREATE INDEX idx_fct_orders_region ON gold.fct_orders(region);
```

## Partitioning Strategy

For tables exceeding 10M+ rows, implement range partitioning:

```sql
CREATE TABLE gold.fct_orders (
    ...
) PARTITION BY RANGE (order_date_day);

CREATE TABLE gold.fct_orders_2024_q1 PARTITION OF gold.fct_orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

## Cost Optimization Notes

1. **Incremental models**: `fct_orders` uses incremental materialization to avoid full table scans
2. **Ephemeral models**: Intermediate models are not materialized, reducing storage
3. **View materialization**: Silver layer uses views (zero storage cost, always fresh)
4. **Connection pooling**: SQLAlchemy QueuePool reduces connection overhead
