"""New passenger cars per year, split into SUVs and everything else, for the
EU-27 (2001-2025), with T&E's EU+UK+Norway end points and the US light-truck
split for comparison; plus T&E's average new-car bonnet height by year.

Reads  data/raw/icct/fig3-3_segments_extracted.csv (EU-27 SUV share; totals 2001-2012)
       data/raw/eurostat/road_eqr_carpda.csv        (EU-27 new car registrations, 2013+)
       data/raw/eurostat/demo_gind.csv              (EU-27 average population)
       data/raw/fred/LAUTOSA.csv, LTRUCKSA.csv, POPTHM.csv (US)
       data/raw/te/bonnet_height_digitised.csv
Writes data/final/eu_new_cars_suv.csv
       data/final/eu_bonnet_height.csv

    python scripts/build_eu_new_cars_suv.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, FINAL = ROOT / "data" / "raw", ROOT / "data" / "final"
ICCT = "ICCT European Vehicle Market Statistics Pocketbook 2025/26, Fig. 3-3 (values read from the PDF's vector paths)"


def main() -> None:
    icct = pd.read_csv(RAW / "icct" / "fig3-3_segments_extracted.csv").set_index("year")
    es = pd.read_csv(RAW / "eurostat" / "road_eqr_carpda.csv")
    es = es[(es.mot_nrg == "TOTAL") & (es.geo == "EU27_2020")].set_index("TIME_PERIOD").OBS_VALUE
    g = pd.read_csv(RAW / "eurostat" / "demo_gind.csv", low_memory=False)
    pop = g[(g.indic_de == "AVG") & (g.geo == "EU27_2020")].set_index("TIME_PERIOD").OBS_VALUE

    rows = []
    for y in range(2001, int(es.index.max()) + 1):
        share = icct.suv_share.get(y)
        if y in es.index:
            total, src = es[y], f"total: Eurostat road_eqr_carpda; SUV share: {ICCT}"
        else:
            total, src = icct.total_m[y] * 1e6, f"total and SUV share: {ICCT}"
        rows.append(dict(year=y, geo="EU27", total_new_cars=round(total), suv_share=share,
                         suv_count=round(total * share) if pd.notna(share) else None,
                         per_1000=round(total / pop[y] * 1000, 2), source=src,
                         definition="Passenger cars (M1); SUV = ICCT 'SUV/off-road' segment"))

    for y, share in ((2010, 0.115), (2024, 0.555)):
        rows.append(dict(year=y, geo="EU+UK+NO", suv_share=share, definition="Passenger cars (M1); SUV per EEA (2010) and Dataforce (2024)",
                         source="T&E 'Ever higher' (June 2025) p. 9: 11.5% (EEA data) and 55.5% (T&E analysis of Dataforce)"))

    fred = {}
    for s in ("LAUTOSA", "LTRUCKSA", "POPTHM"):
        f = pd.read_csv(RAW / "fred" / f"{s}.csv", parse_dates=[0])
        f = f[f.observation_date.dt.year <= 2025]  # complete years only
        fred[s] = f.groupby(f.observation_date.dt.year)[s].mean()
    for y in range(2000, 2026):
        cars, trucks = fred["LAUTOSA"][y] * 1e6, fred["LTRUCKSA"][y] * 1e6
        rows.append(dict(year=y, geo="US", total_new_cars=round(cars + trucks), suv_share=round(trucks / (cars + trucks), 3),
                         suv_count=round(trucks), per_1000=round((cars + trucks) / (fred["POPTHM"][y] * 1000) * 1000, 2),
                         source="BEA via FRED LAUTOSA + LTRUCKSA (annual mean of SAAR) / POPTHM",
                         definition="US light vehicles; 'suv' columns hold LIGHT TRUCKS (SUVs, crossovers, pickups, minivans), not SUVs alone"))

    out = pd.DataFrame(rows)[["year", "geo", "total_new_cars", "suv_share", "suv_count", "per_1000", "source", "definition"]]
    FINAL.mkdir(parents=True, exist_ok=True)
    out.to_csv(FINAL / "eu_new_cars_suv.csv", index=False)
    print(out.drop(columns=["source", "definition"]).to_string(index=False))

    b = pd.read_csv(RAW / "te" / "bonnet_height_digitised.csv")
    b["bonnet_height_cm"] = b.bonnet_height_cm.round(1)
    b["geo"] = "EU+UK+NO"
    b["source"] = "T&E 'Ever higher' (June 2025) p. 9 chart, digitised (+/-0.1 cm); T&E text gives 76.9 (2010) and 83.8 (2024)"
    b.to_csv(FINAL / "eu_bonnet_height.csv", index=False)
    print(b[["year", "bonnet_height_cm"]].to_string(index=False))


if __name__ == "__main__":
    main()
