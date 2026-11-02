"""Run each KPI query in sql/ and save the result as a CSV in results/.

    PYTHONPATH=src python -m eu_ecom.kpis
"""
import os
from pathlib import Path

import pandas as pd
import psycopg

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"
RESULTS_DIR = ROOT / "results"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/eu_ecommerce")


def run_query(url, sql_text):
    with psycopg.connect(url) as conn:
        cur = conn.execute(sql_text)
        return pd.DataFrame(cur.fetchall(), columns=[c.name for c in cur.description])


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    for sql_file in sorted(SQL_DIR.glob("[0-9]*.sql")):
        result = run_query(DATABASE_URL, sql_file.read_text())
        result.to_csv(RESULTS_DIR / f"{sql_file.stem}.csv", index=False)
        print(f"{sql_file.name}: {len(result)} rows")


if __name__ == "__main__":
    main()
