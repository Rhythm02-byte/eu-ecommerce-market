-- Germany's position among the 27 EU countries in the latest year Germany has a value for each indicator.
-- Rank 1 is the highest value. For "buying from national sellers", a high value is not better or worse; it means less cross-border buying.
WITH latest AS (
    SELECT series_key, MAX(year) AS year
    FROM fact_observation
    WHERE geo = 'DE'
    GROUP BY series_key
),
ranked AS (
    SELECT
        f.series_key,
        f.year,
        f.geo,
        c.country,
        f.value,
        RANK() OVER (PARTITION BY f.series_key ORDER BY f.value DESC) AS rank,
        COUNT(*) OVER (PARTITION BY f.series_key)                      AS countries
    FROM fact_observation f
    JOIN latest l USING (series_key, year)
    JOIN dim_country c USING (geo)
    WHERE c.is_eu27
)
SELECT
    r.series_key,
    r.year,
    ROUND(r.value::numeric, 2)    AS germany,
    r.rank                        AS germany_rank,
    r.countries                   AS countries_with_data,
    top.country                   AS top_country,
    ROUND(top.value::numeric, 2)  AS top_value
FROM ranked r
JOIN ranked top ON top.series_key = r.series_key AND top.rank = 1
WHERE r.geo = 'DE'
ORDER BY r.series_key;
