import os
from typing import Literal

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine

load_dotenv(override=True)


def get_engine():
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "retailpulse")
    user = os.getenv("POSTGRES_USER", "retailpulse")
    pwd = os.getenv("POSTGRES_PASSWORD", "retailpulse")
    url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url)


def write_dataframe(
    df,
    table_name: str,
    schema: str,
    if_exists: Literal["append", "replace"] = "append",
):
    """
    Lightweight helper that writes a pandas DataFrame using SQLAlchemy Core.
    Avoids pandas.to_sql's dependency on pandas-sqlalchemy integration.
    """
    engine = get_engine()
    metadata = MetaData()
    table = Table(table_name, metadata, schema=schema, autoload_with=engine)
    records = df.to_dict(orient="records")

    if not records:
        return

    with engine.begin() as conn:
        if if_exists == "replace":
            conn.execute(table.delete())
        conn.execute(table.insert(), records)