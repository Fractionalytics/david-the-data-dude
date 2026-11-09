"""Pedestrian deaths per 100,000 people, 2000 onward: EU-27 (2020 borders),
five big Western European countries, and the US; then cross-check 2013 and 2022
against the CDC MMWR table.

Reads  data/raw/eurostat/tran_sf_roadus.csv  (deaths, pers_cat=PED)
       data/raw/eurostat/demo_gind.csv       (average population, indic_de=AVG)
       data/raw/dft/gb_pedestrian_deaths.csv (UK 2019+, Great Britain only)
       data/raw/iihs/pedestrian_deaths.csv + data/raw/fred/POPTHM.csv (US)
       data/raw/cdc/pedestrian_rates_by_country.csv
Writes data/final/eu_pedestrian_rates.csv
       data/final/eu_pedestrian_rates_vs_cdc.csv

    python scripts/build_eu_pedestrian_rates.py

Eurostat's own EU27_2020 total is just the sum of whichever members reported
(complete only from 2016), so the EU rate here divides reporting members'
deaths by reporting members' population, and logs who is missing.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, FINAL = ROOT / "data" / "raw", ROOT / "data" / "final"
EU27 = "AT BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK".split()
BIG5 = ["DE", "FR", "ES", "IT", "UK"]
CDC_NAMES = {"Austria": "AT", "Belgium": "BE", "Czechia": "CZ", "Denmark": "DK", "Finland": "FI", "France": "FR",
             "Germany": "DE", "Greece": "EL", "Hungary": "HU", "Ireland": "IE", "Italy": "IT", "Lithuania": "LT",
             "Netherlands": "NL", "Norway": "NO", "Poland": "PL", "Portugal": "PT", "Slovenia": "SI", "Spain": "ES",
             "Sweden": "SE", "Switzerland": "CH", "United Kingdom": "UK", "United States": "US"}
ES_SRC = "Eurostat tran_sf_roadus (deaths) / demo_gind AVG (population)"


def main() -> None:
    d = pd.read_csv(RAW / "eurostat" / "tran_sf_roadus.csv", low_memory=False)
    d = d[(d.pers_cat == "PED") & (d.sex == "T") & (d.age == "TOTAL") & (d.unit == "NR")]
    deaths = d.pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE").loc[2000:]
    g = pd.read_csv(RAW / "eurostat" / "demo_gind.csv", low_memory=False)
    pop = g[g.indic_de == "AVG"].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")

    rows = []
    for y, row in deaths[EU27].iterrows():
        rep = [c for c in EU27 if pd.notna(row[c])]
        p_rep, p_all = pop.loc[y, rep].sum(), pop.loc[y, EU27].sum()
        rows.append(dict(year=y, geo="EU27_2020", deaths=row[rep].sum(), population=p_rep, source=ES_SRC,
                         note=f"{len(rep)} of 27 members reporting ({p_rep / p_all:.1%} of EU-27 population); "
                              f"missing: {','.join(c for c in EU27 if c not in rep) or 'none'}"))
    for geo in BIG5:
        for y, v in deaths[geo].dropna().items():
            rows.append(dict(year=y, geo=geo, deaths=v, population=pop.loc[y, geo], source=ES_SRC, note=""))

    gb = pd.read_csv(RAW / "dft" / "gb_pedestrian_deaths.csv")
    for r in gb[gb.year > deaths["UK"].last_valid_index()].itertuples():
        rows.append(dict(year=r.year, geo="UK", deaths=r.pedestrian_deaths, population=pop.loc[r.year, "UK"],
                         source="DfT pedestrian factsheet 2024 (deaths, Great Britain) / Eurostat demo_gind AVG (UK population)",
                         note="GB deaths over UK population: excludes Northern Ireland (about 16 pedestrian deaths in 2018), "
                              "so the rate is about 3% low"))

    us = pd.read_csv(RAW / "iihs" / "pedestrian_deaths.csv")
    fp = pd.read_csv(RAW / "fred" / "POPTHM.csv", parse_dates=[0])
    us_pop = fp.groupby(fp.observation_date.dt.year).POPTHM.mean() * 1000
    for r in us[us.year >= 2000].itertuples():
        if r.year in us_pop.index:
            rows.append(dict(year=r.year, geo="US", deaths=r.pedestrian_deaths, population=round(us_pop[r.year]),
                             source="IIHS (FARS) deaths / FRED POPTHM annual mean population", note=""))

    out = pd.DataFrame(rows)
    out["rate_per_100k"] = (out.deaths / out.population * 1e5).round(3)
    out = out[["year", "geo", "deaths", "population", "rate_per_100k", "source", "note"]].sort_values(["geo", "year"])
    FINAL.mkdir(parents=True, exist_ok=True)
    out.to_csv(FINAL / "eu_pedestrian_rates.csv", index=False)
    w = out.pivot(index="year", columns="geo", values="rate_per_100k")
    print(w.round(2).to_string())

    # Cross-check every CDC country Eurostat covers (UK and US use the same rows as above).
    cdc = pd.read_csv(RAW / "cdc" / "pedestrian_rates_by_country.csv")
    chk = []
    for c in cdc.itertuples():
        geo = CDC_NAMES.get(c.country)
        if not geo:
            continue
        for y, cdc_rate in ((2013, c.ped_rate_2013), (2022, c.ped_rate_2022)):
            if geo == "US" or (geo == "UK" and y > 2018):
                m = out[(out.geo == geo) & (out.year == y)]
                dth, ours = (m.deaths.item(), m.rate_per_100k.item()) if len(m) else (None, None)
            else:
                dth = deaths.loc[y, geo] if geo in deaths else None
                ours = round(dth / pop.loc[y, geo] * 1e5, 3) if pd.notna(dth) else None
            chk.append(dict(country=c.country, geo=geo, year=y, deaths=dth, ours=ours, cdc=cdc_rate,
                            diff=None if ours is None else round(ours - cdc_rate, 3)))
    chk = pd.DataFrame(chk)
    chk.to_csv(FINAL / "eu_pedestrian_rates_vs_cdc.csv", index=False)
    print(chk.to_string())
    print("max |diff|:", chk["diff"].abs().max(), " rows with |diff| > 0.05:")
    print(chk[chk["diff"].abs() > 0.05].to_string())


if __name__ == "__main__":
    main()
