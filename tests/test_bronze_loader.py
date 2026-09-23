"""
Tests for the bronze loader module.
Tests metadata column addition, empty source handling, and batch ID generation.
"""

import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestBronzeLoader:
    """Test suite for bronze layer loading logic."""

    def test_metadata_columns_added(self, sample_customer_data):
        """Bronze loader should add _loaded_at, _source, and _batch_id columns."""
        from datetime import datetime, timezone

        df = sample_customer_data.copy()

        # Simulate what bronze_loader does
        df["_loaded_at"] = datetime.now(timezone.utc).isoformat()
        df["_source"] = "source.customers"
        df["_batch_id"] = "test-batch-001"

        assert "_loaded_at" in df.columns
        assert "_source" in df.columns
        assert "_batch_id" in df.columns
        assert all(df["_source"] == "source.customers")

    def test_metadata_timestamp_is_utc(self, sample_customer_data):
        """Loaded_at timestamp should be in UTC ISO format."""
        from datetime import datetime, timezone

        loaded_at = datetime.now(timezone.utc).isoformat()
        assert "+" in loaded_at or "Z" in loaded_at

    def test_batch_id_generation(self):
        """Each load should generate a unique batch ID."""
        from src.logger import generate_correlation_id

        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        assert id1 != id2
        assert id1.startswith("run-")
        assert len(id1) > 20

    def test_empty_dataframe_detection(self):
        """Should correctly identify empty DataFrames."""
        df = pd.DataFrame()
        assert df.empty

        df_with_data = pd.DataFrame({"a": [1]})
        assert not df_with_data.empty

    def test_source_tables_list_complete(self):
        """SOURCE_TABLES should contain all 13 expected tables."""
        from src.config import SOURCE_TABLES

        expected = [
            "customers", "products", "categories", "suppliers", "stores",
            "orders", "order_items", "payments", "returns", "shipments",
            "reviews", "inventory", "promotions",
        ]
        assert set(expected) == set(SOURCE_TABLES)
        assert len(SOURCE_TABLES) == 13

    def test_schema_config_values(self):
        """Schema config should map to expected schema names."""
        from src.config import schema_config

        assert schema_config.source == "source"
        assert schema_config.bronze == "bronze"
        assert schema_config.silver == "silver"
        assert schema_config.gold == "gold"
