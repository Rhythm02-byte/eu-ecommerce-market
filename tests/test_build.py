import pytest

from eu_ecom.build import build_dim_country, build_dim_indicator, select_observations
from eu_ecom.series import Series


def row(geo, year, value, flag=None, indic="I_BLT12"):
    return {"freq": "A", "ind_type": "IND_TOTAL", "indic_is": indic, "unit": "PC_IND",
            "geo": geo, "year": year, "value": value, "flag": flag}


FILTERS = {"freq": "A", "ind_type": "IND_TOTAL", "indic_is": "I_BLT12", "unit": "PC_IND"}
OLD = Series("bought", "Bought online", "consumer", "%", "old_ds", FILTERS)
NEW = Series("bought", "Bought online", "consumer", "%", "new_ds", FILTERS)


def test_select_keeps_matching_rows_and_drops_missing_values_and_other_countries():
    data = {"old_ds": [row("DE", 2019, 79.4), row("DE", 2018, None, "u"), row("US", 2019, 90.0),
                       row("DE", 2019, 5.0, indic="I_OTHER")]}

    fact = select_observations(data, series=[OLD], geos=["DE"])

    assert fact[["geo", "year", "value"]].values.tolist() == [["DE", 2019, 79.4]]


def test_two_datasets_join_into_one_series_and_keep_flags():
    data = {"old_ds": [row("DE", 2019, 79.4)], "new_ds": [row("DE", 2020, 82.6), row("DE", 2021, 76.0, "b")]}

    fact = select_observations(data, series=[OLD, NEW], geos=["DE"])

    assert fact["year"].tolist() == [2019, 2020, 2021]
    assert fact["dataset"].tolist() == ["old_ds", "new_ds", "new_ds"]
    assert fact["flag"].tolist()[2] == "b"


def test_overlapping_years_are_rejected():
    data = {"old_ds": [row("DE", 2020, 80.0)], "new_ds": [row("DE", 2020, 82.6)]}

    with pytest.raises(ValueError):
        select_observations(data, series=[OLD, NEW], geos=["DE"])


def test_dimensions_mark_the_eu_average_and_merge_split_series():
    countries = build_dim_country({"DE": "Germany"}, geos=["DE", "EU27_2020"])
    indicators = build_dim_indicator([OLD, NEW])

    assert countries.set_index("geo").loc["EU27_2020", "is_aggregate"]
    assert countries.set_index("geo").loc["DE", "country"] == "Germany"
    assert indicators["datasets"].tolist() == ["old_ds, new_ds"]
