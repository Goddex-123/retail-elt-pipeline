"""
Retail ELT Platform — Synthetic Data Generator
===============================================
Generates realistic retail data across 13 tables using Faker.
Introduces intentional data quality issues (nulls, duplicates,
negative values, late-arriving records) to simulate real-world
source system behavior.

Usage:
    python scripts/data_generator.py [--records 1000] [--output-csv]
"""

import sys
import os
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from faker import Faker
except ImportError:
    print("Installing faker...")
    os.system("pip install faker")
    from faker import Faker

from src.config import db_config, schema_config, SOURCE_TABLES
from src.logger import get_logger, generate_correlation_id
from src.db import get_engine, ensure_schemas
from src.utils import timer

fake = Faker("en_IN")  # Indian locale for realistic Bombay Bazaar data
Faker.seed(42)
random.seed(42)
np.random.seed(42)

logger = get_logger(__name__)


# ============================================================
# Dimension Generators
# ============================================================

def generate_categories(n: int = 8) -> pd.DataFrame:
    """Generate product category hierarchy."""
    categories = [
        {"category_id": 1, "category_name": "Electronics", "parent_category_id": None},
        {"category_id": 2, "category_name": "Clothing", "parent_category_id": None},
        {"category_id": 3, "category_name": "Home & Kitchen", "parent_category_id": None},
        {"category_id": 4, "category_name": "Books", "parent_category_id": None},
        {"category_id": 5, "category_name": "Smartphones", "parent_category_id": 1},
        {"category_id": 6, "category_name": "Laptops", "parent_category_id": 1},
        {"category_id": 7, "category_name": "Men's Fashion", "parent_category_id": 2},
        {"category_id": 8, "category_name": "Women's Fashion", "parent_category_id": 2},
    ]
    return pd.DataFrame(categories[:n])


def generate_suppliers(n: int = 10) -> pd.DataFrame:
    """Generate supplier data with contact information."""
    data = []
    for i in range(1, n + 1):
        data.append({
            "supplier_id": i,
            "supplier_name": fake.company(),
            "contact_name": fake.name(),
            "contact_email": fake.company_email(),
            "contact_phone": fake.phone_number(),
            "city": random.choice(["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad"]),
            "country": "India",
            "created_at": fake.date_between(start_date="-3y", end_date="-1y"),
        })
    return pd.DataFrame(data)


def generate_stores(n: int = 12) -> pd.DataFrame:
    """Generate retail store locations."""
    regions = {
        "Mumbai": "West", "Pune": "West", "Ahmedabad": "West",
        "Delhi": "North", "Jaipur": "North", "Lucknow": "North",
        "Bangalore": "South", "Chennai": "South", "Hyderabad": "South",
        "Kolkata": "East", "Bhubaneswar": "East", "Guwahati": "East",
    }
    cities = list(regions.keys())[:n]
    data = []
    for i, city in enumerate(cities, 1):
        data.append({
            "store_id": i,
            "store_name": f"Bombay Bazaar - {city}",
            "city": city,
            "region": regions[city],
            "store_type": random.choice(["Flagship", "Standard", "Express"]),
            "opening_date": fake.date_between(start_date="-5y", end_date="-6m"),
            "is_active": random.choices([True, False], weights=[95, 5])[0],
        })
    return pd.DataFrame(data)


def generate_customers(n: int = 500) -> pd.DataFrame:
    """
    Generate customer data with intentional quality issues:
    - Null cities (~5%)
    - Inconsistent casing
    - Duplicate rows (~10%)
    - Leading/trailing whitespace
    """
    logger.info(f"Generating {n} customers with quality issues...")
    cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad",
              "Kolkata", "Jaipur", None, "mumbai", " DEL ", "  Pune  "]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]

    data = []
    for i in range(1, n + 1):
        data.append({
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number() if random.random() > 0.1 else None,
            "city": random.choice(cities),
            "loyalty_tier": random.choices(tiers, weights=[40, 30, 20, 10])[0],
            "signup_date": fake.date_between(start_date="-3y", end_date="today"),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=70),
        })

    df = pd.DataFrame(data)

    # Introduce ~10% duplicate rows (simulates source system bug)
    duplicates = df.sample(int(n * 0.1), random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)

    return df


