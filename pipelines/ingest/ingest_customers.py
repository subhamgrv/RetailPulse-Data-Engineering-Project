import pandas as pd
from pathlib import Path
from pipelines.utils.db import write_dataframe


def run():
    path = Path("data/raw/customers.csv")
    df = pd.read_csv(path)
    df["source_file"] = path.name
    write_dataframe(df, "customers", schema="raw", if_exists="append")
    print(f"Loaded {len(df)} customer rows")


if __name__ == "__main__":
    run()