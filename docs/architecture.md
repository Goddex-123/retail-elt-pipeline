# Retail ELT Platform — Technical Architecture & Design Document

## 1. Overview & Architectural Principles

The Retail ELT Platform implements a production-grade **Medallion Architecture** (Bronze → Silver → Gold) modeled after modern data stack standards (Databricks, Netflix, Snowflake). The primary philosophy is **ELT over ETL**: raw application events and transactional records are extracted and loaded into warehouse staging without destructive pre-filtering, enabling 100% auditability, replayability, and downstream modeling within dbt SQL.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Source Systems │       │  Bronze Layer   │       │  Silver Layer   │       │   Gold Layer    │
│ (Postgres/APIs) │──────>│ (Raw+Metadata)  │──────>│(Cleaned/Deduped)│──────>│(Business Marts) │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │                         │                         │
                                   ▼                         ▼                         ▼
                            _loaded_at, batch_id      dbt tests, views        Star schema, SCD2
```

---

## 2. Medallion Layer Specifications

| Layer | Schema | Materialization | Storage Engine | Responsibility |
|---|---|---|---|---|
| **Source** | `source` | Tables | PostgreSQL | Simulates external transactional systems (OLTP ERP, POS, E-commerce APIs). |
| **Bronze** | `bronze` | Tables | PostgreSQL | Append-only landing zone. Preserves raw fidelity while adding lineage audit columns (`_loaded_at` UTC, `_batch_id` UUID). |
| **Silver** | `silver` | Views / Ephemeral | dbt / PostgreSQL | Standardization, schema conformance, deduplication (window functions), casing normalization, type casting, and domain validation. |
| **Gold** | `gold` | Tables (Incremental/Table) | dbt / PostgreSQL | Dimensional models (Kimball Star Schema), facts, aggregated business marts, RFM scoring, churn modeling, and SCD Type 2 dimension. |

---

## 3. Ingestion & Incremental Strategy

### High-Water Mark (CDC Pattern)
For fact tables that append rapidly (e.g., `orders`, `order_items`), re-reading historical partitions causes severe compute overhead. The platform employs an incremental high-water mark strategy:

1. **State Tracking**: Queries `MAX(order_date)` from the target bronze table. If the target table is empty, falls back to epoch (`1970-01-01T00:00:00Z`).
2. **Safe Extraction**: Uses parameterized queries with strict column and table identifier whitelisting to eliminate SQL injection risks.
3. **Audit Injection**: Stamps every ingested batch with a cryptographically unique `_batch_id` and ISO-8601 UTC timestamp.
4. **dbt Incremental Processing**: `fct_orders` uses dbt's `incremental` materialization with `unique_key = 'order_item_id'`:
   ```sql
   {% if is_incremental() %}
     where order_date > (select max(order_date) from {{ this }})
   {% endif %}
   ```

---

## 4. Slowly Changing Dimensions (SCD Type 2)

Customer profile changes (e.g., tier upgrades from `Silver` to `Platinum`, address migrations) must be tracked historically without overwriting prior records.

- **Implementation**: Managed natively via dbt Snapshots (`dbt_retail/snapshots/snap_customers.sql`).
- **Strategy**: `timestamp` strategy using `signup_date` as updated tracking key.
- **Dimensional Mart**: `dim_customers_scd2` exposes:
  - `dbt_scd_id`: Unique surrogate key for each customer version.
  - `customer_id`: Natural business key.
  - `valid_from`: Start timestamp of the dimension state.
  - `valid_to`: End timestamp (or `NULL` if active).
  - `is_current`: Derived boolean flag (`valid_to IS NULL`).

---

## 5. Data Quality, Integrity & Anomaly Detection

Quality is enforced via a two-layer defense strategy:

### Layer 1: Declarative dbt Tests (In-Pipeline Gates)
Over 60 dbt tests execute within the DAG between staging and mart generation:
- **Primary & Foreign Key Integrity**: `unique`, `not_null`, and `relationships` tests prevent orphaned order items or missing dimension keys.
- **Domain Constraints**: `accepted_values` tests enforce allowed loyalty tiers, payment methods, order statuses, and geographical regions.
- **Custom Business Rules**: Custom generic test `positive_value` guarantees that pricing and transaction amounts are strictly positive.

### Layer 2: Python Data Quality & Anomaly Engine (`src/quality.py`)
An independent quality module monitors data health and generates structured telemetry:
- **Completeness**: Null rates across critical columns with configurable thresholds.
- **Uniqueness**: Duplicate rate detection across entity identifiers.
- **Volume & Freshness**: Minimum row counts and SLA freshness bounds.
- **Health Scoring**: Computes a composite Data Quality Index (0–100%) and publishes structured reports into pipeline logs and the Streamlit dashboard.

---

## 6. Failure Recovery, Idempotency & Retries

1. **Connection Resilience**: `src/db.py` implements a singleton `QueuePool` with connection pre-ping (`pool_pre_ping=True`) and exponential backoff retry logic (3 attempts: 2s, 4s, 8s delay).
2. **Transaction Isolation**: Multi-statement operations execute within `execute_in_transaction()` context blocks, guaranteeing atomic commit or rollback.
3. **Airflow Task Reliability**:
   - Explicit `execution_timeout` on all tasks preventing zombie deadlocks.
   - Configurable retry counts with exponential backoff on transient network blips.
   - Dedicated failure callbacks (`dags/common/callbacks.py`) generating JSON structured alerts with execution context.
4. **Idempotency**: All ingestion steps use either deterministic high-water mark offsets or atomic table recreation, preventing duplicate records upon rerun.

---

## 7. Observability & Tracing Architecture

- **Structured JSON Logging**: Every log emitted uses scoped `LoggerAdapter` instances injecting `correlation_id`, `run_id`, `environment`, and execution durations.
- **Tracing Across Layers**: Correlation IDs propagate from Airflow DAG executions into Python data loaders and data quality reports.
- **SLA Monitoring**: Daily pipeline configured with 4-hour completion SLA, triggering automated breach alerts if execution exceeds boundaries.

---

## 8. Scalability & Cloud Migration Roadmap

| Component | Current (Local / Portfolio) | Cloud Scale-Up (Enterprise Production) |
|---|---|---|
| **Warehouse** | PostgreSQL 13 (Docker) | Snowflake / AWS Redshift / Google BigQuery |
| **Orchestrator** | Apache Airflow LocalExecutor | Managed Airflow (MWAA / Astronomer / Cloud Composer) |
| **Transformations** | dbt-postgres | dbt-snowflake / dbt-bigquery with CI Cloud Jobs |
| **Object Storage** | Shared container volume | AWS S3 / Google Cloud Storage / Azure ADLS Gen2 |
| **Streaming** | PySpark + Kafka (Optional Compose) | Confluent Cloud + Databricks Structured Streaming |
