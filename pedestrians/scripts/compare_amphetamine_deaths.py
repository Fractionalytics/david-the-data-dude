"""US vs. Europe deaths from amphetamine use disorders, per 100,000 (WHO Global
Health Estimates 2021, via Our World in Data), 2000-2021.

    python scripts/compare_amphetamine_deaths.py
      reads  data/raw/who_ghe/death-rate-amphetamine-who.csv
             (downloaded 2026-11-10 from ourworldindata.org/grapher/death-rate-amphetamine-who.csv)
             data/final/eu_pedestrian_rates.csv  (country list and population weights)
      writes data/final/compare_amphetamine_deaths.csv

"Europe" = the EU members in the Reel's pedestrian comparison, weighted by
population. WHO's cause "amphetamine use disorders" covers deaths attributed to
amphetamine-type stimulants (including methamphetamine) as the underlying
cause; it is a modelled estimate built to be comparable across countries, not a
count of death certificates.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from us_eu_decompose import EU27, YEARS, eurostat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE", "DE": "DEU", "DK": "DNK", "EE": "EST",
        "EL": "GRC", "ES": "ESP", "FI": "FIN", "FR": "FRA", "HR": "HRV", "HU": "HUN", "IE": "IRL", "IT": "ITA",
        "LT": "LTU", "LU": "LUX", "LV": "LVA", "MT": "MLT", "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU",
        "SE": "SWE", "SI": "SVN", "SK": "SVK"}

w = pd.read_csv(ROOT / "data/raw/who_ghe/death-rate-amphetamine-who.csv")
w.columns = ["entity", "code", "year", "rate"]
d, pop = eurostat()
ped = d[(d.pers_cat == "PED") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
tot = d[(d.pers_cat == "TOTAL") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
full = [c for c in EU27 if ped.reindex(YEARS)[c].notna().all() and tot.reindex(YEARS)[c].notna().all()]
print("EU members (same rule as us_eu_decompose.py):", full, len(full))
eu = pop[full].stack().rename("population").reset_index()
eu.columns = ["year", "geo", "population"]
eu = eu.assign(code=eu.geo.map(ISO3))
m = eu.merge(w, on=["code", "year"])
agg = m.groupby("year").apply(lambda x: (x.rate * x.population).sum() / x.population.sum()).rename("eu")
us = w[w.code == "USA"].set_index("year").rate.rename("us")
cz = w[w.code == "CZE"].set_index("year").rate.rename("czechia")
sk = w[w.code == "SVK"].set_index("year").rate.rename("slovakia")
out = pd.concat([us, agg, cz, sk], axis=1).loc[2000:2021]
out["us_to_eu"] = out.us / out.eu
out.round(3).to_csv(ROOT / "data/final/compare_amphetamine_deaths.csv")
print(out.loc[[2000, 2005, 2009, 2010, 2011, 2015, 2019, 2020, 2021]].round(3).to_string())
last = w[(w.year == 2021) & w.code.notna() & ~w.code.astype(str).str.startswith("OWID")]
print("\n2021 highest:\n", last.sort_values("rate", ascending=False).head(8)[["entity", "rate"]].to_string(index=False))
