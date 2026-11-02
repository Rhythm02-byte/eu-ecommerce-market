# Power BI build guide

How to build the report from the files in `powerbi/`. Power BI Desktop is free, but it runs only on Windows.

## 1. Import the data

Get data → Text/CSV, and load these four files:

| File | Rows | What it is |
|---|---|---|
| `fact_observation.csv` | one per indicator, country and year | The values. Columns: `series_key`, `geo`, `year`, `value`, `flag`, `dataset` |
| `dim_country.csv` | 28 | The 27 EU countries plus the EU-27 average. Columns: `geo`, `country`, `is_eu27`, `is_aggregate` |
| `dim_indicator.csv` | 9 | One row per indicator. Columns: `series_key`, `label`, `side`, `unit`, `datasets` |
| `sources.csv` | 5 | Eurostat dataset codes, links and access dates, for the notes page |

Check the column types in Power Query:
- `year`: Whole number
- `value`: Decimal number
- `is_eu27`, `is_aggregate`: True/False
- Everything else: Text

## 2. Model

Model view → create two relationships, both one-to-many with single-direction filtering:

- `dim_country[geo]` (1) → `fact_observation[geo]` (*)
- `dim_indicator[series_key]` (1) → `fact_observation[series_key]` (*)

This is a star schema: the fact table in the middle, and a dimension table on each side.

## 3. Measures

Create these in a new table called `_Measures` (Home → Enter data, then add measures to it).

```DAX
Value =
IF (
    HASONEVALUE ( dim_indicator[series_key] ),
    AVERAGE ( fact_observation[value] )
)
```
Each indicator, country and year has exactly one value. `HASONEVALUE` stops the measure from mixing different indicators, which would give a meaningless number.

```DAX
Germany = CALCULATE ( [Value], dim_country[geo] = "DE" )

EU-27 average = CALCULATE ( [Value], dim_country[geo] = "EU27_2020" )

Gap (pp) = [Germany] - [EU-27 average]
```
The gap is in percentage points: Germany's percentage minus the EU's percentage.

```DAX
Germany rank (EU-27) =
VAR germany = [Germany]
RETURN
    IF (
        NOT ISBLANK ( germany ),
        COUNTROWS (
            FILTER (
                ALL ( dim_country ),
                dim_country[is_eu27] && CALCULATE ( [Value] ) > germany
            )
        ) + 1
    )
```
Counts how many EU countries have a higher value than Germany, plus one. Use it with a single year selected.

```DAX
Flag = IF ( HASONEVALUE ( fact_observation[year] ), MAX ( fact_observation[flag] ) )

Bar colour = IF ( SELECTEDVALUE ( dim_country[geo] ) = "DE", "#D62728", "#1F77B4" )
```

## 4. Report pages

**Page 1: Overview**
- Slicer: `fact_observation[year]`, single select, default to the latest year.
- Table: rows `dim_indicator[label]`. Values `Germany`, `EU-27 average`, `Gap (pp)`, `Germany rank (EU-27)`.
- Conditional formatting on `Gap (pp)`: red below 0, green above 0.
- Note: the consumer cross-border indicators end in 2023, so pick 2023 to see them.

**Page 2: Trends**
- Slicer: `dim_indicator[label]`, single select.
- Line chart: x-axis `fact_observation[year]`, y-axis `Value`, legend `dim_country[country]`.
- Filter on the visual: `dim_country[geo]` is DE or EU27_2020.
- Text box: "Breaks in series: values flagged b (mostly 2021) were collected with a new survey method. Changes across them are not like-for-like."

**Page 3: EU ranking**
- Slicers: `dim_indicator[label]` and `fact_observation[year]`, both single select.
- Bar chart: y-axis `dim_country[country]`, x-axis `Value`, sorted by value.
- Filter on the visual: `dim_country[is_eu27]` is True.
- Bars → Colour → fx → Format style "Field value" → `Bar colour`, so Germany is red.

**Page 4: Cross-border shopping**
- Filter on the page: `dim_indicator[series_key]` is `ind_buy_national`, `ind_buy_foreign`, `ind_buy_other_eu`, `ind_buy_non_eu`; year 2023.
- Clustered bar chart: y-axis `dim_indicator[label]`, values `Germany` and `EU-27 average`.
- Text box: "Shoppers can buy from several origins, so the shares don't add up to 100%."

**Page 5: Notes and sources**
- Table of `sources.csv`.
- Text box with the Eurostat citation and licence (see the README) and the flag meanings: b = break in series, e = estimated.

## 5. Publish to the repo

- Save the report as `powerbi/eu_ecommerce_market.pbix` and commit it.
- Export each page as an image (File → Export → PDF, or screenshots) into `docs/powerbi/`, and link them from the README, so people without Power BI can see the report.
