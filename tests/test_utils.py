"""
Tests for utility functions.
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import (
    current_utc_timestamp,
    sanitize_column_name,
    validate_dataframe,
    chunked,
)


class TestUtils:
    """Test suite for utility functions."""

    def test_current_utc_timestamp_format(self):
        ts = current_utc_timestamp()
        assert "T" in ts
        assert "+" in ts or "Z" in ts

    def test_sanitize_column_name(self):
        assert sanitize_column_name("  Order ID  ") == "order_id"
        assert sanitize_column_name("Total Amount ($)") == "total_amount"
        assert sanitize_column_name("customer__name") == "customer_name"
        assert sanitize_column_name("UPPER_CASE") == "upper_case"

    def test_chunked(self):
        items = list(range(10))
        chunks = list(chunked(items, 3))
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[-1] == [9]

    def test_chunked_exact_division(self):
        items = list(range(9))
        chunks = list(chunked(items, 3))
        assert len(chunks) == 3

    def test_validate_dataframe_success(self):
        df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        assert validate_dataframe(df, ["a", "b"], "test") is True

    def test_validate_dataframe_missing_columns(self):
        df = pd.DataFrame({"a": [1], "b": [2]})
        with pytest.raises(ValueError, match="missing columns"):
            validate_dataframe(df, ["a", "b", "c"], "test")

    def test_chunked_empty_list(self):
        """Chunking an empty list should return no chunks."""
        chunks = list(chunked([], 3))
        assert len(chunks) == 0

    def test_chunked_single_element(self):
        """Chunking a single element should return one chunk."""
        chunks = list(chunked([1], 5))
        assert len(chunks) == 1
        assert chunks[0] == [1]

    def test_sanitize_empty_string(self):
        """Sanitizing empty string should return empty string."""
        result = sanitize_column_name("")
        assert result == ""

    def test_sanitize_special_characters(self):
        """Sanitizing special characters should replace with underscores."""
        assert sanitize_column_name("col@#$%") == "col"
        assert sanitize_column_name("a.b.c") == "a_b_c"

    def test_validate_dataframe_empty(self):
        """Validating an empty DataFrame should still check columns."""
        df = pd.DataFrame({"a": [], "b": []})
        assert validate_dataframe(df, ["a", "b"], "empty_table") is True

    def test_current_utc_timestamp_is_recent(self):
        """Timestamp should be from the current day."""
        from datetime import datetime
        ts = current_utc_timestamp()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        assert today in ts

    def test_validate_not_empty_success(self):
        """Non-empty dataframe should pass validation."""
        from src.utils import validate_not_empty
        df = pd.DataFrame({"a": [1, 2]})
        assert validate_not_empty(df, "test_table") is True

    def test_validate_not_empty_raises_on_empty(self):
        """Empty dataframe should raise ValueError."""
        from src.utils import validate_not_empty
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="is empty"):
            validate_not_empty(df, "test_table")

    def test_validate_not_empty_raises_on_none(self):
        """None should raise ValueError."""
        from src.utils import validate_not_empty
        with pytest.raises(ValueError, match="is empty"):
            validate_not_empty(None, "test_table")
