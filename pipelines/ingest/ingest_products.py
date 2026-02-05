import pandas as pd
from pathlib import Path
from pipelines.utils.db import write_dataframe


def run():
    path = Path("data/raw/products.csv")
    df = pd.read_csv(path)
    df["source_file"] = path.name
    write_dataframe(df, "products", schema="raw", if_exists="append")
    print(f"Loaded {len(df)} product rows")


if __name__ == "__main__":
    run()