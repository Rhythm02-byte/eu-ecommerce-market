-- Star schema: one fact table and two dimension tables.

CREATE TABLE IF NOT EXISTS dim_country (
    geo          TEXT PRIMARY KEY,
    country      TEXT NOT NULL,
    is_eu27      BOOLEAN NOT NULL,
    is_aggregate BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_indicator (
    series_key TEXT PRIMARY KEY,
    label      TEXT NOT NULL,
    side       TEXT NOT NULL,   -- "business" (enterprises) or "consumer" (individuals)
    unit       TEXT NOT NULL,
    datasets   TEXT NOT NULL    -- Eurostat dataset code(s) the indicator comes from
);

CREATE TABLE IF NOT EXISTS fact_observation (
    series_key TEXT NOT NULL REFERENCES dim_indicator (series_key),
    geo        TEXT NOT NULL REFERENCES dim_country (geo),
    year       INTEGER NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    flag       TEXT,            -- Eurostat flag: b = break in series, e = estimated, u = low reliability
    dataset    TEXT NOT NULL,
    PRIMARY KEY (series_key, geo, year)
);
