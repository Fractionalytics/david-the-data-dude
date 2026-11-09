"""Pre-registered tests P1-P3 (docs/hypothesis-test.md): do pedestrian deaths
grow faster in poor, middle-density and car-free census tracts?

    python scripts/test_tracts.py tracts     download 2010 TIGER/Line tracts (cached)
    python scripts/test_tracts.py locate     geolocate deaths to tracts
    python scripts/test_tracts.py acs        download ACS 2008-12 tract data (needs
                                             CENSUS_DATA_API_KEY in the root .env; cached)
    python scripts/test_tracts.py analyze    quintile tables and PASS/FAIL
      reads  data/raw/fars/FARS<YEAR>NationalCSV.zip (2009-11, 2020-22)
             data/raw/tiger/tl_2010_<SS>_tract10.zip (www2.census.gov, 51 files)
             data/raw/acs/acs5_2012_<SS>.json        (api.census.gov, one per state)
      writes data/final/test_tracts_deaths.csv       one row per pedestrian death
             data/final/test_tracts_coverage.csv     deaths with/without a tract, by year
             data/final/test_tracts_tracts.csv       tract values and quintiles
             data/final/test_tracts_p1_poverty.csv
             data/final/test_tracts_p2_density.csv
             data/final/test_tracts_p3_novehicle.csv
             data/final/test_tracts_extra_dark.csv          (not pre-registered)
             data/final/test_tracts_extra_poverty_density.csv  (not pre-registered)

Steps
  1. Deaths: PERSON PER_TYP 5, INJ_SEV 4, joined to ACCIDENT LATITUDE/LONGITUD
     and LGT_COND on ST_CASE within each year. Coordinates are invalid when
     latitude is outside 17-72 or longitude outside -180 to -60 (covers the
     77.7777 / 88.8888 / 99.9999 and 777.7777 / 888.8888 / 999.9999 codes, and
     blanks). Dark = LGT_COND 2, 3, 6.
  2. Each valid point is joined to the 2010 tract polygon that contains it
     (TIGER/Line, full resolution, so points on bridges and shorelines still
     land). The tract's state is checked against the state in ST_CASE.
  3. Tract values from ACS 2008-12: poverty rate B17001_002E / B17001_001E;
     density B01003_001E / ALAND10 (per km2); no-vehicle share
     (B25044_003E + B25044_010E) / B25044_001E. Tracts with a zero denominator
     get no value and no quintile.
  4. Population-weighted quintiles: tracts sorted by value (ties by GEOID),
     each tract's quintile set by where its population midpoint falls in the
     cumulative national population, so each quintile holds about a fifth.
  5. Per quintile: population, deaths per year 2009-11 and 2020-22, rate per
     100k (ACS population), % change in rate, share of 2009-11 deaths, share of
     added deaths. Shares use deaths in tracts that have a quintile.
  P3 (decided before running): no-vehicle quintiles are the national ones from
  step 4, restricted to tracts in density quintiles 2-4. As a labeled
  sensitivity, quintiles recomputed within the density 2-4 tracts are also
  reported; the national version decides PASS/FAIL.
"""

import json
import os
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fars_pedestrians import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TIGER = ROOT / "data" / "raw" / "tiger"
ACS = ROOT / "data" / "raw" / "acs"
FINAL = ROOT / "data" / "final"
UA = {"User-Agent": "content-engine-research-bot/1.0"}
STATES = ["01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16", "17", "18",
          "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
          "34", "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48", "49",
          "50", "51", "53", "54", "55", "56"]
PRE, POST = [2009, 2010, 2011], [2020, 2021, 2022]
ACS_VARS = ["B01003_001E", "B17001_001E", "B17001_002E", "B25044_001E", "B25044_003E", "B25044_010E"]


def get(url: str) -> requests.Response:
    r = requests.get(url, headers=UA, timeout=180)
    print(r.status_code, r.headers.get("content-type"), len(r.content), url.split("?")[0], flush=True)
    if r.status_code in (403, 429) or "text/html" in (r.headers.get("content-type") or ""):
        raise SystemExit(f"blocked or not data ({r.status_code}), stopping: {url.split('?')[0]}")
    r.raise_for_status()
    return r


