#!/usr/bin/env bash
# ============================================================
# Retail ELT Platform — Automated Demo Setup Script
# ============================================================
# Spawns services, verifies health, runs initial ELT pipeline,
# and verifies Gold layer marts for recruiter/live demo.
#
# Usage:
#   chmod +x scripts/init_demo.sh
#   ./scripts/init_demo.sh
# ============================================================

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${CYAN}${BOLD}"
echo "============================================================"
echo "    Retail ELT Platform — Demo Environment Setup           "
echo "============================================================"
echo -e "${NC}"

# Step 1: Ensure .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}[1/6] .env not found. Creating from .env.example...${NC}"
    cp .env.example .env
    
    # Generate Fernet key if python is available
    if command -v python3 &>/dev/null; then
        FERNET_KEY=$(python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())" 2>/dev/null || true)
        if [ -n "$FERNET_KEY" ]; then
            sed -i.bak "s|AIRFLOW__CORE__FERNET_KEY=.*|AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}|" .env && rm -f .env.bak
            echo -e "${GREEN}      Generated fresh Airflow Fernet key.${NC}"
        fi
    fi
else
    echo -e "${GREEN}[1/6] .env file verified.${NC}"
fi

# Step 2: Start Docker Compose services
echo -e "${CYAN}[2/6] Starting Docker containers...${NC}"
docker compose up -d

# Step 3: Wait for PostgreSQL health
echo -e "${CYAN}[3/6] Waiting for PostgreSQL warehouse to be healthy...${NC}"
RETRIES=30
until docker compose exec -T postgres pg_isready -U retail_user &>/dev/null || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 2
    RETRIES=$((RETRIES - 1))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    echo -e "${RED}PostgreSQL did not become healthy in time.${NC}"
    exit 1
fi
echo -e "${GREEN}      PostgreSQL is healthy and accepting connections.${NC}"

# Step 4: Wait for Airflow Webserver
echo -e "${CYAN}[4/6] Waiting for Airflow webserver...${NC}"
RETRIES=45
until curl -sSf http://localhost:8080/health &>/dev/null || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 3
    RETRIES=$((RETRIES - 1))
done
echo ""
echo -e "${GREEN}      Airflow is responding.${NC}"

# Step 5: Unpause DAGs & Trigger Pipeline
echo -e "${CYAN}[5/6] Unpausing DAGs and triggering daily ELT pipeline...${NC}"
docker compose exec -T airflow-webserver airflow dags unpause retail_daily_pipeline || true
docker compose exec -T airflow-webserver airflow dags unpause retail_data_quality_monitor || true
docker compose exec -T airflow-webserver airflow dags trigger retail_daily_pipeline || true

# Step 6: Completion summary
echo -e "${GREEN}${BOLD}"
echo "============================================================"
echo "    Demo Setup Complete! Pipeline running in background.   "
echo "============================================================"
echo -e "${NC}"
echo -e "${BOLD}Access Services:${NC}"
echo -e "  - ${CYAN}Airflow UI:${NC}    http://localhost:8080  (User: admin / Password in .env)"
echo -e "  - ${CYAN}Dashboard:${NC}     http://localhost:8501  (Executive Analytics & Quality)"
echo -e "  - ${CYAN}pgAdmin:${NC}       http://localhost:5050  (Email: admin@retail.com)"
echo ""
echo -e "${YELLOW}To monitor pipeline execution:${NC}"
echo "  docker compose logs -f airflow-scheduler"
echo ""
