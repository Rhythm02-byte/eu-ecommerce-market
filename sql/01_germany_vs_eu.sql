-- Germany against the EU-27 average for every indicator and year.
-- gap_pp is Germany minus the EU average, in percentage points. Flags are shown so breaks in series stay visible.
SELECT
    i.series_key,
    i.label,
    f.year,
    MAX(f.value) FILTER (WHERE f.geo = 'DE')                                AS germany,
    MAX(f.value) FILTER (WHERE f.geo = 'EU27_2020')                         AS eu27,
    ROUND((MAX(f.value) FILTER (WHERE f.geo = 'DE')
         - MAX(f.value) FILTER (WHERE f.geo = 'EU27_2020'))::numeric, 2)    AS gap_pp,
    MAX(f.flag) FILTER (WHERE f.geo = 'DE')                                 AS germany_flag,
    MAX(f.flag) FILTER (WHERE f.geo = 'EU27_2020')                          AS eu27_flag
FROM fact_observation f
JOIN dim_indicator i USING (series_key)
WHERE f.geo IN ('DE', 'EU27_2020')
GROUP BY i.series_key, i.label, f.year
ORDER BY i.series_key, f.year;
