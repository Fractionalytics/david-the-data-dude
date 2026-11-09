"""Export the numbers the Reel's charts draw, so the video never hard-codes data.

    python scripts/export_video_data.py
      reads  data/final/us_eu_decompose.csv      US and EU (18 fixed members) pedestrian rates
             data/final/test_ped_drugs.csv        stimulant-positive share of tested pedestrians killed
             data/final/test_meth_wonder.csv      state meth overdose vs. pedestrian rate changes (P10)
             data/final/fars_ped_totals_check.csv US pedestrian deaths by year
      writes video/src/data/data.json
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "data" / "final"


def main() -> None:
    d = pd.read_csv(FINAL / "us_eu_decompose.csv")
    rates = {}
    for geo, key in (("US", "us"), ("EU fixed", "eu")):
        s = d[(d.geo == geo) & (d.group == "pedestrian")].sort_values("year")
        rates[key] = [{"year": int(y), "rate": round(float(r), 3)} for y, r in zip(s.year, s.rate_per_100k)]

    t = pd.read_csv(FINAL / "test_ped_drugs.csv")
    t = t[(t.definition == "primary") & t.year.astype(str).str.fullmatch(r"\d{4}")]
    stim = [{"year": int(y), "share": round(float(s) / float(n), 4)} for y, s, n in zip(t.year, t.stimulant, t.tested)]

    w = pd.read_csv(FINAL / "test_meth_wonder.csv")
    w = w[w.included == True]  # noqa: E712
    states = [{"state": s, "meth": round(float(m), 2), "ped": round(float(p), 3)}
              for s, m, p in zip(w.state, w.meth_rate_change, w.ped_rate_change)]

    tot = pd.read_csv(FINAL / "fars_ped_totals_check.csv")
    deaths = [{"year": int(y), "deaths": int(n)} for y, n in zip(tot.year, tot.fars_ped_deaths)]

    # Card 8: share of new vehicles. Europe (EU27, ICCT) = SUVs; US (BEA) = all light trucks.
    e = pd.read_csv(FINAL / "eu_new_cars_suv.csv")
    suv = {k: [{"year": int(y), "share": round(float(s), 3)} for y, s in zip(g.year, g.suv_share) if pd.notna(s) and y <= 2024]
           for k, g in (("eu", e[e.geo == "EU27"]), ("us", e[e.geo == "US"]))}

    # Card 25: P1 poverty quintiles, % change in pedestrian death rate 2009-11 -> 2020-22.
    q = pd.read_csv(FINAL / "test_tracts_p1_poverty.csv")
    poverty = [{"q": int(a), "pct": round(float(b), 1)} for a, b in zip(q.quintile, q.pct_change_rate)]

    # Card 48: US psychostimulant (T43.6) overdose deaths, CDC VSRR provisional, 12 months ending December.
    v = pd.read_csv(ROOT / "data" / "raw" / "cdc_meth" / "vsrr_provisional_drug_overdose_xkb8-kh2a.csv")
    v = v[(v.State == "US") & (v.Indicator == "Psychostimulants with abuse potential (T43.6)")
          & (v.Month == "December") & (v.Period == "12 month-ending")]
    meth = [{"year": int(y), "deaths": int(d)} for y, d in zip(v.Year, v["Data Value"])]

    # Card 51: pedestrians vs. everyone else killed on the road, FARS 2015-2024 plus 2025 projections
    # (pedestrians: GHSA, 6,732; all traffic deaths: NHTSA early estimate DOT HS 813 800, 36,640).
    fatals = {2015: 35484, 2016: 37806, 2017: 37473, 2018: 36835, 2019: 36355, 2020: 39007, 2021: 43230,
              2022: 42721, 2023: 41025, 2024: 39254, 2025: 36640}  # FARS ACCIDENT.FATALS sums; 2025 NHTSA estimate
    ped = {d["year"]: d["deaths"] for d in deaths}
    ped[2025] = 6732
    road = [{"year": y, "ped": ped[y], "other": fatals[y] - ped[y], "projected": y == 2025} for y in sorted(fatals)]

    out = ROOT / "video" / "src" / "data" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"rates": rates, "stimulant": stim, "states": states, "deaths": deaths, "suv": suv,
                               "poverty": poverty, "meth": meth, "road": road}, indent=1))
    print("wrote", out, "| states", len(states), "| stim years", len(stim))


if __name__ == "__main__":
    main()
