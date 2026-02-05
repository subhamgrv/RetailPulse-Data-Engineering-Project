import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys
import pandas as pd
from faker import Faker
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.utils.db import get_engine, write_dataframe

load_dotenv()
fake = Faker()
random.seed(42)

BASE = Path("data")
RAW = BASE / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def generate_customers(n=200):
    rows = []
    countries = ["Germany", "DE", "germany", "India", "IN", "France"]
    segments = ["bronze", "silver", "gold"]
    for i in range(1, n + 1):
        rows.append({
            "customer_id": f"C{i:04d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "country": random.choice(countries),
            "signup_date": fake.date_between(start_date="-2y", end_date="today"),
            "customer_segment": random.choice(segments),
        })
    df = pd.DataFrame(rows)
    df.to_csv(RAW / "customers.csv", index=False)
    return df


def generate_products(n=50):
    rows = []
    categories = ["Electronics", "Fashion", "Home", "Sports"]
    brands = ["Alpha", "Nova", "Prime", "Zen"]
    for i in range(1, n + 1):
        sale = round(random.uniform(10, 500), 2)
        cost = round(sale * random.uniform(0.4, 0.8), 2)
        rows.append({
            "product_id": f"P{i:04d}",
            "product_name": f"Product {i}",
            "category": random.choice(categories),
            "brand": random.choice(brands),
            "cost_price": cost,
            "sale_price": sale,
            "is_active": random.choice([True, True, True, False]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(RAW / "products.csv", index=False)
    return df




def generate_orders(customers, products, n=1000):
    rows = []
    shipping_rows = []
    now = datetime.now()
    channels = ["organic", "paid_search", "social", "email"]
    statuses = ["placed", "completed", "cancelled"]
    for i in range(1, n + 1):
        customer_id = customers.sample(1).iloc[0]["customer_id"]
        p = products.sample(1).iloc[0]
        ts = now - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        quantity = random.choice([1, 1, 1, 2, 3, -1])
        discount = round(random.choice([0, 0, 5, 10]), 2)
        order_id = f"O{i:05d}"
        payment_id = f"PAY{i:05d}"
        shipping_id = f"SHIP{i:05d}"
        rows.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "product_id": p["product_id"],
            "order_timestamp": ts,
            "quantity": quantity,
            "unit_price": float(p["sale_price"]),
            "discount_amount": discount,
            "payment_id": payment_id,
            "shipping_id": shipping_id,
            "channel": random.choice(channels),
            "order_status": random.choice(statuses),
        })
        shipped = ts.date() + timedelta(days=random.randint(0, 3))
        delivered = shipped + timedelta(days=random.randint(1, 7))
        shipping_rows.append({
            "shipping_id": shipping_id,
            "order_id": order_id,
            "shipped_date": shipped,
            "delivered_date": delivered,
            "carrier": random.choice(["DHL", "UPS", "DPD"]),
            "shipping_status": random.choice(["shipped", "delivered", "in_transit"]),
            "warehouse_location": random.choice(["Berlin", "Munich", "Hamburg"]),
        })
    orders = pd.DataFrame(rows)
    shipping = pd.DataFrame(shipping_rows)
    engine = get_engine()
    write_dataframe(orders, "orders", schema="source", if_exists="replace")
    shipping.to_csv(RAW / "shipping.csv", index=False)
    return orders, shipping


def generate_web_events(customers, products, n=2000):
    rows = []
    event_types = ["page_view", "add_to_cart", "purchase"]
    for i in range(1, n + 1):
        customer_id = customers.sample(1).iloc[0]["customer_id"]
        product_id = products.sample(1).iloc[0]["product_id"]
        rows.append({
            "event_id": f"E{i:06d}",
            "customer_id": customer_id,
            "session_id": fake.uuid4(),
            "event_type": random.choice(event_types),
            "product_id": product_id,
            "event_timestamp": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
            "page_url": f"/product/{product_id}",
            "device_type": random.choice(["mobile", "desktop", "tablet"]),
            "traffic_source": random.choice(["google", "facebook", "direct", "newsletter"]),
        })
    path = RAW / "web_events.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    customers = generate_customers()
    products = generate_products()
    generate_orders(customers, products)
    generate_web_events(customers, products)
    print("Synthetic data generated successfully.")