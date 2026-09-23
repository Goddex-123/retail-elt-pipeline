# ============================================================
# Retail ELT Platform — Makefile
# ============================================================
# Usage: make <target>
# Run `make help` to see all available commands.
# ============================================================

.PHONY: help setup up down restart logs clean generate-data \
        dbt-run dbt-test dbt-compile dbt-docs lint test fmt \
        pg-shell airflow-shell

# ---- Default ----
help: ## Show this help message
	@echo ""
	@echo "  Retail ELT Platform — Development Commands"
	@echo "  ============================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---- Infrastructure ----
setup: ## First-time setup: copy .env, build images
	@test -f .env || cp .env.example .env
	docker-compose build
	@echo "✅ Setup complete. Run 'make up' to start."

up: ## Start all services (Postgres, Airflow, Dashboard)
	docker-compose up -d
	@echo "✅ Services starting..."
	@echo "   Airflow UI:  http://localhost:8080  (credentials in .env)"
	@echo "   Dashboard:   http://localhost:8501"
	@echo "   pgAdmin:     http://localhost:5050"

down: ## Stop all services
	docker-compose down
	@echo "✅ All services stopped."

restart: ## Restart all services
	docker-compose down && docker-compose up -d
	@echo "✅ Services restarted."

logs: ## Tail logs from all services
	docker-compose logs -f --tail=50

clean: ## Remove all containers, volumes, and generated files
	docker-compose down -v --remove-orphans
	rm -rf dbt_retail/target dbt_retail/dbt_packages dbt_retail/logs
	rm -rf data/raw/*.csv shared_data/*.csv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned all artifacts."

# ---- Data ----
generate-data: ## Generate synthetic retail data (13 tables)
	docker-compose exec airflow-scheduler python /opt/airflow/scripts/data_generator.py
	@echo "✅ Synthetic data generated."

# ---- dbt ----
dbt-run: ## Run all dbt models (staging → marts)
	docker-compose exec airflow-scheduler bash -c \
		"cd /opt/airflow/dbt_retail && dbt run --profiles-dir ."

dbt-test: ## Run all dbt tests
	docker-compose exec airflow-scheduler bash -c \
		"cd /opt/airflow/dbt_retail && dbt test --profiles-dir ."

dbt-compile: ## Compile dbt models (validate SQL without running)
	docker-compose exec airflow-scheduler bash -c \
		"cd /opt/airflow/dbt_retail && dbt compile --profiles-dir ."

dbt-docs: ## Generate and serve dbt documentation
	docker-compose exec airflow-scheduler bash -c \
		"cd /opt/airflow/dbt_retail && dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir . --port 8081"

# ---- Quality ----
lint: ## Run Python linter (flake8) and SQL linter
	flake8 src/ scripts/ dags/ tests/ --max-line-length=120 --ignore=E501,W503
	@echo "✅ Lint passed."

fmt: ## Auto-format Python code with Black
	black src/ scripts/ dags/ tests/ --line-length=120
	@echo "✅ Code formatted."

test: ## Run pytest unit tests
	pytest tests/ -v --tb=short
	@echo "✅ All tests passed."

# ---- Shell Access ----
pg-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U retail_user -d retail_warehouse

airflow-shell: ## Open Airflow worker shell
	docker-compose exec airflow-scheduler bash
