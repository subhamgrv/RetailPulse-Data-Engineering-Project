import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pipelines.utils.db import write_dataframe

load_dotenv()


def run():
    url = os.getenv("PAYMENTS_API_URL", "http://localhost:8000/payments")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    df["source_file"] = "payments_api"
    write_dataframe(df, "payments", schema="raw", if_exists="append")
    print(f"Loaded {len(df)} payment rows")


if __name__ == "__main__":
    run()