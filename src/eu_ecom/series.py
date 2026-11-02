"""The indicators used in the analysis, and exactly where each one comes from in Eurostat.

A series is picked out of a Eurostat dataset by fixing every dimension except country (geo) and year.
"""
from dataclasses import dataclass

# Eurostat's headline enterprise figures: enterprises with 10 or more persons employed,
# all sectors covered by the survey except the financial sector.
ENTERPRISES = {"freq": "A", "size_emp": "GE10", "nace_r2": "C10-S951_X_K"}
# All individuals aged 16 to 74 (the survey's population).
INDIVIDUALS = {"freq": "A", "ind_type": "IND_TOTAL"}

EU27 = [
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
    "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
]
EU27_AVERAGE = "EU27_2020"
GEOS = EU27 + [EU27_AVERAGE]


@dataclass
class Series:
    key: str
    label: str
    side: str
    unit: str
    dataset: str
    filters: dict


SERIES = [
    Series("ent_esales", "Enterprises with e-commerce sales", "business", "% of enterprises",
           "isoc_ec_esels", {**ENTERPRISES, "indic_is": "E_AESELL", "unit": "PC_ENT"}),
    Series("ent_eturnover", "E-commerce sales as a share of enterprise turnover", "business", "% of turnover",
           "isoc_ec_evals", {**ENTERPRISES, "indic_is": "E_ETURN", "unit": "PC_TURN"}),
    Series("ent_websales_other_eu", "Enterprises with web sales to other EU countries", "business",
           "% of enterprises", "isoc_ec_esels", {**ENTERPRISES, "indic_is": "E_AWSEU", "unit": "PC_ENT"}),
    Series("ent_websales_world", "Enterprises with web sales to the rest of the world", "business",
           "% of enterprises", "isoc_ec_esels", {**ENTERPRISES, "indic_is": "E_AWSWW", "unit": "PC_ENT"}),
    # Eurostat changed the household survey in 2020, so this indicator lives in two datasets.
    # Both parts share one key; the dataset column in the fact table shows which part a value came from.
    Series("ind_bought_12m", "Individuals who bought online in the last 12 months", "consumer",
           "% of individuals", "isoc_ec_ibuy", {**INDIVIDUALS, "indic_is": "I_BLT12", "unit": "PC_IND"}),
    Series("ind_bought_12m", "Individuals who bought online in the last 12 months", "consumer",
           "% of individuals", "isoc_ec_ib20", {**INDIVIDUALS, "indic_is": "I_BLT12", "unit": "PC_IND"}),
    Series("ind_buy_national", "Online shoppers buying from national sellers", "consumer",
           "% of online shoppers (last 3 months)", "isoc_ec_ibos",
           {**INDIVIDUALS, "indic_is": "I_BPG_DOM", "unit": "PC_IND_BUY3"}),
    # The seller-origin answers are multiple choice, so the shares don't add up to 100%.
    # "Any foreign seller" is the cleanest single measure of cross-border buying.
    Series("ind_buy_foreign", "Online shoppers buying from any foreign seller (EU or non-EU)", "consumer",
           "% of online shoppers (last 3 months)", "isoc_ec_ibos",
           {**INDIVIDUALS, "indic_is": "I_BPG_FOR", "unit": "PC_IND_BUY3"}),
    Series("ind_buy_other_eu", "Online shoppers buying from sellers in other EU countries", "consumer",
           "% of online shoppers (last 3 months)", "isoc_ec_ibos",
           {**INDIVIDUALS, "indic_is": "I_BPG_EU", "unit": "PC_IND_BUY3"}),
    Series("ind_buy_non_eu", "Online shoppers buying from sellers outside the EU", "consumer",
           "% of online shoppers (last 3 months)", "isoc_ec_ibos",
           {**INDIVIDUALS, "indic_is": "I_BPG_WRLD", "unit": "PC_IND_BUY3"}),
]

DATASETS = sorted({s.dataset for s in SERIES})
