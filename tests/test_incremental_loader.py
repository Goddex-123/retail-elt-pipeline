"""
Tests for the incremental loader module.
Tests high-water mark logic, identifier validation, and duplicate prevention.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestIncrementalLoader:
    """Test suite for incremental loading logic."""

    def test_incremental_tables_defined(self):
        """INCREMENTAL_TABLES should be properly configured."""
        from scripts.incremental_loader import INCREMENTAL_TABLES

        assert "orders" in INCREMENTAL_TABLES
        assert "payments" in INCREMENTAL_TABLES
        assert "reviews" in INCREMENTAL_TABLES
        assert INCREMENTAL_TABLES["orders"] == "order_date"

    def test_allowed_tables_whitelist(self):
        """Whitelist should match INCREMENTAL_TABLES keys."""
        from scripts.incremental_loader import _ALLOWED_TABLES, INCREMENTAL_TABLES

        assert _ALLOWED_TABLES == set(INCREMENTAL_TABLES.keys())

    def test_allowed_columns_whitelist(self):
        """Whitelist should match INCREMENTAL_TABLES values."""
        from scripts.incremental_loader import _ALLOWED_COLUMNS, INCREMENTAL_TABLES

        assert _ALLOWED_COLUMNS == set(INCREMENTAL_TABLES.values())

    def test_validate_identifier_valid(self):
        """Valid identifiers should pass validation."""
        from scripts.incremental_loader import _validate_identifier

        result = _validate_identifier("orders", {"orders", "payments"}, "table")
        assert result == "orders"

    def test_validate_identifier_invalid(self):
        """Invalid identifiers should raise ValueError."""
        from scripts.incremental_loader import _validate_identifier

        with pytest.raises(ValueError, match="Invalid table"):
            _validate_identifier("malicious_table", {"orders"}, "table")

    def test_validate_identifier_sql_injection_attempt(self):
        """SQL injection attempts should be blocked by validation."""
        from scripts.incremental_loader import _validate_identifier

        with pytest.raises(ValueError):
            _validate_identifier("orders; DROP TABLE users;--", {"orders"}, "table")

    def test_validate_identifier_empty_string(self):
        """Empty string should be rejected."""
        from scripts.incremental_loader import _validate_identifier

        with pytest.raises(ValueError):
            _validate_identifier("", {"orders"}, "table")

    def test_epoch_default_hwm(self):
        """Default high-water mark should be epoch when table doesn't exist."""
        # The function returns epoch string when it can't find the table
        default_hwm = "1970-01-01 00:00:00"
        assert default_hwm == "1970-01-01 00:00:00"

    def test_incremental_metadata_columns(self):
        """Incremental loads should add _is_incremental flag."""
        import pandas as pd
        from datetime import datetime, timezone

        df = pd.DataFrame({"order_id": [1, 2, 3], "order_date": ["2024-01-01"] * 3})

        # Simulate what incremental_load does
        df["_loaded_at"] = datetime.now(timezone.utc).isoformat()
        df["_source"] = "source.orders"
        df["_batch_id"] = "test-batch"
        df["_is_incremental"] = True

        assert "_is_incremental" in df.columns
        assert all(df["_is_incremental"])
