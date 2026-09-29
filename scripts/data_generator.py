import sys
import os
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any

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

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

logger = get_logger(__name__)


# ============================================================
# Profiles
# ============================================================
PROFILES = {
    "development": {
        "customers": 10000,
        "products": 2000,
        "stores": 12,
        "orders": 100000,
    },
    "demo": {
        "customers": 100000,
        "products": 20000,
        "stores": 100,
        "orders": 1000000,
    },
    "stress": {
        "customers": 500000,
        "products": 50000,
        "stores": 200,
        "orders": 5000000,
    }
}

# ============================================================
# Dimension Generators
# ============================================================

def generate_categories() -> pd.DataFrame:
    categories = [
        {"category_id": 1, "category_name": "Electronics", "parent_category_id": None},
        {"category_id": 2, "category_name": "Clothing", "parent_category_id": None},
        {"category_id": 3, "category_name": "Home & Kitchen", "parent_category_id": None},
        {"category_id": 4, "category_name": "Books", "parent_category_id": None},
        {"category_id": 5, "category_name": "Smartphones", "parent_category_id": 1},
        {"category_id": 6, "category_name": "Laptops", "parent_category_id": 1},
        {"category_id": 7, "category_name": "Men's Fashion", "parent_category_id": 2},
        {"category_id": 8, "category_name": "Women's Fashion", "parent_category_id": 2},
        {"category_id": 9, "category_name": "Furniture", "parent_category_id": 3},
        {"category_id": 10, "category_name": "Toys", "parent_category_id": None},
    ]
    return pd.DataFrame(categories)


def generate_suppliers(n: int = 50) -> pd.DataFrame:
    data = []
    cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
    for i in range(1, n + 1):
        data.append({
            "supplier_id": i,
            "supplier_name": fake.company(),
            "contact_name": fake.name(),
            "contact_email": fake.company_email(),
            "contact_phone": fake.phone_number(),
            "city": random.choice(cities),
            "country": "India",
            "created_at": fake.date_between(start_date="-5y", end_date="-1y"),
        })
    return pd.DataFrame(data)


def generate_stores(n: int) -> pd.DataFrame:
    regions = {
        "Mumbai": "West", "Pune": "West", "Ahmedabad": "West", "Surat": "West",
        "Delhi": "North", "Jaipur": "North", "Lucknow": "North", "Chandigarh": "North",
        "Bangalore": "South", "Chennai": "South", "Hyderabad": "South", "Kochi": "South",
        "Kolkata": "East", "Bhubaneswar": "East", "Guwahati": "East", "Patna": "East",
    }
    cities = list(regions.keys())
    data = []
    for i in range(1, n + 1):
        city = cities[i % len(cities)]
        data.append({
            "store_id": i,
            "store_name": f"Bombay Bazaar - {city} {i}",
            "city": city,
            "region": regions[city],
            "store_type": random.choices(["Flagship", "Standard", "Express"], weights=[10, 60, 30])[0],
            "opening_date": fake.date_between(start_date="-10y", end_date="-1y"),
            "is_active": random.choices([True, False], weights=[95, 5])[0],
        })
    return pd.DataFrame(data)


