from sqlalchemy import text
from pipelines.utils.db import get_engine


def run():
    engine = get_engine()
    with engine.begin() as conn:
        count = conn.execute(text("select count(*) from source.orders")).scalar()
    print(f"Orders already available in source.orders: {count}")


if __name__ == "__main__":
    run()