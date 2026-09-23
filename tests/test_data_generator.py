"""
Tests for the data generator module.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDataGenerator:
    """Test suite for data generation functions."""

    def test_generate_categories(self):
        from scripts.data_generator import generate_categories

        df = generate_categories()
        assert len(df) == 8
        assert "category_id" in df.columns
        assert "category_name" in df.columns
        assert df["category_id"].is_unique

    def test_generate_suppliers(self):
        from scripts.data_generator import generate_suppliers

        df = generate_suppliers(n=5)
        assert len(df) == 5
        assert "supplier_id" in df.columns
        assert "supplier_name" in df.columns
        assert df["supplier_id"].is_unique

    def test_generate_stores(self):
        from scripts.data_generator import generate_stores

        df = generate_stores(n=6)
        assert len(df) == 6
        assert "store_id" in df.columns
        assert "region" in df.columns
        assert all(r in ["North", "South", "East", "West"] for r in df["region"])

    def test_generate_customers_has_duplicates(self):
        """Verify intentional duplicates are introduced."""
        from scripts.data_generator import generate_customers

        df = generate_customers(n=100)
        # Should have ~110 rows (100 + 10% duplicates)
        assert len(df) > 100
        assert len(df) <= 115

    def test_generate_customers_has_null_cities(self):
        """Verify intentional null cities exist."""
        from scripts.data_generator import generate_customers

        df = generate_customers(n=200)
        null_count = df["city"].isna().sum()
        assert null_count > 0, "Expected some null cities for data quality testing"

    def test_generate_products(self):
        from scripts.data_generator import generate_products

        df = generate_products(n=10)
        assert len(df) == 10
        assert "product_id" in df.columns
        assert "unit_price" in df.columns
        assert "cost_price" in df.columns
        assert all(df["cost_price"] <= df["unit_price"])

    def test_generate_orders(self):
        from scripts.data_generator import generate_orders

        df = generate_orders(
            customer_ids=[1, 2, 3],
            store_ids=[1, 2],
            n=50,
        )
        assert len(df) == 50
        assert "order_id" in df.columns
        assert all(df["customer_id"].isin([1, 2, 3]))

    def test_generate_order_items(self):
        from scripts.data_generator import generate_order_items

        df = generate_order_items(
            order_ids=[10001, 10002],
            product_ids=[1, 2, 3],
        )
        assert len(df) > 0
        assert "order_item_id" in df.columns
        assert "line_total_gross" not in df.columns  # Calculated in staging

    def test_generate_payments(self):
        from scripts.data_generator import generate_payments

        df = generate_payments(order_ids=[10001, 10002, 10003])
        assert len(df) == 3
        assert "payment_method" in df.columns
        assert "payment_status" in df.columns

    def test_generate_all_data_returns_13_tables(self):
        from scripts.data_generator import generate_all_data

        tables = generate_all_data(n_customers=50, n_orders=100)
        assert len(tables) == 13
        expected_tables = [
            "customers", "products", "categories", "suppliers", "stores",
            "orders", "order_items", "payments", "returns", "shipments",
            "reviews", "inventory", "promotions",
        ]
        for table in expected_tables:
            assert table in tables, f"Missing table: {table}"
            assert len(tables[table]) > 0, f"Table {table} is empty"

    def test_generate_customers_zero(self):
        """Zero customers requested should return empty dataframe."""
        from scripts.data_generator import generate_customers
        df = generate_customers(n=0)
        assert len(df) == 0

    def test_generate_orders_future_dates_present(self):
        """Verify clock-skew simulation introduces future-dated orders."""
        from datetime import datetime
        from scripts.data_generator import generate_orders
        df = generate_orders(customer_ids=[1, 2], store_ids=[1], n=200)
        future_orders = df[df["order_date"] > datetime.now()]
        assert len(future_orders) > 0, "Expected simulated future-dated orders"

    def test_generate_order_items_negative_quantities_present(self):
        """Verify legacy bug simulation introduces negative quantities."""
        from scripts.data_generator import generate_order_items
        df = generate_order_items(order_ids=list(range(1, 300)), product_ids=[1, 2, 3])
        negative_qty = df[df["quantity"] < 0]
        assert len(negative_qty) > 0, "Expected simulated negative quantity bug"