def generate_products(n: int = 50) -> pd.DataFrame:
    """Generate product catalog with pricing."""
    product_names = [
        "Laptop Pro 15", "Smartphone X", "Wireless Headphones", "4K Monitor",
        "Mechanical Keyboard", "USB-C Hub", "Tablet Air", "Smartwatch Elite",
        "Bluetooth Speaker", "Gaming Mouse", "Webcam HD", "External SSD 1TB",
        "Noise Cancelling Earbuds", "Portable Charger", "LED Desk Lamp",
        "Ergonomic Chair", "Standing Desk", "Monitor Arm", "Cable Organizer",
        "Laptop Stand", "Cotton T-Shirt", "Denim Jeans", "Silk Saree",
        "Running Shoes", "Leather Wallet", "Backpack Pro", "Sunglasses UV",
        "Wrist Watch Classic", "Formal Shirt", "Kurta Set",
        "Non-Stick Pan Set", "Pressure Cooker", "Blender Pro", "Coffee Maker",
        "Water Purifier", "Air Purifier", "Vacuum Cleaner", "Iron Steam",
        "Microwave Oven", "Induction Cooktop",
        "Python Programming", "Data Engineering Guide", "ML Handbook",
        "Fiction Novel", "Self-Help Book", "Cookbook India", "History Atlas",
        "Science for Kids", "Art of Design", "Business Strategy",
    ]

    data = []
    for i in range(1, min(n, len(product_names)) + 1):
        cat_id = (1 if i <= 20 else 2 if i <= 30 else 3 if i <= 40 else 4)
        data.append({
            "product_id": i,
            "product_name": product_names[i - 1],
            "category_id": cat_id,
            "supplier_id": random.randint(1, 10),
            "unit_price": round(random.uniform(199, 89999), 2),
            "cost_price": None,  # Will be derived
            "weight_kg": round(random.uniform(0.1, 15.0), 2),
            "is_active": random.choices([True, False], weights=[90, 10])[0],
            "created_at": fake.date_between(start_date="-2y", end_date="-30d"),
        })

    df = pd.DataFrame(data)
    # cost_price = 40-80% of unit_price
    df["cost_price"] = (df["unit_price"] * np.random.uniform(0.4, 0.8, len(df))).round(2)

    return df


# ============================================================
# Fact / Transactional Generators
# ============================================================

def generate_orders(customer_ids: list, store_ids: list, n: int = 2000) -> pd.DataFrame:
    """
    Generate order headers with intentional issues:
    - ~3% negative quantities (legacy system bug simulation)
    - ~2% future-dated orders (clock skew simulation)
    """
    logger.info(f"Generating {n} orders...")
    statuses = ["completed", "pending", "shipped", "cancelled", "returned"]

    data = []
    for i in range(1, n + 1):
        order_date = fake.date_time_between(start_date="-90d", end_date="now")
        data.append({
            "order_id": 10000 + i,
            "customer_id": random.choice(customer_ids),
            "store_id": random.choice(store_ids),
            "order_date": order_date,
            "status": random.choices(statuses, weights=[60, 15, 10, 10, 5])[0],
            "total_amount": 0,  # Will be calculated from order_items
            "discount_amount": round(random.uniform(0, 500), 2) if random.random() > 0.7 else 0,
            "shipping_cost": round(random.uniform(0, 150), 2),
        })

    df = pd.DataFrame(data)

    # ~2% future-dated orders (simulates clock skew)
    future_idx = df.sample(int(n * 0.02), random_state=42).index
    df.loc[future_idx, "order_date"] = df.loc[future_idx, "order_date"] + timedelta(days=random.randint(30, 90))

    return df


def generate_order_items(order_ids: list, product_ids: list, n_per_order_max: int = 5) -> pd.DataFrame:
    """Generate order line items — multiple items per order."""
    logger.info("Generating order items...")
    data = []
    item_id = 1

    for order_id in order_ids:
        num_items = random.randint(1, n_per_order_max)
        selected_products = random.sample(product_ids, min(num_items, len(product_ids)))

        for product_id in selected_products:
            qty = random.randint(1, 5)
            # ~3% negative quantity bug
            if random.random() < 0.03:
                qty = -1
            data.append({
                "order_item_id": item_id,
                "order_id": order_id,
                "product_id": product_id,
                "quantity": qty,
                "unit_price": round(random.uniform(199, 89999), 2),
                "discount_pct": random.choice([0, 0, 0, 5, 10, 15, 20]),
            })
            item_id += 1

    return pd.DataFrame(data)


