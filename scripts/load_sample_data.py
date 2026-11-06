import sys
from pathlib import Path

import pandas as pd


def main():
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

    from app.db import engine, init_db

    init_db()

    for table in ["customers", "products", "orders", "tickets"]:
        sample_file = project_root / "data" / "sample" / f"{table}.csv"
        df = pd.read_csv(sample_file)
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows into {table}")


if __name__ == "__main__":
    main()
