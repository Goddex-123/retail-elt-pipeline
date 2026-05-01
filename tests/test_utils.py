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
