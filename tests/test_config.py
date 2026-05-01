"""
Tests for the configuration module.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestConfig:
    """Test suite for configuration loading."""

    def test_database_config_defaults(self):
        from src.config import DatabaseConfig

        config = DatabaseConfig()
        assert config.host in ("postgres", os.getenv("POSTGRES_HOST", "postgres"))
        assert config.port == int(os.getenv("POSTGRES_PORT", "5432"))
        assert config.database in ("retail_warehouse", os.getenv("POSTGRES_DB", "retail_warehouse"))

    def test_database_url_format(self):
        from src.config import DatabaseConfig

        config = DatabaseConfig()
        url = config.url
        assert url.startswith("postgresql+psycopg2://")
        assert "@" in url
        assert ":" in url

    def test_pipeline_config_defaults(self):
        from src.config import PipelineConfig

        config = PipelineConfig()
        assert config.log_level in ("INFO", os.getenv("PIPELINE_LOG_LEVEL", "INFO"))
        assert config.batch_size > 0

    def test_schema_config(self):
        from src.config import SchemaConfig

        config = SchemaConfig()
        assert config.source == "source"
        assert config.bronze == "bronze"
        assert config.silver == "silver"
        assert config.gold == "gold"

    def test_source_tables_complete(self):
        from src.config import SOURCE_TABLES

        assert len(SOURCE_TABLES) == 13
        assert "customers" in SOURCE_TABLES
        assert "orders" in SOURCE_TABLES
        assert "promotions" in SOURCE_TABLES

    def test_table_classification(self):
        from src.config import DIMENSION_TABLES, FACT_TABLES

        assert "customers" in DIMENSION_TABLES
        assert "products" in DIMENSION_TABLES
        assert "orders" in FACT_TABLES
        assert "payments" in FACT_TABLES

        # No overlap
        overlap = set(DIMENSION_TABLES) & set(FACT_TABLES)
        assert len(overlap) == 0, f"Overlap between dimensions and facts: {overlap}"
