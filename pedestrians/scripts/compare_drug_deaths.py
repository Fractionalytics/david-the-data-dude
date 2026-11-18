"""EU drug-induced deaths by toxicology (with / without opioids), per million,
from EUDA Statistical Bulletin tables DRD-17 to DRD-20 (downloaded by David,
2026-11-10), against Eurostat population.

    python scripts/compare_drug_deaths.py
      reads  data/raw/euda/DRD-17.xlsx  cases with known toxicology
             data/raw/euda/DRD-18.xlsx  with opioids
             data/raw/euda/DRD-19.xlsx  without opioids
             data/raw/euda/DRD-20.xlsx  unknown / mixed / unspecified
             data/raw/eurostat/demo_gind.csv (population)
      writes data/final/compare_drug_deaths_eu.csv

Each country reports its latest year (2021-2024) under its own national
definition, so the EU totals mix years and definitions (as EUDA's own totals do).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from us_eu_decompose import eurostat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EUDA = ROOT / "data" / "raw" / "euda"
TABLES = {"DRD-17": "known_tox", "DRD-18": "with_opioids", "DRD-19": "without_opioids", "DRD-20": "unknown_mixed"}
GEO = {"Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ",
       "Denmark": "DK", "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE", "Greece": "EL",
       "Hungary": "HU", "Ireland": "IE", "Italy": "IT", "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU",
       "Malta": "MT", "Netherlands": "NL", "Poland": "PL", "Portugal": "PT", "Romania": "RO", "Slovakia": "SK",
       "Slovenia": "SI", "Spain": "ES", "Sweden": "SE"}


def read(code: str) -> pd.DataFrame:
    d = pd.read_excel(EUDA / f"{code}.xlsx", header=3)
    d = d[["Country", "Year", "Definition", "Total"]].dropna(subset=["Country", "Total"])
    return d.rename(columns={"Total": TABLES[code]})


def main() -> None:
    t = read("DRD-17")
    for code in ("DRD-18", "DRD-19", "DRD-20"):
        t = t.merge(read(code)[["Country", TABLES[code]]], on="Country", how="outer")
    t["geo"] = t.Country.map(GEO)
    _, pop = eurostat()
    t["pop"] = [pop.at[int(y), g] if g in pop and int(y) in pop.index else float("nan") for g, y in zip(t.geo, t.Year)]
    eu = t[t.geo.notna()].copy()
    print("not EU members (left out):", sorted(t.Country[t.geo.isna()].tolist()))
    print("EU members missing:", sorted(set(GEO) - set(eu.Country)))
    for c in ("known_tox", "with_opioids", "without_opioids", "unknown_mixed"):
        eu[f"{c}_per_m"] = eu[c] / eu["pop"] * 1e6
    eu.round(2).to_csv(ROOT / "data" / "final" / "compare_drug_deaths_eu.csv", index=False)
    s = eu[["known_tox", "with_opioids", "without_opioids", "unknown_mixed", "pop"]].sum()
    print(eu[["Country", "Year", "known_tox", "with_opioids", "without_opioids", "unknown_mixed",
              "without_opioids_per_m"]].round(1).to_string(index=False))
    print("\nEU total:", s.round(0).to_dict())
    for c in ("known_tox", "with_opioids", "without_opioids"):
        print(f"  {c}: {s[c] / s['pop'] * 1e6:.1f} per million people")


if __name__ == "__main__":
    main()
