-- For enterprises with e-commerce sales: Germany's largest lead over the EU average, and the first year it fell behind.
WITH gap AS (
    SELECT
        year,
        MAX(value) FILTER (WHERE geo = 'DE') - MAX(value) FILTER (WHERE geo = 'EU27_2020') AS gap_pp
    FROM fact_observation
    WHERE series_key = 'ent_esales' AND geo IN ('DE', 'EU27_2020')
    GROUP BY year
    HAVING COUNT(*) = 2
)
SELECT
    (SELECT year FROM gap ORDER BY gap_pp DESC LIMIT 1)                     AS largest_lead_year,
    (SELECT ROUND(MAX(gap_pp)::numeric, 2) FROM gap)                        AS largest_lead_pp,
    (SELECT MIN(year) FROM gap WHERE gap_pp < 0)                            AS first_year_behind,
    (SELECT COUNT(*) FROM gap WHERE gap_pp < 0)                             AS years_behind,
    (SELECT ROUND(gap_pp::numeric, 2) FROM gap ORDER BY year DESC LIMIT 1)  AS latest_gap_pp;
