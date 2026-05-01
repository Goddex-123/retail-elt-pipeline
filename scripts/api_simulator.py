"""
Retail ELT Platform — API Source Simulator
===========================================
Simulates a REST API data source for promotions and inventory updates.
Returns JSON payloads that the pipeline can consume as if calling
an external vendor API.
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.logger import get_logger

logger = get_logger(__name__)

try:
    from faker import Faker
    fake = Faker("en_IN")
except ImportError:
    fake = None


def fetch_inventory_updates(n: int = 25) -> List[Dict]:
    """
    Simulate fetching inventory adjustment events from a warehouse API.

    Returns:
        List of inventory update event dicts.
    """
    events = []
    for _ in range(n):
        events.append({
            "event_type": random.choice(["restock", "adjustment", "damage", "transfer"]),
            "product_id": random.randint(1, 50),
            "store_id": random.randint(1, 12),
            "quantity_change": random.randint(-20, 100),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "warehouse_api",
            "reference_id": f"INV-{random.randint(100000, 999999)}",
        })

    logger.info(f"Fetched {len(events)} inventory updates from API", extra={"pipeline_stage": "api_ingest"})
    return events


def fetch_promotion_updates() -> List[Dict]:
    """
    Simulate fetching active promotions from a marketing platform API.

    Returns:
        List of promotion event dicts.
    """
    promotions = []
    for _ in range(random.randint(3, 8)):
        start = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7))
        promotions.append({
            "promotion_code": f"PROMO-{random.randint(1000, 9999)}",
            "description": fake.catch_phrase() if fake else f"Sale Event {random.randint(1, 100)}",
            "discount_type": random.choice(["percentage", "flat"]),
            "discount_value": random.choice([5, 10, 15, 20, 25]),
            "valid_from": start.isoformat(),
            "valid_until": (start + timedelta(days=random.randint(7, 30))).isoformat(),
            "min_order_value": random.choice([0, 499, 999, 1999]),
            "source": "marketing_api",
        })

    logger.info(f"Fetched {len(promotions)} promotions from API", extra={"pipeline_stage": "api_ingest"})
    return promotions


def fetch_late_arriving_orders(n: int = 10) -> List[Dict]:
    """
    Simulate late-arriving order records from a partner system.
    These orders have historical dates but arrive in the current batch.

    Returns:
        List of late-arriving order dicts.
    """
    orders = []
    for i in range(n):
        # Orders dated 5-30 days ago but arriving now
        order_date = datetime.now(timezone.utc) - timedelta(days=random.randint(5, 30))
        orders.append({
            "order_id": 90000 + i,
            "customer_id": random.randint(1, 500),
            "store_id": random.randint(1, 12),
            "order_date": order_date.isoformat(),
            "status": "completed",
            "total_amount": round(random.uniform(500, 25000), 2),
            "source": "partner_api",
            "is_late_arriving": True,
        })

    logger.info(
        f"Fetched {len(orders)} late-arriving orders",
        extra={"pipeline_stage": "api_ingest"},
    )
    return orders


if __name__ == "__main__":
    print("=== Inventory Updates ===")
    print(json.dumps(fetch_inventory_updates(3), indent=2, default=str))

    print("\n=== Promotion Updates ===")
    print(json.dumps(fetch_promotion_updates(), indent=2, default=str))

    print("\n=== Late-Arriving Orders ===")
    print(json.dumps(fetch_late_arriving_orders(3), indent=2, default=str))
