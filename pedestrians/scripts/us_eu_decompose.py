"""Why the US and EU pedestrian lines cross: a fixed-membership EU series, the
West/East split, pedestrians vs. everyone else on the road, and older pedestrians.

    python scripts/us_eu_decompose.py   (after fars_nonoccupants.py)
      -> data/final/us_eu_decompose.csv   year, geo, group, deaths, population, rate_per_100k

EU groups use only members that reported pedestrian deaths in every year
2000-2024, so changes in who reports can't move the line. West = members
before 2004; East = members from 2004 on. US pedestrians include people on
personal conveyances, the international definition (see fars_nonoccupants.py).
US non-pedestrian deaths = all motor-vehicle deaths (IIHS) minus those.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, FINAL = ROOT / "data" / "raw", ROOT / "data" / "final"
EU27 = "AT BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK".split()
WEST = "AT BE DE DK EL ES FI FR IE IT LU NL PT SE".split()
YEARS = range(2000, 2025)


def eurostat() -> tuple[pd.DataFrame, pd.DataFrame]:
    d = pd.read_csv(RAW / "eurostat" / "tran_sf_roadus.csv", low_memory=False)
    d = d[(d.sex == "T") & (d.unit == "NR")]
    g = pd.read_csv(RAW / "eurostat" / "demo_gind.csv", low_memory=False)
    pop = g[g.indic_de == "AVG"].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    return d, pop


def main() -> None:
    d, pop = eurostat()
    ped = d[(d.pers_cat == "PED") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    tot = d[(d.pers_cat == "TOTAL") & (d.age == "TOTAL")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    old = d[(d.pers_cat == "PED") & (d.age == "Y_GE65")].pivot_table(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    full = [c for c in EU27 if ped.reindex(YEARS)[c].notna().all() and tot.reindex(YEARS)[c].notna().all()]
    print(f"{len(full)} members report every year 2000-2024: {' '.join(full)}")
    print(f"missing some year: {' '.join(c for c in EU27 if c not in full)}")

    rows = []
    groups = {"EU fixed": full, "EU West": [c for c in full if c in WEST], "EU East": [c for c in full if c not in WEST]}
    for name, members in groups.items():
        for y in YEARS:
            p = pop.loc[y, members].sum()
            rows += [dict(year=y, geo=name, group="pedestrian", deaths=ped.loc[y, members].sum(), population=p),
                     dict(year=y, geo=name, group="other road users",
                          deaths=tot.loc[y, members].sum() - ped.loc[y, members].sum(), population=p)]
            o = old.reindex(YEARS).loc[y, members]
            if o.notna().all():
                rows.append(dict(year=y, geo=name, group="pedestrian 65+", deaths=o.sum(), population=p))

    us = pd.read_csv(FINAL / "fars_nonoccupant_deaths.csv").set_index("year")
    allmv = pd.read_csv(RAW / "iihs" / "pedestrian_deaths.csv").set_index("year").all_motor_vehicle_deaths
    up = pd.read_csv(RAW / "fred" / "POPTHM.csv", parse_dates=[0]).set_index("observation_date").iloc[:, 0]
    up = up.groupby(up.index.year).mean() * 1000
    for y in YEARS:
        rows += [dict(year=y, geo="US", group="pedestrian", deaths=us.loc[y, "ped_plus_conveyance"], population=up[y]),
                 dict(year=y, geo="US", group="other road users",
                      deaths=allmv[y] - us.loc[y, "ped_plus_conveyance"], population=up[y])]

    out = pd.DataFrame(rows)
    out["rate_per_100k"] = (out.deaths / out.population * 1e5).round(3)
    out.to_csv(FINAL / "us_eu_decompose.csv", index=False)
    t = out.pivot_table(index="year", columns=["geo", "group"], values="rate_per_100k")
    print(t.loc[[2000, 2005, 2009, 2010, 2013, 2019, 2022, 2024]].round(2).T.to_string())


if __name__ == "__main__":
    main()
