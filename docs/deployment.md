# Deployment Guide

## Local Development (Docker)

### Prerequisites
- Docker Desktop (v24+)
- Docker Compose (v2+)
- Git
- 4GB+ RAM allocated to Docker

### Quick Start
```bash
# 1. Clone and setup
git clone https://github.com/Goddex-123/retail-elt-pipeline.git
cd retail-elt-pipeline
cp .env.example .env

# 2. Start services
make up    # or: docker-compose up -d

# 3. Wait for initialization (~2 minutes)
# 4. Access services:
#    Airflow:   http://localhost:8080 (airflow/airflow)
#    Dashboard: http://localhost:8501
#    pgAdmin:   http://localhost:5050 (admin@retail.com/admin)

# 5. Trigger the pipeline
# Go to Airflow UI → retail_daily_pipeline → Toggle ON → Trigger
```

### Development Commands
```bash
make help            # Show all available commands
make generate-data   # Generate synthetic data
make dbt-run         # Run dbt models
make dbt-test        # Run dbt tests
make lint            # Run Python linter
make test            # Run pytest
make logs            # Tail service logs
make clean           # Remove all artifacts
make down            # Stop services
```

## Production Deployment (Cloud)

### Recommended Architecture

```
                    ┌─────────────────┐
                    │  GitHub Actions  │ ← CI/CD
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Cloud Composer │ ← Managed Airflow
                    │   (or MWAA)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──┐  ┌───────▼─────┐  ┌────▼────────┐
    │  Cloud SQL  │  │  Snowflake  │  │   BigQuery   │
    │ (PostgreSQL)│  │  Warehouse  │  │  Data Lake   │
    └─────────────┘  └─────────────┘  └──────────────┘
```

### Environment Variables (Production)
```bash
POSTGRES_HOST=your-cloud-db-host
POSTGRES_USER=pipeline_service_account
POSTGRES_PASSWORD=<from-secrets-manager>
POSTGRES_DB=retail_warehouse
POSTGRES_PORT=5432
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
PIPELINE_LOG_LEVEL=WARNING
```

### Security Checklist
- [ ] Rotate FERNET_KEY and store in secrets manager
- [ ] Use IAM roles instead of password auth where possible
- [ ] Enable SSL for database connections
- [ ] Restrict network access to database
- [ ] Set up audit logging
- [ ] Enable backup retention (7+ days)