def fetch_tracts() -> None:
    TIGER.mkdir(parents=True, exist_ok=True)
    for s in STATES:
        dest = TIGER / f"tl_2010_{s}_tract10.zip"
        if dest.exists():
            continue
        dest.write_bytes(get(f"https://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/{dest.name}").content)
        time.sleep(1)


def read_tracts() -> gpd.GeoDataFrame:
    parts = [gpd.read_file(f"zip://{TIGER / f'tl_2010_{s}_tract10.zip'}")[["GEOID10", "STATEFP10", "ALAND10", "geometry"]]
             for s in STATES]
    t = pd.concat(parts, ignore_index=True)
    return gpd.GeoDataFrame(t, geometry="geometry", crs=parts[0].crs)


def deaths() -> pd.DataFrame:
    frames = []
    for y in PRE + POST:
        p = load(y, "person", ["ST_CASE", "PER_TYP", "INJ_SEV"])
        a = load(y, "accident", ["ST_CASE", "LATITUDE", "LONGITUD", "LGT_COND"])
        missing = {"ST_CASE", "LATITUDE", "LONGITUD", "LGT_COND"} - set(a.columns)
        if missing or "ST_CASE" not in p:
            raise SystemExit(f"{y}: columns missing {missing}")
        d = p[(p.PER_TYP == 5) & (p.INJ_SEV == 4)].merge(a, on="ST_CASE", how="left", validate="m:1")
        d["year"] = y
        frames.append(d[["year", "ST_CASE", "LATITUDE", "LONGITUD", "LGT_COND"]])
    d = pd.concat(frames, ignore_index=True)
    d["state_fips"] = (d.ST_CASE // 10000).astype(int).map("{:02d}".format)
    d["valid_xy"] = d.LATITUDE.between(17, 72) & d.LONGITUD.between(-180, -60)
    d["dark"] = d.LGT_COND.isin([2, 3, 6])
    return d


def locate() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    d = deaths()
    tr = read_tracts()
    v = d[d.valid_xy]
    pts = gpd.GeoDataFrame(v, geometry=gpd.points_from_xy(v.LONGITUD, v.LATITUDE), crs="EPSG:4269")
    j = gpd.sjoin(pts, tr.to_crs("EPSG:4269"), how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]  # a point on a shared edge can match two tracts
    d["GEOID10"] = j.GEOID10.reindex(d.index)
    d["tract_state"] = j.STATEFP10.reindex(d.index)
    d["state_mismatch"] = d.GEOID10.notna() & (d.tract_state != d.state_fips)
    d.drop(columns="tract_state").to_csv(FINAL / "test_tracts_deaths.csv", index=False)
    cov = d.groupby("year").agg(deaths=("valid_xy", "size"), invalid_xy=("valid_xy", lambda s: (~s).sum()),
                                valid_no_tract=("GEOID10", lambda s: 0), in_tract=("GEOID10", lambda s: s.notna().sum()),
                                tract_in_other_state=("state_mismatch", "sum"))
    cov["valid_no_tract"] = cov.deaths - cov.invalid_xy - cov.in_tract
    cov["in_tract_share"] = (cov.in_tract / cov.deaths).round(4)
    cov.to_csv(FINAL / "test_tracts_coverage.csv")
    print(cov.to_string())


def fetch_acs() -> None:
    key = os.environ.get("CENSUS_DATA_API_KEY")
    if not key:
        env = ROOT.parents[1] / ".env"
        for line in env.read_text().splitlines() if env.exists() else []:
            if line.startswith("CENSUS_DATA_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key or key == "REPLACE_ME":
        raise SystemExit("api.census.gov asks for a key: add CENSUS_DATA_API_KEY to the root .env")
    ACS.mkdir(parents=True, exist_ok=True)
    for s in STATES:
        dest = ACS / f"acs5_2012_{s}.json"
        if dest.exists():
            continue
        url = (f"https://api.census.gov/data/2012/acs/acs5?get={','.join(ACS_VARS)}"
               f"&for=tract:*&in=state:{s}&key={key}")
        dest.write_text(json.dumps(get(url).json()))
        time.sleep(1)


def quintile(df: pd.DataFrame, col: str) -> pd.Series:
    t = df[df[col].notna() & (df.pop_ > 0)].sort_values([col, "GEOID10"])
    mid = t.pop_.cumsum() - t.pop_ / 2
    return (np.floor(mid / t.pop_.sum() * 5) + 1).clip(1, 5).astype(int).reindex(df.index)


def tract_values() -> pd.DataFrame:
    rows = []
    for s in STATES:
        js = json.loads((ACS / f"acs5_2012_{s}.json").read_text())
        rows.append(pd.DataFrame(js[1:], columns=js[0]))
    a = pd.concat(rows, ignore_index=True)
    a["GEOID10"] = a.state + a.county + a.tract
    for c in ACS_VARS:
        a[c] = pd.to_numeric(a[c], errors="coerce").where(lambda x: x >= 0)
    land = read_tracts()[["GEOID10", "ALAND10"]]
    t = land.merge(a[["GEOID10"] + ACS_VARS], on="GEOID10", how="left", validate="1:1")
    t["pop_"] = t.B01003_001E.fillna(0)
    t["poverty"] = (t.B17001_002E / t.B17001_001E).where(t.B17001_001E > 0)
    t["density"] = (t.pop_ / (t.ALAND10 / 1e6)).where((t.ALAND10 > 0) & (t.pop_ > 0))
    t["novehicle"] = ((t.B25044_003E + t.B25044_010E) / t.B25044_001E).where(t.B25044_001E > 0)
    for c in ["poverty", "density", "novehicle"]:
        t[f"q_{c}"] = quintile(t, c)
    return t


def qtable(d: pd.DataFrame, t: pd.DataFrame, qcol: str) -> pd.DataFrame:
    pop = t.groupby(qcol).pop_.sum()
    dd = d[d[qcol].notna()]
    pre = dd[dd.year.isin(PRE)].groupby(qcol).size() / 3
    post = dd[dd.year.isin(POST)].groupby(qcol).size() / 3
    o = pd.DataFrame({"pop_2010": pop, "deaths_2009_11": pre, "deaths_2020_22": post}).fillna(0)
    o.index = o.index.astype(int)
    o.index.name = "quintile"
    o["rate_2009_11"] = o.deaths_2009_11 / o.pop_2010 * 1e5
    o["rate_2020_22"] = o.deaths_2020_22 / o.pop_2010 * 1e5
    o["pct_change_rate"] = (o.rate_2020_22 / o.rate_2009_11 - 1) * 100
    o["share_2009_11"] = o.deaths_2009_11 / o.deaths_2009_11.sum()
    added = o.deaths_2020_22 - o.deaths_2009_11
    o["share_added"] = added / added.sum()
    return o.round(4)


def analyze() -> None:
    t = tract_values()
    t.drop(columns="geometry", errors="ignore").to_csv(FINAL / "test_tracts_tracts.csv", index=False)
    d = pd.read_csv(FINAL / "test_tracts_deaths.csv", dtype={"GEOID10": str})
    d = d[d.GEOID10.notna()].merge(t[["GEOID10", "q_poverty", "q_density", "q_novehicle"]], on="GEOID10", how="left")
    print("deaths in a tract with no quintile:", {c: int(d[c].isna().sum()) for c in ["q_poverty", "q_density", "q_novehicle"]})

    p1, p2 = qtable(d, t, "q_poverty"), qtable(d, t, "q_density")
    mid_t = t[t.q_density.between(2, 4)].copy()
    mid_d = d[d.q_density.between(2, 4)].copy()
    p3 = qtable(mid_d, mid_t, "q_novehicle")
    mid_t["q_novehicle_within"] = quintile(mid_t, "novehicle")
    mid_d = mid_d.merge(mid_t[["GEOID10", "q_novehicle_within"]], on="GEOID10", how="left")
    p3w = qtable(mid_d, mid_t, "q_novehicle_within")
    p1.to_csv(FINAL / "test_tracts_p1_poverty.csv")
    p2.to_csv(FINAL / "test_tracts_p2_density.csv")
    pd.concat({"national_quintiles": p3, "within_middle_density_sensitivity": p3w}, names=["version"]).to_csv(
        FINAL / "test_tracts_p3_novehicle.csv")

    c1 = p1.loc[5, "share_added"] > p1.loc[5, "share_2009_11"]
    c2 = p1.loc[5, "pct_change_rate"] > p1.loc[1, "pct_change_rate"]
    mid_share = p2.loc[[2, 3, 4], "deaths_2020_22"].sum() - p2.loc[[2, 3, 4], "deaths_2009_11"].sum()
    mid_share /= p2.deaths_2020_22.sum() - p2.deaths_2009_11.sum()
    mid_rate = (p2.loc[[2, 3, 4], "deaths_2020_22"].sum() / p2.loc[[2, 3, 4], "deaths_2009_11"].sum() - 1) * 100
    p2a, p2b = mid_share > 0.5, mid_rate > p2.loc[5, "pct_change_rate"]
    p3a = p3.loc[5, "pct_change_rate"] > p3.loc[1, "pct_change_rate"]
    for name, tab in [("P1 poverty", p1), ("P2 density", p2), ("P3 no-vehicle, density 2-4", p3),
                      ("P3 sensitivity: quintiles within density 2-4", p3w)]:
        print(f"\n== {name}\n{tab.to_string()}")
    print(f"\nP1 {'PASS' if c1 and c2 else 'FAIL'}: top share added {p1.loc[5, 'share_added']:.3f} vs 2009-11 "
          f"{p1.loc[5, 'share_2009_11']:.3f}; rate change Q5 {p1.loc[5, 'pct_change_rate']:.1f}% vs Q1 {p1.loc[1, 'pct_change_rate']:.1f}%")
    print(f"P2 {'PASS' if p2a and p2b else 'FAIL'}: Q2-4 share of added {mid_share:.3f}; Q2-4 rate change {mid_rate:.1f}% "
          f"vs densest {p2.loc[5, 'pct_change_rate']:.1f}%")
    print(f"P3 {'PASS' if p3a else 'FAIL'}: Q5 {p3.loc[5, 'pct_change_rate']:.1f}% vs Q1 {p3.loc[1, 'pct_change_rate']:.1f}%")

    # Not pre-registered: dark vs. not dark, and poverty x density.
    ex = []
    for dark in [True, False]:
        dd = d[d.dark == dark]
        mid = dd[dd.q_density.between(2, 4)]
        for test, tab in [("P1_poverty", qtable(dd, t, "q_poverty")), ("P2_density", qtable(dd, t, "q_density")),
                          ("P3_novehicle_density2_4", qtable(mid, mid_t, "q_novehicle"))]:
            ex.append(tab.assign(test=test, dark=dark).reset_index())
    ex = pd.concat(ex)[["test", "dark"] + list(p1.reset_index().columns)]
    ex.to_csv(FINAL / "test_tracts_extra_dark.csv", index=False)
    print("\n== NOT PRE-REGISTERED: dark vs not dark\n" + ex.to_string(index=False))
    cr = []
    for qd in range(1, 6):
        tab = qtable(d[d.q_density == qd], t[t.q_density == qd], "q_poverty")
        cr.append(tab.assign(density_quintile=qd).reset_index().rename(columns={"quintile": "poverty_quintile"}))
    cr = pd.concat(cr)
    cr.to_csv(FINAL / "test_tracts_extra_poverty_density.csv", index=False)
    print("\n== NOT PRE-REGISTERED: % change in rate, poverty (rows) x density (cols)")
    print(cr.pivot(index="poverty_quintile", columns="density_quintile", values="pct_change_rate").round(1).to_string())


if __name__ == "__main__":
    {"tracts": fetch_tracts, "locate": locate, "acs": fetch_acs, "analyze": analyze}[sys.argv[1]]()
