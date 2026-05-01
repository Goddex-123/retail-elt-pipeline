"""
Retail ELT Platform — Centralized Configuration
================================================
All pipeline configuration loaded from environment variables
with sensible defaults. Never hardcode credentials.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseConfig:
    """PostgreSQL connection configuration."""

    user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "airflow"))
    password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "airflow"))
    host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "postgres"))
    port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    database: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "retail_warehouse"))

    @property
    def url(self) -> str:
        """SQLAlchemy-compatible connection URL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass(frozen=True)
class PipelineConfig:
    """Pipeline runtime configuration."""

    log_level: str = field(default_factory=lambda: os.getenv("PIPELINE_LOG_LEVEL", "INFO"))
    batch_size: int = field(default_factory=lambda: int(os.getenv("PIPELINE_BATCH_SIZE", "1000")))
    enable_streaming: bool = field(
        default_factory=lambda: os.getenv("PIPELINE_ENABLE_STREAMING", "false").lower() == "true"
    )
    dbt_profiles_dir: str = field(default_factory=lambda: os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt_retail"))
    dbt_target: str = field(default_factory=lambda: os.getenv("DBT_TARGET", "dev"))


@dataclass(frozen=True)
class SchemaConfig:
    """Database schema names for each layer."""

    source: str = "source"
    bronze: str = "bronze"
    silver: str = "silver"
    gold: str = "gold"


# ---- Singleton Instances ----
db_config = DatabaseConfig()
pipeline_config = PipelineConfig()
schema_config = SchemaConfig()


# ---- Table Registry ----
SOURCE_TABLES = [
    "customers",
    "products",
    "categories",
    "suppliers",
    "stores",
    "orders",
    "order_items",
    "payments",
    "returns",
    "shipments",
    "reviews",
    "inventory",
    "promotions",
]

DIMENSION_TABLES = ["customers", "products", "categories", "suppliers", "stores"]
FACT_TABLES = ["orders", "order_items", "payments", "returns", "shipments", "reviews", "inventory", "promotions"]
