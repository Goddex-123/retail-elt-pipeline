# 🛒 Bombay Bazaar: Modern Data Stack ELT Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.7.1-017CEE?logo=apache-airflow)](https://airflow.apache.org/)
[![dbt](https://img.shields.io/badge/dbt-1.6.0-FF694B?logo=dbt)](https://www.getdbt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-316192?logo=postgresql)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.2-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)

An end-to-end ELT (Extract, Load, Transform) data pipeline built with the **Modern Data Stack (MDS)** to process retail sales data, orchestrate workflows, and power a real-time executive dashboard.

## 🌟 Live Demo (Local Setup Required)
Since this project runs entirely on your local machine using Docker, you must follow the **Quick Start** guide below before clicking the demo links.

<div align="center">
  <a href="http://localhost:8080">
    <img src="https://img.shields.io/badge/⚙️_View_Airflow_Pipeline-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white" alt="Airflow UI" />
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="http://localhost:8501">
    <img src="https://img.shields.io/badge/📊_View_Streamlit_Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Dashboard" />
  </a>
</div>
<br>

---

## 🏗️ Architecture (Medallion Pattern)

This project strictly follows the **Medallion Architecture** (Bronze ➔ Silver ➔ Gold) to progressively enrich and clean data.

```mermaid
graph LR
    subgraph Data Sources
    A[Fake Data Generator]
    end

    subgraph Data Warehouse (PostgreSQL)
    B[(Source Schema)]
    C[(Bronze Schema)]
    D[(Silver Schema)]
    E[(Gold Schema)]
    end

    subgraph Orchestration
    F((Apache Airflow))
    end

    subgraph Transformation
    G{dbt}
    end

    subgraph BI
    H[Streamlit Dashboard]
    end

    A -- Python Load --> B
    F -- Triggers Task 1 --> A
    
    B -- Python Extract --> C
    F -- Triggers Task 2 --> C
    
    C -- dbt Models --> D
    F -- Triggers Task 3 & 4 --> G
    
    D -- dbt Marts --> E
    F -- Triggers Task 5 --> G
    
    E -- Live SQL Queries --> H
```

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed.
- Git installed.

### 1. Clone the repository
```bash
git clone https://github.com/Goddex-123/retail-elt-pipeline.git
cd retail-elt-pipeline
```

### 2. Start the Infrastructure
Spin up Airflow, PostgreSQL, Zookeeper, Kafka, and the Streamlit Dashboard using Docker Compose.
```bash
docker-compose up -d
```
*Note: The initial setup may take a few minutes as Airflow initializes its database.*

### 3. Run the ELT Pipeline
1. Open the **Airflow UI** at [http://localhost:8080](http://localhost:8080)
2. **Login:** `airflow` / `airflow`
3. Locate the `retail_elt_pipeline` DAG.
4. Toggle it **ON** and click the ▶️ **Trigger DAG** button.
5. Watch the pipeline extract, load, transform, and test the data in real-time!

### 4. View the Executive Dashboard
Once the Airflow pipeline successfully reaches the `dbt_run_marts` step (meaning the Gold Schema is populated), open the **Streamlit Dashboard** at [http://localhost:8501](http://localhost:8501) to view the live analytics.

## 🛠️ Project Structure

```text
├── dags/
│   └── retail_elt_dag.py        # Airflow DAG definition orchestrating the whole pipeline
├── dashboard/
│   ├── app.py                   # Premium Streamlit analytics app (Glassmorphism UI)
│   └── requirements.txt         # Dashboard dependencies
├── dbt_retail/
│   ├── models/
│   │   ├── staging/             # Silver Layer (stg_customers.sql, stg_orders.sql, schema.yml)
│   │   └── marts/               # Gold Layer (fct_orders.sql)
│   └── profiles.yml             # dbt database connection config
├── scripts/
│   ├── data_generator.py        # Mocks raw operational data
│   └── custom_extractor.py      # Moves data to Bronze layer
├── docker-compose.yml           # Multi-container architecture setup
└── .gitignore
```

## 📈 Key Features
- **Data Quality Testing:** Uses `dbt test` to ensure `customer_id` uniqueness, non-null checks, and positive quantity constraints before data enters the Gold layer.
- **Automated Dependency Management:** Airflow correctly chains Python Extractions and dbt Transformations.
- **Real-Time Analytics:** The Streamlit dashboard bypasses static CSVs and connects directly to the Data Warehouse (PostgreSQL) for live metrics.
- **Premium UI:** The dashboard features a custom dark mode, glassmorphism cards, and interactive Plotly charts.

---
*Built with ❤️ for Data Engineering.*