def generate_customers(n: int) -> pd.DataFrame:
    logger.info(f"Generating {n} customers...")
    
    segments = np.random.choice(
        ["Frequent", "Regular", "Occasional", "Inactive"], 
        size=n, 
        p=[0.1, 0.3, 0.4, 0.2]
    )
    
    tier_map = {"Frequent": [0.0, 0.1, 0.4, 0.5], "Regular": [0.1, 0.5, 0.3, 0.1], 
                "Occasional": [0.6, 0.3, 0.1, 0.0], "Inactive": [0.9, 0.1, 0.0, 0.0]}
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad",
              "Kolkata", "Jaipur", None, "mumbai", " DEL ", "  Pune  "]
    
    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "segment": segments,
        "city": np.random.choice(cities, size=n)
    })
    
    # Pre-generate loyalty tiers based on segment to speed up (vectorized alternative to apply)
    df["loyalty_tier"] = "Bronze" # Default
    for seg in tier_map:
        mask = df["segment"] == seg
        count = mask.sum()
        if count > 0:
            df.loc[mask, "loyalty_tier"] = np.random.choice(tiers, size=count, p=tier_map[seg])
            
    pool_size = min(10000, n)
    faker_pool = [{"first_name": fake.first_name(), "last_name": fake.last_name()} for _ in range(pool_size)]
    pool_df = pd.DataFrame(faker_pool)
    
    sampled_names = pool_df.sample(n, replace=True).reset_index(drop=True)
    df["first_name"] = sampled_names["first_name"]
    df["last_name"] = sampled_names["last_name"]
    
    df["email"] = df["first_name"].str.lower() + "." + df["last_name"].str.lower() + df["customer_id"].astype(str) + "@example.com"
    
    # Phone numbers
    has_phone = np.random.random(n) < 0.9
    phone_pool = ["+91" + "".join(np.random.choice(list("0123456789"), 10)) for _ in range(min(n, 5000))]
    phones = np.full(n, None, dtype=object)
    phones[has_phone] = np.random.choice(phone_pool, size=has_phone.sum())
    df["phone"] = phones
    
    today = datetime.now()
    start_date = today - timedelta(days=3*365)
    random_days = np.random.randint(0, 3*365, size=n)
    df["signup_date"] = [start_date + timedelta(days=int(d)) for d in random_days]
    
    age_days = np.random.randint(18*365, 70*365, size=n)
    df["date_of_birth"] = [today - timedelta(days=int(d)) for d in age_days]
    
    df = df.drop(columns=["segment"])
    
    duplicates = df.sample(int(n * 0.05), random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df


def generate_products(n: int) -> pd.DataFrame:
    logger.info(f"Generating {n} products...")
    cat_ids = np.random.randint(1, 11, size=n)
    supp_ids = np.random.randint(1, 51, size=n)
    
    prices = np.random.lognormal(mean=6.5, sigma=1.2, size=n)
    prices = np.clip(prices, 50, 200000).round(2)
    costs = (prices * np.random.uniform(0.4, 0.8, size=n)).round(2)
    
    pool_size = min(5000, n)
    product_names_pool = [fake.catch_phrase() for _ in range(pool_size)]
    
    df = pd.DataFrame({
        "product_id": np.arange(1, n + 1),
        "product_name": [product_names_pool[i % pool_size] + f" {i}" for i in range(n)],
        "category_id": cat_ids,
        "supplier_id": supp_ids,
        "unit_price": prices,
        "cost_price": costs,
        "weight_kg": np.round(np.random.uniform(0.1, 20.0, size=n), 2),
        "is_active": np.random.choice([True, False], size=n, p=[0.9, 0.1])
    })
    
    today = datetime.now()
    random_days = np.random.randint(30, 3*365, size=n)
    df["created_at"] = [today - timedelta(days=int(d)) for d in random_days]
    
    return df


def generate_promotions(n: int = 50) -> pd.DataFrame:
    logger.info(f"Generating {n} promotions...")
    data = []
    for i in range(1, n + 1):
        start = fake.date_between(start_date="-3y", end_date="+30d")
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
# Fact / Transactional Generators
# ============================================================

def generate_orders_and_items(customers: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame, n_orders: int):
    logger.info(f"Generating {n_orders} orders and items (This may take a moment)...")
    
    today = datetime.now()
    start_date = today - timedelta(days=3*365)
    days_range = 3 * 365
    raw_days = np.random.randint(0, days_range, size=n_orders)
    order_dates = np.array([start_date + timedelta(days=int(d)) for d in raw_days])
    
    cust_ids = customers["customer_id"].values
    # Approximate Zipf with a geometric-like sampling for speed and stability
    # Simple Pareto-like approach
    ranks = np.random.pareto(1.5, size=n_orders)
    ranks = (ranks / ranks.max() * len(cust_ids)).astype(int)
    ranks = np.clip(ranks, 0, len(cust_ids) - 1)
    sampled_customers = cust_ids[ranks]
    
    store_ids = stores["store_id"].values
    sampled_stores = np.random.choice(store_ids, size=n_orders)
    statuses = np.random.choice(["completed", "pending", "shipped", "cancelled", "returned"], size=n_orders, p=[0.75, 0.05, 0.10, 0.05, 0.05])
    
    orders = pd.DataFrame({
        "order_id": np.arange(10001, 10001 + n_orders),
        "customer_id": sampled_customers,
        "store_id": sampled_stores,
        "order_date": order_dates,
        "status": statuses,
        "shipping_cost": np.round(np.random.uniform(0, 150, size=n_orders), 2),
        "discount_amount": 0.0
    })
    
    future_idx = np.random.choice(orders.index, size=int(n_orders * 0.02), replace=False)
    orders.loc[future_idx, "order_date"] = orders.loc[future_idx, "order_date"] + pd.to_timedelta(np.random.randint(30, 90, size=len(future_idx)), unit='d')
    
    items_per_order = np.random.poisson(lam=1.5, size=n_orders) + 1
    total_items = items_per_order.sum()
    logger.info(f"Generating {total_items} order items...")
    
    order_ids_repeated = np.repeat(orders["order_id"].values, items_per_order)
    prod_ids = products["product_id"].values
    prod_prices = products["unit_price"].values
    
    ranks_prod = np.random.pareto(1.2, size=total_items)
    ranks_prod = (ranks_prod / ranks_prod.max() * len(prod_ids)).astype(int)
    ranks_prod = np.clip(ranks_prod, 0, len(prod_ids) - 1)
    
    sampled_products = prod_ids[ranks_prod]
    sampled_prices = prod_prices[ranks_prod]
    quantities = np.random.choice([1, 2, 3, 4, 5, -1], size=total_items, p=[0.7, 0.15, 0.08, 0.03, 0.02, 0.02])
    item_discounts = np.random.choice([0, 5, 10, 15, 20], size=total_items, p=[0.7, 0.1, 0.1, 0.05, 0.05])
    
    order_items = pd.DataFrame({
        "order_item_id": np.arange(1, total_items + 1),
        "order_id": order_ids_repeated,
        "product_id": sampled_products,
        "quantity": quantities,
        "unit_price": sampled_prices,
        "discount_pct": item_discounts
    })
    
    valid_qty = np.maximum(order_items["quantity"].values, 0)
    line_totals = order_items["unit_price"].values * valid_qty * (1 - order_items["discount_pct"].values / 100.0)
    order_items["_line_total"] = line_totals
    
    order_totals = order_items.groupby("order_id")["_line_total"].sum().reset_index()
    order_totals.rename(columns={"_line_total": "total_amount"}, inplace=True)
    
    orders = orders.merge(order_totals, on="order_id", how="left")
    orders["total_amount"] = orders["total_amount"].fillna(0).round(2)
    order_items = order_items.drop(columns=["_line_total"])
    
    has_discount = np.random.random(n_orders) < 0.2
    orders.loc[has_discount, "discount_amount"] = (orders.loc[has_discount, "total_amount"] * np.random.uniform(0.05, 0.2, size=has_discount.sum())).round(2)
    
    return orders, order_items


def generate_payments(orders: pd.DataFrame) -> pd.DataFrame:
    n = len(orders)
    logger.info(f"Generating payments for {n} orders...")
    methods = ["credit_card", "debit_card", "upi", "net_banking", "cash_on_delivery", "wallet"]
    df = pd.DataFrame({
        "payment_id": np.arange(1, n + 1),
        "order_id": orders["order_id"].values,
        "payment_method": np.random.choice(methods, size=n, p=[0.25, 0.20, 0.30, 0.10, 0.10, 0.05]),
        "payment_status": np.random.choice(["success", "failed", "pending", "refunded"], size=n, p=[0.88, 0.05, 0.02, 0.05]),
        "payment_date": orders["order_date"].values + pd.to_timedelta(np.random.randint(0, 3, size=n), unit='h'),
        "amount": orders["total_amount"].values,
        "currency": "INR"
    })
    return df


def generate_returns(orders: pd.DataFrame) -> pd.DataFrame:
    returned_orders = orders[orders["status"].isin(["returned", "cancelled"])].copy()
    if returned_orders.empty:
        returned_orders = orders.sample(frac=0.05)
    
    n = len(returned_orders)
    logger.info(f"Generating {n} returns...")
    reasons = ["defective", "wrong_item", "size_issue", "changed_mind", "damaged_in_transit", "late_delivery", "quality_issue"]
    
    df = pd.DataFrame({
        "return_id": np.arange(1, n + 1),
        "order_id": returned_orders["order_id"].values,
        "return_date": returned_orders["order_date"].values + pd.to_timedelta(np.random.randint(2, 15, size=n), unit='d'),
        "reason": np.random.choice(reasons, size=n),
        "refund_amount": returned_orders["total_amount"].values,
        "refund_status": np.random.choice(["processed", "pending", "rejected"], size=n, p=[0.8, 0.15, 0.05])
    })
    return df


def generate_shipments(orders: pd.DataFrame) -> pd.DataFrame:
    ship_orders = orders[orders["status"].isin(["shipped", "completed"])].copy()
    n = len(ship_orders)
    logger.info(f"Generating {n} shipments...")
    carriers = ["BlueDart", "Delhivery", "DTDC", "FedEx India", "Ecom Express"]
    delivery_days = np.random.randint(1, 14, size=n)
    delays = np.random.choice([0, 1, 2, 5, 10], size=n, p=[0.8, 0.1, 0.05, 0.03, 0.02])
    
    df = pd.DataFrame({
        "shipment_id": np.arange(1, n + 1),
        "order_id": ship_orders["order_id"].values,
        "carrier": np.random.choice(carriers, size=n),
        "tracking_number": ["TRK" + str(np.random.randint(10000000, 99999999)) for _ in range(n)],
        "shipped_date": ship_orders["order_date"].values + pd.to_timedelta(np.random.randint(0, 3, size=n), unit='d'),
    })
    
    df["estimated_delivery"] = df["shipped_date"] + pd.to_timedelta(delivery_days, unit='d')
    df["actual_delivery"] = df["estimated_delivery"] + pd.to_timedelta(delays, unit='d')
    df["status"] = np.where(delays > 0, "delayed", "delivered")
    
    in_transit_mask = np.random.random(n) < 0.05
    df.loc[in_transit_mask, "status"] = "in_transit"
    df.loc[in_transit_mask, "actual_delivery"] = pd.NaT
    return df


def generate_reviews(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    reviewed_items = order_items.sample(frac=0.1)
    n = len(reviewed_items)
    logger.info(f"Generating {n} reviews...")
    
    df = pd.DataFrame({
        "review_id": np.arange(1, n + 1),
        "order_id": reviewed_items["order_id"].values,
        "product_id": reviewed_items["product_id"].values,
        "rating": np.random.choice([1, 2, 3, 4, 5], size=n, p=[0.05, 0.05, 0.10, 0.30, 0.50]),
    })
    
    df = df.merge(orders[["order_id", "customer_id", "order_date"]], on="order_id", how="inner")
    df["review_date"] = df["order_date"] + pd.to_timedelta(np.random.randint(5, 30, size=len(df)), unit='d')
    df = df.drop(columns=["order_date"])
    
    pool_size = min(1000, n)
    text_pool = [fake.paragraph(nb_sentences=2) for _ in range(pool_size)]
    has_text = np.random.random(len(df)) < 0.3
    texts = np.full(len(df), None, dtype=object)
    texts[has_text] = [text_pool[i % pool_size] for i in range(has_text.sum())]
    df["review_text"] = texts
    
    return df


def generate_inventory(products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generating inventory records...")
    prod_ids = products["product_id"].values
    store_ids = stores["store_id"].values
    
    df = pd.MultiIndex.from_product([prod_ids, store_ids], names=["product_id", "store_id"]).to_frame(index=False)
    n = len(df)
    df["inventory_id"] = np.arange(1, n + 1)
    
    inv_types = np.random.choice(["Healthy", "Low", "Stockout", "Overstock"], size=n, p=[0.6, 0.2, 0.1, 0.1])
    qty = np.zeros(n, dtype=int)
    qty[inv_types == "Healthy"] = np.random.randint(50, 150, size=(inv_types == "Healthy").sum())
    qty[inv_types == "Low"] = np.random.randint(1, 20, size=(inv_types == "Low").sum())
    qty[inv_types == "Stockout"] = 0
    qty[inv_types == "Overstock"] = np.random.randint(200, 500, size=(inv_types == "Overstock").sum())
    
    df["quantity_on_hand"] = qty
    df["reorder_level"] = np.random.randint(10, 30, size=n)
    
    today = datetime.now()
    random_days = np.random.randint(0, 30, size=n)
    df["last_restock_date"] = [today - timedelta(days=int(d)) for d in random_days]
    random_hours = np.random.randint(0, 24, size=n)
    df["updated_at"] = [today - timedelta(hours=int(h)) for h in random_hours]
    
    df = df[["inventory_id", "product_id", "store_id", "quantity_on_hand", "reorder_level", "last_restock_date", "updated_at"]]
    return df


# ============================================================
# Main Orchestrator
# ============================================================

@timer
def generate_all_data(profile: str = "development", custom_overrides: Dict[str, int] = None) -> Dict[str, pd.DataFrame]:
    correlation_id = generate_correlation_id()
    logger.info(f"Starting data generation (Profile: {profile})", extra={"correlation_id": correlation_id})
    
    prof_settings = PROFILES.get(profile, PROFILES["development"]).copy()
    if custom_overrides:
        prof_settings.update({k: v for k, v in custom_overrides.items() if v is not None})
    
    n_customers = prof_settings["customers"]
    n_products = prof_settings["products"]
    n_stores = prof_settings["stores"]
    n_orders = prof_settings["orders"]

    categories = generate_categories()
    suppliers = generate_suppliers(n=50)
    stores = generate_stores(n=n_stores)
    customers = generate_customers(n=n_customers)
    products = generate_products(n=n_products)
    promotions = generate_promotions(n=50)

    # Use a dynamic seed for fact generation so metrics change every run
    import time
    dynamic_seed = int(time.time())
    random.seed(dynamic_seed)
    np.random.seed(dynamic_seed)
    Faker.seed(dynamic_seed)

    orders, order_items = generate_orders_and_items(customers, products, stores, n_orders)
    
    payments = generate_payments(orders)
    returns = generate_returns(orders)
    shipments = generate_shipments(orders)
    reviews = generate_reviews(orders, order_items)
    inventory = generate_inventory(products, stores)

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
    if tables is None:
        raise ValueError("No tables provided to load_to_db")

    engine = get_engine()
    ensure_schemas()

    for table_name, df in tables.items():
        for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
            df[col] = df[col].dt.tz_localize(None)
            
        df.to_sql(
            table_name,
            engine,
            schema=schema_config.source,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=10000
        )
        logger.info(
            f"Loaded {table_name} to {schema_config.source}",
            extra={"table_name": table_name, "row_count": len(df)},
        )

    logger.info(f"All {len(tables)} tables loaded to '{schema_config.source}' schema")


def export_to_csv(tables: Dict[str, pd.DataFrame], output_dir: str = "data/raw") -> None:
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
    parser.add_argument("--profile", type=str, choices=list(PROFILES.keys()), default="development", 
                        help="Configuration profile for dataset size")
    parser.add_argument("--customers", type=int, help="Override number of customers")
    parser.add_argument("--products", type=int, help="Override number of products")
    parser.add_argument("--stores", type=int, help="Override number of stores")
    parser.add_argument("--orders", type=int, help="Override number of orders")
    parser.add_argument("--output-csv", action="store_true", help="Also export to CSV files")
    
    args = parser.parse_args()
    
    overrides = {
        "customers": args.customers,
        "products": args.products,
        "stores": args.stores,
        "orders": args.orders
    }

    tables = generate_all_data(profile=args.profile, custom_overrides=overrides)
    load_to_db(tables)

    if args.output_csv:
        export_to_csv(tables)

    print(f"\n[OK] Data generation complete! (Profile: {args.profile})")
    for name, df in tables.items():
        print(f"   {name:20s} → {len(df):>10,} rows")