def generate_payments(order_ids: list) -> pd.DataFrame:
    """Generate payment records — one per order, ~5% failures."""
    logger.info("Generating payments...")
    methods = ["credit_card", "debit_card", "upi", "net_banking", "cash_on_delivery", "wallet"]

    data = []
    for i, order_id in enumerate(order_ids, 1):
        status = random.choices(["success", "failed", "pending", "refunded"], weights=[85, 5, 5, 5])[0]
        data.append({
            "payment_id": i,
            "order_id": order_id,
            "payment_method": random.choices(methods, weights=[25, 20, 30, 10, 10, 5])[0],
            "payment_status": status,
            "payment_date": fake.date_time_between(start_date="-90d", end_date="now"),
            "amount": round(random.uniform(199, 99999), 2),
            "currency": "INR",
        })
    return pd.DataFrame(data)


def generate_returns(order_ids: list, n: int = 150) -> pd.DataFrame:
    """Generate return/refund records for ~7% of orders."""
    logger.info(f"Generating {n} returns...")
    reasons = [
        "defective", "wrong_item", "size_issue", "changed_mind",
        "damaged_in_transit", "late_delivery", "quality_issue",
    ]
    return_orders = random.sample(order_ids, min(n, len(order_ids)))

    data = []
    for i, order_id in enumerate(return_orders, 1):
        data.append({
            "return_id": i,
            "order_id": order_id,
            "return_date": fake.date_time_between(start_date="-60d", end_date="now"),
            "reason": random.choice(reasons),
            "refund_amount": round(random.uniform(199, 50000), 2),
            "refund_status": random.choice(["processed", "pending", "rejected"]),
        })
    return pd.DataFrame(data)


def generate_shipments(order_ids: list) -> pd.DataFrame:
    """Generate shipment tracking for non-cancelled orders."""
    logger.info("Generating shipments...")
    carriers = ["BlueDart", "Delhivery", "DTDC", "FedEx India", "Ecom Express"]

    data = []
    for i, order_id in enumerate(order_ids, 1):
        ship_date = fake.date_time_between(start_date="-85d", end_date="now")
        delivery_days = random.randint(1, 14)
        data.append({
            "shipment_id": i,
            "order_id": order_id,
            "carrier": random.choice(carriers),
            "tracking_number": fake.bothify(text="??########"),
            "shipped_date": ship_date,
            "estimated_delivery": ship_date + timedelta(days=delivery_days),
            "actual_delivery": (
                ship_date + timedelta(days=delivery_days + random.randint(-2, 5))
                if random.random() > 0.1 else None  # ~10% not yet delivered
            ),
            "status": random.choices(
                ["delivered", "in_transit", "out_for_delivery", "delayed"],
                weights=[70, 15, 10, 5],
            )[0],
        })
    return pd.DataFrame(data)


def generate_reviews(order_ids: list, customer_ids: list, product_ids: list, n: int = 800) -> pd.DataFrame:
    """Generate product reviews with ratings and text."""
    logger.info(f"Generating {n} reviews...")
    data = []
    for i in range(1, n + 1):
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 35, 35])[0]
        data.append({
            "review_id": i,
            "order_id": random.choice(order_ids),
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "rating": rating,
            "review_text": fake.paragraph(nb_sentences=random.randint(1, 4)) if random.random() > 0.3 else None,
            "review_date": fake.date_time_between(start_date="-60d", end_date="now"),
        })
    return pd.DataFrame(data)


def generate_inventory(product_ids: list, store_ids: list) -> pd.DataFrame:
    """Generate current inventory levels per product per store."""
    logger.info("Generating inventory records...")
    data = []
    inv_id = 1
    for product_id in product_ids:
        for store_id in store_ids:
            qty = random.randint(0, 200)
            data.append({
                "inventory_id": inv_id,
                "product_id": product_id,
                "store_id": store_id,
                "quantity_on_hand": qty,
                "reorder_level": random.randint(10, 50),
                "last_restock_date": fake.date_between(start_date="-30d", end_date="today"),
                "updated_at": fake.date_time_between(start_date="-7d", end_date="now"),
            })
            inv_id += 1
    return pd.DataFrame(data)


