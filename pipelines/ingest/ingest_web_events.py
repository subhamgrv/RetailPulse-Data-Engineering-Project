import json
import pandas as pd
from pathlib import Path
from pipelines.utils.db import write_dataframe


def run():
    path = Path("data/raw/web_events.jsonl")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    df = pd.DataFrame(records)
    df["source_file"] = path.name
    write_dataframe(df, "web_events", schema="raw", if_exists="append")
    print(f"Loaded {len(df)} web event rows")


if __name__ == "__main__":
    run()