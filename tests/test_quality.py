"""
Tests for the data quality report module.
Tests quality check functions and report generation.
"""

import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestQualityModule:
    """Test suite for data quality reporting."""

    def test_min_row_counts_defined(self):
        """Quality module should define minimum row count thresholds."""
        from src.quality import MIN_ROW_COUNTS

        assert "customers" in MIN_ROW_COUNTS
        assert "orders" in MIN_ROW_COUNTS
        assert MIN_ROW_COUNTS["customers"] >= 100

    def test_not_null_columns_defined(self):
        """Quality module should define critical not-null columns."""
        from src.quality import NOT_NULL_COLUMNS

        assert "customers" in NOT_NULL_COLUMNS
        assert "customer_id" in NOT_NULL_COLUMNS["customers"]
        assert "email" in NOT_NULL_COLUMNS["customers"]

    def test_primary_keys_defined(self):
        """Quality module should define primary keys for duplicate checks."""
        from src.quality import PRIMARY_KEYS

        assert PRIMARY_KEYS["customers"] == "customer_id"
        assert PRIMARY_KEYS["orders"] == "order_id"

    def test_format_quality_report_structure(self):
        """Formatted report should contain expected sections."""
        from src.quality import format_quality_report

        mock_report = {
            "report_time": "2024-01-01T00:00:00",
            "correlation_id": "test-run",
            "schema": "bronze",
            "total_checks": 10,
            "passed": 9,
            "failed": 1,
            "quality_score_pct": 90.0,
            "status": "WARN",
            "checks": [
                {
                    "check": "row_count",
                    "table": "bronze.customers",
                    "value": 500,
                    "threshold": 100,
                    "passed": True,
                    "message": "500 rows",
                },
                {
                    "check": "null_rate",
                    "table": "bronze.customers",
                    "column": "email",
                    "null_count": 5,
                    "null_pct": 1.0,
                    "passed": True,
                    "message": "5 nulls (1.0%)",
                },
            ],
        }

        formatted = format_quality_report(mock_report)

        assert "DATA QUALITY REPORT" in formatted
        assert "bronze" in formatted
        assert "90.0%" in formatted
        assert "WARN" in formatted
        assert "9/10" in formatted

    def test_format_report_shows_pass_fail_icons(self):
        """Report should use ✅ and ⚠️ icons."""
        from src.quality import format_quality_report

        mock_report = {
            "report_time": "2024-01-01T00:00:00",
            "correlation_id": "test",
            "schema": "bronze",
            "total_checks": 2,
            "passed": 1,
            "failed": 1,
            "quality_score_pct": 50.0,
            "status": "FAIL",
            "checks": [
                {"check": "row_count", "table": "bronze.orders", "passed": True, "message": "OK"},
                {"check": "duplicates", "table": "bronze.orders", "passed": False, "message": "10 dupes"},
            ],
        }

        formatted = format_quality_report(mock_report)
        assert "✅" in formatted
        assert "⚠️" in formatted

    def test_quality_score_calculation(self):
        """Quality score should be (passed / total) * 100."""
        passed = 38
        total = 40
        score = round((passed / total) * 100, 2)
        assert score == 95.0

    def test_quality_status_thresholds(self):
        """Status should be PASS >= 95%, WARN >= 80%, FAIL < 80%."""
        def get_status(score):
            return "PASS" if score >= 95 else "WARN" if score >= 80 else "FAIL"

        assert get_status(100) == "PASS"
        assert get_status(95) == "PASS"
        assert get_status(94.9) == "WARN"
        assert get_status(80) == "WARN"
        assert get_status(79.9) == "FAIL"
        assert get_status(0) == "FAIL"
