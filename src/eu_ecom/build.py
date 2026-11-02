"""Build the star schema from the raw Eurostat files, load it into PostgreSQL, and export it for Power BI.

Tables:
    dim_country       one row per country or aggregate (EU-27 average)
    dim_indicator     one row per indicator in series.py
    fact_observation  one row per indicator, country and year that has a value

Run from the project root:
    PYTHONPATH=src python -m eu_ecom.build            # downloads the data first
    PYTHONPATH=src python -m eu_ecom.build --offline  # reuses files already in data/raw
"""
import argparse
import json
import os
from pathlib import Path

import pandas as pd
import psycopg

from eu_ecom.eurostat import (
    DATASET_PAGE,
    download,
    download_codelist,
    read_codelist,
    read_wide_tsv,
    write_manifest,
)
from eu_ecom.series import DATASETS, EU27, EU27_AVERAGE, GEOS, SERIES

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
POWERBI_DIR = ROOT / "powerbi"
SCHEMA_SQL = ROOT / "sql" / "schema.sql"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/eu_ecommerce")


def select_observations(rows_by_dataset, series=SERIES, geos=GEOS):
    """Keep only the cells that belong to a series, for the chosen countries, with a value."""
    records = []
    for s in series:
        for row in rows_by_dataset[s.dataset]:
            if row["geo"] not in geos or row["value"] is None:
                continue
            if all(row.get(dim) == code for dim, code in s.filters.items()):
                records.append({
                    "series_key": s.key,
                    "geo": row["geo"],
                    "year": row["year"],
                    "value": row["value"],
                    "flag": row["flag"],
                    "dataset": s.dataset,
                })
    fact = pd.DataFrame(records, columns=["series_key", "geo", "year", "value", "flag", "dataset"])
    duplicates = fact.duplicated(subset=["series_key", "geo", "year"]).sum()
    if duplicates:
        raise ValueError(f"{duplicates} indicator/country/year combinations appear more than once")
    return fact.sort_values(["series_key", "geo", "year"]).reset_index(drop=True)


def build_dim_country(geo_labels, geos=GEOS):
    return pd.DataFrame([
        {
            "geo": geo,
            "country": "EU-27 average" if geo == EU27_AVERAGE else geo_labels.get(geo, geo),
            "is_eu27": geo in EU27,
            "is_aggregate": geo == EU27_AVERAGE,
        }
        for geo in geos
    ])


def build_dim_indicator(series=SERIES):
    rows = {}
    for s in series:
        entry = rows.setdefault(s.key, {"series_key": s.key, "label": s.label, "side": s.side,
                                        "unit": s.unit, "datasets": []})
        entry["datasets"].append(s.dataset)
    for entry in rows.values():
        entry["datasets"] = ", ".join(entry["datasets"])
    return pd.DataFrame(rows.values())


def build_sources(manifest):
    return pd.DataFrame([
        {"dataset": code, "url": info["url"], "accessed": info["accessed"]}
        for code, info in sorted(manifest.items())
    ])


def copy_frame(conn, df, table):
    columns = list(df.columns)
    with conn.cursor().copy(f"COPY {table} ({', '.join(columns)}) FROM STDIN") as copy:
        for values in df.itertuples(index=False, name=None):
            copy.write_row([None if pd.isna(v) else v for v in values])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="reuse the files already in data/raw")
    args = parser.parse_args()

    if not args.offline:
        for code in DATASETS:
            download(code, RAW_DIR)
        download_codelist("GEO", RAW_DIR)
        write_manifest(DATASETS, RAW_DIR)
    manifest = json.loads((RAW_DIR / "manifest.json").read_text())

    rows_by_dataset = {code: list(read_wide_tsv(RAW_DIR / f"{code}.tsv")) for code in DATASETS}
    fact = select_observations(rows_by_dataset)
    dim_country = build_dim_country(read_codelist(RAW_DIR / "codelist_GEO.tsv"))
    dim_indicator = build_dim_indicator()
    sources = build_sources(manifest)

    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(SCHEMA_SQL.read_text())
        # Clear all three together: the fact table references both dimensions, so they can't be emptied one by one
        conn.execute("TRUNCATE fact_observation, dim_indicator, dim_country")
        copy_frame(conn, dim_country, "dim_country")
        copy_frame(conn, dim_indicator, "dim_indicator")
        copy_frame(conn, fact, "fact_observation")
        conn.commit()

    # The same tables as CSVs, ready to import into Power BI
    POWERBI_DIR.mkdir(exist_ok=True)
    fact.to_csv(POWERBI_DIR / "fact_observation.csv", index=False)
    dim_country.to_csv(POWERBI_DIR / "dim_country.csv", index=False)
    dim_indicator.to_csv(POWERBI_DIR / "dim_indicator.csv", index=False)
    sources.to_csv(POWERBI_DIR / "sources.csv", index=False)

    print(f"fact_observation: {len(fact)} rows, {fact['series_key'].nunique()} indicators, "
          f"{fact['geo'].nunique()} countries, years {fact['year'].min()}-{fact['year'].max()}")
    print(f"flagged values: {fact['flag'].notna().sum()} ({fact['flag'].value_counts().to_dict()})")


if __name__ == "__main__":
    main()
