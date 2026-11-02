-- Change from the first to the last year in which both Germany and the EU average have a value.
-- crosses_break is true when the period includes a Eurostat break in series (flag "b") or a switch between
-- source datasets. Those changes mix real movement with a change in survey method, so treat them with care.
WITH paired AS (
    SELECT
        series_key,
        year,
        MAX(value) FILTER (WHERE geo = 'DE')        AS germany,
        MAX(value) FILTER (WHERE geo = 'EU27_2020') AS eu27
    FROM fact_observation
    WHERE geo IN ('DE', 'EU27_2020')
    GROUP BY series_key, year
    HAVING COUNT(*) = 2
),
bounds AS (
    SELECT series_key, MIN(year) AS first_year, MAX(year) AS last_year
    FROM paired
    GROUP BY series_key
)
SELECT
    b.series_key,
    b.first_year,
    b.last_year,
    ROUND(first.germany::numeric, 2)                       AS germany_first,
    ROUND(last.germany::numeric, 2)                        AS germany_last,
    ROUND((last.germany - first.germany)::numeric, 2)      AS germany_change_pp,
    ROUND(first.eu27::numeric, 2)                          AS eu27_first,
    ROUND(last.eu27::numeric, 2)                           AS eu27_last,
    ROUND((last.eu27 - first.eu27)::numeric, 2)            AS eu27_change_pp,
    EXISTS (
        SELECT 1 FROM fact_observation f
        WHERE f.series_key = b.series_key
          AND f.geo IN ('DE', 'EU27_2020')
          AND f.year > b.first_year AND f.year <= b.last_year
          AND f.flag = 'b'
    )
    OR (
        SELECT COUNT(DISTINCT f.dataset) FROM fact_observation f
        WHERE f.series_key = b.series_key
          AND f.geo IN ('DE', 'EU27_2020')
          AND f.year BETWEEN b.first_year AND b.last_year
    ) > 1                                                  AS crosses_break
FROM bounds b
JOIN paired first ON first.series_key = b.series_key AND first.year = b.first_year
JOIN paired last  ON last.series_key  = b.series_key AND last.year  = b.last_year
ORDER BY b.series_key;
