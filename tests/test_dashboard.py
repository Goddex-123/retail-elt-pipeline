"""
Tests for the Streamlit dashboard application.
Verifies clean parsing, component execution, and error resilience.
"""

import sys
import os
from datetime import datetime
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDashboard:
    """Dashboard execution and render verification tests."""

    def test_dashboard_compiles(self):
        """dashboard/app.py should be valid Python code without syntax errors."""
        import py_compile
        app_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py")
        result = py_compile.compile(app_path)
        assert result is not None

    def test_dashboard_runs_offline_gracefully(self):
        """Dashboard should render diagnostics and stop gracefully when DB is offline."""
        from streamlit.testing.v1 import AppTest
        app_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py")
        at = AppTest.from_file(app_path)
        at.run()
        # Verify no unhandled Python exceptions occurred
        assert len(at.exception) == 0

    @patch("sqlalchemy.create_engine")
    @patch("pandas.read_sql")
    def test_dashboard_renders_all_components_with_data(self, mock_read_sql, mock_engine):
        """When gold data is present, all tabs, KPIs, and charts should render without errors."""
        import streamlit as st
        from streamlit.testing.v1 import AppTest

        st.cache_data.clear()
        mock_engine.return_value = MagicMock()

        # Mock standard gold mart datasets
        fct_orders = pd.DataFrame({
            "order_item_id": [1, 2, 3, 4],
            "order_id": [101, 102, 103, 104],
            "customer_id": [1, 2, 1, 3],
            "region": ["North", "South", "East", "West"],
            "order_status": ["completed", "completed", "completed", "pending"],
            "line_total_net": [1200.0, 850.0, 450.0, 300.0],
            "line_total_gross": [1300.0, 900.0, 500.0, 320.0],
            "discount_amount": [100.0, 50.0, 50.0, 20.0],
            "gross_profit": [400.0, 250.0, 150.0, 80.0],
        })

        daily_sales = pd.DataFrame({
            "sale_date": pd.date_range("2024-01-01", periods=10),
            "net_revenue": [1000, 1500, 1200, 1800, 1400, 1600, 2000, 1900, 2100, 2200],
            "revenue_7d_ma": [1000, 1250, 1233, 1375, 1380, 1416, 1500, 1628, 1714, 1800],
        })

        clv = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "customer_name": ["Alice", "Bob", "Charlie"],
            "customer_city": ["Mumbai", "Delhi", "Bangalore"],
            "loyalty_tier": ["Gold", "Silver", "Bronze"],
            "customer_segment": ["Champions", "Loyal Customers", "At Risk"],
            "estimated_clv": [15000.0, 8000.0, 3000.0],
            "total_orders": [5, 3, 1],
            "total_revenue": [6000.0, 2550.0, 300.0],
            "days_since_last_order": [5, 18, 75],
            "churn_status": ["active", "warm", "at_risk"],
            "winback_priority": ["low_priority", "medium_priority", "high_priority"],
        })

        churn = clv.copy()

        top_prods = pd.DataFrame({
            "product_name": [f"Product {i}" for i in range(1, 11)],
            "total_revenue": [5000 - i * 300 for i in range(10)],
            "revenue_contribution_pct": [20.0, 15.0, 12.0, 10.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0],
        })

        region_rev = pd.DataFrame({
            "region": ["North", "South", "East", "West"],
            "store_count": [3, 3, 3, 3],
            "total_orders": [500, 400, 350, 300],
            "net_revenue": [600000.0, 450000.0, 350000.0, 300000.0],
            "revenue_share_pct": [35.0, 26.5, 20.5, 18.0],
        })

        payment_rates = pd.DataFrame({
            "payment_method": ["upi", "credit_card", "net_banking", "cod"],
            "total_transactions": [1000, 600, 300, 100],
            "successful_transactions": [980, 570, 280, 85],
            "success_rate_pct": [98.0, 95.0, 93.3, 85.0],
            "reliability_tier": ["excellent", "excellent", "good", "fair"],
        })

        stock_alerts = pd.DataFrame({
            "inventory_id": [1, 2],
            "product_name": ["Product A", "Product B"],
            "store_name": ["Store 1", "Store 2"],
            "region": ["North", "South"],
            "quantity_on_hand": [0, 5],
            "reorder_level": [20, 20],
            "suggested_reorder_qty": [40, 35],
            "alert_severity": ["critical", "high"],
        })

        inv_turnover = pd.DataFrame({
            "product_name": ["Product A", "Product B"],
            "turnover_category": ["fast_moving", "moderate"],
            "turnover_ratio": [6.2, 3.1],
        })

        gross_margin = pd.DataFrame({
            "product_name": [f"Product {i}" for i in range(1, 11)],
            "gross_margin_pct": [55.0 - i * 3 for i in range(10)],
            "margin_tier": ["high_margin"] * 5 + ["medium_margin"] * 5,
        })

        refund_data = pd.DataFrame({
            "return_category": ["Defective", "Wrong Item", "Buyer Remorse"],
            "return_count": [25, 15, 10],
        })

        data_map = {
            "gold.fct_orders": fct_orders,
            "gold.daily_sales": daily_sales,
            "gold.customer_lifetime_value": clv,
            "gold.churn_risk": churn,
            "gold.top_products": top_prods,
            "gold.revenue_by_region": region_rev,
            "gold.payment_success_rate": payment_rates,
            "gold.stock_alerts": stock_alerts,
            "gold.inventory_turnover": inv_turnover,
            "gold.gross_margin": gross_margin,
            "gold.refund_analysis": refund_data,
        }

        def mock_sql_dispatcher(query, *args, **kwargs):
            if "MAX(_loaded_at::timestamp)" in query:
                return pd.DataFrame({"last_load": [datetime.utcnow()]})
            for table_key, df in data_map.items():
                if table_key in query:
                    return df
            return pd.DataFrame()

        mock_read_sql.side_effect = mock_sql_dispatcher

        app_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py")
        at = AppTest.from_file(app_path)
        at.run()

        # Verify no unhandled exceptions occurred
        assert len(at.exception) == 0

        # Verify metrics rendered
        labels = [m.label.upper() for m in at.metric]
        assert "NET REVENUE" in labels
        assert "COMPLETED ORDERS" in labels
