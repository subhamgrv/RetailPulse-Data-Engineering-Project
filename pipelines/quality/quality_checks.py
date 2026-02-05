import pandas as pd
from pipelines.utils.db import get_engine


def run():
    engine = get_engine()
    checks = {}

    checks["duplicate_orders"] = pd.read_sql(
        "select count(*) as cnt from (select order_id, count(*) from staging.orders_clean group by 1 having count(*) > 1) t",
        engine,
    ).iloc[0]["cnt"]

    checks["invalid_ship_dates"] = pd.read_sql(
        "select count(*) as cnt from staging.shipping_clean where delivered_date < shipped_date",
        engine,
    ).iloc[0]["cnt"]

    checks["future_orders"] = pd.read_sql(
        "select count(*) as cnt from staging.orders_clean where order_timestamp > now()",
        engine,
    ).iloc[0]["cnt"]

    checks["negative_payments"] = pd.read_sql(
        "select count(*) as cnt from staging.payments_clean where amount_paid < 0",
        engine,
    ).iloc[0]["cnt"]

    print("QUALITY CHECK REPORT")
    for name, value in checks.items():
        print(f"{name}: {value}")

    return checks


if __name__ == "__main__":
    run()