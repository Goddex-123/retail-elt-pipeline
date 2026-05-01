"""
Retail ELT Platform — Test Configuration
==========================================
Shared pytest fixtures for all test modules.
"""

import pytest
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    import pandas as pd

    return pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "first_name": ["Amit", "Priya", "Raj", "Sneha", "Vikram"],
        "last_name": ["Sharma", "Patel", "Kumar", "Gupta", "Singh"],
        "email": ["amit@test.com", "priya@test.com", "raj@test.com", "sneha@test.com", "vikram@test.com"],
        "phone": ["9876543210", None, "9876543212", "9876543213", "9876543214"],
        "city": ["Mumbai", None, " DEL ", "Pune", "mumbai"],
        "loyalty_tier": ["Gold", "Silver", "Bronze", "Platinum", "Silver"],
        "signup_date": ["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05", "2024-05-01"],
        "date_of_birth": ["1990-05-15", "1985-08-20", "1992-01-10", "1988-11-05", "1995-03-01"],
    })


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    import pandas as pd

    return pd.DataFrame({
        "product_id": [1, 2, 3],
        "product_name": ["Laptop Pro 15", "Smartphone X", "Headphones"],
        "category_id": [1, 1, 2],
        "supplier_id": [1, 2, 1],
        "unit_price": [49999.99, 29999.99, 1999.99],
        "cost_price": [30000.00, 18000.00, 800.00],
        "weight_kg": [2.1, 0.2, 0.3],
        "is_active": [True, True, False],
        "created_at": ["2024-01-01", "2024-01-01", "2024-02-01"],
    })


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    import pandas as pd

    return pd.DataFrame({
        "order_id": [10001, 10002, 10003],
        "customer_id": [1, 2, 3],
        "store_id": [1, 2, 1],
        "order_date": ["2024-06-01 10:00:00", "2024-06-02 11:00:00", "2024-06-03 12:00:00"],
        "status": ["completed", "pending", "cancelled"],
        "total_amount": [49999.99, 29999.99, 0],
        "discount_amount": [0, 500, 0],
        "shipping_cost": [99, 49, 0],
    })
