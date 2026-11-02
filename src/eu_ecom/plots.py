"""Charts from the exported tables in powerbi/. Run after eu_ecom.build.

    PYTHONPATH=src python -m eu_ecom.plots
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
POWERBI_DIR = ROOT / "powerbi"
RESULTS_DIR = ROOT / "results"
GERMANY, EU = "DE", "EU27_2020"


def load():
    fact = pd.read_csv(POWERBI_DIR / "fact_observation.csv")
    countries = pd.read_csv(POWERBI_DIR / "dim_country.csv")
    return fact, countries


def series_for(fact, key, geo):
    return fact[(fact.series_key == key) & (fact.geo == geo)].sort_values("year")


def plot_business_esales(fact, path):
    de, eu = series_for(fact, "ent_esales", GERMANY), series_for(fact, "ent_esales", EU)
    gap = de.set_index("year")["value"] - eu.set_index("year")["value"]
    behind = gap[gap < 0].index

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(de.year, de.value, marker="o", label="Germany")
    ax.plot(eu.year, eu.value, marker="o", label="EU-27 average")
    if len(behind):
        ax.axvspan(behind.min() - 0.5, behind.max() + 0.5, color="grey", alpha=0.12, label="Germany below EU average")
    ax.set_ylabel("% of enterprises (10+ employees)")
    ax.set_title("Enterprises with e-commerce sales: Germany lost its lead")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_consumers_bought_online(fact, path):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for geo, name in [(GERMANY, "Germany"), (EU, "EU-27 average")]:
        s = series_for(fact, "ind_bought_12m", geo)
        line, = ax.plot(s.year, s.value, marker="o", label=name)
        flagged = s[s.flag == "b"]
        ax.scatter(flagged.year, flagged.value, s=110, facecolors="none", edgecolors=line.get_color())
    # The indicator moves to a new Eurostat dataset in 2020, when the survey changed
    ax.axvline(2019.5, color="grey", linestyle="--", linewidth=1)
    ax.text(2019.6, ax.get_ylim()[0] + 3, "new survey\n(2020 onwards)", fontsize=8, color="grey")
    ax.scatter([], [], s=110, facecolors="none", edgecolors="grey", label="break in series (flag b)")
    ax.set_ylabel("% of individuals aged 16-74")
    ax.set_title("Individuals who bought online in the last 12 months")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_cross_border_shoppers(fact, countries, path, key="ind_buy_other_eu"):
    year = series_for(fact, key, GERMANY).year.max()
    latest = fact[(fact.series_key == key) & (fact.year == year)].merge(countries, on="geo")
    eu_value = latest.loc[latest.geo == EU, "value"].iloc[0]
    bars = latest[latest.is_eu27].sort_values("value")

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = ["C3" if geo == GERMANY else "C0" for geo in bars.geo]
    ax.barh(bars.country, bars.value, color=colors)
    ax.axvline(eu_value, color="grey", linestyle="--", linewidth=1, label=f"EU-27 average ({eu_value:.1f}%)")
    ax.set_xlabel("% of online shoppers (last 3 months)")
    ax.set_title(f"Online shoppers buying from sellers in other EU countries, {year}")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    RESULTS_DIR.mkdir(exist_ok=True)
    fact, countries = load()
    plot_business_esales(fact, RESULTS_DIR / "business_esales_de_vs_eu.png")
    plot_consumers_bought_online(fact, RESULTS_DIR / "consumers_bought_online_de_vs_eu.png")
    plot_cross_border_shoppers(fact, countries, RESULTS_DIR / "cross_border_shoppers_by_country.png")
    print("Saved three charts to results/")
