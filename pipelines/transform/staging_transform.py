import pandas as pd
from sqlalchemy import text
from pipelines.utils.db import get_engine, write_dataframe


def normalize_country(country: str) -> str:
    if pd.isna(country):
        return "UNKNOWN"
    country = str(country).strip().lower()
    mapping = {
        "de": "GERMANY",
        "germany": "GERMANY",
        "in": "INDIA",
        "india": "INDIA",
        "france": "FRANCE",
    }
    return mapping.get(country, country.upper())


def run():
    engine = get_engine()

    orders = pd.read_sql("select * from source.orders", engine)
    customers = pd.read_sql("select * from raw.customers", engine)
    products = pd.read_sql("select * from raw.products", engine)
    shipping = pd.read_sql("select * from raw.shipping", engine)
    web_events = pd.read_sql("select * from raw.web_events", engine)
    payments = pd.read_sql("select * from raw.payments", engine)

    orders = orders.drop_duplicates(subset=["order_id"])
    orders["order_timestamp"] = pd.to_datetime(orders["order_timestamp"], errors="coerce", utc=True)
    orders = orders[orders["quantity"] > 0]
    orders["order_date"] = orders["order_timestamp"].dt.date

    customers = customers.drop_duplicates(subset=["customer_id"], keep="last")
    customers["country"] = customers["country"].apply(normalize_country)

    products = products.drop_duplicates(subset=["product_id"], keep="last")
    shipping = shipping.drop_duplicates(subset=["shipping_id"], keep="last")
    payments = payments.drop_duplicates(subset=["payment_id"], keep="last")
    payments = payments[payments["amount_paid"] >= 0]
    web_events = web_events.drop_duplicates(subset=["event_id"], keep="last")

    with engine.begin() as conn:
        conn.execute(text("truncate table staging.orders_clean"))
        conn.execute(text("truncate table staging.customers_clean"))
        conn.execute(text("truncate table staging.products_clean"))
        conn.execute(text("truncate table staging.shipping_clean"))
        conn.execute(text("truncate table staging.web_events_clean"))
        conn.execute(text("truncate table staging.payments_clean"))

    write_dataframe(orders, "orders_clean", schema="staging", if_exists="append")
    write_dataframe(customers, "customers_clean", schema="staging", if_exists="append")
    write_dataframe(products, "products_clean", schema="staging", if_exists="append")
    write_dataframe(shipping, "shipping_clean", schema="staging", if_exists="append")
    write_dataframe(web_events, "web_events_clean", schema="staging", if_exists="append")
    write_dataframe(payments, "payments_clean", schema="staging", if_exists="append")

    print("Staging transformations completed.")


if __name__ == "__main__":
    run()