def generate_promotions(n: int = 15) -> pd.DataFrame:
    """Generate promotional campaigns."""
    logger.info(f"Generating {n} promotions...")
    data = []
    for i in range(1, n + 1):
        start = fake.date_between(start_date="-60d", end_date="+30d")
        data.append({
            "promotion_id": i,
            "promotion_name": fake.catch_phrase(),
            "discount_type": random.choice(["percentage", "flat", "bogo"]),
            "discount_value": random.choice([5, 10, 15, 20, 25, 50, 100, 500]),
            "start_date": start,
            "end_date": start + timedelta(days=random.randint(7, 30)),
            "min_order_value": random.choice([0, 499, 999, 1999, 4999]),
            "is_active": random.choices([True, False], weights=[70, 30])[0],
        })
    return pd.DataFrame(data)


# ============================================================
# Main Orchestrator
# ============================================================

@timer
def generate_all_data(n_customers: int = 500, n_orders: int = 2000) -> Dict[str, pd.DataFrame]:
    """
    Generate all 13 source tables with realistic data.

    Args:
        n_customers: Number of customer records.
        n_orders: Number of order records.

    Returns:
        Dictionary mapping table names to DataFrames.
    """
    correlation_id = generate_correlation_id()
    logger.info("Starting data generation", extra={"correlation_id": correlation_id})

    # Dimensions
    categories = generate_categories()
    suppliers = generate_suppliers()
    stores = generate_stores()
    customers = generate_customers(n_customers)
    products = generate_products()

    # Facts
    customer_ids = customers["customer_id"].dropna().unique().tolist()
    product_ids = products["product_id"].tolist()
    store_ids = stores["store_id"].tolist()

    orders = generate_orders(customer_ids, store_ids, n_orders)
    order_ids = orders["order_id"].tolist()

    order_items = generate_order_items(order_ids, product_ids)
    payments = generate_payments(order_ids)
    returns = generate_returns(order_ids)
    shipments = generate_shipments(order_ids[:int(len(order_ids) * 0.85)])  # 85% have shipments
    reviews = generate_reviews(order_ids, customer_ids, product_ids)
    inventory = generate_inventory(product_ids, store_ids)
    promotions = generate_promotions()

    # Update order totals from order_items
    order_totals = order_items.groupby("order_id").apply(
        lambda x: (x["unit_price"] * x["quantity"].clip(lower=0)).sum()
    ).reset_index(name="total_amount")
    orders = orders.drop(columns=["total_amount"]).merge(order_totals, on="order_id", how="left")
    orders["total_amount"] = orders["total_amount"].fillna(0).round(2)

    tables = {
        "categories": categories,
        "suppliers": suppliers,
        "stores": stores,
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "returns": returns,
        "shipments": shipments,
        "reviews": reviews,
        "inventory": inventory,
        "promotions": promotions,
    }

    for name, df in tables.items():
        logger.info(f"Generated {name}", extra={"table_name": name, "row_count": len(df)})

    return tables


@timer
def load_to_db(tables: Dict[str, pd.DataFrame] = None) -> None:
    """
    Load all generated tables into the source schema (idempotent).

    Args:
        tables: Pre-generated tables dict. If None, generates fresh data.
    """
    if tables is None:
        tables = generate_all_data()

    engine = get_engine()
    ensure_schemas()

    for table_name, df in tables.items():
        df.to_sql(
            table_name,
            engine,
            schema=schema_config.source,
            if_exists="replace",
            index=False,
            method="multi",
        )
        logger.info(
            f"Loaded {table_name} to {schema_config.source}",
            extra={"table_name": table_name, "row_count": len(df)},
        )

    logger.info(f"All {len(tables)} tables loaded to '{schema_config.source}' schema")


def export_to_csv(tables: Dict[str, pd.DataFrame], output_dir: str = "data/raw") -> None:
    """Export generated data to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    for name, df in tables.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        logger.info(f"Exported {name} to {path}", extra={"table_name": name, "row_count": len(df)})


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic retail data")
    parser.add_argument("--customers", type=int, default=500, help="Number of customers")
    parser.add_argument("--orders", type=int, default=2000, help="Number of orders")
    parser.add_argument("--output-csv", action="store_true", help="Also export to CSV files")
    args = parser.parse_args()

    tables = generate_all_data(n_customers=args.customers, n_orders=args.orders)
    load_to_db(tables)

    if args.output_csv:
        export_to_csv(tables)

    print("\n[OK] Data generation complete!")
    for name, df in tables.items():
        print(f"   {name:20s} → {len(df):>6,} rows")
