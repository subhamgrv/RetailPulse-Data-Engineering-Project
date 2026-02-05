import random
from datetime import datetime, timedelta
from fastapi import FastAPI

app = FastAPI(title="RetailPulse Payments API")


@app.get("/payments")
def get_payments(limit: int = 1000):
    methods = ["card", "paypal", "bank_transfer"]
    statuses = ["paid", "failed", "refunded"]
    rows = []
    for i in range(1, limit + 1):
        rows.append({
            "payment_id": f"PAY{i:05d}",
            "order_id": f"O{i:05d}",
            "payment_timestamp": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            "payment_method": random.choice(methods),
            "payment_status": random.choice(statuses),
            "amount_paid": round(random.uniform(10, 500), 2),
            "currency": "EUR",
        })
    return rows